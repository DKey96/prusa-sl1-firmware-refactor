# part of SL1 firmware
# 2014-2018 Futur3d - www.futur3d.net
# 2018-2019 Prusa Research s.r.o. - www.prusa3d.com

import os

from sl1fw import defines
from sl1fw.libPages import Page
from sl1fw.pages import page


class PageSetup(Page):

    def __init__(self, display):
        super(PageSetup, self).__init__(display)
        self.pageUI = "setup"
        self.autorepeat = {
                'minus2g1' : (5, 1), 'plus2g1' : (5, 1),
                'minus2g2' : (5, 1), 'plus2g2' : (5, 1),
                'minus2g3' : (5, 1), 'plus2g3' : (5, 1),
                'minus2g4' : (5, 1), 'plus2g4' : (5, 1),
                'minus2g5' : (5, 1), 'plus2g5' : (5, 1),
                'minus2g6' : (5, 1), 'plus2g6' : (5, 1),
                'minus2g7' : (5, 1), 'plus2g7' : (5, 1),
                'minus2g8' : (5, 1), 'plus2g8' : (5, 1),
                }
        self.changed = {}
    #enddef


    def show(self):
        self.items.update({
                'button1' : _("Export"),
                'button2' : _("Import"),
                'button4' : _("Save"),
                })
        super(PageSetup, self).show()
    #enddef


    def button1ButtonRelease(self):
        ''' export '''
        savepath = self.getSavePath()
        if savepath is None:
            self.display.pages['error'].setParams(
                text=_("No USB storage present"))
            return "error"
        #endif

        config_file = os.path.join(savepath, defines.hwConfigFileName)

        if not self.display.hwConfig.writeFile(config_file):
            self.display.pages['error'].setParams(
                text = _("Cannot save configuration"))
            return "error"
        #endif
    #enddef


    def button2ButtonRelease(self):
        ''' import '''
        savepath = self.getSavePath()
        if savepath is None:
            self.display.pages['error'].setParams(
                text=_("No USB storage present"))
            return "error"
        #endif

        config_file = os.path.join(savepath, defines.hwConfigFileName)

        if not os.path.isfile(config_file):
            self.display.pages['error'].setParams(
                text=_("Cannot find configuration to import"))
            return "error"
        #endif

        try:
            with open(config_file, "r") as f:
                self.display.hwConfig.parseText(f.read())
            #endwith
        except Exception:
            self.logger.exception("import exception:")
            self.display.pages['error'].setParams(
                text=_("Cannot import configuration"))
            return "error"
        #endtry

        # TODO: Does import also means also save? There is special button for it.
        if not self.display.hwConfig.writeFile(defines.hwConfigFile):
            self.display.pages['error'].setParams(
                text=_("Cannot save imported configuration"))
            return "error"
        #endif

        self.show()
    #enddef


    def button4ButtonRelease(self):
        ''' save '''
        self.display.hwConfig.update(**self.changed)
        if not self.display.hwConfig.writeFile():
            self.display.pages['error'].setParams(
                text = _("Cannot save configuration"))
            return "error"
        #endif
        return super(PageSetup, self).backButtonRelease()
    #endif
#enddef


