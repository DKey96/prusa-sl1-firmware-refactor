from sl1fw.libPages import page, Page
from sl1fw import libConfig


def item_updater(str_func = None):
    def new_decorator(func):
        def new_func(self, value):
            func(self, value)

            key = func.__name__
            if str_func:
                value = str_func(getattr(self, func.__name__))
            else:
                value = getattr(self, func.__name__)
            #endif

            self.showItems(**{key: value})
        #enddef
        return new_func
    #enddef
    return new_decorator
#enddef


def value_saturate(min, max):
    def new_decorator(func):
        def new_func(self, value):
            if not min <= value <= max:
                self.display.hw.beepAlarm(1)
                return
            else:
                func(self, value)
            #enddif
        #enddef
        return new_func
    #enddef
    return new_decorator
#enddef


def confirm_leave(func):
    def new_func(self):
        retc = self.confirmChanges()
        if retc:
            return retc
        else:
            return func(self)
        #endif
    #enddef
    return new_func
#enddef


@page
class PageAdvancedSettings(Page):
    Name = "advancedsettings"

    def __init__(self, display):
        super(PageAdvancedSettings, self).__init__(display)
        self.pageUI = "advancedsettings"
        self.pageTitle = N_("Advanced Settings")
        self._display_test = False
        self.configwrapper = None
        self._calibTowerOffset_mm = None
        self.confirmReturnPending = False

        self.autorepeat = {
            'minus_tiltsensitivity': (5, 1), 'plus_tiltsensitivity': (5, 1),
            'minus_towersensitivity': (5, 1), 'plus_towersensitivity': (5, 1),
            'minus_fasttiltlimit': (5, 1), 'plus_fasttiltlimit': (5, 1),
            'minus_toweroffset': (5, 1), 'plus_toweroffset': (5, 1),
            'minus_rearfanspeed': (5, 1), 'plus_rearfanspeed': (5, 1),
        }
    #enddef


    @property
    def tilt_sensitivity(self):
        return self.configwrapper.tiltSensitivity
    #enddef

    @tilt_sensitivity.setter
    @value_saturate(-2, 2)
    @item_updater()
    def tilt_sensitivity(self, value):
        self.configwrapper.tiltSensitivity = value
    #enddef


    @property
    def tower_sensitivity(self):
        return self.configwrapper.towerSensitivity
    #enddef

    @tower_sensitivity.setter
    @value_saturate(-2, 2)
    @item_updater()
    def tower_sensitivity(self, value):
        self.configwrapper.towerSensitivity = value
    #enddef


    @property
    def fast_tilt_limit(self):
        return self.configwrapper.limit4fast
    #enddef

    @fast_tilt_limit.setter
    @value_saturate(0, 100)
    @item_updater()
    def fast_tilt_limit(self, value):
        self.configwrapper.limit4fast = value
    #enddef


    @property
    def tower_offset(self):
        if self._calibTowerOffset_mm is None:
            self._calibTowerOffset_mm = self.display.hwConfig.calcMM(self.configwrapper.calibTowerOffset)
        #endif
        return self._calibTowerOffset_mm
    #enddef

    @tower_offset.setter
    @value_saturate(-0.5, 0.5)
    @item_updater(str_func=lambda x: "%+.3f" % x)
    def tower_offset(self, value):
        self._calibTowerOffset_mm = value
        self.configwrapper.calibTowerOffset = self.display.hwConfig.calcMicroSteps(value)
    #enddef


    @property
    def rear_fan_speed(self):
        return self.configwrapper.fan3Pwm
    #enddef

    @rear_fan_speed.setter
    @value_saturate(0, 100)
    @item_updater()
    def rear_fan_speed(self, value):
        self.configwrapper.fan3Pwm = value
        # TODO: This is wrong, it would be nice to have API to set just one fan
        self.display.hw.setFansPwm((self.configwrapper.fan1Pwm,
                                   self.configwrapper.fan2Pwm,
                                   self.configwrapper.fan3Pwm))
        self.display.hw.setFans((False, False, True))
    #enddef


    @property
    def auto_power_off(self):
        return self.configwrapper.autoOff
    #enddef

    @auto_power_off.setter
    @item_updater()
    def auto_power_off(self, value):
        self.configwrapper.autoOff = value
    #enddef


    @property
    def cover_check(self):
        return self.configwrapper.coverCheck
    #enddef

    @cover_check.setter
    @item_updater()
    def cover_check(self, value):
        self.configwrapper.coverCheck = value
    #enddef


    @property
    def resin_sensor(self):
        return self.configwrapper.resinSensor
    #enddef

    @resin_sensor.setter
    @item_updater()
    def resin_sensor(self, value):
        self.configwrapper.resinSensor = value
    #enddef


    def show(self):
        if self.configwrapper is None or not self.confirmReturnPending:
            self.configwrapper = libConfig.ConfigHelper(self.display.hwConfig)
        else:
            self.confirmReturnPending = False
        #endif
        self._calibTowerOffset_mm = None

        self.items.update({
            'showAdmin': self.display.show_admin, # TODO: Remove once client uses show_admin
            'show_admin': self.display.show_admin,
            'tilt_sensitivity': self.tilt_sensitivity,
            'tower_sensitivity': self.tower_sensitivity,
            'fast_tilt_limit': self.fast_tilt_limit,
            'tower_offset': "%+.3f" % self.tower_offset,
            'rear_fan_speed': self.rear_fan_speed,
            'auto_power_off': self.auto_power_off,
            'cover_check': self.cover_check,
            'resin_sensor': self.resin_sensor,
        })
        super(PageAdvancedSettings, self).show()
    #enddef


    # Move platform
    @confirm_leave
    def towermoveButtonRelease(self):
        return "towermove"
    #enddef


    # Move resin tank
    @confirm_leave
    def tiltmoveButtonRelease(self):
        return "tiltmove"
    #enddef


    # Time settings
    @confirm_leave
    def timesettingsButtonRelease(self):
        return "timesettings"
    #enddef


    # Change language (TODO: Not in the graphical design, not yet implemented properly)
    @confirm_leave
    def setlanguageButtonRelease(self):
        return "setlanguage"
    #enddef


    # Hostname
    @confirm_leave
    def sethostnameButtonRelease(self):
        return "sethostname"
    #enddef


    # Change name/password
    @confirm_leave
    def setremoteaccessButtonRelease(self):
        return "setlogincredentials"
    #enddef


    # Tilt sensitivity
    def minus_tiltsensitivityButton(self):
        self.tilt_sensitivity -= 1
    #enddef
    def plus_tiltsensitivityButton(self):
        self.tilt_sensitivity += 1
    #enddef


    # Tower sensitivity
    def minus_towersensitivityButton(self):
        self.tower_sensitivity -= 1
    # enddef
    def plus_towersensitivityButton(self):
        self.tower_sensitivity += 1
    # enddef


    # Limit for fast tilt
    def minus_fasttiltlimitButton(self):
        self.fast_tilt_limit -= 1
    #enddef
    def plus_fasttiltlimitButton(self):
        self.fast_tilt_limit += 1
    #enddef


    # Tower offset
    # TODO: Adjust in mm, compute steps
    # Currently we are adjusting steps, but showing mm. This in counterintuitive.
    def minus_toweroffsetButton(self):
        self.tower_offset -= 0.001
    #enddef
    def plus_toweroffsetButton(self):
        self.tower_offset += 0.001
    #enddef


    # Display test
    @confirm_leave
    def displaytestButtonRelease(self):
        return "displaytest"
    #enddef

    # Rear fan speed
    def minus_rearfanspeedButton(self):
        self.rear_fan_speed -= 1
    #enddef
    def plus_rearfanspeedButton(self):
        self.rear_fan_speed += 1
    #enddef


    # Auto power off
    def autopoweroffButtonRelease(self):
        self.auto_power_off = not self.auto_power_off
    #enddef


    # Cover check
    def covercheckButtonRelease(self):
        if self.cover_check:
            self.display.pages['yesno'].setParams(
                yesFce = self.disableCoverCheck,
                noFce = self._doConfirmReturn,
                text = _("Disable the cover sensor?\n"
                       "\n"
                       "CAUTION: This may lead to unwanted exposure to UV light. This action is not recommended!"))
            return "yesno"
        else:
            self.cover_check = True
        #endif
    #enddef


    def disableCoverCheck(self):
        self.cover_check = False
        return self._doConfirmReturn()
    #enddef


    def _doConfirmReturn(self):
        self.confirmReturnPending = True
        return "_BACK_"
    #enddef


    # Resin Sensor
    def resinsensorButtonRelease(self):
        if self.resin_sensor:
            self.display.pages['yesno'].setParams(
                yesFce = self.disableResinSensor,
                noFce = self._doConfirmReturn,
                text = _("Disable the resin sensor?\n"
                       "\n"
                       "CAUTION: This may lead to failed prints or resin tank overflow! This action is not recommended!"))
            return "yesno"
        else:
            self.resin_sensor = True
        #endif
    #enddef


    def disableResinSensor(self):
        self.resin_sensor = False
        return self._doConfirmReturn()
    #enddef


    # Firmware update
    @confirm_leave
    def firmwareupdateButtonRelease(self):
        return "firmwareupdate"
    #enddef


    # Factory reset
    @confirm_leave
    def factoryresetButtonRelease(self):
        return "factoryreset"
    #enddef


    # Admin
    @confirm_leave
    def adminButtonRelease(self):
        if self.display.show_admin:
            return "admin"
        #endif
    #enddef


    # Logs export to usb
    def exportlogstoflashdiskButtonRelease(self):
        return self.saveLogsToUSB()
    #enddef


    # Show wizard
    @confirm_leave
    def wizardButtonRelease(self):
        return "wizard1"
    #enddef


    @confirm_leave
    def backButtonRelease(self):
        return super(PageAdvancedSettings, self).backButtonRelease()
    #enddef


    def confirmChanges(self):
        self.display.hw.stopFans()
        if self.configwrapper.changed():
            self.display.pages['yesno'].setParams(
                    pageTitle = N_("Save changes?"),
                    text = _("Save changes?"))
            if self.display.doMenu("yesno"):
                # save changes
                sensitivity_changed = self.configwrapper.changed('towersensitivity') or self.configwrapper.changed('tiltsensitivity')
                if not self.configwrapper.commit():
                    self.display.pages['error'].setParams(
                        text = _("Cannot save configuration"))
                    return "error"
                #endif
                if sensitivity_changed:
                    self.logger.info("Motor sensitivity changed. Updating profiles.")
                    self._updatesensitivity()
                #endif
            else:
                # discard changes
                # TODO: This is wrong, it would be nice to have API to set just one fan
                self.display.hw.setFansPwm((self.display.hwConfig.fan1Pwm,
                                            self.display.hwConfig.fan2Pwm,
                                            self.display.hwConfig.fan3Pwm))
            #endif
        #endif
    #enddef


    def _updatesensitivity(self):
        # adjust tilt profiles
        profiles = self.display.hw.getTiltProfiles()
        self.logger.debug("profiles %s", profiles)
        profiles[0][4] = self.display.hw._tiltAdjust['homingFast'][self.display.hwConfig.tiltSensitivity + 2][0]
        profiles[0][5] = self.display.hw._tiltAdjust['homingFast'][self.display.hwConfig.tiltSensitivity + 2][1]
        profiles[1][4] = self.display.hw._tiltAdjust['homingSlow'][self.display.hwConfig.tiltSensitivity + 2][0]
        profiles[1][5] = self.display.hw._tiltAdjust['homingSlow'][self.display.hwConfig.tiltSensitivity + 2][1]
        self.display.hw.setTiltProfiles(profiles)
        self.logger.debug("profiles %s", profiles)

        # adjust tower profiles
        profiles = self.display.hw.getTowerProfiles()
        self.logger.debug("profiles %s", profiles)
        profiles[0][4] = self.display.hw._towerAdjust['homingFast'][self.display.hwConfig.towerSensitivity + 2][0]
        profiles[0][5] = self.display.hw._towerAdjust['homingFast'][self.display.hwConfig.towerSensitivity + 2][1]
        profiles[1][4] = self.display.hw._towerAdjust['homingSlow'][self.display.hwConfig.towerSensitivity + 2][0]
        profiles[1][5] = self.display.hw._towerAdjust['homingSlow'][self.display.hwConfig.towerSensitivity + 2][1]
        self.display.hw.setTowerProfiles(profiles)
        self.logger.debug("profiles %s", profiles)
    #enddef

#endclass
