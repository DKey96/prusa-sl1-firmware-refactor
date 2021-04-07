# This file is part of the SL1 firmware
# Copyright (C) 2021 Prusa Development a.s. - www.prusa3d.com
# SPDX-License-Identifier: GPL-3.0-or-later

# DAC datasheet: https://www.ti.com/lit/ds/symlink/dac43401.pdf
# GPIO datasheet: https://www.mouser.com/datasheet/2/115/PI4IOE5V9536-1107656.pdf
# EEPROM datasheet: https://www.mouser.com/datasheet/2/268/Atmel-8815-SEEPROM-AT24CS01-02-Datasheet-1368744.pdf

import logging
from time import sleep
from typing import Optional
from smbus2 import SMBus, i2c_msg

from sl1fw.errors.exceptions import BoosterError

class Booster:

    I2C_BUS_ID = 3
    DAC_ADDR = 0x48
    GPIO_ADDR = 0x41
    EEPROM_ADDR = 0x50
    SN_ADDR = 0x58

    DAC_STATUS = 0xD0
    DAC_GENERAL_CONFIG = 0xD1
    DAC_MED_ALARM_CONFIG = 0xD2
    DAC_TRIGGER = 0xD3
    DAC_DATA = 0x21
    DAC_MARGIN_HIGH = 0x25
    DAC_MARGIN_LOW = 0x26
    DAC_PMBUS_OP = 0x01
    DAC_PMBUS_STATUS_BYTE = 0x78
    DAC_PMBUS_VERSION = 0x98

    EEPROM_PAGE_SIZE = 8
    EEPROM_WRITE_CYCLE_TIME = 0.005 # 5 ms

    def __init__(self):
        self._logger = logging.getLogger(__name__)
        self._bus: Optional[SMBus] = None
        self._sn = ""

    def __del__(self):
        self.disconnect()

    def connect(self) -> None:
        self._bus = SMBus(self.I2C_BUS_ID)

        # EEPROM
        try:
            self._eeprom_read_serial()
        except Exception as e:
            raise BoosterError("EEPROM read serial") from e
        self._logger.info("Booster SN: %s", self._sn)

        # DAC
        try:
            status = self._dac_read(self.DAC_STATUS)
        except Exception as e:
            raise BoosterError("DAC read status") from e
        if (status & 0x3F) != 0x14:
            raise BoosterError("DAC wrong status (0x%04X)" % status)
        # Spock! TODO something!
        if status & (1 << 12):
            self._logger.warning("DAC_UPDATE_BUSY")
        if status & (1 << 13):
            self._logger.warning("DAC_NVM_BUSY")
        if status & (1 << 14):
            self._logger.warning("DAC_NVM_CRC_ALARM_INTERNAL")
        if status & (1 << 15):
            self._logger.warning("DAC_NVM_CRC_ALARM_USER")
        # power-up the output, enable internal reference with 2x output span
        self._dac_write(self.DAC_GENERAL_CONFIG, 0x1E5)

        # GPIO
        try:
            self.status()
        except Exception as e:
            raise BoosterError("GPIO read") from e

    def disconnect(self) -> None:
        if self._bus:
            self._bus.close()

    def eeprom_read_byte(self, address: int) -> int:
        return self.eeprom_read_block(address, 1)[0]

    def eeprom_read_block(self, address: int, count: int) -> list:
        data = self._bus.read_i2c_block_data(self.EEPROM_ADDR, address, count if count < 32 else 32)
        count -= 32
        if count > 0:
            msg = i2c_msg.read(self.EEPROM_ADDR, count)
            self._bus.i2c_rdwr(msg)
            data += list(msg)
        self._logger.debug("data: %s", " ".join("{:02X}".format(x) for x in data))
        return data

    def eeprom_write_byte(self, address: int, value: int) -> None:
        self.eeprom_write_block(address, list((value,)))

    def eeprom_write_block(self, address: int, values: list) -> None:
        size = self.EEPROM_PAGE_SIZE - (address % self.EEPROM_PAGE_SIZE)
        if size:
            self._logger.debug("head %d byte(s)", size)
            self._bus.write_i2c_block_data(self.EEPROM_ADDR, address, values[:size])
            sleep(self.EEPROM_WRITE_CYCLE_TIME)
            address += size
        while size + self.EEPROM_PAGE_SIZE <= len(values):
            self._logger.debug("body %d byte(s)", self.EEPROM_PAGE_SIZE)
            self._bus.write_i2c_block_data(self.EEPROM_ADDR, address, values[size:size + self.EEPROM_PAGE_SIZE])
            sleep(self.EEPROM_WRITE_CYCLE_TIME)
            address += self.EEPROM_PAGE_SIZE
            size += self.EEPROM_PAGE_SIZE
        tail = len(values) - size
        self._logger.debug("tail %d byte(s)", tail)
        if tail:
            self._bus.write_i2c_block_data(self.EEPROM_ADDR, address, values[size:])
            sleep(self.EEPROM_WRITE_CYCLE_TIME)

    # TODO return something to check OK/NOK
    def status(self) -> None:
        status = self._bus.read_byte_data(self.GPIO_ADDR, 0)
        self._logger.debug("GPIO reg0: 0x%02X", status)
        self._logger.info("LED channel 0 is %s", "ON" if status & 1 else "OFF")
        self._logger.info("LED channel 1 is %s", "ON" if status & (1 << 1) else "OFF")
        self._logger.info("LED channel 2 is %s", "ON" if status & (1 << 2) else "OFF")
        self._logger.info("DAC is %s", "ON" if status & (1 << 3) else "OFF")

    @property
    def pwm(self) -> int:
        return self._dac_read(self.DAC_DATA) >> 4

    @pwm.setter
    def pwm(self, pwm: int) -> None:
        self._dac_write(self.DAC_DATA, pwm << 4)
        # TODO should be here?
        self.status()

    @property
    def board_serial_no(self) -> str:
        return self._sn

    def _dac_read(self, register: int) -> int:
        msb, lsb = self._bus.read_i2c_block_data(self.DAC_ADDR, register, 2)
        value = msb * 256 + lsb
        self._logger.debug("DAC read 0x%04X <- 0x%02X", value, register)
        return value

    def _dac_write(self, register: int, value: int) -> None:
        self._logger.debug("DAC write 0x%04X -> 0x%02X", value, register)
        self._bus.write_i2c_block_data(self.DAC_ADDR, register, (value // 256, value % 256))

    def _eeprom_read_serial(self) -> None:
        serial = self._bus.read_i2c_block_data(self.SN_ADDR, 0x80, 16)
        self._sn = "".join("{:02X}".format(x) for x in serial)
