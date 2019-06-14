"""
"""

import numpy
import unittest
import datetime
from math import pi
from oyb import earth

class TimeTests(unittest.TestCase):
    def test_example5p6(self):
        t_dt = datetime.datetime(2004, 3, 3, 4, 30, 0)
        gmst_rad = earth.getGmst(t_dt)
        self.assertTrue(abs(gmst_rad - 228.79354 * pi / 180) / gmst_rad < 1e-3)
        
class TopoTests(unittest.TestCase):
    def test_example5p7(self):
        t_dt = datetime.datetime(2016, 11, 2, 5, 39, 5)
        gmst_rad = earth.getGmst(t_dt)
        self.assertTrue(abs(gmst_rad - 126.7 * pi / 180) / gmst_rad < 1e-3)
        rEci_m = numpy.array([-5.368e6, -1.784e6, 3.691e6])
        rSiteLla_radm = [20 * pi / 180, 60 * pi / 180, 0]
        rSiteEci_m = earth.lla2eci(rSiteLla_radm, t_dt)
        errEci_m = abs(rSiteEci_m - numpy.array([-5.955e6, -6.995e5, 2.168e6]))
        err_pct = errEci_m.dot(errEci_m)**0.5 / rSiteEci_m.dot(rSiteEci_m)**0.5
        self.assertTrue(err_pct < 1e-3)
        lst_rad = gmst_rad + rSiteLla_radm[1]

if __name__ == '__main__':
    unittest.main()
