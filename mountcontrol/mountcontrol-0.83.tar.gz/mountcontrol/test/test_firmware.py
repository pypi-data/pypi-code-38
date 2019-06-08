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
import unittest.mock as mock
# external packages
# local imports
from mountcontrol.firmware import Firmware


class TestConfigData(unittest.TestCase):

    def setUp(self):
        pass

    #
    #
    # testing host
    #
    #

    def test_Setting_host_ok1(self):
        fw = Firmware()
        fw.host = ('192.168.2.1', 1234)
        self.assertEqual(('192.168.2.1', 1234), fw.host)
        self.assertEqual(('192.168.2.1', 1234), fw._host)

    def test_Setting_host_ok2(self):
        fw = Firmware()
        fw.host = '192.168.2.1'
        self.assertEqual(('192.168.2.1', 3492), fw.host)

    def test_Setting_host_not_ok1(self):
        fw = Firmware()
        fw.host = ''
        self.assertEqual(None, fw.host)

    def test_Setting_host_not_ok2(self):
        fw = Firmware()
        fw.host = 2357
        self.assertEqual(None, fw.host)

    #
    #
    # testing firmware class it's attribute
    #
    #

    def test_Firmware_ok(self):
        fw = Firmware()

        fw.productName = 'Test'
        self.assertEqual('Test', fw.productName)
        self.assertEqual('Test', fw._productName)
        fw.numberString = '2.15.08'
        self.assertEqual('2.15.08', fw.numberString)
        self.assertEqual('2.15.08', fw._numberString)
        self.assertEqual(fw.number(), 21508)
        fw.hwVersion = '4.5'
        self.assertEqual('4.5', fw.hwVersion)
        self.assertEqual('4.5', fw._hwVersion)
        fw.fwdate = '2018-07-08'
        self.assertEqual('2018-07-08', fw.fwdate)
        self.assertEqual('2018-07-08', fw._fwdate)
        fw.fwtime = '14:50'
        self.assertEqual('14:50', fw.fwtime)
        self.assertEqual('14:50', fw._fwtime)
        self.assertEqual(True, fw.checkNewer(26000))

    def test_Firmware_not_ok_numberString(self):
        fw = Firmware()

        fw.numberString = '2.1508'
        self.assertEqual(None, fw.numberString)
        fw.numberString = '21508'
        self.assertEqual(None, fw.numberString)
        fw.numberString = '2.ee.15'
        self.assertEqual(None, fw.numberString)
        fw.numberString = ''
        self.assertEqual(None, fw.numberString)
        fw._numberString = '2.ee.15'
        self.assertEqual(None, fw.number())

    def test_Firmware_checkNewer(self):
        fw = Firmware()
        fw.numberString = 5
        self.assertEqual(None, fw.checkNewer(100))

    #
    #
    # testing pollSetting
    #
    #

    def test_Firmware_parse_ok1(self):
        fw = Firmware()

        response = ['Mar 19 2018', '2.15.14',
                    '10micron GM1000HPS', '15:56:53', 'Q-TYPE2012']
        suc = fw._parse(response, 5)
        self.assertEqual(True, suc)

    def test_Firmware_parse_ok2(self):
        fw = Firmware()

        response = ['Mar 19 2018', '2.15.14',
                    '10micron GM1000HPS', '15:56:53', 'Q-TYPE2012']
        suc = fw._parse(response, 5)
        self.assertEqual(True, suc)

    def test_Firmware_parse_not_ok1(self):
        fw = Firmware()

        response = ['Mar 19 2018', '2.15.14',
                    '10micron GM1000HPS', '15:56:53']
        suc = fw._parse(response, 5)
        self.assertEqual(False, suc)

    def test_Firmware_parse_not_ok2(self):
        fw = Firmware()

        response = []
        suc = fw._parse(response, 5)
        self.assertEqual(False, suc)

    def test_Firmware_parse_not_ok3(self):
        fw = Firmware()

        response = ['Mar 19 2018', '2.15.14',
                    '10micron GM1000HPS', '15:56:53', 'Q-TYPE2012']

        suc = fw._parse(response, 5)
        self.assertEqual(True, suc)

    def test_Firmware_parse_not_ok4(self):
        fw = Firmware()

        response = ['Mar 19 2018', '2.1514',
                    '10micron GM1000HPS', '15:56:53', 'Q-TYPE2012']

        suc = fw._parse(response, 5)
        self.assertEqual(True, suc)

    def test_Firmware_parse_not_ok5(self):
        fw = Firmware()

        response = ['Mar 19 2018', '2.15.14',
                    '10micron GM1000HPS', '15:56:53', 'Q-TYPE2012']

        suc = fw._parse(response, 5)
        self.assertEqual(True, suc)

    def test_Firmware_parse_not_ok6(self):
        fw = Firmware()

        response = ['Mar 19 2018', '2.15.14',
                    '10micron GM1000HPS', '15:56:53', 'Q-TYPE2012']

        suc = fw._parse(response, 5)
        self.assertEqual(True, suc)

    def test_Firmware_poll_ok(self):
        fw = Firmware()

        response = ['Mar 19 2018', '2.15.14',
                    '10micron GM1000HPS', '15:56:53', 'Q-TYPE2012']

        with mock.patch('mountcontrol.firmware.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 5
            suc = fw.poll()
            self.assertEqual(True, suc)

    def test_Firmware_poll_not_ok1(self):
        fw = Firmware()

        response = ['Mar 19 2018', '2.15.14',
                    '10micron GM1000HPS', '15:56:53', 'Q-TYPE2012']

        with mock.patch('mountcontrol.firmware.Connection') as mConn:
            mConn.return_value.communicate.return_value = False, response, 5
            suc = fw.poll()
            self.assertEqual(False, suc)
