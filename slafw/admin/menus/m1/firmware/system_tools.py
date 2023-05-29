# This file is part of the SLA firmware
# Copyright (C) 2021-2022 Prusa Development a.s. - www.prusa3d.com
# SPDX-License-Identifier: GPL-3.0-or-later

from slafw.admin.control import AdminControl
from slafw.admin.items import AdminAction, AdminBoolValue
from slafw.admin.menus.common.firmware.system_tools import SystemToolsMenu as SystemToolsMenuCommon, SetChannelMenu
from slafw.libPrinter import Printer


class SystemToolsMenu(SystemToolsMenuCommon):
    SYSTEMD_DBUS = ".systemd1"

    def __init__(self, control: AdminControl, printer: Printer):
        super().__init__(control, printer)

        self.add_items(
            (
                AdminAction(
                    "Update channel",
                    lambda: self._control.enter(SetChannelMenu(self._control)),
                    "support_color"
                ),
                AdminAction("Switch to SL1S", self._switch_sl1s, "cover_color"),
                AdminBoolValue.from_property(self, SystemToolsMenu.factory_mode, "factory_color"),
                AdminBoolValue.from_property(self, SystemToolsMenu.ssh, "network-icon"),
                AdminBoolValue.from_property(self, SystemToolsMenu.serial, "remote_control_color"),
                AdminAction("Send wizard data", self._send_printer_data, "upload_cloud_color"),
                AdminAction("Fake setup", self._fake_setup, "settings_color"),
                AdminAction("Download examples", self._download_examples, "download"),
            )
        )
