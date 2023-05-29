# This file is part of the SLA firmware
# Copyright (C) 2021-2022 Prusa Development a.s. - www.prusa3d.com
# SPDX-License-Identifier: GPL-3.0-or-later

from slafw.admin.control import AdminControl
from slafw.admin.items import AdminAction
from slafw.admin.menus.common.hardware.tests import HardwareTestMenu as HardwareTestMenuCommon
from slafw.libPrinter import Printer


class HardwareTestMenu(HardwareTestMenuCommon):
    def __init__(self, control: AdminControl, printer: Printer):
        super().__init__(control, printer)
        self.add_items(
            (
                AdminAction("Resin sensor test", self.resin_sensor_test, "refill_color"),
                AdminAction("Infinite UV calibrator test", self.infinite_uv_calibrator_test, "uv_calibration"),
                AdminAction("Infinite complex test", self.infinite_test, "restart"),
                AdminAction("Touchscreen test", self._control.touchscreen_test, "touchscreen-icon"),
            )
        )
