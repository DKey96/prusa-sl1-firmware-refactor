# This file is part of the SLA firmware
# Copyright (C) 2021-2022 Prusa Development a.s. - www.prusa3d.com
# SPDX-License-Identifier: GPL-3.0-or-later

from slafw.admin.control import AdminControl
from slafw.admin.menus.common.firmware.system_info import SystemInfoMenu as SystemInfoMenuCommon
from slafw.libPrinter import Printer


class SystemInfoMenu(SystemInfoMenuCommon):
    def __init__(self, control: AdminControl, printer: Printer):
        super().__init__(control, printer)
