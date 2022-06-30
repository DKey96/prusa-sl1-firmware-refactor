# This file is part of the SLA firmware
# Copyright (C) 2022 Prusa Research a.s. - www.prusa3d.com
# SPDX-License-Identifier: GPL-3.0-or-later

from typing import Optional
from unittest.mock import Mock

from slafw.configs.hw import HwConfig
from slafw.configs.unit import Unit
from slafw.hardware.axis import Axis, HomingStatus
from slafw.hardware.power_led import PowerLed
from slafw.hardware.tilt import Tilt
from slafw.hardware.tower import Tower
from slafw.hardware.base.profiles import SingleProfile, ProfileSet
from slafw.hardware.tilt import MovingProfilesTilt
from slafw.hardware.tower import MovingProfilesTower
from slafw.motion_controller.controller import MotionController


class MockAxis(Axis):
    # pylint: disable = too-many-arguments
    def __init__(self, mcc: MotionController, config: HwConfig,
                 power_led: PowerLed):
        super().__init__(config, power_led)
        self._mcc = mcc
        self._target_position = Unit(0)
        self._homing_status = HomingStatus.UNKNOWN
        self._actual_profile: Optional[SingleProfile] = None

    @property
    def position(self) -> Unit:
        return self._target_position

    @position.setter
    def position(self, position: Unit):
        self._target_position = position

    @property
    def moving(self) -> bool:
        return False

    def move(self, position: Unit) -> None:
        self.position = position

    def stop(self) -> None:
        self.position = self.position

    def release(self) -> None:
        self._homing_status = HomingStatus.UNKNOWN

    def go_to_fullstep(self, go_up: bool):
        pass

    def sync(self) -> None:
        self._homing_status = HomingStatus.SYNCED

    @property
    def homing_status(self) -> HomingStatus:
        return self._homing_status

    async def home_calibrate_wait_async(self):
        pass

    async def verify_async(self) -> None:
        self.sync()

    @property
    def profiles(self) -> ProfileSet:
        pass

    @property
    def actual_profile(self) -> SingleProfile:
        return self._actual_profile

    @actual_profile.setter
    def actual_profile(self, profile: SingleProfile):
        self._actual_profile = profile

    def apply_profile(self):
        pass

    def apply_all_profiles(self):
        pass

    def sensitivity(self) -> int:
        pass

    def set_stepper_sensitivity(self, sensitivity: int):
        pass

    def _move_api_get_profile(self, speed: int) -> SingleProfile:
        pass


class MockTower(Tower, MockAxis):
    @property
    def profiles(self) -> MovingProfilesTower:
        return Mock()


class MockTilt(Tilt, MockAxis):
    def layer_up_wait(self, slowMove: bool = False,
                      tiltHeight: int = 0) -> None:
        self.move(self._config.tiltHeight)

    async def layer_down_wait_async(self, slowMove: bool = False) -> None:
        self._move_api_min()

    async def stir_resin_async(self) -> None:
        pass

    @property
    def profiles(self) -> MovingProfilesTilt:
        return Mock()
