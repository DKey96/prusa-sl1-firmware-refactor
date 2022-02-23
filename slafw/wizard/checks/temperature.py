# This file is part of the SLA firmware
# Copyright (C) 2020-2021 Prusa Research a.s. - www.prusa3d.com
# SPDX-License-Identifier: GPL-3.0-or-later

from dataclasses import dataclass, asdict
from threading import Thread
from time import sleep
from typing import Dict, Any, Optional

from slafw import defines
from slafw.errors.errors import A64Overheat, UVLEDOverheat
from slafw.errors.warnings import AmbientTooCold, AmbientTooHot
from slafw.functions.system import shut_down
from slafw.hardware.base.hardware import BaseHardware
from slafw.wizard.actions import UserActionBroker
from slafw.wizard.checks.base import WizardCheckType, Check
from slafw.wizard.setup import Configuration


@dataclass
class CheckData:
    # UV LED temperature at the beginning of test (should be close to ambient)
    wizardTempUvInit: float
    # ambient sensor temperature
    wizardTempAmbient: float
    # A64 temperature
    wizardTempA64: float


class TemperatureTest(Check):
    def __init__(self, hw: BaseHardware):
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
        uv = self._hw.uv_led_temp
        if uv.value > uv.critical:
            raise UVLEDOverheat(uv.value)

        ambient = self._hw.ambient_temp
        if ambient.value < ambient.min:
            raise AmbientTooCold(ambient.value)
        if ambient.value > ambient.max:
            raise AmbientTooHot(ambient.value)

        self._check_data = CheckData(uv.value, ambient.value, a64_temperature)

    def _overheat(self):
        for _ in range(10):
            self._hw.beepAlarm(3)
            sleep(1)
        shut_down(self._hw)

    def get_result_data(self) -> Dict[str, Any]:
        return asdict(self._check_data)
