# This file is part of the SL1 firmware
# Copyright (C) 2014-2018 Futur3d - www.futur3d.net
# Copyright (C) 2018-2019 Prusa Research s.r.o. - www.prusa3d.com
# SPDX-License-Identifier: GPL-3.0-or-later

# TODO: Fix following pylint problems
# pylint: disable=too-many-statements

import os
from time import sleep

import unittest

from mock import patch

from sl1fw.tests.integration.base import Sl1FwIntegrationTestCaseBase

from sl1fw.libConfig import HwConfig, TomlConfig


class TestIntegrationPages(Sl1FwIntegrationTestCaseBase):
    def test_turnoff(self):
        # Turn off
        self.press("turnoff")
        self.waitPage("yesno")
        self.press("yes")

    def test_control(self):
        self.switchPage("control")
        self.press("top")
        self.waitPage("wait")
        self.waitPage("control", timeout_sec=30)
        self.press("tankres")
        self.waitPage("wait")
        self.waitPage("control", timeout_sec=30)
        self.press("disablesteppers")

        self.test_turnoff()

    def test_support(self):
        self.switchPage("settings")
        self.switchPage("support")

        for page in ["manual", "videos", "sysinfo", "about"]:
            self.switchPage(page)
            self.press("back")
            self.waitPage("support")

        self.press("back")
        self.waitPage("settings")

        self.press("back")
        self.waitPage("home")

        self.test_turnoff()

    def test_advancedsettings(self):
        self.switchPage("settings")
        self.switchPage("advancedsettings")

        # Test moves
        for page in ["towermove", "tiltmove"]:
            self.switchPage(page)

            for action in ["upfast", "upslow", "downfast", "downslow"]:
                self.press(action)

            self.press("back")
            self.waitPage("advancedsettings")

        # Test language settings
        self.switchPage("setlanguage")
        # TODO: Implement and try changing language
        self.press("back")
        self.waitPage("advancedsettings")

        # Test hostname settings
        self.switchPage("sethostname")
        # Try changning hostname
        self.press("back")
        self.waitPage("advancedsettings")

        # Test login credentials settings
        self.press("setremoteaccess")
        self.waitPage("setlogincredentials")
        self.press("back")
        self.waitPage("advancedsettings")

        # TODO: Test changing settings

        # Test display & UV settings
        self.press("uvdispsettings")
        self.waitPage("uvdispsettings")  # Enter into UV submenu
        self.press("back")
        self.waitPage("advancedsettings")

        # Test firmware update
        self.switchPage("firmwareupdate")
        self.press("back")
        self.waitPage("advancedsettings")

        self.press("back")
        self.waitPage("settings")

        self.press("back")
        self.waitPage("home")

        self.test_turnoff()

    def test_display_passing(self):
        self.printer.hwConfig.coverCheck = False
        self.switchPage("settings")
        self.switchPage("advancedsettings")
        self.switchPage("uvdispsettings")

        self.press("displaytest")
        self.waitPage("confirm")  # Please unscrew and remove ...
        self.press("cont")
        self.waitPage("confirm")  # Please close the orange lid...
        self.press("cont")
        self.waitPage("yesno")  # Can you see company logo...
        self.press("yes")
        self.waitPage("uvdispsettings")

    def test_display_failing(self):
        self.printer.hwConfig.coverCheck = False
        self.switchPage("settings")
        self.switchPage("advancedsettings")
        self.switchPage("uvdispsettings")

        self.press("displaytest")
        self.waitPage("confirm")  # Please unscrew and remove ...
        self.press("cont")
        self.waitPage("confirm")  # Please close the orange lid...
        self.press("cont")
        self.waitPage("yesno")  # Can you see company logo...
        self.press("no")
        self.waitPage("error")  # No logo, contact service
        self.press("ok")
        self.waitPage("uvdispsettings")

    def uv_calibration_enter_exit(self):
        self.printer.hwConfig.coverCheck = False
        self.switchPage("settings")
        self.switchPage("advancedsettings")
        self.switchPage("uvdispsettings")

        self.press("uvcalibration")
        self.waitPage("confirm")  # Welcome to UV calibration ...
        self.press("back")
        self.waitPage("yesno")  # Cancel calibration? ...
        self.press("yes")
        self.waitPage("uvdispsettings")

    def test_uv_calibration_no_uvmeter(self):
        self.printer.hwConfig.coverCheck = False
        self.switchPage("settings")
        self.switchPage("advancedsettings")
        self.switchPage("uvdispsettings")

        with patch("sl1fw.test_runtime.test_uvmeter_present", False):
            self.printer.hwConfig.coverCheck = False
            self.press("uvcalibration")
            self.waitPage("confirm")  # Welcome to UV calibration ...
            self.press("cont")
            self.waitPage("yesno")  # New expo display? ...
            self.press("no")
            self.waitPage("yesno")  # New uv led set? ...
            self.press("no")
            self.waitPage("wait")  # Start positions
            self.waitPage("yesno")  # Display test. Can you see the logo? ...
            self.press("yes")
            self.waitPage("confirm")  # Place the UV meter in and close lid ...
            self.press("cont")
            self.waitPage("wait")  # Waiting for UV meter
            self.waitPage("error")  # No UV meter connected
            self.press("ok")
            self.waitPage("uvdispsettings")

    def test_uv_calibration_pass(self):
        with patch("sl1fw.test_runtime.test_fan_error_override", True):
            self.printer.hwConfig.coverCheck = False
            self.switchPage("settings")
            self.switchPage("advancedsettings")
            self.switchPage("uvdispsettings")

            self.printer.hwConfig.coverCheck = False
            self.press("uvcalibration")
            self.waitPage("confirm")  # Welcome to UV calibration ...
            self.press("cont")
            self.waitPage("yesno")  # New expo display? ...
            self.press("yes")
            self.waitPage("yesno")  # New uv led set? ...
            self.press("no")
            self.waitPage("confirm")  # Warning abour reseting counters and write to factory
            self.press("cont")
            self.waitPage("wait")  # Start positions
            self.waitPage("yesno", timeout_sec=15)  # Display test. Can you see the logo? ...
            self.press("yes")
            self.waitPage("confirm")  # Place the UV meter in and close lid ...
            self.press("cont")
            self.waitPage("wait")  # Waiting for UV meter
            self.waitPage("yesno", timeout_sec=180)  # use new calibration
            self.press("no")
            self.waitPage("uvdispsettings")

            self.test_turnoff()

    def test_uv_calibration_pass_factory(self):
        with patch("sl1fw.test_runtime.test_fan_error_override", True):
            self.printer.hwConfig.coverCheck = False
            self.switchPage("settings")
            self.switchPage("advancedsettings")
            self.switchPage("uvdispsettings")

            self.printer.hwConfig.coverCheck = False
            self.press("uvcalibration")
            self.waitPage("confirm")  # Welcome to UV calibration ...
            self.press("cont")
            self.waitPage("yesno")  # New expo display? ...
            self.press("no")
            self.waitPage("yesno")  # New uv led set? ...
            self.press("yes")
            self.waitPage("confirm")  # Warning abour reseting counters and write to factory
            self.press("cont")
            self.waitPage("wait")  # Start positions
            self.waitPage("yesno", timeout_sec=15)  # Display test. Can you see the logo? ...
            self.press("yes")
            self.waitPage("confirm")  # Place the UV meter in and close lid ...
            self.press("cont")
            self.waitPage("wait")  # Waiting for UV meter
            self.waitPage("yesno", timeout_sec=180)  # use new calibration
            self.press("no")
            self.waitPage("uvdispsettings")

            self.test_turnoff()

    def test_uv_calibration_pass_with_errors(self):
        with patch("sl1fw.test_runtime.test_fan_error_override", True), patch("sl1fw.test_runtime.uv_error_each", 3):
            self.printer.hwConfig.coverCheck = False
            self.switchPage("settings")
            self.switchPage("advancedsettings")
            self.switchPage("uvdispsettings")

            self.printer.hwConfig.coverCheck = False
            self.press("uvcalibration")
            self.waitPage("confirm")  # Welcome to UV calibration ...
            self.press("cont")
            self.waitPage("yesno")  # New expo display? ...
            self.press("no")
            self.waitPage("yesno")  # New uv led set? ...
            self.press("no")
            self.waitPage("wait")  # Start positions
            self.waitPage("yesno", timeout_sec=15)  # Display test. Can you see the logo? ...
            self.press("yes")
            self.waitPage("confirm")  # Place the UV meter in and close lid ...
            self.press("cont")
            self.waitPage("wait")  # Waiting for UV meter
            self.waitPage("yesno", timeout_sec=180)  # use new calibration
            self.press("no")
            self.waitPage("uvdispsettings")

            self.test_turnoff()

    def test_factory_reset_factory_complete(self):
        self._fake_calibration()

        self.printer.hw.boardData = ("TEST complete", False)
        self.printer.runtime_config.factory_mode = True
        self.switchPage("settings")
        self.switchPage("advancedsettings")
        self.press("factoryreset")
        # confirm
        self.waitPage("yesno")
        self.press("yes")
        self.waitPage("wait")  # Relax...
        self.waitPage("confirm", timeout_sec=30)  # Insert protective foam
        self.press("cont")
        self.waitPage("wait")  # Printer is being set to packing positions
        self._check_factory_reset(unboxing=True, factoryMode=False)

    def test_factory_reset_factory_kit(self):
        self.printer.hw.boardData = ("TEST kit", True)
        self.printer.runtime_config.factory_mode = True
        self.switchPage("settings")
        self.switchPage("advancedsettings")
        self.press("factoryreset")
        self.waitPage("yesno") # confirm
        self.press("yes")
        self.waitPage("wait")  # Relax...
        sleep(5)
        self._check_factory_reset(unboxing=True, factoryMode=False)

    def test_factory_reset_user_complete(self):
        self.printer.hw.boardData = ("TEST complete", False)
        self.printer.runtime_config.factory_mode = False
        self.switchPage("settings")
        self.switchPage("advancedsettings")
        self.press("factoryreset")
        self.waitPage("yesno") # erase projects?
        self.press("no")
        self.waitPage("yesno") # confirm
        self.press("yes")
        self.waitPage("wait")  # Relax...
        sleep(5)
        self._check_factory_reset(unboxing=False, factoryMode=True)  # user reset doesn't reset factoryMode

    def test_factory_reset_user_kit(self):
        self.printer.hw.boardData = ("TEST kit", True)
        self.printer.runtime_config.factory_mode = False
        self.switchPage("settings")
        self.switchPage("advancedsettings")
        self.press("factoryreset")
        self.waitPage("yesno") # erase projects?
        self.press("no")
        self.waitPage("yesno") # confirm
        self.press("yes")
        self.waitPage("wait")  # Relax...
        sleep(5)
        self._check_factory_reset(unboxing=False, factoryMode=True)  # user reset doesn't reset factoryMode

    def _check_factory_reset(self, unboxing, factoryMode):
        self.assertFalse(os.path.exists(self.API_KEY_FILE), "apikey reset check")
        self.assertFalse(os.path.exists(self.UV_CALIB_DATA_FILE), "user UV calibration data reset check")
        hwConfig = HwConfig(self.HARDWARE_FILE)
        hwConfig.read_file()
        self.assertTrue(hwConfig.showUnboxing == unboxing, "config reset check")
        factoryConfig = TomlConfig(self.FACTORY_CONFIG_FILE)
        factoryConfig.load()
        self.assertTrue(factoryConfig.data["factoryMode"] == factoryMode, "factory is disabled check")
        # TODO check D-BUS hostname reset
        # TODO check D-BUS wifi reset
        # TODO check D-BUS timezone reset
        # TODO check D-BUS locale reset
        # TODO check D-Bus NTP reset

    def test_print_not_calibrated(self):
        # Try to print
        self.press("print")
        # Expect problem with not being calibrated
        self.waitPage("confirm")
        self.press("back")
        self.waitPage("yesno")
        self.press("yes")
        # Return to home
        self.waitPage("home")

        self.test_turnoff()

    def test_print(self):
        PROJECT_NAME = "numbers"

        self._fake_calibration()

        self.press("print")
        self.waitPage("sourceselect")
        choice = None
        for source in self.readItems()["sources"]:
            if source["name"] == PROJECT_NAME:
                choice = source["choice"]
        self.assertIsNotNone(choice, f"Test project name ({PROJECT_NAME} in sources")
        self.press("source", data={"choice": choice})
        self.waitPage("wait")  # reading project data
        self.waitPage("printpreviewswipe")
        self.press("change")
        self.waitPage("change")
        self.press("expossubsecond")
        # 1.0 -> 10.0
        self.press("exposfirstaddsecond")
        self.press("exposfirstaddsecond")
        self.press("exposfirstaddsecond")
        self.press("exposfirstaddsecond")
        self.press("exposfirstaddsecond")
        self.press("exposfirstaddsecond")
        self.press("exposfirstaddsecond")
        self.press("exposfirstaddsecond")
        self.press("exposfirstaddsecond")
        self.press("back")
        self.waitPage("printpreviewswipe")
        self.press("cont")
        self.waitPage("preprintchecks", timeout_sec=120)  # checks
        self.waitPage("print", timeout_sec=30)  # printing
        self.waitPage("wait", timeout_sec=240)  # moving platform to the top
        self.waitPage("home", timeout_sec=30)
        # auto off enabled

    def test_wizard(self):
        self.test_turnoff()

    def test_calibration(self):
        self.printer.hwConfig.coverCheck = False

        self.switchPage("settings")
        self.press("recalibration")
        self.waitPage("confirm")  # If platform is not yet inserted ...
        self.press("cont")
        self.waitPage("wait")  # Printer homing
        self.waitPage("confirm", timeout_sec=30)  # Loosen the small screw ...
        self.press("cont")
        self.waitPage("confirm")  # Unscrew the tank ...
        self.press("cont")
        self.waitPage("wait", timeout_sec=60)  # Moving to start position
        self.waitPage("confirm")  # In the next step, move ...
        self.press("cont")
        self.waitPage("tiltmovecalibration")
        self.press("slowDown")
        self.press("slowUp")
        self.press("ok")
        self.waitPage("confirm")  # Make sure the platform, tank ...
        self.press("cont")
        self.waitPage("confirm")  # Return the tank to the original
        self.press("cont")
        self.waitPage("confirm")  # Check whenever the platform ...
        self.press("cont")
        self.waitPage("confirm")  # Please close the orange lid.
        self.press("cont")
        self.waitPage("wait")  # Platform calibration
        self.waitPage("confirm", timeout_sec=30)  # Adjust the platform ...
        self.press("cont")
        self.waitPage("confirm")  # Tighten the small screw
        self.press("cont")
        self.waitPage("wait")  # Measuring tilt times
        self.waitPage("confirm", timeout_sec=120)  # Calibration done
        self.press("cont")

        self.waitPage("settings")
        self.press("back")
        self.waitPage("home")

        self.test_turnoff()

    def _fake_calibration(self):
        # Fake calibration
        self.printer.hwConfig.calibrated = True
        self.printer.hwConfig.fanCheck = False
        self.printer.hwConfig.coverCheck = False
        self.printer.hwConfig.resinSensor = False


if __name__ == "__main__":
    unittest.main()