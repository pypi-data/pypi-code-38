############################################################
# -*- coding: utf-8 -*-
#
# MOUNTCONTROL
#
# Python-based Tool for interaction with the 10micron mounts
# GUI with PyQT5 for python
# Python  v3.6.5
#
# Michael Würtenberger
# (c) 2018
#
# Licence APL2.0
#
############################################################
# standard libraries
import unittest
# external packages
# local imports
from mountcontrol.convert import stringToDegree
from mountcontrol.convert import stringToAngle
from mountcontrol.convert import valueToFloat
from mountcontrol.convert import valueToAngle
from mountcontrol.convert import valueToInt
from mountcontrol.convert import topoToAltAz


class TestConfigData(unittest.TestCase):

    def setUp(self):
        pass

    #
    #
    # testing the conversion functions
    #
    #

    def test_valueToDegree_ok1(self):
        parameter = '12:45:33.01'
        value = stringToDegree(parameter)
        self.assertAlmostEqual(12.759169444444444, value, 6)

    def test_stringToDegree_ok2(self):
        parameter = '12:45'
        value = stringToDegree(parameter)
        self.assertAlmostEqual(12.75, value, 6)

    def test_stringToDegree_ok3(self):
        parameter = '+56*30:00.0'
        value = stringToDegree(parameter)
        self.assertAlmostEqual(56.5, value, 6)

    def test_stringToDegree_ok4(self):
        parameter = '-56*30:00.0'
        value = stringToDegree(parameter)
        self.assertAlmostEqual(value, -56.5, 6)

    def test_stringToDegree_ok5(self):
        parameter = '+56*30*00.0'
        value = stringToDegree(parameter)
        self.assertAlmostEqual(56.5, value)

    def test_stringToDegree_ok6(self):
        parameter = '+56*30'
        value = stringToDegree(parameter)
        self.assertAlmostEqual(56.5, value, 6)

    def test_stringToDegree_ok7(self):
        parameter = '+56:30:00.0'
        value = stringToDegree(parameter)
        self.assertAlmostEqual(56.5, value, 6)

    def test_stringToDegree_ok8(self):
        parameter = '56deg 30\'00.0"'
        value = stringToDegree(parameter)
        self.assertAlmostEqual(56.5, value, 6)

    def test_stringToDegree_ok9(self):
        parameter = '56 30 00.0'
        value = stringToDegree(parameter)
        self.assertAlmostEqual(56.5, value, 6)

    def test_stringToDegree_ok10(self):
        parameter = '11deg 35\' 00.0"'
        value = stringToDegree(parameter)
        self.assertAlmostEqual(11.5833333, value, 6)

    def test_stringToDegree_bad1(self):
        parameter = ''
        value = stringToDegree(parameter)
        self.assertEqual(None, value)

    def test_stringToDegree_bad2(self):
        parameter = '12:45:33:01.01'
        value = stringToDegree(parameter)
        self.assertEqual(None, value)

    def test_stringToDegree_bad3(self):
        parameter = '++56*30:00.0'
        value = stringToDegree(parameter)
        self.assertAlmostEqual(None, value)

    def test_stringToDegree_bad4(self):
        parameter = ' 56*30:00.0'
        value = stringToDegree(parameter)
        self.assertAlmostEqual(value, 56.5, 6)

    def test_stringToDegree_bad5(self):
        parameter = '--56*30:00.0'
        value = stringToDegree(parameter)
        self.assertAlmostEqual(None, value)

    def test_stringToDegree_bad6(self):
        parameter = '-56*dd:00.0'
        value = stringToDegree(parameter)
        self.assertAlmostEqual(None, value)

    def test_stringToAngle_ok(self):
        parameter = '+50*30:00.0'
        value = stringToAngle(parameter)
        self.assertEqual(50.5, value.degrees)

    def test_stringToAngle_ok1(self):
        parameter = '+50*30:00.0'
        value = stringToAngle(parameter, preference='hours')
        self.assertEqual(50.5, value.hours)

    def test_stringToAngle_ok2(self):
        parameter = '+50*30:00.0'
        value = stringToAngle(parameter, preference='degrees')
        self.assertEqual(50.5, value.degrees)

    def test_valueToAngle_ok(self):
        parameter = 50.5
        value = valueToAngle(parameter)
        self.assertEqual(50.5, value.degrees)

    def test_valueToAngle_ok1(self):
        parameter = 50.5
        value = valueToAngle(parameter, preference='hours')
        self.assertEqual(50.5, value.hours)

    def test_valueToAngle_ok2(self):
        parameter = 50.5
        value = valueToAngle(parameter, preference='degrees')
        self.assertEqual(50.5, value.degrees)

    def test_valueToAngle_ok3(self):
        parameter = '50.5'
        value = valueToAngle(parameter, preference='degrees')
        self.assertEqual(50.5, value.degrees)

    def test_valueToAngle_ok4(self):
        parameter = '00.000'
        value = valueToAngle(parameter, preference='degrees')
        self.assertEqual(0, value.degrees)

    def test_stringToAngle_not_ok1(self):
        parameter = 178
        value = stringToAngle(parameter)
        self.assertEqual(None, value)

    def test_valueToInt_ok(self):
        parameter = '156'
        value = valueToInt(parameter)
        self.assertEqual(156, value)

    def test_valueToInt_not_ok(self):
        parameter = 'df'
        value = valueToInt(parameter)
        self.assertEqual(None, value)

    def test_valueToFloat_ok(self):
        parameter = '156'
        value = valueToFloat(parameter)
        self.assertEqual(156, value)

    def test_valueToFloat_not_ok(self):
        parameter = 'df'
        value = valueToFloat(parameter)
        self.assertEqual(None, value)

    def test_topoToAltAz_ok1(self):
        alt, az = topoToAltAz(0, 0, None)
        self.assertEqual(None, alt)
        self.assertEqual(None, az)

    def test_topoToAltAz_ok2(self):
        alt, az = topoToAltAz(0, 0, 0)
        self.assertEqual(90, alt)
        self.assertEqual(270, az)

    def test_topoToAltAz_ok3(self):
        alt, az = topoToAltAz(12, 0, 0)
        self.assertEqual(-90, alt)
        self.assertEqual(270, az)

    def test_topoToAltAz_ok4(self):
        alt, az = topoToAltAz(12, 180, 0)
        self.assertEqual(90, alt)
        self.assertEqual(360, az)

    def test_topoToAltAz_ok5(self):
        alt, az = topoToAltAz(-12, 0, 0)
        self.assertEqual(-90, alt)
        self.assertEqual(270, az)
