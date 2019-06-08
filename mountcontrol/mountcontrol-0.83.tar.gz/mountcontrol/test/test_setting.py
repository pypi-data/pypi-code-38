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
from mountcontrol.setting import Setting


class TestConfigData(unittest.TestCase):

    def setUp(self):
        pass

    #
    #
    # testing host
    #
    #

    def test_Setting_host_ok1(self):
        sett = Setting()
        sett.host = ('192.168.2.1', 1234)
        self.assertEqual(('192.168.2.1', 1234), sett.host)

    def test_Setting_host_ok2(self):
        sett = Setting()
        sett.host = '192.168.2.1'
        self.assertEqual(('192.168.2.1', 3492), sett.host)

    def test_Setting_host_not_ok1(self):
        sett = Setting()
        sett.host = ''
        self.assertEqual(None, sett.host)

    def test_Setting_host_not_ok2(self):
        sett = Setting()
        sett.host = 2357
        self.assertEqual(None, sett.host)
        self.assertEqual(None, sett._host)

    #
    #
    # testing the class Setting and it's attribute
    #
    #

    def test_Setting_slewRate(self):
        sett = Setting()
        sett.slewRate = '67'
        self.assertEqual(67, sett.slewRate)
        self.assertEqual(67, sett._slewRate)

    def test_Setting_timeToFlip(self):
        sett = Setting()
        sett.timeToFlip = '67'
        self.assertEqual(67, sett.timeToFlip)
        self.assertEqual(67, sett._timeToFlip)

    def test_Setting_meridianLimitTrack(self):
        sett = Setting()
        sett.meridianLimitTrack = '67'
        self.assertEqual(67, sett.meridianLimitTrack)
        self.assertEqual(67, sett._meridianLimitTrack)

    def test_Setting_meridianLimitSlew(self):
        sett = Setting()
        sett.meridianLimitSlew = '67'
        self.assertEqual(67, sett.meridianLimitSlew)
        self.assertEqual(67, sett._meridianLimitSlew)

    def test_Setting_timeToMeridian(self):
        sett = Setting()
        sett.timeToFlip = '10'
        sett.meridianLimitTrack = '5'
        self.assertEqual(-10, sett.timeToMeridian())

    def test_Setting_refractionTemp(self):
        sett = Setting()
        sett.refractionTemp = '67'
        self.assertEqual(67, sett.refractionTemp)
        self.assertEqual(67, sett._refractionTemp)

    def test_Setting_refractionPress(self):
        sett = Setting()
        sett.refractionPress = '67'
        self.assertEqual(67, sett.refractionPress)
        self.assertEqual(67, sett._refractionPress)

    def test_Setting_trackingRate(self):
        sett = Setting()
        sett.trackingRate = '67'
        self.assertEqual(67, sett.trackingRate)

    def test_Checking_trackingRate1(self):
        sett = Setting()
        sett.trackingRate = '62.4'
        self.assertEqual(True, sett.checkRateLunar())
        self.assertEqual(False, sett.checkRateSidereal())
        self.assertEqual(False, sett.checkRateSolar())

    def test_Checking_trackingRate2(self):
        sett = Setting()
        sett.trackingRate = '60.2'
        self.assertEqual(False, sett.checkRateLunar())
        self.assertEqual(True, sett.checkRateSidereal())
        self.assertEqual(False, sett.checkRateSolar())

    def test_Checking_trackingRate3(self):
        sett = Setting()
        sett.trackingRate = '60.3'
        self.assertEqual(False, sett.checkRateLunar())
        self.assertEqual(False, sett.checkRateSidereal())
        self.assertEqual(True, sett.checkRateSolar())

    def test_Checking_trackingRate4(self):
        sett = Setting()
        sett.trackingRate = '6'
        self.assertEqual(False, sett.checkRateLunar())
        self.assertEqual(False, sett.checkRateSidereal())
        self.assertEqual(False, sett.checkRateSolar())

    def test_Setting_telescopeTempDEC(self):
        sett = Setting()
        sett.telescopeTempDEC = '67'
        self.assertEqual(67, sett.telescopeTempDEC)

    def test_Setting_statusRefraction(self):
        sett = Setting()
        sett.statusRefraction = 1
        self.assertEqual(True, sett.statusRefraction)
        self.assertEqual(True, sett._statusRefraction)

    def test_Setting_statusUnattendedFlip(self):
        sett = Setting()
        sett.statusUnattendedFlip = 1
        self.assertEqual(True, sett.statusUnattendedFlip)
        self.assertEqual(True, sett._statusUnattendedFlip)

    def test_Setting_statusDualTracking(self):
        sett = Setting()
        sett.statusDualTracking = 1
        self.assertEqual(True, sett.statusDualTracking)
        self.assertEqual(True, sett._statusDualTracking)

    def test_Setting_horizonLimitHigh(self):
        sett = Setting()
        sett.horizonLimitHigh = '67'
        self.assertEqual(67, sett.horizonLimitHigh)
        self.assertEqual(67, sett._horizonLimitHigh)

    def test_Setting_horizonLimitLow(self):
        sett = Setting()
        sett.horizonLimitLow = '67'
        self.assertEqual(67, sett.horizonLimitLow)
        self.assertEqual(67, sett._horizonLimitLow)

    def test_Setting_UTCValid(self):
        sett = Setting()
        sett.UTCValid = 1
        self.assertEqual(True, sett.UTCValid)
        self.assertEqual(True, sett._UTCValid)

    def test_Setting_UTCExpire(self):
        sett = Setting()
        sett.UTCExpire = '67'
        self.assertEqual('67', sett.UTCExpire)
        self.assertEqual('67', sett._UTCExpire)

    def test_Setting_UTCExpire1(self):
        sett = Setting()
        sett.UTCExpire = 67
        self.assertEqual(None, sett.UTCExpire)
        self.assertEqual(None, sett._UTCExpire)

    def test_Setting_typeConnection_1(self):
        sett = Setting()
        sett.typeConnection = 5
        self.assertEqual(None, sett.typeConnection)
        self.assertEqual(None, sett._typeConnection)

    def test_Setting_typeConnection_2(self):
        sett = Setting()
        sett.typeConnection = 3
        self.assertEqual(3, sett.typeConnection)
        self.assertEqual(3, sett._typeConnection)

    def test_Setting_gpsSynced_1(self):
        sett = Setting()
        sett.gpsSynced = 5
        self.assertEqual(True, sett.gpsSynced)
        self.assertEqual(True, sett._gpsSynced)

    def test_Setting_gpsSynced_2(self):
        sett = Setting()
        sett.gpsSynced = 0
        self.assertEqual(False, sett.gpsSynced)
        self.assertEqual(False, sett._gpsSynced)

    def test_Setting_addressLanMAC_1(self):
        sett = Setting()
        value = '00:00:00:00:00:00'
        sett.addressLanMAC = '00:00:00:00:00:00'
        self.assertEqual(value, sett.addressLanMAC)
        self.assertEqual(value, sett._addressLanMAC)

    def test_Setting_addressWirelessMAC_1(self):
        sett = Setting()
        value = '00:00:00:00:00:00'
        sett.addressWirelessMAC = '00:00:00:00:00:00'
        self.assertEqual(value, sett.addressWirelessMAC)
        self.assertEqual(value, sett._addressWirelessMAC)

    #
    #
    # testing pollSetting med
    #
    #

    def test_Setting_parse_ok(self):
        sett = Setting()
        response = ['15', '0426', '05', '03', '+010.0', '0950.0', '60.2', '+033.0', '101+90*',
                    '+00*', 'E,2018-08-11', '1', '0', '00:00:00:00:00:00']
        suc = sett._parseSetting(response, 14)
        self.assertEqual(True, suc)

    def test_Setting_parse_not_ok1(self):
        sett = Setting()
        response = ['15', '0426', '05', '03', '+010.0', '0EEE.0', '60.2', '+033.0', '101+90*',
                    '+00*', 'E,2018-08-11', '1', '0', '00:00:00:00:00:00']
        suc = sett._parseSetting(response, 14)
        self.assertEqual(True, suc)

    def test_Setting_parse_not_ok2(self):
        sett = Setting()
        response = ['15', '0426', '05', '03', '+010.0', '0950.0', '60.2', '+033.0', '+90*',
                    '+00*', 'E,2018-08-11', '1', '0', '00:00:00:00:00:00']
        suc = sett._parseSetting(response, 14)
        self.assertEqual(True, suc)

    def test_Setting_parse_not_ok3(self):
        sett = Setting()
        response = ['15', '0426', '05', '03', '+010.0', '0950.0', '60.2', '+033.0', '101+90*',
                    '+00', 'E,2018-08-11', '1', '0', '00:00:00:00:00:00']

        suc = sett._parseSetting(response, 14)
        self.assertEqual(True, suc)

    def test_Setting_parse_not_ok4(self):
        sett = Setting(
                       )
        response = ['15', '0426', '05', '03', '+010.0', '0950.0', '60.2', '+033.0', '101+90*',
                    '+00*', ',2018-08-11', '1', '0', '00:00:00:00:00:00']

        suc = sett._parseSetting(response, 14)

        self.assertEqual(True, suc)

    def test_Setting_poll_ok1(self):
        sett = Setting()

        response = ['15', '0426', '05', '03', '+010.0', '0950.0', '60.2', '+033.0',
                    '101+90*', '+00*', 'E,2018-08-11', '1', '0', '00:00:00:00:00:00']

        with mock.patch('mountcontrol.setting.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 14
            suc = sett.pollSetting()
            self.assertEqual(True, suc)

    def test_Setting_poll_ok2(self):
        sett = Setting()

        response = ['15', '0426', '05', '03', '+010.0', '0950.0', '60.2', '+033.0',
                    '101+90*', '+00*', 'E,2018-08-11', '1', '0', '00:00:00:00:00:00']

        with mock.patch('mountcontrol.setting.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 14
            suc = sett.pollSetting()
            self.assertEqual(True, suc)

    def test_Setting_poll_not_ok1(self):
        sett = Setting()

        response = ['15', '0426', '05', '03', '+010.0', '0950.0', '60.2', '+033.0',
                    '101+90*', '+00*', 'E,2018-08-11', '1', '0', '00:00:00:00:00:00']

        with mock.patch('mountcontrol.setting.Connection') as mConn:
            mConn.return_value.communicate.return_value = False, response, 14
            suc = sett.pollSetting()
            self.assertEqual(False, suc)

    def test_Setting_poll_not_ok2(self):
        sett = Setting()

        response = ['15', '0426', '05', '03', '+010.0', '0950.0', '60.2', '+033.0',
                    '101+90*', '+00*', 'E,2018-08-11', '1', '0', '00:00:00:00:00:00']

        with mock.patch('mountcontrol.setting.Connection') as mConn:
            mConn.return_value.communicate.return_value = False, response, 6
            suc = sett.pollSetting()
            self.assertEqual(False, suc)

    #
    #
    # testing host
    #
    #

    def test_mac_ok1(self):
        sett = Setting()

        value = sett.checkFormatMAC('00:00:00:00:00:00')
        self.assertEqual('00:00:00:00:00:00', value)

    def test_mac_ok2(self):
        sett = Setting()

        value = sett.checkFormatMAC('00:aa:00:00:00:00')
        self.assertEqual('00:AA:00:00:00:00', value)

    def test_mac_ok3(self):
        sett = Setting()

        value = sett.checkFormatMAC('00:00:eF:00:00:00')
        self.assertEqual('00:00:EF:00:00:00', value)

    def test_mac_ok4(self):
        sett = Setting()

        value = sett.checkFormatMAC('00.00.00.00.00.00')
        self.assertEqual('00:00:00:00:00:00', value)

    def test_mac_not_ok1(self):
        sett = Setting()

        value = sett.checkFormatMAC('00:00:000:00:00:00')
        self.assertEqual(None, value)

    def test_mac_not_ok2(self):
        sett = Setting()

        value = sett.checkFormatMAC('00:00:0:00:00:00')
        self.assertEqual(None, value)

    def test_mac_not_ok3(self):
        sett = Setting()

        value = sett.checkFormatMAC('00:00:00:00:00')
        self.assertEqual(None, value)

    def test_mac_not_ok4(self):
        sett = Setting()

        value = sett.checkFormatMAC('0h:00:00:00:00:00')
        self.assertEqual(None, value)
