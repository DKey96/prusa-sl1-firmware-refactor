# This file is part of the SL1 firmware
# Copyright (C) 2020 Prusa Research a.s. - www.prusa3d.com
# SPDX-License-Identifier: GPL-3.0-or-later

import re

from sl1fw.errors.warnings import WrongA64SerialFormat, WrongMCSerialFormat
from sl1fw.libHardware import Hardware
from sl1fw.wizard.actions import UserActionBroker
from sl1fw.wizard.checks.base import Check, WizardCheckType
from sl1fw.wizard.setup import Configuration


class SerialNumberTest(Check):
    def __init__(self, hw: Hardware):
        super().__init__(
            WizardCheckType.SERIAL_NUMBER, Configuration(None, None), [],
        )
        self.hw = hw

    async def async_task_run(self, actions: UserActionBroker):
        self._logger.debug("Checking serial number")

        # check serial numbers
        if not re.match(r"CZPX\d{4}X009X[CK]\d{5}", self.hw.cpuSerialNo):
            self.add_warning(WrongA64SerialFormat(self.hw.cpuSerialNo))

        self.progress = 0.5

        if not re.match(r"CZPX\d{4}X012X[CK01]\d{5}", self.hw.mcSerialNo):
            self.add_warning(WrongMCSerialFormat(self.hw.mcSerialNo))

        self._logger.debug("Checking serial number done")
