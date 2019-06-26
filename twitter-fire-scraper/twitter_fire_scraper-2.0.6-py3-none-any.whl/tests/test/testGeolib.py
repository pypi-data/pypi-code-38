import unittest

# noinspection PyUnresolvedReferences
from models import Point
from util import flatten_points, geobox_to_geocode


class TestGeoLib(unittest.TestCase):
    def testPointFlattening(self):
        self.assertEqual(flatten_points([Point(1, 2), Point(2, 3), Point(3, 4)]), [1, 2, 2, 3, 3, 4])

    def testGeocodeCreation(self):
        self.assertEqual(geobox_to_geocode([Point(-1, -1), Point(2, 2)], "20km"), "0.5,0.5,20km")
