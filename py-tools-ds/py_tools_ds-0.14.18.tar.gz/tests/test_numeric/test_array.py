#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_array
----------

Tests for `py_tools_ds.numeric.array` module.
"""

import unittest
import numpy as np

from py_tools_ds.numeric.array import get_array_tilebounds


class Test_get_array_tilebounds(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.arr = np.random.randint(1, 10, (100, 100, 5))

    def _run_and_validate(self, tile_shape):
        tile_shape = tile_shape[0] or self.arr.shape[0], tile_shape[1] or self.arr.shape[1]

        bounds = get_array_tilebounds(self.arr.shape, tile_shape)
        (rS, rE), (cS, cE) = bounds[0]
        self.assertEqual(self.arr[rS: rE + 1, cS: cE + 1].shape[:2], tile_shape)

    def test_block_tile(self):
        self._run_and_validate(tile_shape=(10, 10))

    def test_row(self):
        self._run_and_validate(tile_shape=(1, None))

    def test_col(self):
        self._run_and_validate(tile_shape=(None, 1))

    def test_pixel(self):
        self._run_and_validate(tile_shape=(1, 1))
