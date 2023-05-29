# This file is part of the SLA firmware
# Copyright (C) 2021-2022 Prusa Development a.s. - www.prusa3d.com
# SPDX-License-Identifier: GPL-3.0-or-later

from slafw.admin.control import AdminControl
from slafw.admin.items import AdminAction
from slafw.admin.menus.common.firmware.wizards_test import WizardsTestMenu as WizardsTestMenuCommon, \
    TestUVCalibrationWizardMenu
from slafw.libPrinter import Printer


class WizardsTestMenu(WizardsTestMenuCommon):
    def __init__(self, control: AdminControl, printer: Printer):
        super().__init__(control, printer)
        self.add_items(
            (
                AdminAction("Display test", self.api_display_test, "display_test_color"),
                AdminAction("Unpacking (C)", self.api_unpacking_c, "cover_color"),
                AdminAction("Unpacking (K)", self.api_unpacking_k, "cover_color"),
                AdminAction("Self test", self.api_self_test, "wizard_color"),
                AdminAction("Calibration", self.api_calibration, "calibration_color"),
                AdminAction("Factory reset", self.api_factory_reset, "factory_color"),
                AdminAction("Packing (Factory factory reset)", self.api_packing, "factory_color"),
                AdminAction(
                    "API UV Calibration wizard",
                    lambda: self._control.enter(TestUVCalibrationWizardMenu(self._control, self._printer)),
                    "uv_calibration"
                ),
                AdminAction("SL1S upgrade", self.sl1s_upgrade, "cover_color"),
                AdminAction("SL1 downgrade", self.sl1_downgrade, "cover_color"),
                AdminAction("Self-test - UV & fans test only", self.api_selftest_uvfans, "led_set_replacement"),
                AdminAction("Calibration - tilt times only", self.api_calibration_tilt_times, "tank_reset_color"),
                AdminAction("Tank Surface Cleaner", self.tank_surface_cleaner, "clean-tank-icon"),
                AdminAction("New expo panel", self.new_expo_panel, "display_replacement")
            )
        )
