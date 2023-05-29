# This file is part of the SLA firmware
# Copyright (C) 2020-2022 Prusa Development a.s. - www.prusa3d.com
# SPDX-License-Identifier: GPL-3.0-or-later
from slafw.admin.control import AdminControl
from slafw.admin.menus.contexts.menu_context import AdminMenuContext
from slafw.admin.menus.m1.root import RootMenu as M1RootMenu
from slafw.admin.menus.sl1.root import RootMenu as SL1RootMenu
from slafw.admin.menus.sl1s.root import RootMenu as SL1sRootMenu
from slafw.hardware.printer_model import PrinterModel
from slafw.libPrinter import Printer


class RootMenuContext(AdminMenuContext):
    def __init__(self, control: AdminControl, printer: Printer):
        if printer.hw.printer_model == PrinterModel.M1:
            strategy = M1RootMenu(control, printer)
        elif printer.hw.printer_model == PrinterModel.SL1S:
            strategy = SL1sRootMenu(control, printer)
        else:
            strategy = SL1RootMenu(control, printer)

        super().__init__(strategy)
