#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_coord_grid
---------------

Tests for `py_tools_ds.geo.coord_grid` module.
"""

import unittest
from shapely.geometry import Polygon

from py_tools_ds.geo.coord_grid import move_shapelyPoly_to_image_grid


poly_local = Polygon([(5708.2, -3006), (5708, -3262), (5452, -3262), (5452, -3006), (5708, -3006)])


class Test_move_shapelyPoly_to_image_grid(unittest.TestCase):

    # TODO test different roundAlgs

    def test_image_coord_grid(self):
        poly_on_grid = move_shapelyPoly_to_image_grid(poly_local, (0, 1, 0, 0, 0, -1), rows=6281, cols=11162)
        self.assertTrue(isinstance(poly_on_grid, Polygon))
        self.assertEqual(str(poly_on_grid), 'POLYGON ((5708 -3262, 5708 -3006, 5452 -3006, 5452 -3262, 5708 -3262))')
