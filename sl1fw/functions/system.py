# This file is part of the SL1 firmware
# Copyright (C) 2014-2018 Futur3d - www.futur3d.net
# Copyright (C) 2018-2019 Prusa Research s.r.o. - www.prusa3d.com
# Copyright (C) 2020 Prusa Development a.s. - www.prusa3d.com
# SPDX-License-Identifier: GPL-3.0-or-later

import logging
import os
import subprocess
from math import isclose

from sl1fw import defines, test_runtime
from sl1fw.configs.hw import HwConfig
from sl1fw.configs.toml import TomlConfig
from sl1fw.errors.errors import (
    FailedUpdateChannelSet,
    FailedUpdateChannelGet,
    ConfigException, DisplayTransmittanceNotValid, CalculatedUVPWMNotInRange,
)
from sl1fw.hardware.printer_model import PrinterModel
from sl1fw.image.exposure_image import ExposureImage
from sl1fw.libHardware import Hardware


def shut_down(hw: Hardware, reboot=False):
    if test_runtime.testing:
        print("Skipping poweroff due to testing")
        return

    hw.uvLed(False)
    hw.motorsRelease()

    if reboot:
        os.system("reboot")
    else:
        os.system("poweroff")


def save_factory_mode(enable: bool):
    """
    Save factory mode

    This has to be called with factory partition mounted rw

    :param enable: Required factory mode state
    :return: True if successful, false otherwise
    """
    return TomlConfig(defines.factoryConfigPath).save(data={"factoryMode": enable})


def get_update_channel() -> str:
    try:
        return defines.update_channel.read_text().strip()
    except (FileNotFoundError, PermissionError) as e:
        raise FailedUpdateChannelGet() from e


def set_update_channel(channel: str):
    try:
        subprocess.check_call([defines.set_update_channel_bin, channel])
    except Exception as e:
        raise FailedUpdateChannelSet() from e


def get_octoprint_auth(logger: logging.Logger) -> str:
    try:
        with open(defines.octoprintAuthFile, "r") as f:
            return f.read()
    except IOError as e:
        logger.exception("Octoprint auth file read failed")
        raise ConfigException("Octoprint auth file read failed") from e


def hw_all_off(hw: Hardware, exposure_image: ExposureImage):
    exposure_image.blank_screen()
    hw.uvLed(False)
    hw.stopFans()
    hw.motorsRelease()


class FactoryMountedRW:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def __enter__(self):
        self.logger.info("Remounting factory partition rw")
        if test_runtime.testing:
            self.logger.warning("Skipping factory RW remount due to testing")
        else:
            subprocess.check_call(["/usr/bin/mount", "-o", "remount,rw", str(defines.factoryMountPoint)])

    def __exit__(self, exception_type, exception_value, exception_traceback):
        self.logger.info("Remounting factory partition ro")
        if test_runtime.testing:
            self.logger.warning("Skipping factory RW remount due to testing")
        else:
            subprocess.check_call(["/usr/bin/mount", "-o", "remount,ro", str(defines.factoryMountPoint)])


def set_configured_printer_model(model: PrinterModel):
    """
    Adjust printer model definition files to match new printer model

    :param model: New printer model
    :raises ValueError: Raised on unknown model - no modification is done
    """

    # Obtain new model file before clearing existing definitions (just in case this raises an exception)
    if model == PrinterModel.SL1:
        model_file = defines.sl1_model_file
    elif model == PrinterModel.SL1S:
        model_file = defines.sl1s_model_file
    else:
        raise ValueError(f"No file defined for model: {model}")

    # Clear existing model definitions
    for file in defines.printer_model.glob("*"):
        if file.is_file():
            file.unlink()

    # Add new model definition
    model_file.parent.mkdir(exist_ok=True)
    model_file.touch()


def get_configured_printer_model() -> PrinterModel:
    if defines.sl1s_model_file.exists():
        return PrinterModel.SL1S

    if defines.sl1_model_file.exists():
        return PrinterModel.SL1

    return PrinterModel.NONE


def set_factory_uvpwm(pwm: int) -> None:
    """
    This is supposed to read current factory config, set the new uvPWM and save factory config
    """
    config = HwConfig(file_path=defines.hwConfigPath, factory_file_path=defines.hwConfigPathFactory, is_master=True)
    config.read_file()
    config.uvPwm = pwm
    with FactoryMountedRW():
        config.write_factory()


def compute_uvpwm(hw: Hardware) -> int:
    trans = hw.exposure_screen.panel.transmittance()
    if isclose(trans, 0.0, abs_tol=0.001):
        raise DisplayTransmittanceNotValid(trans)

    pwm = int(-35 * trans + 350)

    pwm_min = hw.printer_model.calibration_parameters().min_pwm
    pwm_max = hw.printer_model.calibration_parameters().max_pwm
    if not pwm_min < pwm < pwm_max:
        raise CalculatedUVPWMNotInRange(pwm, pwm_min, pwm_max)

    return pwm