@page
class PageSetupHw(PageSetup):
    Name = "setuphw"

    def __init__(self, display):
        super(PageSetupHw, self).__init__(display)
        self.pageTitle = N_("Hardware Setup")
    #enddef


    def show(self):
        self.items.update({
                'label1g1' : _("Fan check"),
                'label1g2' : _("Cover check"),
                'label1g3' : _("MC version check"),
                'label1g4' : _("Use resin sensor"),
                'label1g5' : _("Auto power off"),
                'label1g6' : _("Mute (no beeps)"),

                'label2g1' : _("Screw (mm/rot)"),
                'label2g2' : _("Tilt msteps"),
                'label2g3' : _("Measuring moves count"),
                'label2g4' : _("Stirring moves count"),
                'label2g5' : _("Delay after stirring [s]"),
                'label2g6' : _("Power LED intensity"),

                'label2g8' : _("MC board version"),
                })
        self.changed = {}
        self.temp = {}
        self.temp['screwmm'] = self.display.hwConfig.screwMm
        self.temp['tiltheight'] = self.display.hwConfig.tiltHeight
        self.temp['calibtoweroffset'] = self.display.hwConfig.calibTowerOffset
        self.temp['measuringmoves'] = self.display.hwConfig.measuringMoves
        self.temp['stirringmoves'] = self.display.hwConfig.stirringMoves
        self.temp['stirringdelay'] = self.display.hwConfig.stirringDelay
        self.temp['pwrledpwm'] = self.display.hwConfig.pwrLedPwm
        self.temp['mcboardversion'] = self.display.hwConfig.MCBoardVersion

        self.items['value2g1'] = str(self.temp['screwmm'])
        self.items['value2g2'] = str(self.temp['tiltheight'])
        self.items['value2g3'] = str(self.temp['measuringmoves'])
        self.items['value2g4'] = str(self.temp['stirringmoves'])
        self.items['value2g5'] = self._strTenth(self.temp['stirringdelay'])
        self.items['value2g6'] = str(self.temp['pwrledpwm'])
        self.items['value2g8'] = str(self.temp['mcboardversion'])

        self.temp['fancheck'] = self.display.hwConfig.fanCheck
        self.temp['covercheck'] = self.display.hwConfig.coverCheck
        self.temp['mcversioncheck'] = self.display.hwConfig.MCversionCheck
        self.temp['resinsensor'] = self.display.hwConfig.resinSensor
        self.temp['autooff'] = self.display.hwConfig.autoOff
        self.temp['mute'] = self.display.hwConfig.mute

        self.items['state1g1'] = int(self.temp['fancheck'])
        self.items['state1g2'] = int(self.temp['covercheck'])
        self.items['state1g3'] = int(self.temp['mcversioncheck'])
        self.items['state1g4'] = int(self.temp['resinsensor'])
        self.items['state1g5'] = int(self.temp['autooff'])
        self.items['state1g6'] = int(self.temp['mute'])

        super(PageSetupHw, self).show()
    #enddef


    def state1g1ButtonRelease(self):
        self._onOff(self.temp, self.changed, 0, 'fancheck')
    #enddef


    def state1g2ButtonRelease(self):
        self._onOff(self.temp, self.changed, 1, 'covercheck')
    #enddef


    def state1g3ButtonRelease(self):
        self._onOff(self.temp, self.changed, 2, 'mcversioncheck')
    #enddef


    def state1g4ButtonRelease(self):
        self._onOff(self.temp, self.changed, 3, 'resinsensor')
    #enddef


    def state1g5ButtonRelease(self):
        self._onOff(self.temp, self.changed, 4, 'autooff')
    #enddef


    def state1g6ButtonRelease(self):
        self._onOff(self.temp, self.changed, 5, 'mute')
    #enddef


    def minus2g1Button(self):
        self._value(self.temp, self.changed, 0, 'screwmm', 2, 8, -1)
    #enddef


    def plus2g1Button(self):
        self._value(self.temp, self.changed, 0, 'screwmm', 2, 8, 1)
    #enddef


    def minus2g2Button(self):
        self._value(self.temp, self.changed, 1, 'tiltheight', 1, 6000, -1)
    #enddef


    def plus2g2Button(self):
        self._value(self.temp, self.changed, 1, 'tiltheight', 1, 6000, 1)
    #enddef


    def minus2g3Button(self):
        self._value(self.temp, self.changed, 2, 'measuringmoves', 1, 10, -1)
    #enddef


    def plus2g3Button(self):
        self._value(self.temp, self.changed, 2, 'measuringmoves', 1, 10, 1)
    #enddef


    def minus2g4Button(self):
        self._value(self.temp, self.changed, 3, 'stirringmoves', 1, 10, -1)
    #enddef


    def plus2g4Button(self):
        self._value(self.temp, self.changed, 3, 'stirringmoves', 1, 10, 1)
    #enddef


    def minus2g5Button(self):
        self._value(self.temp, self.changed, 4, 'stirringdelay', 0, 300, -5, self._strTenth)
    #enddef


    def plus2g5Button(self):
        self._value(self.temp, self.changed, 4, 'stirringdelay', 0, 300, 5, self._strTenth)
    #enddef


    def minus2g6Button(self):
        self._value(self.temp, self.changed, 5, 'pwrledpwm', 0, 100, -5)
        self.display.hw.powerLedPwm = self.temp['pwrledpwm']
    #enddef


    def plus2g6Button(self):
        self._value(self.temp, self.changed, 5, 'pwrledpwm', 0, 100, 5)
        self.display.hw.powerLedPwm = self.temp['pwrledpwm']
    #enddef


    def minus2g8Button(self):
        self._value(self.temp, self.changed, 7, 'mcboardversion', 5, 6, -1)
    #enddef


    def plus2g8Button(self):
        self._value(self.temp, self.changed, 7, 'mcboardversion', 5, 6, 1)
    #enddef


    def backButtonRelease(self):
        self.display.hw.powerLedPwm = self.display.hwConfig.pwrLedPwm
        return super(PageSetupHw, self).backButtonRelease()
    #enddef

