# This file is part of the SL1 firmware
# Copyright (C) 2014-2018 Futur3d - www.futur3d.net
# Copyright (C) 2018-2019 Prusa Research s.r.o. - www.prusa3d.com
# Copyright (C) 2020 Prusa Research a.s. - www.prusa3d.com
# SPDX-License-Identifier: GPL-3.0-or-later

from sl1fw.errors.errors import TowerEndstopNotReached, TowerHomeCheckFailed
from sl1fw.errors.exceptions import ConfigException
from sl1fw.pages import page
from sl1fw.pages.base import Page
from sl1fw.pages.wait import PageWait


@page
class PageTowerSensitivity(Page):
    Name = "towersensitivity"

    def __init__(self, display):
        super(PageTowerSensitivity, self).__init__(display)
        self.pageUI = "confirm"
        self.pageTitle = N_("Tower sensitivity")

    def show(self):
        self.items.update(
            {
                "text": _(
                    "Tower axis sensitivity needs to be adjusted for realiable homing. This value will be saved in advanced settings."
                ),
                "no_back": True,
            }
        )
        super(PageTowerSensitivity, self).show()

    def contButtonRelease(self):
        pageWait = PageWait(self.display, line1=_("Tower axis sensitivity adjust"))
        pageWait.show()

        try:
            tower_sensitivity = self.display.hw.get_tower_sensitivity()
        except TowerEndstopNotReached:
            self.display.pages["error"].setParams(
                text=_("Tower endstop not reached!\n\n" "Please check if the tower motor is connected properly.")
            )
            return "error"
        except TowerHomeCheckFailed:
            self.display.pages["error"].setParams(
                text=_(
                    "Tower home check failed!\n\n"
                    "Please contact tech support!\n\n"
                    "Tower profiles need to be changed."
                )
            )
            return "error"

        self.display.hwConfig.towerSensitivity = tower_sensitivity
        self.display.hw.setTowerPosition(self.display.hw.tower_end)
        if self.display.wizardData:
            self.display.wizardData.towerSensitivity = self.display.hwConfig.towerSensitivity

        self.display.hwConfig.towerSensitivity = self.display.hwConfig.towerSensitivity

        try:
            self.display.hwConfig.write()
        except ConfigException:
            self.logger.exception("Cannot save wizard configuration")
            self.display.pages["error"].setParams(text=_("Cannot save wizard configuration"))
            return "error"

        return "_OK_"
