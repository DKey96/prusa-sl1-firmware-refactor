# This file is part of the SLA firmware
# Copyright (C) 2020-2022 Prusa Development a.s. - www.prusa3d.com
# SPDX-License-Identifier: GPL-3.0-or-later
from slafw.admin.menus.common.root import Root

from slafw.admin.control import AdminControl
from slafw.admin.items import AdminAction
from slafw.admin.menus.sl1s.firmware.logging import LoggingMenu
from slafw.admin.menus.sl1s.firmware.net_update import NetUpdate
from slafw.admin.menus.sl1s.firmware.system_info import SystemInfoMenu
from slafw.admin.menus.sl1s.firmware.system_tools import SystemToolsMenu
from slafw.admin.menus.sl1s.firmware.tests import FirmwareTestMenu
from slafw.libPrinter import Printer


class FirmwareRoot(Root):
    def __init__(self, control: AdminControl, printer: Printer):
        super().__init__(control, printer)
        self.add_items(
            (
                AdminAction("Net update", lambda: self.enter(NetUpdate(self._control, printer)), "network-icon"),
                AdminAction("Logging", lambda: self.enter(LoggingMenu(self._control, printer)), "logs-icon"),
                AdminAction("System tools", lambda: self.enter(SystemToolsMenu(self._control, printer)),
                            "about_us_color"),
                AdminAction("System information", lambda: self.enter(SystemInfoMenu(self._control, printer)),
                            "system_info_color"),
                AdminAction("Firmware tests", lambda: self.enter(FirmwareTestMenu(self._control, printer)),
                            "limit_color"),
            ),
        )
