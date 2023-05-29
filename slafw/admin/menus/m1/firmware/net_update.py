# This file is part of the SLA firmware
# Copyright (C) 2020-2022 Prusa Development a.s. - www.prusa3d.com
# SPDX-License-Identifier: GPL-3.0-or-later

from admin.control import AdminControl
from libPrinter import Printer

from slafw.admin.menus.common.firmware.net_update import NetUpdate as NetUpdateCommon


class NetUpdate(NetUpdateCommon):
    def __init__(self, control: AdminControl, printer: Printer):
        super().__init__(control, printer)