#endclass


@page
class PageSetupExposure(PageSetup):
    Name = "setupexpo"

    def __init__(self, display):
        super(PageSetupExposure, self).__init__(display)
        self.pageTitle = N_("Exposure Setup")
    #enddef


    def show(self):
        self.items.update({
                'label1g1' : _("Blink exposure"),
                'label1g2' : _("Per-Partes expos."),
                'label1g3' : _("Use tilt"),
                'label1g4' : _("Up&down UV on"),

                'label2g1' : _("Layer trigger [s]"),
                'label2g2' : _("Layer tower hop [mm]"),
                'label2g3' : _("Delay before expos. [s]"),
                'label2g4' : _("Delay after expos. [s]"),
                'label2g5' : _("Up&down wait [s]"),
                'label2g6' : _("Up&down every n-th l."),
                'label2g7' : _("Up&down Z offset [mm]"),
                'label2g8' : _("Up&down expo comp [s]"),
                })
        self.changed = {}
        self.temp = {}
        self.temp['trigger'] = self.display.hwConfig.trigger
        self.temp['limit4fast'] = self.display.hwConfig.limit4fast
        self.temp['layertowerhop'] = self.display.hwConfig.layerTowerHop
        self.temp['delaybeforeexposure'] = self.display.hwConfig.delayBeforeExposure
        self.temp['delayafterexposure'] = self.display.hwConfig.delayAfterExposure
        self.temp['upanddownwait'] = self.display.hwConfig.upAndDownWait
        self.temp['upanddowneverylayer'] = self.display.hwConfig.upAndDownEveryLayer
        self.temp['upanddownzoffset'] = self.display.hwConfig.upAndDownZoffset
        self.temp['upanddownexpocomp'] = self.display.hwConfig.upAndDownExpoComp

        self.items['value2g1'] = self._strTenth(self.temp['trigger'])
        self.items['value2g2'] = self._strZMove(self.temp['layertowerhop'])
        self.items['value2g3'] = self._strTenth(self.temp['delaybeforeexposure'])
        self.items['value2g4'] = self._strTenth(self.temp['delayafterexposure'])
        self.items['value2g5'] = str(self.temp['upanddownwait'])
        self.items['value2g6'] = str(self.temp['upanddowneverylayer'])
        self.items['value2g7'] = self._strZMove(self.temp['upanddownzoffset'])
        self.items['value2g8'] = self._strTenth(self.temp['upanddownexpocomp'])

        self.temp['blinkexposure'] = self.display.hwConfig.blinkExposure
        self.temp['perpartesexposure'] = self.display.hwConfig.perPartes
        self.temp['tilt'] = self.display.hwConfig.tilt
        self.temp['upanddownuvon'] = self.display.hwConfig.upAndDownUvOn

        self.items['state1g1'] = int(self.temp['blinkexposure'])
        self.items['state1g2'] = int(self.temp['perpartesexposure'])
        self.items['state1g3'] = int(self.temp['tilt'])
        self.items['state1g4'] = int(self.temp['upanddownuvon'])

        super(PageSetupExposure, self).show()
    #enddef


    def _strZMove(self, value):
        return "%.3f" % self.display.hwConfig.calcMM(value)
    #enddef


    def state1g1ButtonRelease(self):
        self._onOff(self.temp, self.changed, 0, 'blinkexposure')
    #enddef


    def state1g2ButtonRelease(self):
        self._onOff(self.temp, self.changed, 1, 'perpartesexposure')
    #enddef


    def state1g3ButtonRelease(self):
        self._onOff(self.temp, self.changed, 2, 'tilt')
        if not self.temp['tilt'] and not self.temp['layertowerhop']:
            self.temp['layertowerhop'] = self.display.hwConfig.calcMicroSteps(5)
            self.changed['layertowerhop'] = str(self.temp['layertowerhop'])
            self.showItems(**{ 'value2g2' : self._strZMove(self.temp['layertowerhop']) })
        #endif
    #enddef


    def state1g4ButtonRelease(self):
        self._onOff(self.temp, self.changed, 3, 'upanddownuvon')
    #enddef


    def minus2g1Button(self):
        self._value(self.temp, self.changed, 0, 'trigger', 0, 20, -1, self._strTenth)
    #enddef


    def plus2g1Button(self):
        self._value(self.temp, self.changed, 0, 'trigger', 0, 20, 1, self._strTenth)
    #enddef


    def minus2g2Button(self):
        self._value(self.temp, self.changed, 1, 'layertowerhop', 0, 8000, -20, self._strZMove)
        if not self.temp['tilt'] and not self.temp['layertowerhop']:
            self.temp['tilt'] = True
            self.changed['tilt'] = "on"
            self.showItems(**{ 'state1g3' : 1 })
        #endif
    #enddef


    def plus2g2Button(self):
        self._value(self.temp, self.changed, 1, 'layertowerhop', 0, 8000, 20, self._strZMove)
    #enddef


    def minus2g3Button(self):
        self._value(self.temp, self.changed, 2, 'delaybeforeexposure', 0, 300, -1, self._strTenth)
    #enddef


    def plus2g3Button(self):
        self._value(self.temp, self.changed, 2, 'delaybeforeexposure', 0, 300, 1, self._strTenth)
    #enddef


    def minus2g4Button(self):
        self._value(self.temp, self.changed, 3, 'delayafterexposure', 0, 300, -1, self._strTenth)
    #enddef


    def plus2g4Button(self):
        self._value(self.temp, self.changed, 3, 'delayafterexposure', 0, 300, 1, self._strTenth)
    #enddef


    def minus2g5Button(self):
        self._value(self.temp, self.changed, 4, 'upanddownwait', 0, 600, -1)
    #enddef


    def plus2g5Button(self):
        self._value(self.temp, self.changed, 4, 'upanddownwait', 0, 600, 1)
    #enddef


    def minus2g6Button(self):
        self._value(self.temp, self.changed, 5, 'upanddowneverylayer', 0, 500, -1)
    #enddef


    def plus2g6Button(self):
        self._value(self.temp, self.changed, 5, 'upanddowneverylayer', 0, 500, 1)
    #enddef


    def minus2g7Button(self):
        self._value(self.temp, self.changed, 6, 'upanddownzoffset', -800, 800, -1, self._strZMove)
    #enddef


    def plus2g7Button(self):
        self._value(self.temp, self.changed, 6, 'upanddownzoffset', -800, 800, 1, self._strZMove)
    #enddef


    def minus2g8Button(self):
        self._value(self.temp, self.changed, 7, 'upanddownexpocomp', -10, 300, -1, self._strTenth)
    #enddef


    def plus2g8Button(self):
        self._value(self.temp, self.changed, 7, 'upanddownexpocomp', -10, 300, 1, self._strTenth)
    #enddef

#endclass
