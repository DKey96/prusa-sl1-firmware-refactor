# This file is part of the SL1 firmware
# Copyright (C) 2021 Prusa Development a.s. - www.prusa3d.com
# SPDX-License-Identifier: GPL-3.0-or-later
from time import sleep

from sl1fw.admin.control import AdminControl
from sl1fw.admin.items import AdminAction, AdminLabel
from sl1fw.admin.menus.dialogs import Wait, Error
from sl1fw.admin.menus.profiles_sets import ProfilesSetsMenu
from sl1fw.admin.safe_menu import SafeAdminMenu
from sl1fw.libPrinter import Printer
from sl1fw.errors.errors import TiltHomeFailed


class TiltAndTowerMenu(SafeAdminMenu):
    def __init__(self, control: AdminControl, printer: Printer):
        super().__init__(control)
        self._printer = printer

        self.add_back()
        self.add_items(
            (
                AdminAction("Tilt home", self.tilt_home),
                AdminAction("Tilt test", self.tilt_test),
                AdminAction("Tilt profiles", self.tilt_profiles),
                AdminAction("Tilt home calib.", self.tilt_home_calib),
                AdminAction("Tower home", self.tower_home),
                AdminAction("Tower test", self.tower_test),
                AdminAction("Tower profiles", self.tower_profiles),
                AdminAction("Tower home calib.", self.tower_home_calib),
                AdminAction("Turn motors off", self.turn_off_motors),
                AdminAction("Tune tilt", self.tune_tilt),
                AdminAction("Tower sensitivity", self.tower_sensitivity),
                AdminAction("Tower offset", self.tower_offset),
                AdminAction("Profiles sets", lambda: self.enter(ProfilesSetsMenu(self._control, self._printer))),
            )
        )

    @SafeAdminMenu.safe_call
    def tilt_home(self):
        self._control.enter(Wait(self._control, self._do_tilt_home))

    def _do_tilt_home(self, status: AdminLabel):
        self._printer.hw.powerLed("warn")
        self._sync_tilt(status)
        self._printer.hw.powerLed("normal")

    def _sync_tilt(self, status: AdminLabel):
        status.set("Tilt home")
        try:
            self._printer.hw.tilt.sync_wait()
        except TiltHomeFailed:
            self._control.enter(Error(self._control, text="Failed to sync tilt"))
            return False
        status.set("Tilt home done")
        return True

    @SafeAdminMenu.safe_call
    def tilt_test(self):
        self._control.enter(Wait(self._control, self._do_tilt_test))

    @SafeAdminMenu.safe_call
    def _do_tilt_test(self, status: AdminLabel):
        self._printer.hw.powerLed("warn")
        status.set("Tilt sync")
        if self._sync_tilt(status):
            self._printer.hw.beepEcho()
            sleep(1)
            status.set("Tilt up")
            self._printer.hw.tilt.layer_up_wait()
            self._printer.hw.beepEcho()
            sleep(1)
            status.set("Tilt down")
            self._printer.hw.tilt.layer_down_wait()
            self._printer.hw.beepEcho()
            sleep(1)
            status.set("Tilt up")
            self._printer.hw.tilt.layer_up_wait()
            self._printer.hw.beepEcho()
        self._printer.hw.powerLed("normal")

    @SafeAdminMenu.safe_call
    def tilt_profiles(self):
        self._printer.display.forcePage("tiltprofiles")

    @SafeAdminMenu.safe_call
    def tilt_home_calib(self):
        self.enter(Wait(self._control, self._do_tilt_home_calib))

    @SafeAdminMenu.safe_call
    def _do_tilt_home_calib(self, status: AdminLabel):
        self._printer.hw.powerLed("warn")
        status.set("Tilt home calibration")
        self._printer.hw.tilt.home_calibrate_wait()
        self._printer.hw.motorsRelease()
        self._printer.hw.powerLed("normal")

    @SafeAdminMenu.safe_call
    def tower_home(self):
        self.enter(Wait(self._control, self._do_sync_tower))

    def _do_sync_tower(self, status: AdminLabel):
        self._printer.hw.powerLed("warn")
        self._sync_tower(status)
        self._printer.hw.powerLed("normal")

    def _sync_tower(self, status: AdminLabel):
        status.set("Tower home")
        if not self._printer.hw.towerSyncWait(retries=2):
            self._control.enter(Error(self._control, text="Failed to sync tower"))
            return False
        status.set("Tower home done")
        return True

    @SafeAdminMenu.safe_call
    def tower_test(self):
        self.enter(Wait(self._control, self._do_tower_test))

    @SafeAdminMenu.safe_call
    def _do_tower_test(self, status: AdminLabel):
        self._printer.hw.powerLed("warn")
        status.set("Moving platform to the top")
        if self._sync_tower(status):
            status.set("Moving platform to zero")
            self._printer.hw.towerToZero()
            status2 = self.add_label()
            while not self._printer.hw.isTowerOnZero():
                sleep(0.25)
                status2.set(self._printer.hw.getTowerPosition())
        self._printer.hw.powerLed("normal")

    @SafeAdminMenu.safe_call
    def tower_profiles(self):
        self._printer.display.forcePage("towerprofiles")

    @SafeAdminMenu.safe_call
    def tower_home_calib(self):
        self.enter(Wait(self._control, self._do_test_home_calib))

    def _do_test_home_calib(self, status: AdminLabel):
        self._printer.hw.powerLed("warn")
        status.set("Tower home calibration")
        self._printer.hw.towerHomeCalibrateWait()
        self._printer.hw.motorsRelease()
        self._printer.hw.powerLed("normal")

    @SafeAdminMenu.safe_call
    def turn_off_motors(self):
        self._printer.hw.motorsRelease()

    @SafeAdminMenu.safe_call
    def tune_tilt(self):
        self._printer.display.forcePage("tunetilt")

    @SafeAdminMenu.safe_call
    def tower_sensitivity(self):
        self._printer.display.forcePage("towersensitivity")

    @SafeAdminMenu.safe_call
    def tower_offset(self):
        self._printer.display.forcePage("toweroffset")
