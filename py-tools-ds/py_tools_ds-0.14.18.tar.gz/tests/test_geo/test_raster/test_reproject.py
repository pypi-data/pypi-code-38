#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_reproject
--------------

Tests for `py_tools_ds.geo.raster.reproject` module.
"""

import os
from unittest import TestCase

import numpy as np
from gdalnumeric import LoadFile

from py_tools_ds import __path__
from py_tools_ds.geo.coord_calc import corner_coord_to_minmax, get_corner_coordinates
from py_tools_ds.geo.raster.reproject import SensorMapGeometryTransformer, SensorMapGeometryTransformer3D


tests_path = os.path.abspath(os.path.join(__path__[0], "..", "tests"))


class Test_SensorMapGeometryTransformer(TestCase):
    def setUp(self):
        self.dem_map_geo = LoadFile(os.path.join(tests_path, 'data', 'dem_map_geo.bsq'))
        self.dem_sensor_geo = LoadFile(os.path.join(tests_path, 'data', 'dem_sensor_geo.bsq'))
        self.lons = LoadFile(os.path.join(tests_path, 'data', 'lons_full_vnir.bsq'))
        self.lats = LoadFile(os.path.join(tests_path, 'data', 'lats_full_vnir.bsq'))
        self.dem_area_extent_coarse_subset_utm = [622613.864409047,  # LL_x
                                                  5254111.40255343,  # LL_x
                                                  660473.864409047,  # LL_x
                                                  5269351.40255343]  # UR_y

        self.expected_dem_area_extent_lonlat = [10.685733901515151,  # LL_x
                                                47.44113415492957,  # LL_y
                                                11.073066098484848,  # UR_x
                                                47.54576584507042]  # UR_y

        self.expected_dem_area_extent_utm = [626938.928052,  # LL_x
                                             5256253.56579,  # LL_y
                                             656188.928052,  # UR_x
                                             5267203.56579]  # UR_y

    def test_to_sensor_geometry(self):
        SMGT = SensorMapGeometryTransformer(lons=self.lons,
                                            lats=self.lats,
                                            resamp_alg='nearest')
        dem_sensors_geo = SMGT.to_sensor_geometry(self.dem_map_geo,
                                                  src_prj=32632, src_extent=self.dem_area_extent_coarse_subset_utm)
        self.assertIsInstance(dem_sensors_geo, np.ndarray)
        self.assertFalse(np.array_equal(np.unique(dem_sensors_geo), np.array([0])))
        self.assertEquals(dem_sensors_geo.shape, (150, 1000))

    def test_to_map_geometry_lonlat(self):
        SMGT = SensorMapGeometryTransformer(lons=self.lons,
                                            lats=self.lats,
                                            resamp_alg='nearest')

        # to Lon/Lat
        dem_map_geo, dem_gt, dem_prj = SMGT.to_map_geometry(self.dem_sensor_geo, tgt_prj=4326)
        self.assertIsInstance(dem_map_geo, np.ndarray)
        self.assertEquals(dem_map_geo.shape, (SMGT.area_definition.height,
                                              SMGT.area_definition.width))
        xmin, xmax, ymin, ymax = corner_coord_to_minmax(get_corner_coordinates(gt=dem_gt,
                                                                               cols=dem_map_geo.shape[1],
                                                                               rows=dem_map_geo.shape[0]))
        self.assertTrue(False not in np.isclose(np.array([xmin, ymin, xmax, ymax]),
                                                np.array(self.expected_dem_area_extent_lonlat)))
        self.assertFalse(np.array_equal(np.unique(dem_map_geo), np.array([0])))

        with self.assertRaises(ValueError):
            SMGT.to_map_geometry(self.dem_sensor_geo[:10, :10], tgt_prj=4326)  # must have the shape of lons/lats

    def test_to_map_geometry_utm(self):
        SMGT = SensorMapGeometryTransformer(lons=self.lons,
                                            lats=self.lats,
                                            resamp_alg='nearest')

        # to UTM32
        dem_map_geo, dem_gt, dem_prj = SMGT.to_map_geometry(self.dem_sensor_geo, tgt_prj=32632, tgt_res=(30, 30))
        self.assertIsInstance(dem_map_geo, np.ndarray)
        self.assertEquals(dem_map_geo.shape, (365, 975))
        xmin, xmax, ymin, ymax = corner_coord_to_minmax(get_corner_coordinates(gt=dem_gt,
                                                                               cols=dem_map_geo.shape[1],
                                                                               rows=dem_map_geo.shape[0]))
        self.assertTrue(False not in np.isclose(np.array([xmin, ymin, xmax, ymax]),
                                                np.array(self.expected_dem_area_extent_utm)))
        self.assertFalse(np.array_equal(np.unique(dem_map_geo), np.array([0])))


class Test_SensorMapGeometryTransformer3D(TestCase):
    def setUp(self):
        dem_map_geo = LoadFile(os.path.join(tests_path, 'data', 'dem_map_geo.bsq'))
        dem_sensor_geo = LoadFile(os.path.join(tests_path, 'data', 'dem_sensor_geo.bsq'))
        lons = LoadFile(os.path.join(tests_path, 'data', 'lons_full_vnir.bsq'))
        lats = LoadFile(os.path.join(tests_path, 'data', 'lats_full_vnir.bsq'))

        self.data_map_geo_3D = np.dstack([dem_map_geo, dem_map_geo])
        self.data_sensor_geo_3D = np.dstack([dem_sensor_geo, dem_sensor_geo])
        self.lons_3D = np.dstack([lons, lons])  # TODO use different lons per band here
        self.lats_3D = np.dstack([lats, lats])  # TODO use different lats per band here

        self.dem_area_extent_coarse_subset_utm = [622613.864409047,  # LL_x
                                                  5254111.40255343,  # LL_x
                                                  660473.864409047,  # LL_x
                                                  5269351.40255343]  # UR_y

        self.expected_dem_area_extent_lonlat = [10.685733901515151,  # LL_x
                                                47.44113415492957,  # LL_y
                                                11.073066098484848,  # UR_x
                                                47.54576584507042]  # UR_y

        self.expected_dem_area_extent_utm = [626938.928052,  # LL_x
                                             5256253.56579,  # LL_y
                                             656188.928052,  # UR_x
                                             5267203.56579]  # UR_y

    def test_to_map_geometry_lonlat_3D_geolayer(self):
        SMGT = SensorMapGeometryTransformer3D(lons=self.lons_3D,
                                              lats=self.lats_3D,
                                              # resamp_alg='nearest',
                                              resamp_alg='bilinear',
                                              )

        # to Lon/Lat
        data_mapgeo_3D, dem_gt, dem_prj = SMGT.to_map_geometry(self.data_sensor_geo_3D, tgt_prj=4326)
        self.assertIsInstance(data_mapgeo_3D, np.ndarray)
        # only validate number of bands (height and width are validated in 2D version
        #   fixed numbers may fail here due to float uncertainty errors
        self.assertEquals(data_mapgeo_3D.shape[2], 2)
        xmin, xmax, ymin, ymax = corner_coord_to_minmax(get_corner_coordinates(gt=dem_gt,
                                                                               cols=data_mapgeo_3D.shape[1],
                                                                               rows=data_mapgeo_3D.shape[0]))
        self.assertTrue(False not in np.isclose(np.array([xmin, ymin, xmax, ymax]),
                                                np.array(self.expected_dem_area_extent_lonlat)))

    def test_to_sensor_geometry(self):
        SMGT = SensorMapGeometryTransformer3D(lons=self.lons_3D,
                                              lats=self.lats_3D,
                                              resamp_alg='nearest',
                                              )
        dem_sensors_geo = SMGT.to_sensor_geometry(self.data_map_geo_3D,
                                                  src_prj=32632, src_extent=self.dem_area_extent_coarse_subset_utm)
        self.assertIsInstance(dem_sensors_geo, np.ndarray)
        self.assertEquals(dem_sensors_geo.shape, (150, 1000,  2))
