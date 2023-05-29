from slafw.admin.control import AdminControl
from slafw.admin.menu import AdminMenu
from slafw.libPrinter import Printer


class Root(AdminMenu):
    def __init__(self, control: AdminControl, printer: Printer):
        super().__init__(control)
        self._printer = printer
        self.add_back()
