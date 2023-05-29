# This file is part of the SLA firmware
# Copyright (C) 2020-2023 Prusa Development a.s. - www.prusa3d.com
# SPDX-License-Identifier: GPL-3.0-or-later
from admin.menus.m1.only_m1_feature import OnlyM1FeatureRoot

from slafw.admin.control import AdminControl
from slafw.admin.items import AdminAction
from slafw.admin.menu import AdminMenu
from slafw.admin.menus.m1.firmware.root import FirmwareRoot
from slafw.admin.menus.m1.hardware.root import HardwareRoot
from slafw.admin.menus.m1.settings.root import SettingsRoot
from slafw.libPrinter import Printer


class RootMenu(AdminMenu):
    def __init__(self, control: AdminControl, printer: Printer):
        super().__init__(control)
        self.add_items(
            (
                AdminAction("<b>Leave admin</b>", self.exit, "back_arrow_white"),
                AdminAction("Settings", lambda: self.enter(SettingsRoot(self._control, printer)), "settings_color"),
                AdminAction("Hardware", lambda: self.enter(HardwareRoot(self._control, printer)), "usb_color"),
                AdminAction("Firmware", lambda: self.enter(FirmwareRoot(self._control, printer)), "firmware-icon"),
                AdminAction("Only M1 feature", lambda: self.enter(OnlyM1FeatureRoot(self._control)), "only")
            ),
        )
