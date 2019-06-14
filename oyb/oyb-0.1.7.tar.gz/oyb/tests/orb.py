"""
"""

import datetime
import unittest
import numpy
from math import pi
import oyb
from oyb import earth, anomaly

class ClassTests(unittest.TestCase):
    def test_default(self):
        o = oyb.Orbit()
        
    def test_args(self):
        o = oyb.Orbit(a_m=1.064e7, e=0.42607, i_rad=39.687*pi/180, O_rad=130.32*pi/180, w_rad=42.373*pi/180, M_rad=4.2866)
        
    def test_example4p3(self):
        rEci_m = numpy.array([-6.045e6, -3.490e6, 2.5e6])
        vEci_mps = numpy.array([-3.457e3, 6.618e3, 2.533e3])
        o = oyb.Orbit.fromRV(rEci_m, vEci_mps)
        h_m2ps = o.getAngMom()
        tht_rad = anomaly.mean2true(o.M_rad, o.e)
        T_s = o.getPeriod()
        self.assertTrue(abs(h_m2ps - 5.831e10) / h_m2ps < 1e-3)
        self.assertTrue(abs(o.i_rad - 153.2 * pi / 180) / o.i_rad < 1e-3)
        self.assertTrue(abs(o.O_rad - 255.3 * pi / 180) / o.O_rad < 1e-3)
        self.assertTrue(abs(o.e - 0.1712) / o.e < 1e-3)
        self.assertTrue(abs(o.w_rad - 20.07 * pi / 180) / o.w_rad < 1e-3)
        self.assertTrue(abs(tht_rad - 28.45 * pi / 180) / tht_rad < 1e-3)
        self.assertTrue(abs(T_s - 2.278 * 3600) / T_s < 1e-3)
        
    def test_example2p8(self):
        o = oyb.Orbit.fromHTht(1.545e6, 126 * pi / 180, 8.52e5, 58 * pi / 180)
        hPer_m, hApo_m = o.getShape()
        T_s = o.getPeriod()
        self.assertTrue(abs(o.a_m - 7.593e6) / o.a_m < 1e-3)
        self.assertTrue(abs(o.e - 0.08164) / o.e < 1e-3)
        self.assertTrue(abs(hPer_m - 5.955e5) / hPer_m < 1e-3)
        self.assertTrue(abs(T_s - 1.829 * 3600) / T_s < 1e-3)
        
class FrameTests(unittest.TestCase):
    def test_pqw(self):
        o = oyb.Orbit(e=0.5, M_rad=0.5*pi)
        rPqw_m = o.getRpqw()
        
    def test_example4p7mod(self):
        e = 0.4
        a_m = 8e10 / (earth.mu_m3ps2 * (1 - e**2))
        M_rad = anomaly.true2mean(30 * pi / 180, e)
        o = oyb.Orbit(a_m=a_m, e=e, i_rad=30*pi/180, O_rad=40*pi/180, w_rad=60*pi/180, M_rad=M_rad)
        rEci_m = o.getReci()
        
class J2Tests(unittest.TestCase):
    def test_raan(self):
        o = oyb.MeanJ2(a_m=6.718e6, e=8.931e-3, i_rad=51.43*pi/180)
        dRaan_degpday = o.getRaanRate() * 180/pi * 86400
        self.assertTrue(abs(dRaan_degpday - 5.181) / dRaan_degpday < 1e-3)

    def test_aop(self):
        o = oyb.MeanJ2(a_m=6.718e6, e=8.931e-3, i_rad=51.43*pi/180)
        dAop_degpday = o.getAopRate() * 180/pi * 86400
        self.assertTrue(abs(dAop_degpday - 3.920) / dAop_degpday < 1e-3)
        
    def test_example4p9(self):
        o = oyb.MeanJ2.fromSunSync(100 * 60)
        self.assertTrue(abs(o.a_m - (7.5863e5 + earth.eqRad_m)) / o.a_m < 1e-3)
        self.assertTrue(abs(o.i_rad - 98.43 * pi / 180) / o.i_rad < 1e-3)
        
    def test_example4p10(self):
        o = oyb.MeanJ2.fromConstAop(3 * 3600)
        shape = o.getShape()
        self.assertTrue(abs(shape[0] - 5.215e5) / shape[0] < 1e-3)
        self.assertTrue(abs(shape[1] - 7.842e6) / shape[1] < 1e-3)
    
    def test_example4p11(self):
        rEci_m = numpy.array([-3.67e6, -3.87e6, 4.4e6])
        vEci_mps = numpy.array([4.7e3, -7.4e3, 1e3])
        o = oyb.MeanJ2.fromRV(rEci_m, vEci_mps)
        rEciNew_m = o.getReci(o.tEpoch_dt + datetime.timedelta(4))
        rNew_m = rEciNew_m.dot(rEciNew_m)**0.5
        drEci_m = rEciNew_m - numpy.array([9.672e6, 4.32e6, -8.691e6])
        self.assertTrue(drEci_m.dot(drEci_m)**0.5 / rNew_m < 1e-3)
        
class PropertyTests(unittest.TestCase):
    def setUp(self):
        hPer_km = 400
        hApo_km = 4000
        self.o = oyb.Orbit()
        self.o.setShape(1e3 * hPer_km, 1e3 * hApo_km)
        
    def test_a(self):
        self.assertTrue(abs(self.o.e - 0.2098) / self.o.e < 1e-3)
        
    def test_b(self):
        h_m2ps = self.o.getAngMom()
        self.assertTrue(abs(h_m2ps - 5.7172e10) / h_m2ps < 1e-3)
        
    def test_cd(self):
        vPer_mps, vApo_mps = self.o.getShapeVel()
        self.assertTrue(abs(vPer_mps - 8.435e3) / vPer_mps < 1e-3)
        self.assertTrue(abs(vApo_mps - 5.509e3) / vApo_mps < 1e-3)
        
    def test_e(self):
        self.assertTrue(abs(self.o.a_m - 8.578e6) / self.o.a_m < 1e-3)
        
    def test_f(self):
        T_s = self.o.getPeriod()
        self.assertTrue(abs(T_s - 2.196 * 3600) / T_s < 1e-3)
        
    def test_g(self):
        rTaa_m = self.o.getTaaRad()
        self.assertTrue(abs(rTaa_m - 8.387e6) / rTaa_m < 1e-3)

if __name__ == '__main__':
    unittest.main()
