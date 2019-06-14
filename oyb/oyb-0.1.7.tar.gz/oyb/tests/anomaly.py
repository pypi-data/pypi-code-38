"""
"""

import unittest
from math import pi
import oyb
from oyb import anomaly, earth

class MeanToTrue(unittest.TestCase):
    def test_example3p1(self):
        o = oyb.Orbit()
        o.setShape(9.6e6 - earth.eqRad_m, 2.1e7 - earth.eqRad_m)
        tht_rad = 120 * pi / 180
        M_rad = anomaly.true2mean(tht_rad, o.e)
        T_s = o.getPeriod()
        dt_s = M_rad * T_s / (2 * pi)
        self.assertTrue(abs(dt_s - 4.077e3) / dt_s < 1e-3)
        
    def test_example3p2(self):
        tht_rad = anomaly.mean2true(3.6029, 0.37255)
        tht_deg = (tht_rad * 180 / pi) % 360
        self.assertTrue(abs(tht_deg - 193.2) < 1e-1)

    def test_example3p2_inv(self):
        M_rad = anomaly.true2mean(193.2 * pi / 180, 0.37255)
        self.assertTrue(abs((M_rad % (2 * pi)) - 3.6029) < 1e-1)
        
if __name__ == '__main__':
    unittest.main()
