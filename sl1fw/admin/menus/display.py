# This file is part of the SL1 firmware
# Copyright (C) 2021 Prusa Development a.s. - www.prusa3d.com
# SPDX-License-Identifier: GPL-3.0-or-later

import functools
import json
from datetime import timedelta, datetime
from itertools import chain
from threading import Thread
from dataclasses import asdict

from sl1fw import defines
from sl1fw.admin.control import AdminControl
from sl1fw.admin.items import AdminAction, AdminBoolValue, AdminIntValue, AdminLabel
from sl1fw.admin.menu import AdminMenu
from sl1fw.admin.menus.dialogs import Info, Confirm, Wait
from sl1fw.admin.safe_menu import SafeAdminMenu
from sl1fw.functions.system import hw_all_off
from sl1fw.functions import files, generate
from sl1fw.libPrinter import Printer
from sl1fw.hardware.tilt import TiltProfile
from sl1fw.libUvLedMeterMulti import UvLedMeterMulti

class DisplayRootMenu(AdminMenu):
    def __init__(self, control: AdminControl, printer: Printer):
        super().__init__(control)
        self._printer = printer

        self.add_back()
        self.add_items(
            (
                AdminAction(
                    "Display service",
                    lambda: self._control.enter(DisplayServiceMenu(self._control, self._printer))
                ),
                AdminAction(
                    "Display control",
                    lambda: self._control.enter(DisplayControlMenu(self._control, self._printer))
                ),
                AdminAction(
                    "Direct UV PWM settings",
                    lambda: self._control.enter(DirectPwmSetMenu(self._control, self._printer))
                ),
            )
        )


class DisplayServiceMenu(SafeAdminMenu):
    def __init__(self, control: AdminControl, printer: Printer):
        super().__init__(control)
        self._printer = printer

        self.add_back()
        self.add_items(
            (
                AdminAction("Erase UV LED counter", self.erase_uv_led_counter),
                AdminAction("Erase Display counter", self.erase_display_counter),
                AdminAction(
                    "Show UV calibration data",
                    lambda: self._control.enter(ShowCalibrationMenu(self._control, self._printer))
                ),
                AdminAction("Display usage heatmap", self.display_usage_heatmap),
            )
        )

    @SafeAdminMenu.safe_call
    def erase_uv_led_counter(self):
        self.logger.info("About to erase UV LED statistics")
        self.logger.info("Current statistics %s", self._printer.hw.getUvStatistics())
        self._control.enter(
            Confirm(
                self._control,
                self._do_erase_uv_led_counter,
                text=f"Do you really want to clear the UV LED counter?\n\n"
                f"UV counter: {timedelta(seconds=self._printer.hw.getUvStatistics()[0])}\n"
                f"Serial number: {self._printer.hw.cpuSerialNo}\n"
                f"IP address: {self._printer.inet.ip}",
            )
        )

    def _do_erase_uv_led_counter(self):
        self._printer.hw.clearUvStatistics()
        self._control.enter(
            Info(
                self._control,
                text="UV counter has been erased.\n\n"
                f"UV counter: {timedelta(seconds=self._printer.hw.getUvStatistics()[0])}\n"
                f"Serial number: {self._printer.hw.cpuSerialNo}\n"
                f"IP address: {self._printer.inet.ip}",
            )
        )

    @SafeAdminMenu.safe_call
    def erase_display_counter(self):
        self.logger.info("About to erase display statistics")
        self.logger.info("Current statistics %s", self._printer.hw.getUvStatistics())

        self._control.enter(
            Confirm(
                self._control,
                self._do_erase_display_counter,
                text=f"Do you really want to clear the Display counter?\n\n"
                f"Display counter: {timedelta(seconds=self._printer.hw.getUvStatistics()[1])}\n"
                f"Serial number: {self._printer.hw.cpuSerialNo}\n"
                f"IP address: {self._printer.inet.ip}",
            )
        )

    def _do_erase_display_counter(self):
        self._printer.hw.clearDisplayStatistics()
        self._control.enter(
            Info(
                self._control,
                text="Display counter has been erased.\n\n"
                f"Display counter: {timedelta(seconds=self._printer.hw.getUvStatistics()[1])}\n"
                f"Serial number: {self._printer.hw.cpuSerialNo}\n"
                f"IP address: {self._printer.inet.ip}",
            )
        )

    @SafeAdminMenu.safe_call
    def display_usage_heatmap(self):
        generate.display_usage_heatmap(
                self._printer.hw.exposure_screen.parameters,
                defines.displayUsageData,
                defines.displayUsagePalette,
                defines.fullscreenImage)
        self._control.fullscreen_image()


