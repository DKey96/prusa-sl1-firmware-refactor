# This file is part of the SLA firmware
# Copyright (C) 2022 Prusa Development a.s. - www.prusa3d.com
# SPDX-License-Identifier: GPL-3.0-or-later

from typing import Optional

from slafw.admin.control import AdminControl
from slafw.admin.items import AdminAction
from slafw.admin.menus.common.hardware.profiles import ProfilesMenu as ProfilesMenuCommon, EditProfiles, ImportProfiles
from slafw.hardware.axis import Axis
from slafw.hardware.profiles import ProfileSet
from slafw.libPrinter import Printer


class ProfilesMenu(ProfilesMenuCommon):
    def __init__(self, control: AdminControl, printer: Printer, pset: ProfileSet, axis: Optional[Axis] = None):
        super().__init__(control, printer, pset, axis)
        self.add_items(
            (
                AdminAction(
                    f"Edit {pset.name}",
                    lambda: self.enter(EditProfiles(self._control, printer, pset, axis)),
                    "edit_white"
                ),
                AdminAction(
                    f"Import {pset.name}",
                    lambda: self.enter(ImportProfiles(self._control, pset)),
                    "save_color"
                ),
                AdminAction(f"Save {pset.name} to USB drive", self.save_to_usb, "usb_color"),
                AdminAction(f"Restore to factory {pset.name}", self.factory_profiles, "factory_color"),
            )
        )
