# This file is part of the SL1 firmware
# Copyright (C) 2020 Prusa Development a.s. - www.prusa3d.com
# SPDX-License-Identifier: GPL-3.0-or-later

from threading import Thread
from time import sleep

from sl1fw.admin.control import AdminControl
from sl1fw.admin.items import (
    AdminLabel,
    AdminTextValue,
    AdminAction,
    AdminIntValue,
)
from sl1fw.admin.menu import AdminMenu
from sl1fw.admin.menus.dialogs import Error, Info, Confirm, Wait


class TestMenu(AdminMenu):
    def __init__(self, control: AdminControl):
        super().__init__(control)
        self._a = 42
        self._b = 0
        self._cnt = 0
        self._text = "inital"
        self._run = True

        self.add_back()
        self.add_item(AdminTextValue.from_property(self, TestMenu.text))
        self.add_item(AdminAction("Print hello", self.print_hello))
        self.add_label(
            "Long text Long text Long text Long text Long" " text Long text Long text Long text Long text Long text"
        )
        self.add_item(AdminIntValue.from_property(self, TestMenu.a, 1))
        self.add_item(AdminIntValue.from_property(self, TestMenu.b, 3))
        self.add_item(AdminAction("Test 2", self.test2))
        self.add_label("<center>Centered</center><br/><h1>Headline</h1>")
        self.add_item(AdminAction("<b>Exit</b>", self.exit))
        self.add_item(AdminAction("Error", self.error))
        self.add_item(AdminAction("Info", self.info))
        self.add_item(AdminAction("Confirm", self.confirm))
        self.add_item(AdminAction("Wait", self.wait))

        self._thread = Thread(target=self._runner)

    def on_enter(self):
        self._thread.start()

    def on_leave(self):
        self._run = False
        self._thread.join()

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, value: str):
        self._text = value

    @staticmethod
    def print_hello():
        print("Hello world")

    @property
    def a(self) -> int:
        return self._a

    @a.setter
    def a(self, value: int) -> None:
        self._a = value

    @property
    def b(self) -> int:
        return self._b

    @b.setter
    def b(self, value: int) -> None:
        self._b = value

    def test2(self):
        self._control.enter(TestMenu2(self._control))

    def exit(self):
        self._control.exit()

    def _runner(self):
        while self._run:
            sleep(0.5)
            self._cnt += 1
            self.text = f"Text: {self._cnt}"
            print(self._cnt)

    def error(self):
        self._control.enter(Error(self._control, text="Synthetic error"))

    def info(self):
        self._control.enter(Info(self._control, "Test info"))

    def confirm(self):
        self._control.enter(Confirm(self._control, self.info, headline="Test confirm", text="Text text text.."))

    def wait(self):
        self._control.enter(Wait(self._control, self._do_wait))

    @staticmethod
    def _do_wait(status: AdminLabel):
        for i in range(15):
            sleep(0.2)
            status.set(f"waiting: {i}")


class TestMenu2(AdminMenu):
    def __init__(self, control: AdminControl):
        super().__init__(control)
        self.add_back()