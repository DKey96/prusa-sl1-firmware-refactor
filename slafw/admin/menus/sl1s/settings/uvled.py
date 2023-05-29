# This file is part of the SLA firmware
# Copyright (C) 2020-2022 Prusa Development a.s. - www.prusa3d.com
# SPDX-License-Identifier: GPL-3.0-or-later

from slafw.admin.control import AdminControl
from slafw.admin.items import AdminIntValue, AdminBoolValue, AdminAction
from slafw.admin.menus.common.settings.uvled import UVLedMenu as UVLedMenuCommon
from slafw.admin.menus.sl1s.settings.direct_uvpwm import DirectPwmSetMenu
from slafw.libPrinter import Printer


class UVLedMenu(UVLedMenuCommon):
    def __init__(self, control: AdminControl, printer: Printer):
        super().__init__(control, printer)

        uv_pwm_item = AdminIntValue.from_value("UV LED PWM", self._temp, "uvPwm", 1, "uv_calibration")
        uv_pwm_item.changed.connect(self._uv_pwm_changed)
        uv_pwm_tune_item = AdminIntValue.from_value("UV LED PWM fine tune", self._temp, "uvPwmTune", 1, "change_color")
        uv_pwm_tune_item.changed.connect(self._uv_pwm_changed)

        self.add_items(
            (
                AdminAction("Direct UV PWM settings", self.enter_direct_uvpwm, "display_test_color"),
                AdminAction("Write PWM to booster board", self._write_to_booster, "firmware-icon"),
                AdminBoolValue.from_value("UV LED", self, "uv_led", "led_set_replacement"),
                uv_pwm_item,
                uv_pwm_tune_item,
                AdminIntValue.from_value("UV calibration warm-up [s]", self._temp, "uvWarmUpTime", 1,
                                         "exposure_times_color"),
                AdminIntValue.from_value("UV calibration intensity", self._temp, "uvCalibIntensity", 1,
                                         "brightness_color"),
                AdminIntValue.from_value("UV calibration min. intensity edge", self._temp, "uvCalibMinIntEdge", 1,
                                         "brightness_color"),
            )
        )

    def _do_enter_direct_uvpwm(self):
        self._control.enter(DirectPwmSetMenu(self._control, self._printer))
