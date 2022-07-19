# This file is part of the SLA firmware
# Copyright (C) 2022 Prusa Research a.s. - www.prusa3d.com
# SPDX-License-Identifier: GPL-3.0-or-later

from pathlib import Path
from typing import List

from slafw import defines
from slafw.configs.hw import HwConfig
from slafw.configs.unit import Nm
from slafw.configs.value import DictOfConfigs
from slafw.errors.errors import TowerPositionFailed
from slafw.hardware.printer_model import PrinterModel
from slafw.hardware.axis import HomingStatus
from slafw.hardware.power_led import PowerLed
from slafw.hardware.tower import MovingProfilesTower, Tower
from slafw.hardware.sl1.axis import SingleProfileSL1, AxisSL1
from slafw.motion_controller.controller import MotionController


TOWER_CFG_LOCAL = defines.configDir / "profiles_tower.json"


class MovingProfilesTowerSL1(MovingProfilesTower):
    # pylint: disable=too-many-ancestors
    homingFast = DictOfConfigs(SingleProfileSL1)  # type: ignore
    homingSlow = DictOfConfigs(SingleProfileSL1)  # type: ignore
    moveFast = DictOfConfigs(SingleProfileSL1)    # type: ignore
    moveSlow = DictOfConfigs(SingleProfileSL1)    # type: ignore
    layer = DictOfConfigs(SingleProfileSL1)       # type: ignore
    layerMove = DictOfConfigs(SingleProfileSL1)   # type: ignore
    superSlow = DictOfConfigs(SingleProfileSL1)   # type: ignore
    resinSensor = DictOfConfigs(SingleProfileSL1) # type: ignore
    __definition_order__ = tuple(locals())


class TowerSL1(Tower, AxisSL1):
    # pylint: disable=too-many-instance-attributes
    # pylint: disable=too-many-public-methods

    def __init__(self, mcc: MotionController, config: HwConfig, power_led: PowerLed, printer_model: PrinterModel):
        super().__init__(config, power_led)
        self._mcc = mcc
        defaults = Path(defines.dataPath) / printer_model.name / f"default_profiles_{self.name}.json" # type: ignore[attr-defined]
        self._profiles = MovingProfilesTowerSL1(factory_file_path=TOWER_CFG_LOCAL, default_file_path=defaults)
        self._sensitivity = {
            #                -2       -1        0        +1       +2
            "homingFast": [[22, 0], [22, 2], [22, 4], [22, 6], [22, 8]],
            "homingSlow": [[14, 0], [15, 0], [16, 1], [16, 3], [16, 5]],
        }

    def start(self):
        self.actual_profile = self._profiles.homingFast    # type: ignore
        try:
            self.set_stepper_sensitivity(self.sensitivity)
        except RuntimeError as e:
            self._logger.error("%s - ignored", e)
        self.apply_all_profiles()

    @property
    def position(self) -> Nm:
        return self._config.tower_microsteps_to_nm(self._mcc.doGetInt("?twpo"))

    @position.setter
    def position(self, position: Nm) -> None:
        self._check_units(position, Nm)
        if self.moving:
            raise TowerPositionFailed(
                "Failed to set tower position since its moving")
        self._mcc.do("!twpo", int(self._config.nm_to_tower_microsteps(position)))
        self._target_position = position
        self._logger.debug("Position set to: %d nm", self._target_position)

    @property
    def moving(self):
        if self._mcc.doGetInt("?mot") & 1:
            return True
        return False

    def move(self, position: Nm) -> None:
        self._check_units(position, Nm)
        self._mcc.do("!twma", int(self._config.nm_to_tower_microsteps(position)))
        self._target_position = position
        self._logger.debug("Move initiated. Target position: %d nm", position)

    # TODO use !brk instead. Motor might stall at !mot 0
    def stop(self):
        axis_moving = self._mcc.doGetInt("?mot")
        self._mcc.do("!mot", axis_moving & ~1)
        self._target_position = self.position
        self._logger.debug("Move stopped. Rewriting target position to: %d nm", self._target_position)

    def go_to_fullstep(self, go_up: bool):
        self._mcc.do("!twgf", int(go_up))

    def release(self) -> None:
        axis_enabled = self._mcc.doGetInt("?ena")
        self._mcc.do("!ena", axis_enabled & ~1)

    @property
    def homing_status(self) -> HomingStatus:
        return HomingStatus(self._mcc.doGetInt("?twho"))

    def sync(self):
        self._mcc.do("!twho")

    async def home_calibrate_wait_async(self):
        self._mcc.do("!twhc")
        await super().home_calibrate_wait_async()

    async def verify_async(self) -> None:
        if not self.synced:
            await self.sync_ensure_async()
        else:
            self.actual_profile = self._profiles.moveFast   # type: ignore
            await self.move_ensure_async(self._config.tower_height_nm)

    @property
    def profiles(self) -> MovingProfilesTowerSL1:
        return self._profiles

    def _read_profile_id(self) -> int:
        return self._mcc.doGetInt("?twcs")

    def _read_profile_data(self) -> List[int]:
        return self._mcc.doGetIntList("?twcf")

    def _write_profile_id(self, profile_id: int):
        self._mcc.do("!twcs", profile_id)

    def _write_profile_data(self):
        self._mcc.do("!twcf", *self._actual_profile.dump())
