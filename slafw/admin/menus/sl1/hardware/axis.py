# This file is part of the SLA firmware
# Copyright (C) 2021-2022 Prusa Development a.s. - www.prusa3d.com
# SPDX-License-Identifier: GPL-3.0-or-later

from slafw.admin.control import AdminControl
from slafw.admin.items import AdminAction
from slafw.admin.menus.common.hardware.axis import AxisMenu as AxisMenuCommon
from slafw.admin.menus.sl1.hardware.profiles import ProfilesMenu
from slafw.hardware.axis import Axis
from slafw.libPrinter import Printer


class AxisMenu(AxisMenuCommon):
    def __init__(self, control: AdminControl, printer: Printer, axis: Axis):
        super().__init__(control, printer, axis)
        self.add_items(
            (
                AdminAction(f"Release {axis.name} motor", self.release_motor, "disable_steppers_color"),
                AdminAction(f"Home {axis.name}", self.home, "home_small_white"),
                AdminAction(f"Move {axis.name} to calibrated position", self.config_position, "finish_white"),
                AdminAction(f"Manual {axis.name} move", self.manual_move, "control_color"),
                AdminAction(
                    f"{axis.name.capitalize()} profiles",
                    lambda: self.enter(ProfilesMenu(self._control, printer, axis.profiles, axis)),
                    "steppers_color"
                ),
                AdminAction("Home calibration", self.home_calib, "calibration_color"),
                AdminAction(f"Test {axis.name}", self.test, "limit_color"),
            )
        )
