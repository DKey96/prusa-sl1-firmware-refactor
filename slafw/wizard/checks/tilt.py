# This file is part of the SLA firmware
# Copyright (C) 2020 Prusa Research a.s. - www.prusa3d.com
# SPDX-License-Identifier: GPL-3.0-or-later

import asyncio
from abc import ABC
from time import time
from typing import Optional, Dict, Any

from slafw import defines
from slafw.configs.unit import Ustep
from slafw.errors.errors import (
    TiltHomeCheckFailed,
    TiltEndstopNotReached,
    TiltAxisCheckFailed,
    InvalidTiltAlignPosition,
    PrinterException,
)
from slafw.hardware.base.hardware import BaseHardware
from slafw import test_runtime
from slafw.states.wizard import WizardState
from slafw.wizard.actions import UserActionBroker, PushState
from slafw.wizard.checks.base import WizardCheckType, DangerousCheck, Check
from slafw.wizard.setup import Configuration, Resource, TankSetup
from slafw.configs.writer import ConfigWriter


class TiltHomeTest(DangerousCheck, ABC):
    def __init__(self, hw: BaseHardware):
        super().__init__(
            hw, WizardCheckType.TILT_HOME, Configuration(None, None), [Resource.TILT, Resource.TOWER_DOWN],
        )

    async def async_task_run(self, actions: UserActionBroker):
        home_status = self._hw.tilt.homing_status
        for _ in range(3):
            await self._hw.tilt.sync_ensure_async()
            home_status = self._hw.tilt.homing_status
            if home_status == -2:
                raise TiltEndstopNotReached()

            if home_status == 0:
                await self._hw.tilt.home_calibrate_wait_async()
                break

        if home_status == -3:
            raise TiltHomeCheckFailed()


class TiltLevelTest(DangerousCheck):
    def __init__(self, hw: BaseHardware):
        super().__init__(
            hw, WizardCheckType.TILT_LEVEL, Configuration(None, None), [Resource.TILT, Resource.TOWER_DOWN]
        )

    async def async_task_run(self, actions: UserActionBroker):
        # This just homes tilt
        # TODO: We should have such a method in Hardware
        self._hw.tilt.actual_profile = self._hw.tilt.profiles.homingFast
        self._hw.tilt.sync()
        home_status = self._hw.tilt.homing_status.value
        while home_status != 0:
            if home_status == -2:
                raise TiltEndstopNotReached()
            if home_status == -3:
                raise TiltHomeCheckFailed()
            if home_status < 0:
                raise PrinterException("Unknown printer home error")
            await asyncio.sleep(0.25)
            home_status = self._hw.tilt.homing_status.value
        self._hw.tilt.position = Ustep(0)

        # Set tilt to leveled position
        self._hw.tilt.actual_profile = self._hw.tilt.profiles.moveFast
        await self._hw.tilt.move_ensure_async(self._hw.config.tiltHeight)


class TiltRangeTest(DangerousCheck):
    def __init__(self, hw: BaseHardware):
        super().__init__(
            hw, WizardCheckType.TILT_RANGE, Configuration(None, None), [Resource.TILT, Resource.TOWER_DOWN],
        )

    async def async_task_run(self, actions: UserActionBroker):
        self._hw.tilt.actual_profile = self._hw.tilt.profiles.moveFast
        self._hw.tilt.move(self._hw.config.tiltMax)
        while self._hw.tilt.moving:
            await asyncio.sleep(0.25)
        self.progress = 0.25

        self._hw.tilt.move(Ustep(512))  # go down fast before endstop
        while self._hw.tilt.moving:
            await asyncio.sleep(0.25)
        self.progress = 0.5

        # finish measurement with slow profile (more accurate)
        self._hw.tilt.actual_profile = self._hw.tilt.profiles.homingSlow
        self._hw.tilt.move(self._hw.config.tiltMin)
        while self._hw.tilt.moving:
            await asyncio.sleep(0.25)
        self.progress = 0.75

        # TODO make MC homing more accurate
        if (
            self._hw.tilt.position < Ustep(-defines.tiltHomingTolerance)
            or self._hw.tilt.position > Ustep(defines.tiltHomingTolerance)
        ) and not test_runtime.testing:
            raise TiltAxisCheckFailed(self._hw.tilt.position)
        self._hw.tilt.actual_profile = self._hw.tilt.profiles.moveFast
        self._hw.tilt.move(self._hw.config.tiltHeight)
        while self._hw.tilt.moving:
            await asyncio.sleep(0.25)


