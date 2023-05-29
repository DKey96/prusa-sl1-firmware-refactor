# This file is part of the SLA firmware
# Copyright (C) 2020-2022 Prusa Development a.s. - www.prusa3d.com
# SPDX-License-Identifier: GPL-3.0-or-later

from slafw.admin.control import AdminControl
from slafw.admin.items import AdminAction
from slafw.admin.menus.common.firmware.admin_api_test import ApiTestMenu
from slafw.admin.menus.common.firmware.errors_test import ErrorsTestMenu, WarningsTestMenu
from slafw.admin.menus.common.firmware.tests import FirmwareTestMenu as FirmwareTestMenuCommon
from slafw.admin.menus.m1.firmware.wizards_test import WizardsTestMenu
from slafw.libPrinter import Printer


class FirmwareTestMenu(FirmwareTestMenuCommon):
    def __init__(self, control: AdminControl, printer: Printer):
        super().__init__(control, printer)
        self.add_items(
            (
                AdminAction("Errors test", lambda: self.enter(ErrorsTestMenu(self._control, self._printer)),
                            "error_small_white"),
                AdminAction("Warnings test", lambda: self.enter(WarningsTestMenu(self._control, self._printer)),
                            "warning_white"),
                AdminAction("Wizards test", lambda: self.enter(WizardsTestMenu(self._control, self._printer)),
                            "wizard_color"),
                AdminAction("Admin API test", lambda: self.enter(ApiTestMenu(self._control))),
                AdminAction("Simulate disconnected display", self.simulate_disconnected_display, "error_small_white"),
            )
        )