class ShowCalibrationMenu(SafeAdminMenu):
    def __init__(self, control: AdminControl, printer: Printer):
        super().__init__(control)
        self._printer = printer

        self.add_back()
        data_paths = (
                defines.wizardHistoryPathFactory.glob("uvcalib_data.*"),
                defines.wizardHistoryPathFactory.glob("uvcalibrationwizard_data.*"),
                defines.wizardHistoryPathFactory.glob("uv_calibration_data.*"),
                defines.wizardHistoryPathFactory.glob(f"{defines.manual_uvc_filename}.*"),
                defines.wizardHistoryPath.glob("uvcalib_data.*"),
                defines.wizardHistoryPath.glob("uvcalibrationwizard_data.*"),
                defines.wizardHistoryPath.glob("uv_calibration_data.*"),
                )
        filenames = sorted(list(chain(*data_paths)), key=lambda path: path.stat().st_mtime, reverse=True)
        if filenames:
            for fn in filenames:
                prefix = "F:" if fn.parent == defines.wizardHistoryPathFactory else "U:"
                self.add_item(AdminAction(prefix + fn.name, functools.partial(self.show_calibration, fn)))
        else:
            self.add_label("(no data)")

    @SafeAdminMenu.safe_call
    def show_calibration(self, filename):
        generate.uv_calibration_result(None, filename, defines.fullscreenImage)
        self._control.fullscreen_image()


class DisplayControlMenu(SafeAdminMenu):
    def __init__(self, control: AdminControl, printer: Printer):
        super().__init__(control)
        self._printer = printer

        self.add_back()
        self.add_items(
            (
                AdminBoolValue("UV", self.get_uv, self.set_uv),
                AdminAction("Chess 8", self.chess_8),
                AdminAction("Chess 16", self.chess_16),
                AdminAction("Grid 8", self.grid_8),
                AdminAction("Grid 16", self.grid_16),
                AdminAction("Maze", self.maze),
                AdminAction("USB:/test.png", self.usb_test),
                AdminAction("Prusa logo", self.prusa),
                AdminAction("Black", self.black),
                AdminAction("Inverse", self.invert),
            )
        )

    def on_leave(self):
        self._printer.hw.saveUvStatistics()
        hw_all_off(self._printer.hw, self._printer.exposure_image)

    def get_uv(self):
        return self._printer.hw.getUvLedState()[0]

    def set_uv(self, enabled: bool):
        if enabled:
            self._printer.hw.startFans()
            self._printer.hw.uvLedPwm = self._printer.hw.config.uvPwm
        else:
            self._printer.hw.stopFans()

        self._printer.hw.uvLed(enabled)

    @SafeAdminMenu.safe_call
    def chess_8(self):
        self._printer.exposure_image.show_system_image("chess8.png")

    @SafeAdminMenu.safe_call
    def chess_16(self):
        self._printer.exposure_image.show_system_image("chess16.png")

    @SafeAdminMenu.safe_call
    def grid_8(self):
        self._printer.exposure_image.show_system_image("grid8.png")

    @SafeAdminMenu.safe_call
    def grid_16(self):
        self._printer.exposure_image.show_system_image("grid16.png")

    @SafeAdminMenu.safe_call
    def maze(self):
        self._printer.exposure_image.show_system_image("maze.png")

    @SafeAdminMenu.safe_call
    def usb_test(self):
        save_path = files.get_save_path()
        if save_path is None:
            raise ValueError("No USB path")
        test_file = save_path / "test.png"
        if not test_file.exists():
            raise FileNotFoundError(f"Test image not found: {test_file}")
        self._printer.exposure_image.show_image_with_path(str(test_file))

    @SafeAdminMenu.safe_call
    def prusa(self):
        self._printer.exposure_image.show_system_image("logo.png")

    @SafeAdminMenu.safe_call
    def black(self):
        self._printer.exposure_image.blank_screen()

    @SafeAdminMenu.safe_call
    def invert(self):
        self._printer.exposure_image.inverse()


