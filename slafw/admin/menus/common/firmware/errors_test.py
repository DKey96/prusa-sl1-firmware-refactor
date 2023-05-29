# This file is part of the SLA firmware
# Copyright (C) 2020-2022 Prusa Development a.s. - www.prusa3d.com
# SPDX-License-Identifier: GPL-3.0-or-later

import functools
from abc import abstractmethod

from slafw.admin.control import AdminControl
from slafw.admin.items import AdminAction
from slafw.admin.menus.common.root import Root
from slafw.errors.tests import get_classes, get_instance
from slafw.libPrinter import Printer


class ExceptionTestMenu(Root):
    def __init__(self, control: AdminControl, printer: Printer):
        super().__init__(control, printer)
        self.add_items(self._get_items())

    @staticmethod
    @abstractmethod
    def _get_classes_list():
        """ implemented in children """

    @staticmethod
    @abstractmethod
    def _get_icon():
        """ implemented in children """

    @staticmethod
    def _sort_classes(data):
        name, cls = data
        return f"{cls.CODE}-{name}"

    def _get_items(self):
        items = []
        for _, cls in sorted(self._get_classes_list(), key=self._sort_classes):
            items.append(AdminAction(f"{cls.CODE.code} - {cls.CODE.title}\n{cls.__name__}",
                                     functools.partial(self.do_error, cls),
                                     self._get_icon())
                         )
        return items

    def do_error(self, cls):
        self._printer.exception_occurred.emit(get_instance(cls))


class WarningsTestMenu(ExceptionTestMenu):

    @staticmethod
    def _get_classes_list():
        return get_classes(get_warnings=True)

    @staticmethod
    def _get_icon():
        return "warning_white"


class ErrorsTestMenu(ExceptionTestMenu):

    @staticmethod
    def _get_classes_list():
        return get_classes(get_errors=True)

    @staticmethod
    def _get_icon():
        return "error_small_white"