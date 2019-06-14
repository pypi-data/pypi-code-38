#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_gdal
---------

Tests for `py_tools_ds.io.raster.gdal` module.
"""

from unittest import TestCase
import numpy as np
from gdal import Dataset
from pandas import DataFrame

from py_tools_ds.io.raster.gdal import get_GDAL_ds_inmem, get_GDAL_driverList


class Test_get_GDAL_ds_inmem(TestCase):
    def setUp(self):
        self.arr2d = np.random.randint(0, 10, (5, 5))
        self.arr3d = np.random.randint(0, 10, (5, 5, 2))
        self.gt = [465567.6, 0.6, 0.0, 3840310.8000000003, 0.0, -0.6]
        self.prj = \
            """
            PROJCS["WGS 84 / UTM zone 36N",
                   GEOGCS["WGS 84",
                          DATUM["WGS_1984",
                                SPHEROID["WGS 84",6378137,298.257223563,
                                         AUTHORITY["EPSG","7030"]],
                                AUTHORITY["EPSG","6326"]],
                          PRIMEM["Greenwich",0,
                                 AUTHORITY["EPSG","8901"]],
                          UNIT["degree",0.0174532925199433,
                               AUTHORITY["EPSG","9122"]],
                          AUTHORITY["EPSG","4326"]],
                   PROJECTION["Transverse_Mercator"],
                   PARAMETER["latitude_of_origin",0],
                   PARAMETER["central_meridian",33],
                   PARAMETER["scale_factor",0.9996],
                   PARAMETER["false_easting",500000],
                   PARAMETER["false_northing",0],
                   UNIT["metre",1,
                        AUTHORITY["EPSG","9001"]],
                   AXIS["Easting",EAST],
                   AXIS["Northing",NORTH],
                   AUTHORITY["EPSG","32636"]]
            """

    def test_2d_array(self):
        ds = get_GDAL_ds_inmem(array=self.arr2d)
        self.assertIsInstance(ds, Dataset)

    def test_3d_array(self):
        ds = get_GDAL_ds_inmem(array=self.arr3d)
        self.assertIsInstance(ds, Dataset)

    def test_2d_array_gt_prj(self):
        ds = get_GDAL_ds_inmem(array=self.arr3d, gt=self.gt, prj=self.prj)
        self.assertIsInstance(ds, Dataset)

    def test_2d_array_gt_prj_nodata(self):
        ds = get_GDAL_ds_inmem(array=self.arr3d, gt=self.gt, prj=self.prj, nodata=0)
        self.assertIsInstance(ds, Dataset)

        with self.assertRaises(TypeError):
            ds = get_GDAL_ds_inmem(array=self.arr3d, gt=self.gt, prj=self.prj, nodata=np.array([0], dtype=np.bool))
            self.assertIsInstance(ds, Dataset)


class Test_get_GDAL_driverList(TestCase):
    def test_check_output(self):
        drvList = get_GDAL_driverList()
        self.assertIsInstance(drvList, DataFrame)
