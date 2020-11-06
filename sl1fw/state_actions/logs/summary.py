# This file is part of the SL1 firmware
# Copyright (C) 2014-2018 Futur3d - www.futur3d.net
# Copyright (C) 2018-2019 Prusa Research s.r.o. - www.prusa3d.com
# Copyright (C) 2020 Prusa Research a.s. - www.prusa3d.com
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import functools
import glob
import hashlib
import json
import logging
import os
import subprocess
import sys
import traceback
from datetime import datetime
from pathlib import Path

import psutil
from pydbus import SystemBus

from sl1fw import defines
from sl1fw.functions.system import get_update_channel
from sl1fw.libHardware import Hardware
from sl1fw.libConfig import TomlConfig, TomlConfigStats

def create_summary(hw: Hardware, logger: logging.Logger, summary_path: Path):
    data_template = {
        "hardware": functools.partial(log_hw, hw),
        "system": log_system,
        "network": log_network,
        "statistics": functools.partial(log_statistics, hw),
        "counters": log_counters,
    }

    data = {}
    exceptions = []
    for name, function in data_template.items():
        try:
            data[name] = function()
        except Exception as exception:
            exc_traceback = sys.exc_info()[2]
            exceptions.append({
                "name": name,
                "class": exception.__class__.__name__,
                "exception": traceback.format_tb(exc_traceback)
            })

    if exceptions:
        data["exceptions"] = exceptions

    try:
        with summary_path.open("w") as summary_file:
            summary_file.write(json.dumps(data, indent=2, sort_keys=True))
            return summary_file.name
    except Exception:
        logger.exception("Printer summary failed to assemble")


def log_hw(hw: Hardware) -> None:
    fans_rpm = hw.getFansRpm()
    voltages = hw.getVoltages()
    try:
        locales = SystemBus().get("org.freedesktop.locale1").Locale[0]
    except Exception:
        locales = "No info"

    data = {
        "Resin Sensor State": hw.getResinSensorState(),
        "Cover State": hw.isCoverClosed(),
        "Power Switch State": hw.getPowerswitchState(),
        "UV LED Temperature": hw.getUvLedTemperature(),
        "Ambient Temperature": hw.getAmbientTemperature(),
        "CPU Temperature": hw.getCpuTemperature(),
        "UV LED fan [rpm]": fans_rpm[0],
        "Blower fan [rpm]": fans_rpm[1],
        "Rear fan [rpm]": fans_rpm[2],
        "A64 Controller SN": hw.cpuSerialNo,
        "MC FW version": hw.mcFwVersion,
        "MC HW Reversion": hw.mcBoardRevision,
        "MC Serial number": hw.mcSerialNo,
        "UV LED Line 1 Voltage": voltages[0],
        "UV LED Line 2 Voltage": voltages[1],
        "UV LED Line 3 Voltage": voltages[2],
        "Power Supply Voltage": voltages[3],
        "Free Space in eMMC": psutil.disk_usage("/"),
        "RAM statistics": psutil.virtual_memory(),
        "CPU usage per core": psutil.cpu_percent(percpu=True),
        "CPU times": psutil.cpu_times(),
        "Language": locales,
    }
    return data


def log_system():
    data = {
        "time settings": {},
        "update channel": {},
        "slots info": {},
        "raucb updates": {},
    }
    time = SystemBus().get("org.freedesktop.timedate1")
    time_data = time.GetAll("org.freedesktop.timedate1")
    time_data["UniversalTime"] = str(datetime.fromtimestamp(time_data["TimeUSec"] // 1000000))
    time_data["RtcTime"] = str(datetime.fromtimestamp(time_data["RTCTimeUSec"] // 1000000))
    data["time settings"] = time_data

    hash_md5 = hashlib.md5()
    with open("/etc/rauc/ca.cert.pem", "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
        data["update channel"] = {"channel": get_update_channel(), "certificate_md5": hash_md5.hexdigest()}

    data["slots info"] = json.loads(
        subprocess.check_output(["rauc", "status", "--detailed", "--output-format=json"], universal_newlines=True)
    )

    fw_files = glob.glob(os.path.join(defines.mediaRootPath, "**/*.raucb"))
    if os.path.exists(defines.firmwareTempFile):
        fw_files.append(defines.firmwareTempFile)

    for key, fw_file in enumerate(fw_files):
        data["raucb updates"][key] = {}
        try:
            data["raucb updates"][key] = json.loads(
                subprocess.check_output(["rauc", "info", "--output-format=json", fw_file], universal_newlines=True)
            )
        except subprocess.CalledProcessError:
            data["raucb updates"][key] = "Error getting info from " + fw_file

    return data


def log_network():
    proxy = SystemBus().get("org.freedesktop.NetworkManager")
    data = {"wifi_enabled": proxy.WirelessEnabled, "primary_conn_type": proxy.PrimaryConnectionType}
    for devPath in proxy.Devices:
        dev = SystemBus().get("org.freedesktop.NetworkManager", devPath)
        data[dev.Interface] = {"state": dev.State, "mac": dev.HwAddress}
        if dev.State > 40:  # is connected to something
            devIp = SystemBus().get("org.freedesktop.NetworkManager", dev.Ip4Config)
            data[dev.Interface] = {"address": devIp.AddressData, "gateway": devIp.Gateway, "dns": devIp.NameserverData}
            if SystemBus().get("org.freedesktop.NetworkManager", dev.Dhcp4Config):
                data[dev.Interface]["dhcp"] = True
            else:
                data[dev.Interface]["dhcp"] = False

    return data


def log_statistics(hw: Hardware):
    data = TomlConfigStats(defines.statsData, None).load()
    data["UV LED Time Counter [h]"] = hw.getUvStatistics()[0] / 3600
    data["Display Time Counter [h]"] = hw.getUvStatistics()[1] / 3600
    return data


def log_counters():
    data = TomlConfig(defines.counterLog).load()
    return data