# This file is part of the SLA firmware
# Copyright (C) 2021-2022 Prusa Development a.s. - www.prusa3d.com
# SPDX-License-Identifier: GPL-3.0-or-later

from slafw.admin.control import AdminControl
from slafw.admin.items import AdminAction
from slafw.admin.menus.common.hardware.display import ExposureDisplayMenu as ExposureDisplayMenuCommon, \
    DisplayControlMenu, ShowCalibrationMenu
from slafw.libPrinter import Printer


class ExposureDisplayMenu(ExposureDisplayMenuCommon):
    def __init__(self, control: AdminControl, printer: Printer):
        super().__init__(control, printer)
        self.add_items(
            (
                AdminAction(
                    "Exposure display control",
                    lambda: self._control.enter(DisplayControlMenu(self._control, self._printer)),
                    "display_test_color"
                ),
                AdminAction("Display usage heatmap", self.display_usage_heatmap, "frequency"),
                AdminAction(
                    "Show UV calibration data",
                    lambda: self._control.enter(ShowCalibrationMenu(self._control)),
                    "logs-icon"
                ),
                AdminAction("Erase display counter", self.erase_display_counter, "display_replacement"),
                AdminAction("Erase UV LED counter", self.erase_uv_led_counter, "led_set_replacement"),
            )
        )
