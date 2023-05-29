from slafw.admin.control import AdminControl
from slafw.admin.menus.common.dialogs import Info, Confirm
from slafw.admin.menus.common.settings.base import SettingsMenu
from slafw.admin.menus.common.settings.direct_uvpwm import DirectPwmSetMenu
from slafw.admin.safe_menu import SafeAdminMenu
from slafw.libPrinter import Printer


class UVLedMenu(SettingsMenu):
    def __init__(self, control: AdminControl, printer: Printer):
        super().__init__(control, printer)
        self._printer = printer

        self._uv_pwm_print = self._temp.uvPwmPrint

    def on_leave(self):
        super().on_leave()
        self._printer.hw.uv_led.save_usage()

    @property
    def uv_led(self) -> bool:
        return self._printer.hw.uv_led.active

    @uv_led.setter
    def uv_led(self, value: bool):
        if value:
            self._printer.hw.start_fans()
            self._printer.hw.uv_led.pwm = self._uv_pwm_print
            self._printer.hw.uv_led.on()
        else:
            self._printer.hw.stop_fans()
            self._printer.hw.uv_led.off()

    @SafeAdminMenu.safe_call
    def _write_to_booster(self):
        self._printer.hw.uv_led.pwm = self._uv_pwm_print
        self._printer.hw.sl1s_booster.save_permanently()
        self._control.enter(Info(self._control, "PWM value was written to the booster board"))

    def _uv_pwm_changed(self):
        # TODO: simplify work with config and config writer
        self._uv_pwm_print = self._temp.uvPwm + self._temp.uvPwmTune
        self._printer.hw.uv_led.pwm = self._uv_pwm_print

    def enter_direct_uvpwm(self):
        self._control.enter(
            Confirm(
                self._control,
                self._do_enter_direct_uvpwm,
                headline="Do you really want to enter the menu?",
                text="It will turn on the UV LED, open the exposure display\n"
                     "and move the tilt. Do not enter during active print job.",
            )
        )

    def _do_enter_direct_uvpwm(self):
        self._control.enter(DirectPwmSetMenu(self._control, self._printer))
