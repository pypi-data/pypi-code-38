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
import mount


class IntegrationTests(unittest.TestCase):

    host = ('192.168.2.15', 3492)

    def setUp(self):
        pass
    #
    #
    # testing firmware
    #
    #

    def test_workaroundAlign(self):
        model = mount.Mount(host=self.host).model
        ok = model.workaroundAlign()
        self.assertEqual(True, ok)

    def test_poll(self):
        fw = mount.Mount(host=self.host).fw
        ok = fw.poll()
        self.assertEqual(True, ok)
        self.assertEqual(21514, fw.number())
        self.assertEqual('2.15.14', fw.numberString)
        self.assertEqual('10micron GM1000HPS', fw.productName)
        self.assertEqual('Q-TYPE2012', fw.hwVersion)
        self.assertEqual('Mar 19 2018', fw.fwdate)
        self.assertEqual('15:56:53', fw.fwtime)

    def test_pollStars(self):
        model = mount.Mount(host=self.host).model
        suc = model.pollStars()
        self.assertEqual(True, suc)

    def test_pollSetting(self):
        sett = mount.Mount(host=self.host).sett
        suc = sett.pollSetting()
        self.assertEqual(True, suc)

    #
    #
    # testing obsSite
    #
    #

    def test_startTracking(self):
        obsSite = mount.Mount(host=self.host).obsSite
        suc = obsSite.startTracking()
        self.assertEqual(True, suc)

    def test_stopTracking(self):
        obsSite = mount.Mount(host=self.host).obsSite
        suc = obsSite.stopTracking()
        self.assertEqual(True, suc)

    def test_setSlewRate1(self):
        obsSite = mount.Mount(host=self.host).obsSite
        suc = obsSite.setSlewRate(1)
        self.assertEqual(False, suc)

    def test_setSlewRate2(self):
        obsSite = mount.Mount(host=self.host).obsSite
        suc = obsSite.setSlewRate(2)
        self.assertEqual(True, suc)

    def test_setSlewRate10(self):
        obsSite = mount.Mount(host=self.host).obsSite
        suc = obsSite.setSlewRate(10)
        self.assertEqual(True, suc)

    def test_setSlewRate15(self):
        obsSite = mount.Mount(host=self.host).obsSite
        suc = obsSite.setSlewRate(15)
        self.assertEqual(True, suc)

    def test_setSlewRate20(self):
        obsSite = mount.Mount(host=self.host).obsSite
        suc = obsSite.setSlewRate(20)
        self.assertEqual(False, suc)

    def test_setRefractionTemp_m50(self):
        obsSite = mount.Mount(host=self.host).obsSite
        suc = obsSite.setRefractionTemp(-50)
        self.assertEqual(False, suc)

    def test_setRefractionTemp_m25(self):
        obsSite = mount.Mount(host=self.host).obsSite
        suc = obsSite.setRefractionTemp(-25)
        self.assertEqual(True, suc)

    def test_setRefractionTemp_0(self):
        obsSite = mount.Mount(host=self.host).obsSite
        suc = obsSite.setRefractionTemp(-0)
        self.assertEqual(True, suc)

    def test_setRefractionTemp_50(self):
        obsSite = mount.Mount(host=self.host).obsSite
        suc = obsSite.setRefractionTemp(50)
        self.assertEqual(True, suc)

    def test_setRefractionTemp_75(self):
        obsSite = mount.Mount(host=self.host).obsSite
        suc = obsSite.setRefractionTemp(75)
        self.assertEqual(True, suc)

    def test_setRefractionTemp_100(self):
        obsSite = mount.Mount(host=self.host).obsSite
        suc = obsSite.setRefractionTemp(100)
        self.assertEqual(False, suc)

    def test_setRefractionPress_800(self):
        obsSite = mount.Mount(host=self.host).obsSite
        suc = obsSite.setRefractionPress(800)
        self.assertEqual(True, suc)

    def test_setRefractionPress_900(self):
        obsSite = mount.Mount(host=self.host).obsSite
        suc = obsSite.setRefractionPress(900)
        self.assertEqual(True, suc)

    def test_setRefractionPress_1000(self):
        obsSite = mount.Mount(host=self.host).obsSite
        suc = obsSite.setRefractionPress(1000)
        self.assertEqual(True, suc)

    def test_setRefractionPress_500(self):
        obsSite = mount.Mount(host=self.host).obsSite
        suc = obsSite.setRefractionPress(500)
        self.assertEqual(True, suc)

    def test_setRefractionPress_200(self):
        obsSite = mount.Mount(host=self.host).obsSite
        suc = obsSite.setRefractionPress(200)
        self.assertEqual(False, suc)

    def test_setRefractionPress_1400(self):
        obsSite = mount.Mount(host=self.host).obsSite
        suc = obsSite.setRefractionPress(1400)
        self.assertEqual(False, suc)

    def test_setRefractionOn(self):
        obsSite = mount.Mount(host=self.host).obsSite
        suc = obsSite.setRefraction(True)
        self.assertEqual(True, suc)

    def test_setRefractionOff(self):
        obsSite = mount.Mount(host=self.host).obsSite
        suc = obsSite.setRefraction(False)
        self.assertEqual(True, suc)

    def test_setUnattendedFlipOn(self):
        obsSite = mount.Mount(host=self.host).obsSite
        suc = obsSite.setUnattendedFlip(True)
        self.assertEqual(True, suc)

    def test_setUnattendedFlipOff(self):
        obsSite = mount.Mount(host=self.host).obsSite
        suc = obsSite.setUnattendedFlip(False)
        self.assertEqual(True, suc)

    def test_setDualAxisTrackingOn(self):
        obsSite = mount.Mount(host=self.host).obsSite
        suc = obsSite.setDualAxisTracking(True)
        self.assertEqual(True, suc)

    def test_setDualAxisTrackingOff(self):
        obsSite = mount.Mount(host=self.host).obsSite
        suc = obsSite.setDualAxisTracking(False)
        self.assertEqual(True, suc)

    def test_setMeridianLimitSlew_m10(self):
        obsSite = mount.Mount(host=self.host).obsSite
        suc = obsSite.setMeridianLimitSlew(-10)
        self.assertEqual(False, suc)

    def test_setMeridianLimitSlew_10(self):
        obsSite = mount.Mount(host=self.host).obsSite
        suc = obsSite.setMeridianLimitSlew(10)
        self.assertEqual(True, suc)

    def test_setMeridianLimitSlew_30(self):
        obsSite = mount.Mount(host=self.host).obsSite
        suc = obsSite.setMeridianLimitSlew(30)
        self.assertEqual(False, suc)

    def test_setMeridianLimitSlew_50(self):
        obsSite = mount.Mount(host=self.host).obsSite
        suc = obsSite.setMeridianLimitSlew(50)
        self.assertEqual(False, suc)

    def test_setMeridianLimitTrack_10(self):
        obsSite = mount.Mount(host=self.host).obsSite
        suc = obsSite.setMeridianLimitTrack(10)
        self.assertEqual(True, suc)

    def test_setMeridianLimitTrack_30(self):
        obsSite = mount.Mount(host=self.host).obsSite
        suc = obsSite.setMeridianLimitTrack(30)
        self.assertEqual(False, suc)

    def test_setMeridianLimitCombinedOK(self):
        obsSite = mount.Mount(host=self.host).obsSite
        suc = obsSite.setMeridianLimitSlew(10)
        self.assertEqual(True, suc)
        suc = obsSite.setMeridianLimitTrack(15)
        self.assertEqual(True, suc)
        suc = obsSite.setMeridianLimitTrack(5)
        self.assertEqual(False, suc)

    def test_setHorizonLimitLow_m10(self):
        obsSite = mount.Mount(host=self.host).obsSite
        suc = obsSite.setHorizonLimitLow(-10)
        self.assertEqual(False, suc)

    def test_setHorizonLimitLow11(self):
        obsSite = mount.Mount(host=self.host).obsSite
        suc = obsSite.setHorizonLimitLow(11)
        self.assertEqual(True, suc)

    def test_setHorizonLimitLow34(self):
        obsSite = mount.Mount(host=self.host).obsSite
        suc = obsSite.setHorizonLimitLow(34)
        self.assertEqual(True, suc)

    def test_setHorizonLimitLow50(self):
        obsSite = mount.Mount(host=self.host).obsSite
        suc = obsSite.setHorizonLimitLow(50)
        self.assertEqual(False, suc)

    def test_setHorizonLimitHigh_m30(self):
        obsSite = mount.Mount(host=self.host).obsSite
        suc = obsSite.setHorizonLimitHigh(-30)
        self.assertEqual(False, suc)

    def test_setHorizonLimitHigh_m15(self):
        obsSite = mount.Mount(host=self.host).obsSite
        suc = obsSite.setHorizonLimitHigh(-15)
        self.assertEqual(False, suc)

    def test_setHorizonLimitHigh_m5(self):
        obsSite = mount.Mount(host=self.host).obsSite
        suc = obsSite.setHorizonLimitHigh(-5)
        self.assertEqual(False, suc)

    def test_setHorizonLimitHigh_45(self):
        obsSite = mount.Mount(host=self.host).obsSite
        suc = obsSite.setHorizonLimitHigh(45)
        self.assertEqual(True, suc)

    def test_setHorizonLimitHigh_90(self):
        obsSite = mount.Mount(host=self.host).obsSite
        suc = obsSite.setHorizonLimitHigh(90)
        self.assertEqual(True, suc)

    def test_setHorizonLimitHigh_91(self):
        obsSite = mount.Mount(host=self.host).obsSite
        suc = obsSite.setHorizonLimitHigh(91)
        self.assertEqual(False, suc)

    #
    #
    # testing model
    #
    #

    def test_storeName(self):
        model = mount.Mount(host=self.host).model
        suc = model.storeName('Test_Store')
        self.assertEqual(True, suc)

    def test_loadName(self):
        model = mount.Mount(host=self.host).model
        suc = model.storeName('Test_Load')
        self.assertEqual(True, suc)
        suc = model.loadName('Test_Load')
        self.assertEqual(True, suc)

    def test_deleteName(self):
        model = mount.Mount(host=self.host).model
        suc = model.storeName('Test_Delete')
        self.assertEqual(True, suc)
        suc = model.deleteName('Test_Delete')
        self.assertEqual(True, suc)

    def test_deletePoint(self):
        model = mount.Mount(host=self.host).model
        suc = model.storeName('Test')
        self.assertEqual(True, suc)
        suc = model.deletePoint(0)
        self.assertEqual(False, suc)
        suc = model.deletePoint(99)
        self.assertEqual(False, suc)
        suc = model.deletePoint(102)
        self.assertEqual(False, suc)
        suc = model.deletePoint(1)
        self.assertEqual(True, suc)
        suc = model.loadName('Test')
        self.assertEqual(True, suc)
    """
    #
    #
    # testing slew command function wise
    #
    #

    @unittest.skipIf(not SLEW, 'mount should movable for this test')
    def test_slewAltAz_pos(self):
        alt = skyfield.api.Angle(degrees=31.251234)
        az = skyfield.api.Angle(degrees=55.77777)

        comm = Command(host=self.host)
        suc = comm.slewAltAz(alt, az)
        self.assertEqual(True, suc)

    @unittest.skipIf(not SLEW, 'mount should movable for this test')
    def test_slewAltAz_neg(self):
        alt = skyfield.api.Angle(degrees=-31.251234)
        az = skyfield.api.Angle(degrees=55.77777)

        comm = Command(host=self.host)
        suc = comm.slewAltAz(alt, az)
        self.assertEqual(True, suc)

    @unittest.skipIf(not SLEW, 'mount should movable for this test')
    def test_slewRaDec_pos(self):
        ra = skyfield.api.Angle(degrees=31.251234)
        dec = skyfield.api.Angle(degrees=55.77777)

        comm = Command(host=self.host)
        suc = comm.slewRaDec(ra, dec)
        self.assertEqual(True, suc)

    @unittest.skipIf(not SLEW, 'mount should movable for this test')
    def test_slewRaDec_neg(self):
        ra = skyfield.api.Angle(degrees=31.251234)
        dec = skyfield.api.Angle(degrees=-55.77777)

        comm = Command(host=self.host)
        suc = comm.slewRaDec(ra, dec)
        self.assertEqual(True, suc)
    """

    #
    #
    # setting standard parameters for work
    #
    #
    @classmethod
    def tearDownClass(cls):

        obsSite = mount.Mount(host=cls.host).obsSite
        obsSite.setRefraction(True)
        obsSite.setHorizonLimitLow(0)
        obsSite.setHorizonLimitHigh(90)
        obsSite.setMeridianLimitSlew(3)
        obsSite.setMeridianLimitTrack(5)
        obsSite.setUnattendedFlip(True)
        obsSite.setRefractionTemp(20)
        obsSite.setRefractionPress(1000)
        obsSite.setUnattendedFlip(False)
        obsSite.setDualAxisTracking(True)
        obsSite.setSlewRate(15)
        obsSite.stopTracking()
        obsSite.park()