class TiltTimingTest(DangerousCheck):
    def __init__(self, hw: BaseHardware, config_writer: ConfigWriter):
        super().__init__(
            hw, WizardCheckType.TILT_TIMING, Configuration(None, None), [Resource.TILT, Resource.TOWER_DOWN],
        )
        self._config_writer = config_writer

    async def async_task_run(self, actions: UserActionBroker):
        self._hw.tower.sync()
        while not self._hw.tower.synced:
            await asyncio.sleep(0.25)

        await self._hw.tilt.sync_ensure_async()  # FIXME MC cant properly home tilt while tower is moving
        self._config_writer.tiltSlowTime = await self._get_tilt_time_sec(slow_move=True)
        self._config_writer.tiltFastTime = await self._get_tilt_time_sec(slow_move=False)
        self._hw.tower.actual_profile = self._hw.tower.profiles.homingFast
        self._hw.tilt.actual_profile = self._hw.tilt.profiles.moveFast
        self.progress = 1
        await self._hw.tilt.move_ensure_async(self._hw.config.tiltHeight)

    async def _get_tilt_time_sec(self, slow_move: bool) -> float:
        """
        Get tilt time in seconds
        :param slow_move: Whenever to do slow tilts
        :return: Tilt time in seconds
        """
        tilt_time: float = 0
        total = self._hw.config.measuringMoves
        for i in range(total):
            self.progress = (i + (3 * (1 - slow_move))) / total / 2
            self._logger.info(
                "Slow move %(count)d/%(total)d" % {"count": i + 1, "total": total}
                if slow_move
                else "Fast move %(count)d/%(total)d" % {"count": i + 1, "total": total}
            )
            await asyncio.sleep(0)
            tilt_start_time = time()
            self._hw.tilt.layer_up_wait(slowMove=slow_move, tiltHeight=self._config_writer.tiltHeight)
            await asyncio.sleep(0)
            await self._hw.tilt.layer_down_wait_async(slow_move)
            tilt_time += time() - tilt_start_time

        return tilt_time / total

    def get_result_data(self) -> Dict[str, Any]:
        return {
            "tilt_slow_time_ms": int(self._config_writer.tiltSlowTime * 1000),
            "tilt_fast_time_ms": int(self._config_writer.tiltFastTime * 1000),
        }


class TiltCalibrationStartTest(DangerousCheck):
    def __init__(self, hw: BaseHardware):
        super().__init__(
            hw, WizardCheckType.TILT_CALIBRATION_START, Configuration(None, None), [Resource.TILT, Resource.TOWER_DOWN],
        )

    async def async_task_run(self, actions: UserActionBroker):
        self._hw.tilt.actual_profile = self._hw.tilt.profiles.homingFast
        self._hw.tilt.move(Ustep(defines.tiltCalibrationStart))
        while self._hw.tilt.moving:
            await asyncio.sleep(0.25)


class TiltAlignTest(Check):
    def __init__(self, hw: BaseHardware, config_writer: ConfigWriter):
        super().__init__(
            WizardCheckType.TILT_CALIBRATION,
            Configuration(TankSetup.REMOVED, None),
            [Resource.TILT, Resource.TOWER_DOWN],
        )
        self._hw = hw
        self._config_writer = config_writer
        self.tilt_aligned_event: Optional[asyncio.Event] = None
        self._loop: Optional[asyncio.AbstractEventLoop] = None

    async def async_task_run(self, actions: UserActionBroker):
        self.tilt_aligned_event = asyncio.Event()
        self._loop = asyncio.get_running_loop()
        actions.tilt_aligned.register_callback(self.tilt_aligned)
        actions.tilt_move.register_callback(self.tilt_move)

        level_tilt_state = PushState(WizardState.LEVEL_TILT)
        actions.push_state(level_tilt_state)
        await self.tilt_aligned_event.wait()
        actions.drop_state(level_tilt_state)

    def tilt_aligned(self):
        position = self._hw.tilt.position
        if position is None:
            self._hw.beepAlarm(3)
            raise InvalidTiltAlignPosition(position)
        self._config_writer.tiltHeight = position
        self._loop.call_soon_threadsafe(self.tilt_aligned_event.set)

    def tilt_move(self, direction: int):
        self._logger.debug("Tilt move direction: %s", direction)
        self._hw.tilt.move_api(direction, fullstep=True)

    def get_result_data(self) -> Dict[str, Any]:
        return {"tiltHeight": int(self._config_writer.tiltHeight)}
