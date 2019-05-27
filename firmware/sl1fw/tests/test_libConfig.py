import unittest
import gettext
import os
import logging

try:
    gettext.install('sl1fw', unicode=1)
except:
    gettext.install('sl1fw')

from sl1fw.libConfig import *
from sl1fw import defines

logging.basicConfig(format = "%(asctime)s - %(levelname)s - %(name)s - %(message)s", level = logging.DEBUG)


class TestHardwareConfig(unittest.TestCase):
    def setUp(self):
        defines.hwConfigFile = os.path.join(os.path.dirname(__file__), "samples/hardware.cfg")
        from shutil import copyfile
        copyfile(defines.hwConfigFile, "hwconfig.test")
        self.hwConfig = HwConfig(defines.hwConfigFile)

    def tearDown(self):
        os.remove("hwconfig.test")

    def test_read(self):
        self.hwConfig.logAllItems()
        self.hwConfig.logFile()

        self.assertTrue(self.hwConfig.coverCheck, "Test cover check read")
        self.assertFalse(self.hwConfig.calibrated, "Test calibrated read")
        self.assertEqual(self.hwConfig.layerTowerHop, 0, "Test layerTowerHop read")

    def test_write(self):
        towerHeight = "1024"
        self.hwConfig.update(towerheight = towerHeight)

        self.assertEqual(self.hwConfig.towerHeight, 1024, "Check towerHeight is set")

        self.hwConfig.logAllItems()
        self.hwConfig.logFile()
        logging.info(self.hwConfig.getSourceString())
        self.assertTrue(self.hwConfig.writeFile("hwconfig.test"), "Write config file")


class TestPrintConfig(unittest.TestCase):
    def setUp(self):
        defines.hwConfigFile = os.path.join(os.path.dirname(__file__), "samples/hardware.cfg")
        self.hwConfig = HwConfig(defines.hwConfigFile)

    def test_read(self):
        config = PrintConfig(self.hwConfig)
        config.logAllItems()
        config.logFile()

        self.assertEqual(config.projectName, "no project", "Check empty project name")

        config.parseFile(os.path.join(os.path.dirname(__file__), "samples/empty-sample.sl1"))

        self.assertIs(config.zipError, None, "Test for no read errors")

        config.logAllItems()
        config.logFile()

        self.assertEqual(config.projectName, "empty-sample", "Check projectName")
        self.assertEqual(config.totalLayers, 20, "Check total layers count")

        logging.info(config.getSourceString())
        config.update(expTime = "5")

        self.assertEqual(config.expTime, 5, "Check expTime value")

        #config.writeFile("printconfig.txt")


class TestWizardData(unittest.TestCase):
    def setUp(self):
        defines.hwConfigFile = os.path.join(os.path.dirname(__file__), "samples/wizardData.cfg")
        from shutil import copyfile
        copyfile(defines.hwConfigFile, "wizardData.test")
        self.wizardData = WizardData(defines.hwConfigFile)

    def tearDown(self):
        os.remove("wizardData.test")

    def test_lists(self):
        sensorData = [98, 105, 108, 128, 136, 111, 145]
        percDiff = [-23.4, -17.9, -15.6, 0.0, 6.3, -13.3, 13.3, -6.2, -10.9, -18.7]
        self.wizardData.update(uvsensordata = sensorData, uvpercdiff = percDiff)

        self.assertEqual(self.wizardData.uvSensorData, sensorData, "Check uvSensorData is set")
        self.assertEqual(self.wizardData.uvPercDiff, percDiff, "Check uvSensorData is set")

        self.wizardData.writeFile("wizardData.test")

        self.wizardData.logAllItems()
        self.wizardData.logFile()

        self.assertEqual(self.wizardData.uvSensorData, sensorData, "Test sensor data read")
        self.assertEqual(self.wizardData.uvPercDiff, percDiff, "Test perc diff read")


class TestConfigHelper(unittest.TestCase):
    CONFIG_PATH = "config.cfg"

    def setUp(self):
        self.hwConfig = HwConfig(TestConfigHelper.CONFIG_PATH)
        self.helper = ConfigHelper(self.hwConfig)

    def tearDown(self):
        if os.path.exists(TestConfigHelper.CONFIG_PATH):
            os.remove(TestConfigHelper.CONFIG_PATH)

    def test_boolValueStore(self):
        self.helper.autoOff = True
        self.helper.resinSensor = False

        self.assertTrue(self.helper.autoOff)
        self.assertFalse(self.helper.resinSensor)
        self.assertIsInstance(self.helper.autoOff, bool)
        self.assertIsInstance(self.helper.resinSensor, bool)

    def test_integerValueStore(self):
        self.helper.towerHeight = 42

        self.assertEqual(self.helper.towerHeight, 42)
        self.assertIsInstance(self.helper.towerHeight, int)

    def test_floatValueStore(self):
        self.helper.pixelSize = 4.2

        self.assertAlmostEqual(self.helper.pixelSize, 4.2)
        self.assertIsInstance(self.helper.pixelSize, float)

    def test_commit(self):
        # Fresh helper is not changed
        self.assertFalse(self.helper.changed())
        self.assertFalse(self.helper.changed('autoOff'))
        self.assertFalse(self.helper.changed('pixelSize'))

        self.helper.autoOff = False

        # Underling valus is intact before commit
        self.assertTrue(self.hwConfig.autoOff)

        # Changed behaviour before commit
        self.assertTrue(self.helper.changed())
        self.assertTrue(self.helper.changed('autoOff'))
        self.assertFalse(self.helper.changed('pixelSize'))

        self.helper.commit()

        # Underling valus is changed after commit
        self.assertFalse(self.hwConfig.autoOff)

        # Changed behaviour after commit
        self.assertFalse(self.helper.changed())
        self.assertFalse(self.helper.changed('autoOff'))
        self.assertFalse(self.helper.changed('pixelSize'))

    def test_changed(self):
        self.assertFalse(self.helper.changed(), "Fresh config is not changed")

        self.helper.autoOff = not self.helper.autoOff

        self.assertTrue(self.helper.changed(), "Modified config is changed")

        self.helper.autoOff = not self.helper.autoOff

        self.assertFalse(self.helper.changed(), "After modify revert the config is not changed")


if __name__ == '__main__':
    unittest.main()