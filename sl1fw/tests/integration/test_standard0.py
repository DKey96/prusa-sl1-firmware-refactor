# This file is part of the SL1 firmware
# Copyright (C) 2014-2018 Futur3d - www.futur3d.net
# Copyright (C) 2018-2019 Prusa Research s.r.o. - www.prusa3d.com
# SPDX-License-Identifier: GPL-3.0-or-later

# pylint: disable=too-few-public-methods

import os
import unittest
from time import sleep

from pydbus import SystemBus, Variant

from sl1fw.tests.integration.base import Sl1FwIntegrationTestCaseBase
from sl1fw.api.standard0 import Standard0, Standard0State


class TestIntegrationStandard0(Sl1FwIntegrationTestCaseBase):
    def setUp(self):
        super().setUp()

        # Fake calibration
        self.printer.hw.config.calibrated = True
        self.printer.hw.config.fanCheck = False
        self.printer.hw.config.coverCheck = False
        self.printer.hw.config.resinSensor = False
        self.standard =  Standard0(self.printer)

        # dbus
        bus = SystemBus()
        self.standard0_dbus = bus.publish(Standard0.__INTERFACE__, Standard0(self.printer))

        # Resolve standard printer and open project
        self.standard0: Standard0 = bus.get("cz.prusa3d.sl1.standard0")
        self.standard0.cmd_select(str(self.SAMPLES_DIR / "numbers.sl1"), False, False)

    def tearDown(self):
        self.standard0_dbus.unpublish()
        super().tearDown()

    def test_read_printer_values(self):
        self.assertEqual(Standard0State.SELECTED.name, self.standard0.state)
        self.assertKeysIn(['temp_led', 'temp_amb', 'cpu_temp'], self.standard0.hw_temperatures)
        self.assertDictEqual({'uv_led': 0, 'blower': 0, 'rear': 0}, self.standard0.hw_fans)
        self.assertKeysIn(['cover_closed', 'temperatures', 'fans', 'state'], self.standard0.hw_telemetry)
        self.assertDictEqual({'type': 'digest', 'password': '32LF9aXN'}, self.standard0.net_authorization)

        # it needs Hostname and NetworkManager dbus
        # self.assertEqual(str, type(self.standard0.net_hostname))
        # self.assertEqual(dict, type(self.standard0.info))
        # self.assertEqual(type,  type(self.standard0.net_ip))

    def test_read_project_values(self):
        self.assertEqual("numbers.sl1",  os.path.basename(self.standard0.project_path))
        self.assertDictEqual(
            {
                'exposure_time_ms': 1000,
                'calibrate_time_ms': 1000,
                'calibration_regions': 0,
                'exposure_time_first_ms': 1000,
                'exposure_user_profile': 0
            },
            self.standard0.project_get_properties(["exposure_times"])
        )
        self.standard0.project_set_properties({ "exposure_time_ms": Variant("i", 1042) })
        self.assertDictEqual({ "exposure_time_ms": 1042 }, self.standard0.project_get_properties(["exposure_time_ms"]))

    def test_cmds_print_pause_cont(self):
        self.standard0.cmd_confirm()
        self._wait_for_state(Standard0State.BUSY, 60) # exposure.HOMING_AXIS
        self._wait_for_state(Standard0State.ATTENTION, 10) # exposure.POUR_IN_RESIN
        self.standard0.cmd_resin_in()
        self._wait_for_state(Standard0State.BUSY, 60) # exposure.CHECKS
        self._wait_for_state(Standard0State.PRINTING, 60)
        self.standard0.cmd_pause("feed_me")
        self._wait_for_state(Standard0State.REFILL, 30)
        self.standard0.cmd_continue()
        self._wait_for_state(Standard0State.PRINTING, 30)
        self.standard0.cmd_cancel()
        self._wait_for_state(Standard0State.READY, 30)

    def test_cmds_print_pause_back(self):
        self.standard0.cmd_confirm()
        self._wait_for_state(Standard0State.BUSY, 60)  # exposure.HOMING_AXIS
        self._wait_for_state(Standard0State.ATTENTION, 10)  # exposure.POUR_IN_RESIN
        self.standard0.cmd_resin_in()
        self._wait_for_state(Standard0State.BUSY, 60)  # exposure.CHECKS
        self._wait_for_state(Standard0State.PRINTING, 60)
        self.standard0.cmd_pause("feed_me")
        self._wait_for_state(Standard0State.REFILL, 30)
        self.standard0.cmd_back()
        self._wait_for_state(Standard0State.PRINTING, 30)
        # wait for end
        self._wait_for_state(Standard0State.READY, 60)

    def _wait_for_state(self, state: Standard0State, timeout_s: int):
        printer_state = None
        for _ in range(timeout_s):
            printer_state = self.standard0.state
            if printer_state == state.name:
                break
            print(f"Waiting for state: {state}, current state: {printer_state}")
            sleep(1)
        self.assertEqual(state.name, printer_state)
        print(f"Finished waiting for state: {state}")

    def assertKeysIn(self, keys:list, container:dict):
        for key in keys:
            self.assertIn(key, container)


if __name__ == "__main__":
    unittest.main()
