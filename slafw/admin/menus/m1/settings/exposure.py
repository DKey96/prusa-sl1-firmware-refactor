# This file is part of the SLA firmware
# Copyright (C) 2020-2022 Prusa Development a.s. - www.prusa3d.com
# SPDX-License-Identifier: GPL-3.0-or-later

from slafw.admin.control import AdminControl
from slafw.admin.items import AdminAction, AdminIntValue, AdminBoolValue, AdminFixedValue
from slafw.admin.menus.common.settings.base import SettingsMenu
from slafw.admin.menus.m1.hardware.profiles import ProfilesMenu
from slafw.libPrinter import Printer


class ExposureSettingsMenu(SettingsMenu):
    def __init__(self, control: AdminControl, printer: Printer):
        super().__init__(control, printer)
        self.add_items(
            (
                AdminAction(
                    "Layer change profiles",
                    lambda: self.enter(ProfilesMenu(self._control, printer, printer.layer_profiles)),
                    "statistics_color"
                ),
                AdminAction(
                    "Exposure profiles",
                    lambda: self.enter(ProfilesMenu(self._control, printer, printer.exposure_profiles)),
                    "uv_calibration"
                ),
                AdminFixedValue.from_value(
                    "Force slow tilt height [mm]",
                    self._temp,
                    "forceSlowTiltHeight",
                    10000,
                    6,
                    2,
                    "move_resin_tank_color"),
                AdminIntValue.from_value(
                    "Limit for fast tilt [%]",
                    self._temp,
                    "limit4fast",
                    1,
                    "limit_color"),
                AdminBoolValue.from_value(
                    "Up&Down UV on",
                    self._temp,
                    "up_and_down_uv_on",
                    "tower_offset_color"),
                AdminIntValue.from_value(
                    "Up&down wait [s]",
                    self._temp,
                    "up_and_down_wait",
                    1,
                    "exposure_times_color"),
                AdminIntValue.from_value(
                    "Up&down every n-th layer",
                    self._temp,
                    "up_and_down_every_layer",
                    1,
                    "tower_offset_color"),
                AdminFixedValue.from_value(
                    "Up&down Z offset [mm]",
                    self._temp,
                    "up_and_down_z_offset_nm",
                    icon="calibration_color"),
                AdminFixedValue.from_value(
                    "Up&down exposure compensation [s]",
                    self._temp,
                    "up_and_down_expo_comp_ms",
                    10,
                    3,
                    2,
                    "exposure_times_color"),
                AdminIntValue.from_value(
                    "Stirring moves count",
                    self._temp,
                    "stirring_moves",
                    1,
                    "move_resin_tank_color"),
                AdminFixedValue.from_value(
                    "Delay after stirring [s]",
                    self._temp,
                    "stirring_delay_ms",
                    icon="exposure_times_color")
            )
        )
