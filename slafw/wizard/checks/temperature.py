# This file is part of the SLA firmware
# Copyright (C) 2020-2021 Prusa Research a.s. - www.prusa3d.com
# SPDX-License-Identifier: GPL-3.0-or-later

from dataclasses import dataclass, asdict
from threading import Thread
from time import sleep
from typing import Dict, Any, Optional

from slafw import defines
from slafw.functions.system import shut_down
from slafw.libHardware import Hardware
from slafw.wizard.actions import UserActionBroker
from slafw.wizard.checks.base import WizardCheckType, Check
from slafw.wizard.setup import Configuration
from slafw.errors.errors import A64Overheat, TempSensorFailed, TempSensorNotInRange


@dataclass
class CheckData:
    # UV LED temperature at the beginning of test (should be close to ambient)
    wizardTempUvInit: float
    # ambient sensor temperature
    wizardTempAmbient: float
    # A64 temperature
    wizardTempA64: float


class TemperatureTest(Check):
    def __init__(self, hw: Hardware):
        super().__init__(
            WizardCheckType.TEMPERATURE, Configuration(None, None), [],
        )
        self._hw = hw
        self._check_data: Optional[CheckData] = None

    async def async_task_run(self, actions: UserActionBroker):
        self._logger.debug("Checking temperatures")

        # A64 overheat check
        self._logger.info("Checking A64 for overheating")
        a64_temperature = self._hw.getCpuTemperature()
        if a64_temperature > defines.maxA64Temp:
            Thread(target=self._overheat, daemon=True).start()
            raise A64Overheat(a64_temperature)

        # Checking MC temperatures
        self._logger.info("Checking MC temperatures")
        temperatures = self._hw.getMcTemperatures()
        led_idx = self._hw.led_temp_idx
        ambient_idx = self._hw.ambient_temp_idx
        for i in (led_idx, ambient_idx):
            if temperatures[i] < 0:
                raise TempSensorFailed(self._hw.getSensorName(i))
            if i == led_idx:
                max_temp = defines.maxUVTemp
            else:
                max_temp = defines.maxAmbientTemp
            if not defines.minAmbientTemp < temperatures[i] < max_temp:
                raise TempSensorNotInRange(
                    self._hw.getSensorName(i),
                    temperatures[i]
                )

        self._check_data = CheckData(temperatures[led_idx], temperatures[ambient_idx], a64_temperature)

    def _overheat(self):
        for _ in range(10):
            self._hw.beepAlarm(3)
            sleep(1)
        shut_down(self._hw)

    def get_result_data(self) -> Dict[str, Any]:
        return asdict(self._check_data)