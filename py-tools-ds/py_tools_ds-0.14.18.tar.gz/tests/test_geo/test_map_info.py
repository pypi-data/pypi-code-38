#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_map_info
-------------

Tests for `py_tools_ds.geo.map_info` module.
"""

import unittest

from py_tools_ds.geo.map_info import geotransform2mapinfo, mapinfo2geotransform
from py_tools_ds.geo.projection import EPSG2WKT


geotransform_utm = (331185.0, 30.0, -0.0, 5840115.0, -0.0, -30.0)
geotransform_utm_rotated = (331185.0, 12.202099292274006, 27.406363729278027,
                            5840115.0, 27.406363729278027, -12.202099292274006)
geotransform_local = (0, 1, 0, 0, 0, -1)
geotransform_local_rotated = (0.0, 6.123233995736766e-17, 1.0, 0.0, 1.0, -6.123233995736766e-17)
map_info_utm = ['UTM', 1, 1, 331185.0, 5840115.0, 30.0, 30.0, 33, 'North', 'WGS-84']
map_info_utm_rotated = ['UTM', 1, 1, 331185.0, 5840115.0, 30.0, 30.0, 33, 'North', 'WGS-84', 'rotation=66.00000']
map_info_local = ['Arbitrary', 1, 1, 0, 0, 1, 1, 0, 'North']
map_info_local_rotated = ['Arbitrary', 1, 1, 0, 0, 1, 1, 0, 'North', 'rotation=90.00000']

wkt_utm = \
    """
    PROJCS["WGS 84 / UTM zone 33N",
           GEOGCS["WGS 84",
                  DATUM["WGS_1984",
                        SPHEROID["WGS 84", 6378137, 298.257223563,
                                 AUTHORITY["EPSG", "7030"]],
                        AUTHORITY["EPSG", "6326"]],
                  PRIMEM["Greenwich", 0,
                         AUTHORITY["EPSG", "8901"]],
                  UNIT["degree", 0.0174532925199433,
                       AUTHORITY["EPSG", "9122"]],
                  AUTHORITY["EPSG", "4326"]],
           PROJECTION["Transverse_Mercator"],
           PARAMETER["latitude_of_origin", 0],
           PARAMETER["central_meridian", 15],
           PARAMETER["scale_factor", 0.9996],
           PARAMETER["false_easting", 500000],
           PARAMETER["false_northing", 0],
           UNIT["metre", 1,
                AUTHORITY["EPSG", "9001"]],
           AXIS["Easting", EAST],
           AXIS["Northing", NORTH],
           AUTHORITY["EPSG", "32633"]]
    """


class Test_geotransform2mapinfo(unittest.TestCase):

    # TODO implement test in case of geographic prj

    def test_UTM_gt_prj(self):
        map_info = geotransform2mapinfo(gt=geotransform_utm, prj=wkt_utm)
        self.assertTrue(isinstance(map_info, list))
        self.assertEqual(map_info, map_info_utm)

    def test_gt_is_none(self):
        # test gt=None
        map_info = geotransform2mapinfo(gt=None, prj=wkt_utm)
        self.assertTrue(isinstance(map_info, list))
        self.assertEqual(map_info, map_info_local)

    def test_gt_is_arbitrary(self):
        # test gt=[0, 1, 0, 0, 0, -1]
        map_info = geotransform2mapinfo(gt=geotransform_local, prj=wkt_utm)
        self.assertTrue(isinstance(map_info, list))
        self.assertEqual(map_info, map_info_local)

    def test_prj_is_empty(self):
        exp_map_info = ['Arbitrary', 1, 1, 331185.0, 5840115.0, 30.0, 30.0, 0, 'North']
        map_info = geotransform2mapinfo(gt=geotransform_utm, prj='')
        self.assertTrue(isinstance(map_info, list))
        self.assertEqual(map_info, exp_map_info)

    def test_prj_is_not_wgs84(self):
        exp_map_info = ['Lambert Azimuthal Equal Area', 1.0, 1.0, 4526026.0, 3284919.5, 10.0, 10.0]
        map_info = geotransform2mapinfo(gt=(4526026.0, 10.0, 0.0, 3284919.5, 0.0, -10.0), prj=EPSG2WKT(3035))
        self.assertTrue(isinstance(map_info, list))
        self.assertEqual(map_info, exp_map_info)

    def test_prj_is_not_wgs84_rotation(self):
        exp_map_info = ['Lambert Azimuthal Equal Area', 1.0, 1.0, 331185.0, 5840115.0, 30.0, 30.0, 'rotation=66']
        map_info = geotransform2mapinfo(gt=geotransform_utm_rotated, prj=EPSG2WKT(3035))
        self.assertTrue(isinstance(map_info, list))
        self.assertEqual(map_info, exp_map_info)

    def test_gt_contains_rotation(self):
        map_info = geotransform2mapinfo(gt=geotransform_utm_rotated, prj=wkt_utm)
        self.assertTrue(isinstance(map_info, list))
        self.assertEqual(map_info, map_info_utm_rotated)

    def test_gt_contains_rotation_prj_is_local(self):
        map_info = geotransform2mapinfo(gt=geotransform_local_rotated, prj='')
        self.assertTrue(isinstance(map_info, list))
        self.assertEqual(map_info, map_info_local_rotated)


class Test_mapinfo2geotransform(unittest.TestCase):

    def test_map_info_is_valid(self):
        gt = mapinfo2geotransform(map_info_utm)
        self.assertTrue(isinstance(gt, (tuple, list)))
        self.assertEqual(gt, geotransform_utm)

        # test
        gt = mapinfo2geotransform(['Arbitrary', 1, 1, 5, -7, 1, 1, 0, 'North'])
        self.assertTrue(isinstance(gt, (tuple, list)))
        self.assertEqual(gt, (5, 1, 0, -7, 0, -1))

    def test_map_info_is_empty(self):
        gt = mapinfo2geotransform(None)
        self.assertTrue(isinstance(gt, (tuple, list)))
        self.assertEqual(gt, geotransform_local)

    def test_map_info_contains_LAEA_proj(self):
        gt = mapinfo2geotransform(['Lambert Azimuthal Equal Area', 1.0, 1.0, 4526026.0, 3284919.5, 10.0, 10.0])
        self.assertTrue(isinstance(gt, (tuple, list)))
        self.assertEqual(gt, (4526026.0, 10.0, 0.0, 3284919.5, 0.0, -10.0))

    def test_map_info_contains_rotation(self):
        gt = mapinfo2geotransform(map_info_utm_rotated)
        self.assertTrue(isinstance(gt, (tuple, list)))
        self.assertEqual(gt, geotransform_utm_rotated)

    def test_map_info_is_local_contains_rotation(self):
        gt = mapinfo2geotransform(map_info_local_rotated)
        self.assertTrue(isinstance(gt, (tuple, list)))
        self.assertEqual(gt, geotransform_local_rotated)
