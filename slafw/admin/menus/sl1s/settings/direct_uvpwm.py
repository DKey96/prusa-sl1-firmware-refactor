# This file is part of the SLA firmware
# Copyright (C) 2022 Prusa Development a.s. - www.prusa3d.com
# SPDX-License-Identifier: GPL-3.0-or-later

from functools import partial
from threading import Thread

from slafw.admin.control import AdminControl
from slafw.admin.items import AdminAction, AdminBoolValue, AdminIntValue, AdminLabel
from slafw.admin.menus.common.settings.direct_uvpwm import DirectPwmSetMenu as DirectPwmSetMenuCommon
from slafw.libPrinter import Printer


class DirectPwmSetMenu(DirectPwmSetMenuCommon):
    def __init__(self, control: AdminControl, printer: Printer):
        super().__init__(control, printer)

        uv_pwm_item = AdminIntValue.from_value("UV LED PWM", self._temp, "uvPwm", 1, "uv_calibration")
        uv_pwm_item.changed.connect(self._uv_pwm_changed)
        uv_pwm_tune_item = AdminIntValue.from_value("UV LED PWM fine tune", self._temp, "uvPwmTune", 1, "change_color")
        uv_pwm_tune_item.changed.connect(self._uv_pwm_changed)
        self.uv_pwm_print_item = AdminLabel.from_property(self, DirectPwmSetMenu.uv_pwm_print, "system_info_color")
        self.add_items(
            (
                AdminBoolValue.from_value("UV LED", self, "uv_led", "led_set_replacement"),
                AdminAction("Open screen", self.open, "print_color"),
                AdminAction("Close screen", self.close, "disabled_color"),
                AdminAction("Calculate PWM from display transmittance", self.calculate_pwm, "statistics_color"),
                self.uv_pwm_print_item,
                uv_pwm_item,
                uv_pwm_tune_item,
                AdminLabel.from_property(self, DirectPwmSetMenu.status, "system_info_color"),
                AdminAction("Show measured data", partial(self.show_calibration), "logs-icon"),
            )
        )
        self._thread = Thread(target=self._measure)
