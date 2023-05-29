# This file is part of the SLA firmware
# Copyright (C) 2020-2022 Prusa Development a.s. - www.prusa3d.com
# SPDX-License-Identifier: GPL-3.0-or-later

from slafw.admin.control import AdminControl
from slafw.admin.items import AdminAction
from slafw.admin.menus.common.settings.backup import BackupConfigMenu as BackupConfigMenuCommon, RestoreFromUsbMenu, \
    RestoreFromNetMenu
from slafw.libPrinter import Printer


class BackupConfigMenu(BackupConfigMenuCommon):
    def __init__(self, control: AdminControl, printer: Printer):
        super().__init__(control, printer)
        self.add_items(
            (
                AdminAction("Restore configuration from factory defaults", self.reset_to_defaults, "factory_color"),
                AdminAction("Save configuration as factory defaults", self.save_as_defaults, "save_color"),
                AdminAction(
                    "Restore configuration from USB drive",
                    lambda: self._control.enter(RestoreFromUsbMenu(self._control, self._printer)),
                    "usb_color"
                ),
                AdminAction("Save configuration to USB drive", self.save_to_usb, "usb_color"),
                AdminAction(
                    "Restore configuration from network",
                    lambda: self._control.enter(RestoreFromNetMenu(self._control, self._printer)),
                    "download"
                ),
                AdminAction("Save configuration to network", self.save_to_net, "upload_cloud_color"),
            ),
        )
