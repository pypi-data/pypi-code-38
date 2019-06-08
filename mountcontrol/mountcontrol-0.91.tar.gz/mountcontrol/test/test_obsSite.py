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
import skyfield.api
# local imports
from mountcontrol.obsSite import ObsSite


class TestConfigData(unittest.TestCase):

    def setUp(self):
        pass

    #
    #
    # testing host
    #
    #

    def test_ObsSite_host_ok1(self):
        obsSite = ObsSite()
        obsSite.host = ('192.168.2.1', 1234)
        self.assertEqual(('192.168.2.1', 1234), obsSite.host)

    def test_ObsSite_host_ok2(self):
        obsSite = ObsSite()
        obsSite.host = '192.168.2.1'
        self.assertEqual(('192.168.2.1', 3492), obsSite.host)
        self.assertEqual(('192.168.2.1', 3492), obsSite._host)

    def test_ObsSite_host_not_ok1(self):
        obsSite = ObsSite()
        obsSite.host = ''
        self.assertEqual(None, obsSite.host)

    def test_ObsSite_host_not_ok2(self):
        obsSite = ObsSite()
        obsSite.host = 2357
        self.assertEqual(None, obsSite.host)
    #
    #
    # testing the timescale reference
    #
    #

    def test_ObsSite_expire_ok(self):
        pathToData = '~/PycharmProjects/mountcontrol/data/'
        obsSite = ObsSite(pathToData=pathToData)
        obsSite.expire = True
        self.assertEqual(True, obsSite.expire)
        obsSite.expire = False
        self.assertEqual(False, obsSite.expire)
        self.assertEqual(False, obsSite._expire)
    """
    def test_ObsSite_expire_not_ok(self):
        pathToData = '~/PycharmProjects/mountcontrol/data/'
        obsSite = ObsSite(pathToData=pathToData)
        obsSite.expire = 5
        self.assertEqual(obsSite.expire, True)
        obsSite.expire = 'ff'
        self.assertEqual(obsSite.expire, True)
    """
    #
    #
    # testing the timescale reference
    #
    #

    def test_Data_without_ts(self):
        obsSite = ObsSite()
        self.assertEqual(isinstance(obsSite.ts, skyfield.api.Timescale), True)

    def test_Data_with_ts(self):
        pathToData = '~/PycharmProjects/mountcontrol/data'
        obsSite = ObsSite(pathToData=pathToData)
        self.assertEqual(isinstance(obsSite.ts, skyfield.api.Timescale), True)

    #
    #
    # testing the obsSite Model and it's attribute
    #
    #

    def test_Site_location_1(self):
        obsSite = ObsSite()

        elev = '999.9'
        lon = '+160*30:45.5'
        lat = '+45*30:45.5'
        obsSite.location = lat, lon, elev
        self.assertAlmostEqual(160, obsSite.location.longitude.dms()[0], 6)
        self.assertAlmostEqual(30, obsSite.location.longitude.dms()[1], 6)
        self.assertAlmostEqual(45.5, obsSite.location.longitude.dms()[2], 6)
        self.assertAlmostEqual(45, obsSite.location.latitude.dms()[0], 6)
        self.assertAlmostEqual(30, obsSite.location.latitude.dms()[1], 6)
        self.assertAlmostEqual(45.5, obsSite.location.latitude.dms()[2], 6)
        self.assertAlmostEqual(999.9, obsSite.location.elevation.m, 6)

    def test_Site_location_2(self):
        obsSite = ObsSite()

        elev = '999.9'
        lon = '+160*30:45.5'
        lat = '+45*30:45.5'
        obsSite.location = (lat, lon, elev)
        self.assertAlmostEqual(160, obsSite.location.longitude.dms()[0], 6)
        self.assertAlmostEqual(30, obsSite.location.longitude.dms()[1], 6)
        self.assertAlmostEqual(45.5, obsSite.location.longitude.dms()[2], 6)
        self.assertAlmostEqual(45, obsSite.location.latitude.dms()[0], 6)
        self.assertAlmostEqual(30, obsSite.location.latitude.dms()[1], 6)
        self.assertAlmostEqual(45.5, obsSite.location.latitude.dms()[2], 6)
        self.assertAlmostEqual(999.9, obsSite.location.elevation.m, 6)

    def test_Site_location_3(self):
        obsSite = ObsSite()

        elev = 100
        lon = 100
        lat = 45
        obsSite.location = skyfield.api.Topos(longitude_degrees=lon,
                                              latitude_degrees=lat,
                                              elevation_m=elev)
        self.assertAlmostEqual(100, obsSite.location.longitude.dms()[0], 6)
        self.assertAlmostEqual(0, obsSite.location.longitude.dms()[1], 6)
        self.assertAlmostEqual(0, obsSite.location.longitude.dms()[2], 6)
        self.assertAlmostEqual(45, obsSite.location.latitude.dms()[0], 6)
        self.assertAlmostEqual(0, obsSite.location.latitude.dms()[1], 6)
        self.assertAlmostEqual(0, obsSite.location.latitude.dms()[2], 6)
        self.assertAlmostEqual(100, obsSite.location.elevation.m, 6)

    def test_Site_location_4(self):
        obsSite = ObsSite()

        lon = '+160*30:45.5'
        lat = '+45*30:45.5'
        obsSite.location = (lat, lon)
        self.assertEqual(None, obsSite.location)
        self.assertEqual(None, obsSite._location)

    def test_Site_location_5(self):
        obsSite = ObsSite()

        lat = '+45*30:45.5'
        obsSite.location = lat
        self.assertEqual(None, obsSite.location)

    def test_Site_timeJD(self):
        pathToData = '~/PycharmProjects/mountcontrol/data'
        obsSite = ObsSite(pathToData=pathToData)

        obsSite.utc_ut1 = '0'
        obsSite.timeJD = '2458240.12345678'
        self.assertEqual(2458240.12345678, obsSite.timeJD.ut1)
        obsSite.timeJD = 2458240.12345678
        self.assertEqual(2458240.12345678, obsSite.timeJD.ut1)
        obsSite.timeJD = '2458240.a23e5678'
        self.assertAlmostEqual(obsSite.ts.now(), obsSite.timeJD, 4)
        self.assertEqual(None, obsSite._timeJD)

    def test_Site_timeJD1(self):
        pathToData = '~/PycharmProjects/mountcontrol/data'
        obsSite = ObsSite(pathToData=pathToData)

        obsSite.timeJD = '2458240.12345678'
        self.assertAlmostEqual(obsSite.ts.now(), obsSite.timeJD, 4)

    def test_Site_utc_ut1(self):
        pathToData = '~/PycharmProjects/mountcontrol/data'
        obsSite = ObsSite(pathToData=pathToData)

        obsSite.utc_ut1 = '123.11'
        self.assertEqual(123.11 / 86400, obsSite.utc_ut1)

    def test_Site_timeSidereal(self):
        obsSite = ObsSite()

        obsSite.timeSidereal = '12:30:30.01'
        self.assertEqual('12:30:30.01', obsSite.timeSidereal)
        obsSite.timeSidereal = '12:aa:30.01'
        self.assertEqual(None, obsSite.timeSidereal)
        self.assertEqual(None, obsSite._timeSidereal)
        obsSite.timeSidereal = 34
        self.assertEqual(None, obsSite.timeSidereal)

    def test_Site_ra(self):
        obsSite = ObsSite()

        obsSite.raJNow = skyfield.api.Angle(hours=34)
        self.assertEqual(34, obsSite.raJNow.hours)
        obsSite.raJNow = 34
        self.assertEqual(34, obsSite.raJNow.hours)
        self.assertEqual(34, obsSite._raJNow.hours)
        obsSite.raJNow = '34'
        self.assertEqual(34, obsSite.raJNow.hours)
        obsSite.raJNow = '34f'
        self.assertEqual(None, obsSite.raJNow)

    def test_Site_dec(self):
        obsSite = ObsSite()

        obsSite.decJNow = skyfield.api.Angle(degrees=34)
        self.assertEqual(34, obsSite.decJNow.degrees)
        obsSite.decJNow = 34
        self.assertEqual(34, obsSite.decJNow.degrees)
        self.assertEqual(34, obsSite._decJNow.degrees)
        obsSite.decJNow = '34'
        self.assertEqual(34, obsSite.decJNow.degrees)
        obsSite.decJNow = '34f'
        self.assertEqual(None, obsSite.decJNow)

    def test_Site_alt(self):
        obsSite = ObsSite()

        obsSite.Alt = skyfield.api.Angle(degrees=34)
        self.assertEqual(34, obsSite.Alt.degrees)
        obsSite.Alt = 34
        self.assertEqual(34, obsSite.Alt.degrees)
        self.assertEqual(34, obsSite._Alt.degrees)
        obsSite.Alt = '34'
        self.assertEqual(34, obsSite.Alt.degrees)
        obsSite.Alt = '34f'
        self.assertEqual(None, obsSite.Alt)

    def test_Site_az(self):
        obsSite = ObsSite()

        obsSite.Az = skyfield.api.Angle(degrees=34)
        self.assertEqual(34, obsSite.Az.degrees)
        obsSite.Az = 34
        self.assertEqual(34, obsSite.Az.degrees)
        self.assertEqual(34, obsSite._Az.degrees)
        obsSite.Az = '34'
        self.assertEqual(34, obsSite.Az.degrees)
        obsSite.Az = '34f'
        self.assertEqual(None, obsSite.Az)

    def test_Site_pierside(self):
        obsSite = ObsSite()

        obsSite.pierside = 'E'
        self.assertEqual(obsSite.pierside, 'E')
        obsSite.pierside = 'e'
        self.assertEqual(obsSite.pierside, 'E')
        obsSite.pierside = 'w'
        self.assertEqual(obsSite.pierside, 'W')
        self.assertEqual(obsSite._pierside, 'W')
        obsSite.pierside = 'W'
        self.assertEqual(obsSite.pierside, 'W')
        obsSite.pierside = 'WW'
        self.assertEqual(obsSite.pierside, None)
        obsSite.pierside = '12'
        self.assertEqual(obsSite.pierside, None)
        obsSite.pierside = 17
        self.assertEqual(obsSite.pierside, None)

    def test_Site_status(self):
        obsSite = ObsSite()

        obsSite.status = '1'
        self.assertEqual(1, obsSite.status)
        obsSite.status = 1
        self.assertEqual(1, obsSite.status)
        self.assertEqual(1, obsSite._status)
        obsSite.status = '1d'
        self.assertEqual(None, obsSite.status)
        obsSite.status = '1d'
        self.assertEqual(None, obsSite.status)
        obsSite.status = '0'
        self.assertEqual(0, obsSite.status)
        obsSite.status = '100'
        self.assertEqual(None, obsSite.status)

    def test_Site_statusText1(self):
        obsSite = ObsSite()

        obsSite.status = '1d'
        self.assertEqual(None, obsSite.status)
        # self.assertEqual(None, obsSite.statusText())

    def test_Site_statusText2(self):
        obsSite = ObsSite()

        obsSite.status = '1'
        self.assertEqual(1, obsSite.status)
        self.assertEqual('Stopped after STOP', obsSite.statusText())

    def test_Site_statusSlew(self):
        obsSite = ObsSite()

        obsSite.statusSlew = '1'
        self.assertEqual(True, obsSite.statusSlew)
        obsSite.statusSlew = 1
        self.assertEqual(True, obsSite.statusSlew)
        self.assertEqual(True, obsSite._statusSlew)
        obsSite.statusSlew = True
        self.assertEqual(True, obsSite.statusSlew)
        obsSite.statusSlew = False
        self.assertEqual(False, obsSite.statusSlew)
        obsSite.statusSlew = 'True'
        self.assertEqual(True, obsSite.statusSlew)
        obsSite.statusSlew = '100'
        self.assertEqual(True, obsSite.statusSlew)
        obsSite.statusSlew = '-100'
        self.assertEqual(True, obsSite.statusSlew)
        obsSite.statusSlew = ''
        self.assertEqual(False, obsSite.statusSlew)
        obsSite.statusSlew = (0, 0)
        self.assertEqual(True, obsSite.statusSlew)

    def test_ObsSite_parse_ok1(self):
        obsSite = ObsSite()

        response = ['+0585.2', '-011:35:00.0', '+48:07:00.0']
        suc = obsSite._parseLocation(response, 3)
        self.assertEqual(True, suc)

    def test_ObsSite_parse_ok2(self):
        obsSite = ObsSite()

        response = ['+0585.2', '+011:35:00.0', '+48:07:00.0']
        suc = obsSite._parseLocation(response, 3)
        self.assertEqual(True, suc)

    def test_ObsSite_parse_not_ok1(self):
        obsSite = ObsSite()
        response = []
        suc = obsSite._parseLocation(response, 3)
        self.assertEqual(False, suc)

    def test_ObsSite_parse_not_ok2(self):
        obsSite = ObsSite()

        response = ['+master', '-011:35:00.0', '+48:07:00.0']

        suc = obsSite._parseLocation(response, 3)
        self.assertEqual(True, suc)

    def test_ObsSite_parse_not_ok3(self):
        obsSite = ObsSite()

        response = ['+0585.2', '-011:35:00.0', '+48:sdj.0']

        suc = obsSite._parseLocation(response, 3)
        self.assertEqual(True, suc)

    def test_ObsSite_parse_not_ok4(self):
        obsSite = ObsSite()

        response = ['+0585.2', '-011:EE:00.0', '+48:07:00.0']

        suc = obsSite._parseLocation(response, 3)
        self.assertEqual(True, suc)

    def test_ObsSite_poll_ok(self):
        obsSite = ObsSite()

        response = ['+0585.2', '-011:35:00.0', '+48:07:00.0']

        with mock.patch('mountcontrol.obsSite.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 3
            suc = obsSite.getLocation()
            self.assertEqual(True, suc)

    def test_ObsSite_poll_not_ok1(self):
        obsSite = ObsSite()

        response = ['+0585.2', '-011:35:00.0', '+48:07:00.0']

        with mock.patch('mountcontrol.obsSite.Connection') as mConn:
            mConn.return_value.communicate.return_value = False, response, 3
            suc = obsSite.getLocation()
            self.assertEqual(False, suc)

    def test_ObsSite_poll_not_ok2(self):
        obsSite = ObsSite()

        response = ['+0585.2', '-011:35:00.0', '+48:07:00.0']

        with mock.patch('mountcontrol.obsSite.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 6
            suc = obsSite.getLocation()
            self.assertEqual(False, suc)

    #
    #
    # testing pollSetting pointing
    #
    #

    def test_ObsSite_parseFast_ok1(self):
        obsSite = ObsSite()

        response = ['13:15:35.68', '0.12',
                    '19.44591,+88.0032,W,002.9803,+47.9945,2458352.10403639,5,0']
        suc = obsSite._parsePointing(response, 3)
        self.assertEqual(True, suc)

    def test_ObsSite_parseFast_ok2(self):
        obsSite = ObsSite()

        response = ['13:15:35.68', '0.12',
                    '19.44591,+88.0032,W,000.0000,+47.9945,2458352.10403639,5,0']
        suc = obsSite._parsePointing(response, 3)
        self.assertEqual(True, suc)
        self.assertEqual(type(obsSite.Az), skyfield.api.Angle)

    def test_ObsSite_parseFast_ok3(self):
        obsSite = ObsSite()

        response = ['13:15:35.68', '0.12',
                    '19.44591,+88.0032,W,000.0001,+00.0000,2458352.10403639,5,0']
        suc = obsSite._parsePointing(response, 3)
        self.assertEqual(True, suc)
        self.assertEqual(type(obsSite.Alt), skyfield.api.Angle)

    def test_ObsSite_pollFast_ok4(self):
        obsSite = ObsSite()

        response = ['13:15:35.68', '0.12',
                    '19.44591,+88.0032,W,002.9803,+47.9945,2458352.10403639,5,0']

        with mock.patch('mountcontrol.obsSite.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 3
            suc = obsSite.pollPointing()
            self.assertEqual(True, suc)

    def test_ObsSite_pollFast_not_ok1(self):
        obsSite = ObsSite()

        response = ['13:15:35.68', '0.12',
                    '19.44591,+88.0032,W,002.9803,+47.9945,2458352.10403639,5,0']

        with mock.patch('mountcontrol.obsSite.Connection') as mConn:
            mConn.return_value.communicate.return_value = False, response, 3
            suc = obsSite.pollPointing()
            self.assertEqual(False, suc)

    def test_ObsSite_pollFast_not_ok2(self):
        obsSite = ObsSite()

        response = ['13:15:35.68', '0.12',
                    '19.44591,+88.0032,W,002.9803,+47.9945,2458352.10403639,5,0']

        with mock.patch('mountcontrol.obsSite.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 6
            suc = obsSite.pollPointing()
            self.assertEqual(False, suc)

    #
    #
    # testing slewAltAz
    #
    #

    def test_ObsSite_slewAltAz_ok1(self):
        obsSite = ObsSite()
        response = ['11']
        with mock.patch('mountcontrol.obsSite.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 2
            alt = skyfield.api.Angle(degrees=30)
            az = skyfield.api.Angle(degrees=30)
            suc = obsSite.slewAltAz(alt, az)
            self.assertEqual(True, suc)

    def test_ObsSite_slewAltAz_not_ok1(self):
        obsSite = ObsSite()
        alt = 0
        az = 0
        suc = obsSite.slewAltAz(alt, az)
        self.assertEqual(False, suc)

    def test_ObsSite_slewAltAz_not_ok2(self):
        obsSite = ObsSite()
        alt = skyfield.api.Angle(degrees=30)
        az = 0
        suc = obsSite.slewAltAz(alt, az)
        self.assertEqual(False, suc)

    def test_ObsSite_slewAltAz_not_ok3(self):
        obsSite = ObsSite()
        alt = skyfield.api.Angle(degrees=30)
        az = skyfield.api.Angle(degrees=30)
        suc = obsSite.slewAltAz(alt, az)
        self.assertEqual(False, suc)

    def test_ObsSite_slewAltAz_not_ok4(self):
        obsSite = ObsSite()
        response = ['00']
        with mock.patch('mountcontrol.obsSite.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 2
            alt = skyfield.api.Angle(degrees=30)
            az = skyfield.api.Angle(degrees=30)
            suc = obsSite.slewAltAz(alt, az)
            self.assertEqual(False, suc)

    def test_ObsSite_slewAltAz_not_ok5(self):
        obsSite = ObsSite()
        response = ['0']
        with mock.patch('mountcontrol.obsSite.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 2
            alt = skyfield.api.Angle(degrees=30)
            az = skyfield.api.Angle(degrees=30)
            suc = obsSite.slewAltAz(alt, az)
            self.assertEqual(False, suc)

    def test_ObsSite_slewAltAz_not_ok6(self):
        obsSite = ObsSite()
        response = ['1#']
        with mock.patch('mountcontrol.obsSite.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 2
            alt = skyfield.api.Angle(degrees=30)
            az = skyfield.api.Angle(degrees=30)
            suc = obsSite.slewAltAz(alt, az)
            self.assertEqual(False, suc)

    def test_ObsSite_slewAltAz_not_ok7(self):
        obsSite = ObsSite()

        response = ['1#']
        with mock.patch('mountcontrol.obsSite.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 2
            alt = skyfield.api.Angle(degrees=30)
            az = skyfield.api.Angle(degrees=30)
            suc = obsSite.slewAltAz(alt, az, slewType='test')
            self.assertEqual(False, suc)

    def test_ObsSite_slewAltAz_not_ok8(self):
        obsSite = ObsSite()
        alt = skyfield.api.Angle(hours=5, preference='hours')
        az = skyfield.api.Angle(degrees=30)
        suc = obsSite.slewAltAz(alt, az)
        self.assertEqual(False, suc)

    def test_ObsSite_slewAltAz_not_ok9(self):
        obsSite = ObsSite()
        alt = skyfield.api.Angle(degrees=30)
        az = skyfield.api.Angle(hours=5, preference='hours')
        suc = obsSite.slewAltAz(alt, az)
        self.assertEqual(False, suc)

    #
    #
    # testing slewRaDec
    #
    #

    def test_ObsSite_slewRaDec_ok1(self):
        obsSite = ObsSite()
        response = ['11']
        with mock.patch('mountcontrol.obsSite.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 2
            ra = skyfield.api.Angle(hours=5, preference='hours')
            dec = skyfield.api.Angle(degrees=30)
            suc = obsSite.slewRaDec(ra, dec)
            self.assertEqual(True, suc)

    def test_ObsSite_slewRaDec_ok2(self):
        obsSite = ObsSite()
        response = ['11']
        with mock.patch('mountcontrol.obsSite.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 2
            ra = skyfield.api.Angle(hours=5, preference='hours')
            dec = skyfield.api.Angle(degrees=30)
            target = skyfield.starlib.Star(ra=ra, dec=dec)
            suc = obsSite.slewRaDec(target=target)
            self.assertEqual(True, suc)

    def test_ObsSite_slewRaDec_not_ok1(self):
        obsSite = ObsSite()
        ra = 0
        dec = 0
        suc = obsSite.slewRaDec(ra, dec)
        self.assertEqual(False, suc)

    def test_ObsSite_slewRaDec_not_ok2(self):
        obsSite = ObsSite()
        ra = None
        dec = None
        suc = obsSite.slewRaDec(ra, dec)
        self.assertEqual(False, suc)

    def test_ObsSite_slewRaDec_not_ok3(self):
        obsSite = ObsSite()
        ra = None
        dec = None
        target = None
        suc = obsSite.slewRaDec(ra, dec, target)
        self.assertEqual(False, suc)

    def test_ObsSite_slewRaDec_not_ok4(self):
        obsSite = ObsSite()
        ra = skyfield.api.Angle(hours=30, preference='hours')
        dec = None
        suc = obsSite.slewRaDec(ra, dec)
        self.assertEqual(False, suc)

    def test_ObsSite_slewRaDec_not_ok5(self):
        obsSite = ObsSite()

        ra = skyfield.api.Angle(hours=30, preference='hours')
        dec = skyfield.api.Angle(degrees=30)
        suc = obsSite.slewRaDec(ra, dec)
        self.assertEqual(False, suc)

    def test_ObsSite_slewRaDec_not_ok6(self):
        obsSite = ObsSite()

        response = ['00']
        with mock.patch('mountcontrol.obsSite.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 2
            ra = skyfield.api.Angle(hours=5, preference='hours')
            dec = skyfield.api.Angle(degrees=30)
            suc = obsSite.slewRaDec(ra, dec)
            self.assertEqual(False, suc)

    def test_ObsSite_slewRaDec_not_ok7(self):
        obsSite = ObsSite()

        response = ['0']
        with mock.patch('mountcontrol.obsSite.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 2
            ra = skyfield.api.Angle(hours=5, preference='hours')
            dec = skyfield.api.Angle(degrees=30)
            suc = obsSite.slewRaDec(ra, dec)
            self.assertEqual(False, suc)

    def test_ObsSite_slewRaDec_not_ok8(self):
        obsSite = ObsSite()

        response = ['1#']
        with mock.patch('mountcontrol.obsSite.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 2
            ra = skyfield.api.Angle(hours=5, preference='hours')
            dec = skyfield.api.Angle(degrees=30)
            suc = obsSite.slewRaDec(ra, dec)
            self.assertEqual(False, suc)

    def test_ObsSite_slewRaDec_not_ok9(self):
        obsSite = ObsSite()

        response = ['1#']
        with mock.patch('mountcontrol.obsSite.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 2
            ra = skyfield.api.Angle(hours=5, preference='hours')
            dec = skyfield.api.Angle(degrees=30)
            suc = obsSite.slewRaDec(ra, dec, slewType='test')
            self.assertEqual(False, suc)

    def test_ObsSite_slewRaDec_not_ok10(self):
        obsSite = ObsSite()
        ra = skyfield.api.Angle(degrees=30)
        dec = skyfield.api.Angle(degrees=30)
        suc = obsSite.slewRaDec(ra, dec)
        self.assertEqual(False, suc)

    def test_ObsSite_slewRaDec_not_ok11(self):
        obsSite = ObsSite()
        ra = skyfield.api.Angle(degrees=30)
        dec = skyfield.api.Angle(hours=5, preference='hours')
        suc = obsSite.slewRaDec(ra, dec)
        self.assertEqual(False, suc)

    #
    #
    # testing shutdown
    #
    #

    def test_ObsSite_shutdown_ok(self):
        obsSite = ObsSite()

        response = ['1']
        with mock.patch('mountcontrol.obsSite.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 1
            suc = obsSite.shutdown()
            self.assertEqual(True, suc)

    def test_ObsSite_shutdown_not_ok1(self):
        obsSite = ObsSite()

        response = ['0']
        with mock.patch('mountcontrol.obsSite.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 1
            suc = obsSite.shutdown()
            self.assertEqual(False, suc)

    def test_ObsSite_shutdown_not_ok2(self):
        obsSite = ObsSite()

        response = ['0']
        with mock.patch('mountcontrol.obsSite.Connection') as mConn:
            mConn.return_value.communicate.return_value = False, response, 1
            suc = obsSite.shutdown()
            self.assertEqual(False, suc)

    #
    #
    # testing setSite
    #
    #

    def test_ObsSite_setLocation_ok(self):
        obsSite = ObsSite()
        observer = skyfield.api.Topos(latitude_degrees=50,
                                      longitude_degrees=11,
                                      elevation_m=580)
        response = ['111']
        with mock.patch('mountcontrol.obsSite.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 1
            suc = obsSite.setLocation(observer)
            self.assertEqual(True, suc)

    def test_ObsSite_setLocation_not_ok1(self):
        obsSite = ObsSite()
        observer = skyfield.api.Topos(latitude_degrees=50,
                                      longitude_degrees=11,
                                      elevation_m=580)
        response = ['101']
        with mock.patch('mountcontrol.obsSite.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 1
            suc = obsSite.setLocation(observer)
            self.assertEqual(False, suc)

    def test_ObsSite_setLocation_not_ok2(self):
        obsSite = ObsSite()

        observer = skyfield.api.Topos(latitude_degrees=50,
                                      longitude_degrees=11,
                                      elevation_m=580)
        response = ['111']
        with mock.patch('mountcontrol.obsSite.Connection') as mConn:
            mConn.return_value.communicate.return_value = False, response, 1
            suc = obsSite.setLocation(observer)
            self.assertEqual(False, suc)

    def test_ObsSite_setLocation_not_ok3(self):
        obsSite = ObsSite()
        response = ['111']
        with mock.patch('mountcontrol.obsSite.Connection') as mConn:
            mConn.return_value.communicate.return_value = False, response, 1
            suc = obsSite.setLocation(1234)
            self.assertEqual(False, suc)

    def test_ObsSite_setLatitude_ok1(self):
        obsSite = ObsSite()
        response = ['1']
        with mock.patch('mountcontrol.obsSite.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 1
            suc = obsSite.setLatitude(lat_degrees=50)
            self.assertEqual(True, suc)

    def test_ObsSite_setLatitude_not_ok1(self):
        obsSite = ObsSite()
        response = ['1']
        with mock.patch('mountcontrol.obsSite.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 1
            suc = obsSite.setLatitude(lat_degrees='50')
            self.assertEqual(False, suc)

    def test_ObsSite_setLatitude_not_ok2(self):
        obsSite = ObsSite()
        response = ['1']
        with mock.patch('mountcontrol.obsSite.Connection') as mConn:
            mConn.return_value.communicate.return_value = False, response, 1
            suc = obsSite.setLatitude(lat_degrees=50)
            self.assertEqual(False, suc)

    def test_ObsSite_setLatitude_not_ok3(self):
        obsSite = ObsSite()
        response = ['0']
        with mock.patch('mountcontrol.obsSite.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 1
            suc = obsSite.setLatitude(lat_degrees=50)
            self.assertEqual(False, suc)

    def test_ObsSite_setLongitude_ok1(self):
        obsSite = ObsSite()
        response = ['1']
        with mock.patch('mountcontrol.obsSite.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 1
            suc = obsSite.setLongitude(lon_degrees=50)
            self.assertEqual(True, suc)

    def test_ObsSite_setLongitude_not_ok1(self):
        obsSite = ObsSite()
        response = ['1']
        with mock.patch('mountcontrol.obsSite.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 1
            suc = obsSite.setLongitude(lon_degrees='50')
            self.assertEqual(False, suc)

    def test_ObsSite_setLongitude_not_ok2(self):
        obsSite = ObsSite()
        response = ['1']
        with mock.patch('mountcontrol.obsSite.Connection') as mConn:
            mConn.return_value.communicate.return_value = False, response, 1
            suc = obsSite.setLongitude(lon_degrees=50)
            self.assertEqual(False, suc)

    def test_ObsSite_setLongitude_not_ok3(self):
        obsSite = ObsSite()

        response = ['0']
        with mock.patch('mountcontrol.obsSite.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 1
            suc = obsSite.setLongitude(lon_degrees=50)
            self.assertEqual(False, suc)

    def test_ObsSite_setElevation_ok1(self):
        obsSite = ObsSite()

        response = ['1']
        with mock.patch('mountcontrol.obsSite.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 1
            suc = obsSite.setElevation('500')
            self.assertEqual(True, suc)

    def test_ObsSite_setElevation_not_ok1(self):
        obsSite = ObsSite()

        response = ['1']
        with mock.patch('mountcontrol.obsSite.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 1
            suc = obsSite.setElevation('er')
            self.assertEqual(False, suc)

    def test_ObsSite_setElevation_not_ok2(self):
        obsSite = ObsSite()

        response = ['1']
        with mock.patch('mountcontrol.obsSite.Connection') as mConn:
            mConn.return_value.communicate.return_value = False, response, 1
            suc = obsSite.setElevation('500')
            self.assertEqual(False, suc)

    def test_ObsSite_setElevation_not_ok3(self):
        obsSite = ObsSite()

        response = ['0']
        with mock.patch('mountcontrol.obsSite.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 1
            suc = obsSite.setElevation('500')
            self.assertEqual(False, suc)

    #
    #
    # testing setSlewRate
    #
    #

    def test_ObsSite_setSlewRate_ok(self):
        obsSite = ObsSite()

        response = ['1']
        with mock.patch('mountcontrol.obsSite.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 1
            suc = obsSite.setSlewRate(5)
            self.assertEqual(True, suc)

    def test_ObsSite_setSlewRate_not_ok1(self):
        obsSite = ObsSite()

        response = ['0']
        with mock.patch('mountcontrol.obsSite.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 1
            suc = obsSite.setSlewRate(5)
            self.assertEqual(False, suc)

    def test_ObsSite_setSlewRate_not_ok2(self):
        obsSite = ObsSite()

        response = ['1']
        with mock.patch('mountcontrol.obsSite.Connection') as mConn:
            mConn.return_value.communicate.return_value = False, response, 1
            suc = obsSite.setSlewRate(5)
            self.assertEqual(False, suc)

    def test_ObsSite_setSlewRate_not_ok3(self):
        obsSite = ObsSite()

        response = ['1']
        with mock.patch('mountcontrol.obsSite.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 1
            suc = obsSite.setSlewRate(0)
            self.assertEqual(False, suc)

    def test_ObsSite_setSlewRate_not_ok4(self):
        obsSite = ObsSite()

        response = ['1']
        with mock.patch('mountcontrol.obsSite.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 1
            suc = obsSite.setSlewRate(25)
            self.assertEqual(False, suc)

    #
    #
    # testing setRefractionParam
    #
    #

    def test_ObsSite_setRefractionParam_ok(self):
        obsSite = ObsSite()

        response = ['11']
        with mock.patch('mountcontrol.obsSite.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 2
            suc = obsSite.setRefractionParam(temperature=5,
                                             pressure=800)
            self.assertEqual(True, suc)

    def test_ObsSite_setRefractionParam_not_ok1(self):
        obsSite = ObsSite()

        response = ['01']
        with mock.patch('mountcontrol.obsSite.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 2
            suc = obsSite.setRefractionParam(temperature=5,
                                             pressure=800)
            self.assertEqual(False, suc)

    def test_ObsSite_setRefractionParam_not_ok2(self):
        obsSite = ObsSite()

        response = ['10']
        with mock.patch('mountcontrol.obsSite.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 2
            suc = obsSite.setRefractionParam(temperature=5,
                                             pressure=800)
            self.assertEqual(False, suc)

    def test_ObsSite_setRefractionParam_not_ok3(self):
        obsSite = ObsSite()

        response = ['11']
        with mock.patch('mountcontrol.obsSite.Connection') as mConn:
            mConn.return_value.communicate.return_value = False, response, 2
            suc = obsSite.setRefractionParam(temperature=5,
                                             pressure=800)
            self.assertEqual(False, suc)

    def test_ObsSite_setRefractionParam_not_ok4(self):
        obsSite = ObsSite()

        response = ['11']
        with mock.patch('mountcontrol.obsSite.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 2
            suc = obsSite.setRefractionParam(temperature=-45,
                                             pressure=800)
            self.assertEqual(False, suc)

    def test_ObsSite_setRefractionParam_not_ok5(self):
        obsSite = ObsSite()

        response = ['11']
        with mock.patch('mountcontrol.obsSite.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 2
            suc = obsSite.setRefractionParam(temperature=85,
                                             pressure=800)
            self.assertEqual(False, suc)

    def test_ObsSite_setRefractionParam_not_ok6(self):
        obsSite = ObsSite()

        response = ['11']
        with mock.patch('mountcontrol.obsSite.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 2
            suc = obsSite.setRefractionParam(temperature=5,
                                             pressure=300)
            self.assertEqual(False, suc)

    def test_ObsSite_setRefractionParam_not_ok7(self):
        obsSite = ObsSite()

        response = ['11']
        with mock.patch('mountcontrol.obsSite.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 2
            suc = obsSite.setRefractionParam(temperature=5,
                                             pressure=1500)
            self.assertEqual(False, suc)

    #
    #
    # testing setRefractionTemp
    #
    #

    def test_ObsSite_setRefractionTemp_ok(self):
        obsSite = ObsSite()

        response = ['1']
        with mock.patch('mountcontrol.obsSite.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 1
            suc = obsSite.setRefractionTemp(5)
            self.assertEqual(True, suc)

    def test_ObsSite_setRefractionTemp_not_ok1(self):
        obsSite = ObsSite()

        response = ['0']
        with mock.patch('mountcontrol.obsSite.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 1
            suc = obsSite.setRefractionTemp(5)
            self.assertEqual(False, suc)

    def test_ObsSite_setRefractionTemp_not_ok2(self):
        obsSite = ObsSite()

        response = ['1']
        with mock.patch('mountcontrol.obsSite.Connection') as mConn:
            mConn.return_value.communicate.return_value = False, response, 1
            suc = obsSite.setRefractionTemp(5)
            self.assertEqual(False, suc)

    def test_ObsSite_setRefractionTemp_not_ok3(self):
        obsSite = ObsSite()

        response = ['1']
        with mock.patch('mountcontrol.obsSite.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 1
            suc = obsSite.setRefractionTemp(-45)
            self.assertEqual(False, suc)

    def test_ObsSite_setRefractionTemp_not_ok4(self):
        obsSite = ObsSite()

        response = ['1']
        with mock.patch('mountcontrol.obsSite.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 1
            suc = obsSite.setRefractionTemp(85)
            self.assertEqual(False, suc)

    def test_ObsSite_setRefractionTemp_not_ok5(self):
        obsSite = ObsSite()

        response = ['1']
        with mock.patch('mountcontrol.obsSite.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 1
            suc = obsSite.setRefractionTemp(-0)
            self.assertEqual(True, suc)

    #
    #
    # testing setRefractionPress
    #
    #

    def test_ObsSite_setRefractionPress_ok(self):
        obsSite = ObsSite()

        response = ['1']
        with mock.patch('mountcontrol.obsSite.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 1
            suc = obsSite.setRefractionPress(1000)
            self.assertEqual(True, suc)

    def test_ObsSite_setRefractionPress_not_ok1(self):
        obsSite = ObsSite()

        response = ['0']
        with mock.patch('mountcontrol.obsSite.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 1
            suc = obsSite.setRefractionPress(1000)
            self.assertEqual(False, suc)

    def test_ObsSite_setRefractionPress_not_ok2(self):
        obsSite = ObsSite()

        response = ['1']
        with mock.patch('mountcontrol.obsSite.Connection') as mConn:
            mConn.return_value.communicate.return_value = False, response, 1
            suc = obsSite.setRefractionPress(1000)
            self.assertEqual(False, suc)

    def test_ObsSite_setRefractionPress_not_ok3(self):
        obsSite = ObsSite()

        response = ['1']
        with mock.patch('mountcontrol.obsSite.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 1
            suc = obsSite.setRefractionPress(450)
            self.assertEqual(False, suc)

    def test_ObsSite_setRefractionPress_not_ok4(self):
        obsSite = ObsSite()

        response = ['1']
        with mock.patch('mountcontrol.obsSite.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 1
            suc = obsSite.setRefractionPress(1400)
            self.assertEqual(False, suc)

    #
    #
    # testing setRefraction
    #
    #

    def test_ObsSite_setRefraction_ok(self):
        obsSite = ObsSite()

        response = ['1']
        with mock.patch('mountcontrol.obsSite.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 1
            suc = obsSite.setRefraction(1)
            self.assertEqual(True, suc)

    def test_ObsSite_setRefraction_not_ok1(self):
        obsSite = ObsSite()

        response = ['0']
        with mock.patch('mountcontrol.obsSite.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 1
            suc = obsSite.setRefraction(1)
            self.assertEqual(False, suc)

    def test_ObsSite_setRefraction_not_ok2(self):
        obsSite = ObsSite()

        response = ['1']
        with mock.patch('mountcontrol.obsSite.Connection') as mConn:
            mConn.return_value.communicate.return_value = False, response, 1
            suc = obsSite.setRefraction(1)
            self.assertEqual(False, suc)

    #
    #
    # testing setUnattendedFlip
    #
    #

    def test_ObsSite_setUnattendedFlip_ok(self):
        obsSite = ObsSite()

        response = ['1']
        with mock.patch('mountcontrol.obsSite.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 1
            suc = obsSite.setUnattendedFlip(1)
            self.assertEqual(True, suc)

    def test_ObsSite_setUnattendedFlip_not_ok1(self):
        obsSite = ObsSite()

        response = []
        with mock.patch('mountcontrol.obsSite.Connection') as mConn:
            mConn.return_value.communicate.return_value = False, response, 0
            suc = obsSite.setUnattendedFlip(1)
            self.assertEqual(False, suc)

    #
    #
    # testing setDualAxisTracking
    #
    #

    def test_ObsSite_setDualAxisTracking_ok(self):
        obsSite = ObsSite()

        response = ['1']
        with mock.patch('mountcontrol.obsSite.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 1
            suc = obsSite.setDualAxisTracking(1)
            self.assertEqual(True, suc)

    def test_ObsSite_setDualAxisTracking_not_ok1(self):
        obsSite = ObsSite()

        response = ['0']
        with mock.patch('mountcontrol.obsSite.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 1
            suc = obsSite.setDualAxisTracking(1)
            self.assertEqual(False, suc)

    def test_ObsSite_setDualAxisTracking_not_ok2(self):
        obsSite = ObsSite()

        response = ['1']
        with mock.patch('mountcontrol.obsSite.Connection') as mConn:
            mConn.return_value.communicate.return_value = False, response, 1
            suc = obsSite.setDualAxisTracking(1)
            self.assertEqual(False, suc)

    #
    #
    # testing setMeridianLimitTrack
    #
    #

    def test_ObsSite_setMeridianLimitTrack_ok(self):
        obsSite = ObsSite()

        response = ['1']
        with mock.patch('mountcontrol.obsSite.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 1
            suc = obsSite.setMeridianLimitTrack(0)
            self.assertEqual(True, suc)

    def test_ObsSite_setMeridianLimitTrack_not_ok1(self):
        obsSite = ObsSite()

        response = ['0']
        with mock.patch('mountcontrol.obsSite.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 1
            suc = obsSite.setMeridianLimitTrack(0)
            self.assertEqual(False, suc)

    def test_ObsSite_setMeridianLimitTrack_not_ok2(self):
        obsSite = ObsSite()

        response = ['1']
        with mock.patch('mountcontrol.obsSite.Connection') as mConn:
            mConn.return_value.communicate.return_value = False, response, 1
            suc = obsSite.setMeridianLimitTrack(0)
            self.assertEqual(False, suc)

    def test_ObsSite_setMeridianLimitTrack_not_ok3(self):
        obsSite = ObsSite()

        response = ['1']
        with mock.patch('mountcontrol.obsSite.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 1
            suc = obsSite.setMeridianLimitTrack(30)
            self.assertEqual(False, suc)

    def test_ObsSite_setMeridianLimitTrack_not_ok4(self):
        obsSite = ObsSite()

        response = ['1']
        with mock.patch('mountcontrol.obsSite.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 1
            suc = obsSite.setMeridianLimitTrack(-30)
            self.assertEqual(False, suc)

    #
    #
    # testing setMeridianLimitSlew
    #
    #

    def test_ObsSite_setMeridianLimitSlew_ok(self):
        obsSite = ObsSite()

        response = ['1']
        with mock.patch('mountcontrol.obsSite.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 1
            suc = obsSite.setMeridianLimitSlew(0)
            self.assertEqual(True, suc)

    def test_ObsSite_setMeridianLimitSlew_not_ok1(self):
        obsSite = ObsSite()

        response = ['0']
        with mock.patch('mountcontrol.obsSite.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 1
            suc = obsSite.setMeridianLimitSlew(0)
            self.assertEqual(False, suc)

    def test_ObsSite_setMeridianLimitSlew_not_ok2(self):
        obsSite = ObsSite()

        response = ['1']
        with mock.patch('mountcontrol.obsSite.Connection') as mConn:
            mConn.return_value.communicate.return_value = False, response, 1
            suc = obsSite.setMeridianLimitSlew(0)
            self.assertEqual(False, suc)

    def test_ObsSite_setMeridianLimitSlew_not_ok3(self):
        obsSite = ObsSite()

        response = ['1']
        with mock.patch('mountcontrol.obsSite.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 1
            suc = obsSite.setMeridianLimitSlew(30)
            self.assertEqual(False, suc)

    def test_ObsSite_setMeridianLimitSlew_not_ok4(self):
        obsSite = ObsSite()

        response = ['1']
        with mock.patch('mountcontrol.obsSite.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 1
            suc = obsSite.setMeridianLimitSlew(-30)
            self.assertEqual(False, suc)

    #
    #
    # testing setHorizonLimitLow
    #
    #

    def test_ObsSite_setHorizonLimitLow_ok(self):
        obsSite = ObsSite()

        response = ['1']
        with mock.patch('mountcontrol.obsSite.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 1
            suc = obsSite.setHorizonLimitLow(0)
            self.assertEqual(True, suc)

    def test_ObsSite_setHorizonLimitLow_not_ok1(self):
        obsSite = ObsSite()

        response = ['0']
        with mock.patch('mountcontrol.obsSite.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 1
            suc = obsSite.setHorizonLimitLow(0)
            self.assertEqual(False, suc)

    def test_ObsSite_setHorizonLimitLow_not_ok2(self):
        obsSite = ObsSite()

        response = ['1']
        with mock.patch('mountcontrol.obsSite.Connection') as mConn:
            mConn.return_value.communicate.return_value = False, response, 1
            suc = obsSite.setHorizonLimitLow(0)
            self.assertEqual(False, suc)

    def test_ObsSite_setHorizonLimitLow_not_ok3(self):
        obsSite = ObsSite()

        response = ['1']
        with mock.patch('mountcontrol.obsSite.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 1
            suc = obsSite.setHorizonLimitLow(-30)
            self.assertEqual(False, suc)

    def test_ObsSite_setHorizonLimitLow_not_ok4(self):
        obsSite = ObsSite()

        response = ['1']
        with mock.patch('mountcontrol.obsSite.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 1
            suc = obsSite.setHorizonLimitLow(50)
            self.assertEqual(False, suc)

    #
    #
    # testing setHorizonLimitLow
    #
    #

    def test_ObsSite_setHorizonLimitHigh_ok(self):
        obsSite = ObsSite()

        response = ['1']
        with mock.patch('mountcontrol.obsSite.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 1
            suc = obsSite.setHorizonLimitHigh(80)
            self.assertEqual(True, suc)

    def test_ObsSite_setHorizonLimitHigh_not_ok1(self):
        obsSite = ObsSite()

        response = ['0']
        with mock.patch('mountcontrol.obsSite.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 1
            suc = obsSite.setHorizonLimitHigh(80)
            self.assertEqual(False, suc)

    def test_ObsSite_setHorizonLimitHigh_not_ok2(self):
        obsSite = ObsSite()

        response = ['1']
        with mock.patch('mountcontrol.obsSite.Connection') as mConn:
            mConn.return_value.communicate.return_value = False, response, 1
            suc = obsSite.setHorizonLimitHigh(80)
            self.assertEqual(False, suc)

    def test_ObsSite_setHorizonLimitHigh_not_ok3(self):
        obsSite = ObsSite()

        response = ['1']
        with mock.patch('mountcontrol.obsSite.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 1
            suc = obsSite.setHorizonLimitHigh(-1)
            self.assertEqual(False, suc)

    def test_ObsSite_setHorizonLimitHigh_not_ok4(self):
        obsSite = ObsSite()

        response = ['1']
        with mock.patch('mountcontrol.obsSite.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 1
            suc = obsSite.setHorizonLimitHigh(100)
            self.assertEqual(False, suc)

    #
    #
    # testing startTracking
    #
    #

    def test_ObsSite_startTracking_ok(self):
        obsSite = ObsSite()

        response = []
        with mock.patch('mountcontrol.obsSite.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 0
            suc = obsSite.startTracking()
            self.assertEqual(True, suc)

    def test_ObsSite_startTracking_not_ok1(self):
        obsSite = ObsSite()

        response = []
        with mock.patch('mountcontrol.obsSite.Connection') as mConn:
            mConn.return_value.communicate.return_value = False, response, 0
            suc = obsSite.startTracking()
            self.assertEqual(False, suc)

    #
    #
    # testing stopTracking
    #
    #

    def test_ObsSite_stopTracking_ok(self):
        obsSite = ObsSite()

        response = []
        with mock.patch('mountcontrol.obsSite.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 0
            suc = obsSite.stopTracking()
            self.assertEqual(True, suc)

    def test_ObsSite_stopTracking_not_ok1(self):
        obsSite = ObsSite()

        response = []
        with mock.patch('mountcontrol.obsSite.Connection') as mConn:
            mConn.return_value.communicate.return_value = False, response, 0
            suc = obsSite.stopTracking()
            self.assertEqual(False, suc)

    #
    #
    # testing setLunarTracking
    #
    #

    def test_ObsSite_setLunarTracking_ok(self):
        obsSite = ObsSite()

        response = []
        with mock.patch('mountcontrol.obsSite.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 0
            suc = obsSite.setLunarTracking()
            self.assertEqual(True, suc)

    def test_ObsSite_setLunarTracking_not_ok1(self):
        obsSite = ObsSite()

        response = []
        with mock.patch('mountcontrol.obsSite.Connection') as mConn:
            mConn.return_value.communicate.return_value = False, response, 0
            suc = obsSite.setLunarTracking()
            self.assertEqual(False, suc)

    #
    #
    # testing setSiderealTracking
    #
    #

    def test_ObsSite_setSiderealTracking_ok(self):
        obsSite = ObsSite()

        response = []
        with mock.patch('mountcontrol.obsSite.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 0
            suc = obsSite.setSiderealTracking()
            self.assertEqual(True, suc)

    def test_ObsSite_setSiderealTracking_not_ok1(self):
        obsSite = ObsSite()

        response = []
        with mock.patch('mountcontrol.obsSite.Connection') as mConn:
            mConn.return_value.communicate.return_value = False, response, 0
            suc = obsSite.setSiderealTracking()
            self.assertEqual(False, suc)

    #
    #
    # testing setSolarTracking
    #
    #

    def test_ObsSite_setSolarTracking_ok(self):
        obsSite = ObsSite()

        response = []
        with mock.patch('mountcontrol.obsSite.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 0
            suc = obsSite.setSolarTracking()
            self.assertEqual(True, suc)

    def test_ObsSite_setSolarTracking_not_ok1(self):
        obsSite = ObsSite()

        response = []
        with mock.patch('mountcontrol.obsSite.Connection') as mConn:
            mConn.return_value.communicate.return_value = False, response, 0
            suc = obsSite.setSolarTracking()
            self.assertEqual(False, suc)

    #
    #
    # testing park
    #
    #

    def test_ObsSite_park_ok(self):
        obsSite = ObsSite()

        response = []
        with mock.patch('mountcontrol.obsSite.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 0
            suc = obsSite.park()
            self.assertEqual(True, suc)

    def test_ObsSite_park_not_ok1(self):
        obsSite = ObsSite()

        response = []
        with mock.patch('mountcontrol.obsSite.Connection') as mConn:
            mConn.return_value.communicate.return_value = False, response, 0
            suc = obsSite.park()
            self.assertEqual(False, suc)

    #
    #
    # testing unpark
    #
    #

    def test_ObsSite_unpark_ok(self):
        obsSite = ObsSite()

        response = []
        with mock.patch('mountcontrol.obsSite.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 0
            suc = obsSite.unpark()
            self.assertEqual(True, suc)

    def test_ObsSite_unpark_not_ok1(self):
        obsSite = ObsSite()

        response = []
        with mock.patch('mountcontrol.obsSite.Connection') as mConn:
            mConn.return_value.communicate.return_value = False, response, 0
            suc = obsSite.unpark()
            self.assertEqual(False, suc)

    #
    #
    # testing stop
    #
    #

    def test_ObsSite_stop_ok(self):
        obsSite = ObsSite()

        response = []
        with mock.patch('mountcontrol.obsSite.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 0
            suc = obsSite.stop()
            self.assertEqual(True, suc)

    def test_ObsSite_stop_not_ok1(self):
        obsSite = ObsSite()

        response = []
        with mock.patch('mountcontrol.obsSite.Connection') as mConn:
            mConn.return_value.communicate.return_value = False, response, 0
            suc = obsSite.stop()
            self.assertEqual(False, suc)

    #
    #
    # testing flip
    #
    #

    def test_ObsSite_flip_ok(self):
        obsSite = ObsSite()

        response = ['1']
        with mock.patch('mountcontrol.obsSite.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 1
            suc = obsSite.flip()
            self.assertEqual(True, suc)

    def test_ObsSite_flip_not_ok1(self):
        obsSite = ObsSite()

        response = ['0']
        with mock.patch('mountcontrol.obsSite.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 1
            suc = obsSite.flip()
            self.assertEqual(False, suc)

    def test_ObsSite_flip_not_ok2(self):
        obsSite = ObsSite()

        response = ['1']
        with mock.patch('mountcontrol.obsSite.Connection') as mConn:
            mConn.return_value.communicate.return_value = False, response, 1
            suc = obsSite.flip()
            self.assertEqual(False, suc)
