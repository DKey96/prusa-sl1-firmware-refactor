# This file is part of the SLA firmware
# Copyright (C) 2021-2022 Prusa Development a.s. - www.prusa3d.com
# SPDX-License-Identifier: GPL-3.0-or-later
from slafw.admin.control import AdminControl
from slafw.admin.items import AdminAction, AdminLabel, AdminBoolValue
from slafw.admin.menus.common.root import Root
from slafw.admin.safe_menu import SafeAdminMenu
from slafw.libPrinter import Printer
from slafw.states.wizard import WizardId
from slafw.wizard.checks.tilt import TiltTimingTest
from slafw.wizard.checks.uvfans import UVFansTest
from slafw.wizard.data_package import fill_wizard_data_package
from slafw.wizard.wizard import SingleCheckWizard
from slafw.wizard.wizards.calibration import CalibrationWizard
from slafw.wizard.wizards.displaytest import DisplayTestWizard
from slafw.wizard.wizards.factory_reset import PackingWizard, FactoryResetWizard
from slafw.wizard.wizards.new_expo_panel import NewExpoPanelWizard
from slafw.wizard.wizards.self_test import SelfTestWizard
from slafw.wizard.wizards.sl1s_upgrade import SL1SUpgradeWizard, SL1DowngradeWizard
from slafw.wizard.wizards.tank_surface_cleaner import TankSurfaceCleaner
from slafw.wizard.wizards.unboxing import CompleteUnboxingWizard, KitUnboxingWizard
from slafw.wizard.wizards.uv_calibration import UVCalibrationWizard


class WizardsTestMenu(Root):
    def __init__(self, control: AdminControl, printer: Printer):
        super().__init__(control, printer)

    def api_display_test(self):
        self._printer.action_manager.start_wizard(DisplayTestWizard(fill_wizard_data_package(self._printer)))

    def api_unpacking_c(self):
        self._printer.action_manager.start_wizard(CompleteUnboxingWizard(fill_wizard_data_package(self._printer)))

    def api_unpacking_k(self):
        self._printer.action_manager.start_wizard(KitUnboxingWizard(fill_wizard_data_package(self._printer)))

    def api_self_test(self):
        self._printer.action_manager.start_wizard(SelfTestWizard(fill_wizard_data_package(self._printer)))

    def api_calibration(self):
        self._printer.action_manager.start_wizard(CalibrationWizard(fill_wizard_data_package(self._printer)))

    def api_packing(self):
        self._printer.action_manager.start_wizard(PackingWizard(fill_wizard_data_package(self._printer)))

    def api_factory_reset(self):
        self._printer.action_manager.start_wizard(FactoryResetWizard(fill_wizard_data_package(self._printer)))

    def sl1s_upgrade(self):
        self._printer.action_manager.start_wizard(SL1SUpgradeWizard(fill_wizard_data_package(self._printer)))

    def sl1_downgrade(self):
        self._printer.action_manager.start_wizard(SL1DowngradeWizard(fill_wizard_data_package(self._printer)))

    def api_selftest_uvfans(self):
        package = fill_wizard_data_package(self._printer)
        self._printer.action_manager.start_wizard(SingleCheckWizard(
            WizardId.SELF_TEST,
            UVFansTest(package),
            package,
            show_results=False))

    def api_calibration_tilt_times(self):
        package = fill_wizard_data_package(self._printer)
        self._printer.action_manager.start_wizard(SingleCheckWizard(
            WizardId.CALIBRATION,
            TiltTimingTest(package),
            package))

    def tank_surface_cleaner(self):
        self._printer.action_manager.start_wizard(TankSurfaceCleaner(fill_wizard_data_package(self._printer)))

    def new_expo_panel(self):
        self._printer.action_manager.start_wizard(NewExpoPanelWizard(fill_wizard_data_package(self._printer)))


class TestUVCalibrationWizardMenu(SafeAdminMenu):
    def __init__(self, control: AdminControl, printer: Printer):
        super().__init__(control)
        self._lcd_replaced = False
        self._led_replaced = False
        self._printer = printer

        self.add_back()
        self.add_item(AdminLabel("UV Calibration wizard setup", "uv_calibration"))
        self.add_item(AdminBoolValue.from_value("LCD replaced", self, "_lcd_replaced", "display_replacement"))
        self.add_item(AdminBoolValue.from_value("LED replaced", self, "_led_replaced", "led_set_replacement"))
        self.add_item(AdminAction("Run calibration", self.run_calibration, "uv_calibration"))

    def run_calibration(self):
        self._control.pop()

        self._printer.action_manager.start_wizard(
            UVCalibrationWizard(
                fill_wizard_data_package(self._printer),
                display_replaced=self._lcd_replaced,
                led_module_replaced=self._led_replaced,
            )
        )
