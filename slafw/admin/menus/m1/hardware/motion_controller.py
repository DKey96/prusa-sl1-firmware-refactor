# This file is part of the SLA firmware
# Copyright (C) 2021-2022 Prusa Development a.s. - www.prusa3d.com
# SPDX-License-Identifier: GPL-3.0-or-later


from slafw.admin.control import AdminControl
from slafw.admin.items import AdminAction
from slafw.admin.menus.common.hardware.motion_controller import MotionControllerMenu as MotionControllerMenuCommon
from slafw.libPrinter import Printer


class MotionControllerMenu(MotionControllerMenuCommon):
    def __init__(self, control: AdminControl, printer: Printer):
        super().__init__(control, printer)
        self.add_items(
            (
                AdminAction("Flash MC", self.flash_mc, "firmware-icon"),
                AdminAction("Erase MC EEPROM", self.erase_mc_eeprom, "delete_small_white"),
                AdminAction("MC2Net (bootloader)", self.mc2net_boot, "remote_small_white"),
                AdminAction("MC2Net (firmware)", self.mc2net_firmware, "remote_control_color"),
            ),
        )
