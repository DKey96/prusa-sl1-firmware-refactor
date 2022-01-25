# This file is part of the SLA firmware
# Copyright (C) 2020 Prusa Research a.s. - www.prusa3d.com
# SPDX-License-Identifier: GPL-3.0-or-later

from typing import Optional
from pathlib import Path
import json
import numpy
from PIL import Image

from slafw.errors.errors import DisplayUsageError, NoUvCalibrationData, DataFromUnknownUvSensor
from slafw.hardware.printer_model import ExposureScreenParameters
from slafw.configs.toml import TomlConfig
from slafw.libUvLedMeterMulti import UvLedMeterMulti

def display_usage_heatmap(
        parameters: ExposureScreenParameters,
        data_filename: str,
        palette_filename: str,
        output_filename: str) -> None:

    try:
        palette_bytes = bytes()
        with open(palette_filename, "r") as f:
            for line in f:
                palette_bytes += bytes.fromhex(line.strip()[1:])
        palette = list(palette_bytes)
    except Exception as e:
        raise DisplayUsageError("Load palette failed.") from e

    try:
        with numpy.load(data_filename) as npzfile:
            saved_data = npzfile["display_usage"]
    except Exception as e:
        raise DisplayUsageError("No display usage data.") from e

    if saved_data.shape != parameters.display_usage_size_px:
        raise DisplayUsageError("Wrong saved data shape: %s" % saved_data.shape)

    max_value = saved_data.max()
    saved_data = saved_data * 255 / max_value # 0-255 range
    image = Image.fromarray(saved_data.astype("int8"), "P").transpose(Image.ROTATE_270)
    # two pixels outline
    output = Image.new("P", (parameters.display_usage_size_px[0] + 4, parameters.display_usage_size_px[1] + 4), 255)
    output.putpalette(palette)
    output.paste(image, (2, 2))
    output.save(output_filename)


def uv_calibration_result(data: Optional[dict], data_filename: Optional[Path], output_filename: str) -> None:
    if not data and data_filename:
        if data_filename.suffix == ".toml":
            data = TomlConfig(data_filename).load()
        elif data_filename.suffix == ".json":
            with open(data_filename, "r") as jf:
                data = json.load(jf)
        else:
            raise NoUvCalibrationData
    if not data:
        raise NoUvCalibrationData
    if data.get('uvSensorType', None) == 0:
        UvLedMeterMulti().save_pic(800, 480, "PWM: %d" % data['uvFoundPwm'], output_filename, data)
    else:
        raise DataFromUnknownUvSensor