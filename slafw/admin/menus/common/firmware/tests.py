# This file is part of the SLA firmware
# Copyright (C) 2020-2022 Prusa Development a.s. - www.prusa3d.com
# SPDX-License-Identifier: GPL-3.0-or-later

import logging

from slafw.admin.control import AdminControl
from slafw.admin.safe_menu import SafeAdminMenu
from slafw.errors.errors import UnknownPrinterModel
from slafw.libPrinter import Printer


class FirmwareTestMenu(SafeAdminMenu):
    def __init__(self, control: AdminControl, printer: Printer):
        super().__init__(control)
        self.logger = logging.getLogger(__name__)
        self._printer = printer

        self.add_back()

    def simulate_disconnected_display(self):
        self._printer.enter_fatal_error(UnknownPrinterModel())
