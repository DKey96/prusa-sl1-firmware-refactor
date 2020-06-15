#!/usr/bin/env python3

# This file is part of the SL1 firmware
# Copyright (C) 2014-2018 Futur3d - www.futur3d.net
# Copyright (C) 2018-2019 Prusa Research s.r.o. - www.prusa3d.com
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest
import numpy
from PIL import Image

from sl1fw.tests.base import Sl1fwTestCase
from sl1fw.libScreen import Screen
from sl1fw import defines, test_runtime


class TestScreen(Sl1fwTestCase):
    NUMBERS = Sl1fwTestCase.SAMPLES_DIR / "numbers.sl1"
    CALIBRATION = Sl1fwTestCase.SAMPLES_DIR / "Resin_calibration_object.sl1"
    CALIBRATION10 = Sl1fwTestCase.SAMPLES_DIR / "Resin_calibration_linear_object.sl1"
    ZABA = Sl1fwTestCase.SAMPLES_DIR / "zaba.png"
    FB_DEV = Sl1fwTestCase.TEMP_DIR / "test.fbdev"
    PREVIEW_FILE = Sl1fwTestCase.TEMP_DIR / "live.png"
    DISPLAY_USAGE = Sl1fwTestCase.TEMP_DIR / "display_usage.npz"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def setUp(self):
        super().setUp()
        defines.fbFile = str(self.FB_DEV)
        defines.factoryConfigFile = str(self.SL1FW_DIR / ".." / "factory" / "factory.toml")
        defines.livePreviewImage = str(self.PREVIEW_FILE)
        defines.displayUsageData = str(self.DISPLAY_USAGE)
        test_runtime.testing = True
        defines.hwConfigFile = str(self.SAMPLES_DIR / "hardware.cfg")

        self.screen = Screen()
        self.screen.start()
        self.params = {
            'project': self.NUMBERS,
            'expTime': 7.5,
            'expTimeFirst': 35,
            'calibrateTime': 1.0,
        }

    def tearDown(self):
        self.screen.ping()
        self.screen.exit()
        files = [
            self.FB_DEV,
            self.PREVIEW_FILE,
            self.DISPLAY_USAGE,
        ]
        for file in files:
            if file.exists():
                file.unlink()

    def test_init(self):
        self.assertSameImage(self._fb, Image.open(self.SAMPLES_DIR / "fbdev" / "all_black.png"),
                             msg="Init - display is not cleared at start")

    def test_getImg(self):
        self.screen.getImg(filename = TestScreen.ZABA)
        self.screen.ping()
        self.assertSameImage(self._fb, Image.open(self.ZABA),
                             msg="getImg - wrong display content")

    def test_mask(self):
        self.screen.startProject(params = self.params)
        retcode, per_partes = self.screen.projectStatus()
        self.assertTrue(retcode, "Mask - retcode")
        self.assertFalse(per_partes, "Mask - perpartes")
        self.assertEqual(233600.0, self.screen.blitImg(), "Mask - wrong number of white pixels")
        self.assertSameImage(self._fb, Image.open(self.SAMPLES_DIR / "fbdev" / "mask.png"),
                             msg="Mask - wrong display content")

    def test_display_usage(self):
        self.screen.startProject(params = self.params)
        retcode, per_partes = self.screen.projectStatus()
        self.assertTrue(retcode, "Display usage - retcode")
        self.assertFalse(per_partes, "Display usage - perpartes")
        self.screen.saveDisplayUsage()
        self.screen.ping()
        with numpy.load(TestScreen.DISPLAY_USAGE) as npzfile:
            savedData = npzfile['display_usage']
        with numpy.load(self.SAMPLES_DIR / "display_usage.npz") as npzfile:
            exampleData = npzfile['display_usage']
        self.assertTrue(numpy.array_equal(savedData, exampleData), "Display usage - wrong display usage data")

    def test_perpartes(self):
        self.params['perPartes'] = True
        self.screen.startProject(params = self.params)
        retcode, perPartes = self.screen.projectStatus()
        self.assertTrue(retcode, "Perpartes - retcode")
        self.assertTrue(perPartes, "Perpartes - perPartes")
        self.screen.screenshot(second = False)
        self.screen.screenshotRename()
        self.assertEqual(233600.0, self.screen.blitImg(second = False), "Perpartes - wrong number of white pixels 1")
        self.assertSameImage(self._fb, Image.open(self.SAMPLES_DIR / "fbdev" / "part1.png"),
                             msg="Perpartes - wrong display content 1")
        self.assertSameImage(Image.open(defines.livePreviewImage), Image.open(self.SAMPLES_DIR / "live1.png"),
                             msg="Perpartes - wrong preview image 1")
        self.screen.screenshot(second = True)
        self.screen.screenshotRename()
        self.assertEqual(233600.0, self.screen.blitImg(second = True), "Perpartes - wrong number of white pixels 2")
        self.assertSameImage(self._fb, Image.open(self.SAMPLES_DIR / "fbdev" / "part2.png"),
                             msg="Perpartes - wrong display content 2")
        self.assertSameImage(Image.open(defines.livePreviewImage), Image.open(self.SAMPLES_DIR / "live2.png"),
                             msg="Perpartes - wrong preview image 2")

    @property
    def _fb(self) -> Image:
        with self.FB_DEV.open("rb") as f:
            return Image.frombytes("RGBX", (defines.screenWidth, defines.screenHeight), f.read())

    def test_calibration_calib_pad(self):
        self.params['project'] = TestScreen.CALIBRATION
        self.params['expTime'] = 4.0
        self.screen.startProject(params = self.params)
        retcode, perPartes = self.screen.projectStatus()
        self.assertTrue(retcode, "calibPad - retcode")
        self.assertFalse(perPartes, "calibPad - perPartes")
        self.assertEqual(1294398, self.screen.blitImg(second = False), "calibPad - wrong number of white pixels")
        self.assertSameImage(self._fb, Image.open(self.SAMPLES_DIR / "fbdev" / "calibPad.png"),
                             msg="calibPad - wrong display content")

    def test_calibration_calib(self):
        self.params['project'] = TestScreen.CALIBRATION
        self.params['expTime'] = 4.0
        self.params['overlayName'] = "calib"
        self.screen.startProject(params = self.params)
        retcode, perPartes = self.screen.projectStatus()
        self.assertTrue(retcode, "calib - retcode")
        self.assertFalse(perPartes, "calib - perPartes")
        white = self.screen.blitImg(second=False)
        self.assertLess(abs(1154913 - white), 50, "calib - wrong number of white pixels")
        self.assertSameImage(self._fb, Image.open(self.SAMPLES_DIR / "fbdev" / "calib.png"), threshold=40,
                             msg = "calib - wrong display content")

    def test_calibration_calib_pad_10(self):
        self.params['project'] = TestScreen.CALIBRATION10
        self.params['expTime'] = 4.0
        self.screen.startProject(params = self.params)
        retcode, perPartes = self.screen.projectStatus()
        self.assertTrue(retcode, "calibPad10 - retcode")
        self.assertFalse(perPartes, "calibPad10 - perPartes")
        white = self.screen.blitImg(second = False)
        self.assertLess(abs(3585976 - white), 50, "calibPad10 - wrong number of white pixels")
        self.assertSameImage(self._fb, Image.open(self.SAMPLES_DIR / "fbdev" / "calibPad10.png"),
                             msg="calibPad10 - wrong display content")

    def test_calibration_calib_10(self):
        self.params['project'] = TestScreen.CALIBRATION10
        self.params['expTime'] = 4.0
        self.params['overlayName'] = "calib"
        self.screen.startProject(params = self.params)
        retcode, perPartes = self.screen.projectStatus()
        self.assertTrue(retcode, "calib10 - retcode")
        self.assertFalse(perPartes, "calib10 - perPartes")
        white = self.screen.blitImg(second = False)
        self.assertLess(abs(3414636 - white), 50, "calib10 - wrong number of white pixels")
        self.assertSameImage(self._fb, Image.open(self.SAMPLES_DIR / "fbdev" / "calib10.png"), threshold=40,
                             msg="calibPad10 - wrong display content")

if __name__ == '__main__':
    unittest.main()
