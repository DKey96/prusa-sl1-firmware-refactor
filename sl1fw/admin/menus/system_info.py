# This file is part of the SL1 firmware
# Copyright (C) 2021 Prusa Development a.s. - www.prusa3d.com
# SPDX-License-Identifier: GPL-3.0-or-later

from datetime import datetime, timedelta
from threading import Thread
from time import sleep

import distro
import psutil

from sl1fw import defines
from sl1fw.admin.control import AdminControl
from sl1fw.admin.items import AdminAction
from sl1fw.admin.menu import AdminMenu
from sl1fw.functions.system import get_octoprint_auth
from sl1fw.libConfig import TomlConfigStats
from sl1fw.libPrinter import Printer


class SystemInfoMenu(AdminMenu):
    # pylint: disable = too-many-instance-attributes
    def __init__(self, control: AdminControl, printer: Printer):
        super().__init__(control)
        self._printer = printer

        self.add_back()

        self.system_time = self.add_label()
        self.system_uptime = self.add_label()
        self.os_version = self.add_label()
        self.a64_sn = self.add_label()
        self.emmc_sn = self.add_label()
        self.api_key = self.add_label()
        self.mc_sn = self.add_label()
        self.mc_sw = self.add_label()
        self.mc_rev = self.add_label()
        self.net_state = self.add_label()
        self.net_dev = self.add_label()
        self.slow_tilt = self.add_label()
        self.fast_tilt = self.add_label()
        self.resin_sensor = self.add_label()
        self.cover = self.add_label()
        self.cpu_temp = self.add_label()
        self.uv_led_temp = self.add_label()
        self.ambient_temp = self.add_label()
        self.fans = self.add_label()
        self.uv_led = self.add_label()
        self.uv_counter = self.add_label()
        self.display_counter = self.add_label()
        self.started_projects = self.add_label()
        self.finished_projects = self.add_label()
        self.total_layers = self.add_label()
        self.total_print_time = self.add_label()
        self.total_resin = self.add_label()

        self.add_item(AdminAction("Display usage heatmap", self._display_usage_heatmap))
        self.add_item(AdminAction("User sysinfo", self._control.sysinfo))

        self._running = True
        self._thread = Thread(target=self._run)

    def on_enter(self):
        self._thread.start()

    def on_leave(self):
        self._running = False
        self._thread.join()

    def _run(self):
        self._printer.hw.resinSensor(True)

        while self._running:
            self.logger.debug("Updating system information")
            self.system_time.set(f"System time: {datetime.now()}")
            self.system_uptime.set(f"System uptime: {datetime.now() - datetime.fromtimestamp(psutil.boot_time())}")
            self.os_version.set(f"OS version: {distro.version()}")
            self.a64_sn.set(f"A64 serial: {self._printer.hw.cpuSerialNo}")
            self.emmc_sn.set(f"eMMC serial: {self._printer.hw.emmc_serial}")
            self.api_key.set(f"API key: {get_octoprint_auth(self.logger)}")
            self.mc_sn.set(f"MC serial: {self._printer.hw.mcSerialNo}")
            self.mc_sw.set(f"MC SW version: {self._printer.hw.mcFwVersion}")
            self.mc_rev.set(f"MC revision: {self._printer.hw.mcBoardRevision}")
            self.net_state.set(f"Network state: {'online' if self._printer.inet.ip else 'offline'}")
            self.net_dev.set(f"Net devices: {self._printer.inet.devices}")
            self.slow_tilt.set(f"Slow tilt time: {self._printer.hwConfig.tiltSlowTime} s")
            self.fast_tilt.set(f"Fast tilt time: {self._printer.hwConfig.tiltFastTime} s")
            self.resin_sensor.set(f"Resin sensor triggered: {self._printer.hw.getResinSensorState()}")
            self.cover.set(f"Cover closed: {self._printer.hw.isCoverClosed()}")
            self.cpu_temp.set(f"CPU temperature: {self._printer.hw.getCpuTemperature()}")
            self.uv_led_temp.set(f"UV temperature: {self._printer.hw.getUvLedTemperature()}")
            self.ambient_temp.set(f"Ambient temperature: {self._printer.hw.getAmbientTemperature()}")
            self.fans.set(f"Fan: {self._printer.hw.getFansRpmDict()} RPM")
            self.uv_led.set(f"UV LED voltages: {self._printer.hw.getVoltages()}")
            uv_stats = self._printer.hw.getUvStatistics()
            self.uv_counter.set(f"UV LED counter: {timedelta(seconds=uv_stats[0])}")
            self.display_counter.set(f"Display counter: {timedelta(seconds=uv_stats[1])}")
            sys_stats = TomlConfigStats(defines.statsData, self._printer.hw)
            self.started_projects.set(f"Total started projects: {sys_stats['started_projects']}")
            self.finished_projects.set(f"Total finished projects: {sys_stats['finished_projects']}")
            self.total_layers.set(f"Total layers: {sys_stats['layers']}")
            self.total_print_time.set(f"Total print time: {timedelta(seconds=sys_stats['total_seconds'])}")
            self.total_resin.set(f"Total resin used: {sys_stats['total_resin']} ml")
            sleep(1)

        self._printer.hw.resinSensor(False)

    def _display_usage_heatmap(self):
        self._printer.display.forcePage("displayusage")
