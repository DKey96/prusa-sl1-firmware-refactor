# This file is part of the SLA firmware
# Copyright (C) 2021-2022 Prusa Development a.s. - www.prusa3d.com
# SPDX-License-Identifier: GPL-3.0-or-later

from slafw.admin.control import AdminControl
from slafw.admin.items import AdminAction
from slafw.admin.menus.common.firmware.wizards_test import WizardsTestMenu as WizardsTestMenuCommon
from slafw.libPrinter import Printer


class WizardsTestMenu(WizardsTestMenuCommon):
    def __init__(self, control: AdminControl, printer: Printer):
        super().__init__(control, printer)
        self.add_items(
            (
                AdminAction("Display test", self.api_display_test, "display_test_color"),
            )
        )
