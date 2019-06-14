#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_geometry
---------------

Tests for `py_tools_ds.geo.vector.geometry` module.
"""

from unittest import TestCase

from py_tools_ds.geo.vector.geometry import boxObj, get_winPoly


class Test_boxObj(TestCase):
    def setUp(self):
        self.wp = (468052.97563192865, 3837548.671939657)
        self.ws = (153.6, 153.6)
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

        self.box = boxObj(wp=self.wp,
                          ws=self.ws,
                          gt=self.gt,
                          prj=self.prj)

    def test_init_with_mapPoly(self):
        mapPoly = self.box.mapPoly

        boxObj(mapPoly=mapPoly, gt=self.gt)

        with self.assertRaises(ValueError):
            boxObj(mapPoly=mapPoly)

    def test_init_with_imPoly(self):
        imPoly = self.box.imPoly

        boxObj(imPoly=imPoly, gt=self.gt)

    def test_init_with_boxMapYX(self):
        boxMapYX = self.box.boxMapYX

        boxObj(boxMapYX=boxMapYX, gt=self.gt)

    def test_init_with_boxImYX(self):
        boxImYX = self.box.boxImYX

        boxObj(boxImYX=boxImYX, gt=self.gt)

    def test_init_with_nothing(self):
        with self.assertRaises(ValueError):
            boxObj()

    def test_mapPoly(self):
        # noinspection PyStatementEffect
        self.box.mapPoly

    def test_imPoly(self):
        # noinspection PyStatementEffect
        self.box.imPoly

    def test_boxMapYX(self):
        boxMapYX = self.box.boxMapYX

        self.box.boxMapYX = boxMapYX

    def test_boxMapXY(self):
        boxMapXY = self.box.boxMapXY
        self.box.boxMapXY = boxMapXY

    def test_boxImYX(self):
        boxImYX = self.box.boxImYX
        self.box.boxImYX = boxImYX

    def test_boxImXY(self):
        boxImXY = self.box.boxImXY
        self.box.boxImXY = boxImXY

    def test_boundsMap(self):
        # noinspection PyStatementEffect
        self.box.boundsMap

    def test_boundsIm(self):
        # noinspection PyStatementEffect
        self.box.boundsIm

    def test_imDimsYX(self):
        # noinspection PyStatementEffect
        self.box.imDimsYX

    def test_imDimsXY(self):
        # noinspection PyStatementEffect
        self.box.imDimsXY

    def test_mapDimsYX(self):
        # noinspection PyStatementEffect
        self.box.mapDimsYX

    def test_mapDimsXY(self):
        # noinspection PyStatementEffect
        self.box.mapDimsXY

    def test_buffer_imXY(self):
        self.box.buffer_imXY(buffImX=1, buffImY=1)

    def test_buffer_mapXY(self):
        self.box.buffer_imXY(buffImX=0.6, buffImY=0.6)

    def test_is_larger_DimXY(self):
        box_bounds = (4014, 4270, 4476, 4732)  # xmin, xmax, ymin, ymax

        # equal bounds
        x_larger, y_larger = self.box.is_larger_DimXY(box_bounds)
        self.assertEqual((x_larger, y_larger), (False, False))

        # x bounds larger
        x_larger, y_larger = self.box.is_larger_DimXY((4015, 4270, 4476, 4732))
        self.assertEqual((x_larger, y_larger), (True, False))
        x_larger, y_larger = self.box.is_larger_DimXY((4014, 4269, 4476, 4732))
        self.assertEqual((x_larger, y_larger), (True, False))

        # y bounds larger
        x_larger, y_larger = self.box.is_larger_DimXY((4014, 4270, 4477, 4732))
        self.assertEqual((x_larger, y_larger), (False, True))
        x_larger, y_larger = self.box.is_larger_DimXY((4014, 4270, 4476, 4731))
        self.assertEqual((x_larger, y_larger), (False, True))

    def test_get_coordArray_MapXY(self):
        self.box.get_coordArray_MapXY()

        # test to return coords array in another projection
        self.box.get_coordArray_MapXY(prj="""
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
                                          """)

        box = self.box
        box.prj = None
        with self.assertRaises(ValueError):
            self.box.get_coordArray_MapXY()


class Test_get_winPoly(TestCase):
    def setUp(self):
        self.wp_imYX = (128, 128)
        self.ws = (256, 256)
        self.gt = [465567.6, 0.6, 0.0, 3840310.8000000003, 0.0, -0.6]

    def test_get_winPoly(self):
        get_winPoly(wp_imYX=self.wp_imYX, ws=self.ws, gt=self.gt)

    def test_get_winPoly_match_grid(self):
        get_winPoly(wp_imYX=self.wp_imYX, ws=self.ws, gt=self.gt, match_grid=True)