class DirectPwmSetMenu(SafeAdminMenu):
    def __init__(self, control: AdminControl, printer: Printer):
        super().__init__(control)
        self._printer = printer
        self._temp = self._printer.hw.config.get_writer()
        self._run = True
        self._status = "<h3>UV meter disconnected<h3>"
        self._data = None

        self.add_back()
        uv_pwm_item = AdminIntValue.from_value("UV LED PWM", self._temp, "uvPwm", 1)
        uv_pwm_item.changed.connect(self._uv_pwm_changed)
        self.add_items(
            (
                AdminBoolValue.from_value("UV LED", self, "uv_led"),
                AdminAction("Inverse", self.invert),
                uv_pwm_item,
                AdminLabel.from_property(self, DirectPwmSetMenu.status),
                AdminAction("Show measured data", functools.partial(self.show_calibration)),
                AdminAction("Save", self.save),
            )
        )
        self._thread = Thread(target=self._measure)

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, value: str):
        self._status = value

    def on_enter(self):
        self._thread.start()
        self.enter(Wait(self._control, self._do_prepare))

    def on_leave(self):
        self._run = False
        hw_all_off(self._printer.hw, self._printer.exposure_image)
        self._printer.hw.saveUvStatistics()
        if self._temp.changed():
            self._control.enter(Info(self._control, "Configuration has been changed but NOT saved."))
        self._thread.join()

    def _measure(self):
        meter = UvLedMeterMulti()
        connected = False
        while self._run:
            if connected:
                if meter.read():
                    self._data = meter.get_data(plain_mean=True)
                    self._data.uvFoundPwm = self._temp.uvPwm
                    self.status = "<h3>ø:%.1f σ:%.1f %.1f°C<h3>" % (
                        self._data.uvMean,
                        self._data.uvStdDev,
                        self._data.uvTemperature,
                    )
                else:
                    self.status = "<h3>UV meter disconnected<h3>"
                    connected = False
            elif meter.connect():
                self.status = "<h3>UV meter connected<h3>"
                connected = True
        meter.close()

    @SafeAdminMenu.safe_call
    def show_calibration(self):
        generate.uv_calibration_result(asdict(self._data) if self._data else None, None, defines.fullscreenImage)
        self._control.fullscreen_image()

    @SafeAdminMenu.safe_call
    def _do_prepare(self, status: AdminLabel):
        self._printer.hw.powerLed("warn")
        status.set("<h3>Tilt is going to level<h3>")
        self._printer.hw.tilt.profile_id = TiltProfile.homingFast
        self._printer.hw.tilt.sync_wait()
        self._printer.hw.tilt.profile_id = TiltProfile.moveFast
        self._printer.hw.tilt.move_up_wait()
        self._printer.hw.powerLed("normal")
        status.set("<h3>Tilt leveled<h3>")
        self._printer.hw.startFans()
        self._printer.hw.uvLedPwm = self._temp.uvPwm
        self._printer.hw.uvLed(True)
        self._printer.exposure_image.blank_screen()
        self._printer.exposure_image.inverse()

    @property
    def uv_led(self) -> bool:
        uv_led_state = self._printer.hw.getUvLedState()
        return uv_led_state[0]

    @uv_led.setter
    def uv_led(self, value: bool):
        if value:
            self._printer.hw.startFans()
            self._printer.hw.uvLedPwm = self._temp.uvPwm
        else:
            self._printer.hw.stopFans()
        self._printer.hw.uvLed(value)

    @SafeAdminMenu.safe_call
    def invert(self):
        self._printer.exposure_image.inverse()

    @SafeAdminMenu.safe_call
    def save(self):
        self._temp.commit(write=True)
        if self._data:
            file_path = defines.wizardHistoryPathFactory / f"{defines.manual_uvc_filename}.{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.json"
            with file_path.open("w") as file:
                json.dump(asdict(self._data), file, indent=2, sort_keys=True)
        self._control.enter(Info(self._control, "Configuration saved"))

    def _uv_pwm_changed(self):
        self._printer.hw.uvLedPwm = self._temp.uvPwm
