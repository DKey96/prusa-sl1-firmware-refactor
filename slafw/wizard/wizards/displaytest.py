# This file is part of the SLA firmware
# Copyright (C) 2020 Prusa Research a.s. - www.prusa3d.com
# SPDX-License-Identifier: GPL-3.0-or-later

import weakref

from slafw.configs.runtime import RuntimeConfig
from slafw.hardware.base import BaseHardware
from slafw.hardware.printer_model import PrinterModel
from slafw.image.exposure_image import ExposureImage
from slafw.states.wizard import WizardId
from slafw.states.wizard import WizardState
from slafw.wizard.actions import UserActionBroker
from slafw.wizard.checks.display import DisplayTest
from slafw.wizard.checks.uvleds import UVLEDsTest
from slafw.wizard.group import CheckGroup
from slafw.wizard.setup import Configuration, TankSetup
from slafw.wizard.wizard import Wizard, WizardDataPackage
from slafw.wizard.wizards.generic import ShowResultsGroup


class DisplayTestCheckGroup(CheckGroup):
    def __init__(self, package: WizardDataPackage):
        super().__init__(
            Configuration(TankSetup.REMOVED, None),
            [UVLEDsTest.get_test(package.hw), DisplayTest(package)],
        )

    async def setup(self, actions: UserActionBroker):
        await self.wait_for_user(actions, actions.prepare_displaytest_done,
                                 WizardState.PREPARE_DISPLAY_TEST)


class DisplayTestWizard(Wizard):
    def __init__(self, hw: BaseHardware, exp_image: ExposureImage,
                 runtime_config: RuntimeConfig, printer_model: PrinterModel):
        self._package = WizardDataPackage(hw=hw, exposure_image=weakref.proxy(
            exp_image), runtime_config=runtime_config,
            model=printer_model)
        super().__init__(
            WizardId.DISPLAY,
            [
                DisplayTestCheckGroup(self._package),
                ShowResultsGroup(),
            ],
            self._package,
        )

    @classmethod
    def get_name(cls) -> str:
        return "display_test"
