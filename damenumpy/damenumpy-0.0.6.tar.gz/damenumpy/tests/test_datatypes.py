#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (C) 2019  David Arroyo Menéndez

# Author: David Arroyo Menéndez <davidam@gnu.org>
# Maintainer: David Arroyo Menéndez <davidam@gnu.org>

# This file is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3, or (at your option)
# any later version.

# This file is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with GNU Emacs; see the file COPYING.  If not, write to
# the Free Software Foundation, Inc., 51 Franklin Street, Fifth Floor,
# Boston, MA 02110-1301 USA,

from unittest import TestCase

import numpy as np

class TestDatatypes(TestCase):
    def test_dtype(self):
        x = np.array([1, 2])
        self.assertEqual(x.dtype, "int64")
        y = np.array([1.0, 2.0])
        self.assertEqual(y.dtype, "float64")

    def test_bool(self):
        a = np.array([[1,2], [3, 4], [5, 6]])
        bool_idx = (a > 2)
        self.assertTrue(np.array_equal(a[a > 2], np.array([3, 4, 5, 6])))
        self.assertTrue(np.array_equal(a[bool_idx], np.array([3, 4, 5, 6])))
        self.assertTrue(np.array_equal(bool_idx, np.array([[False, False], [True, True], [True, True]])))

# Elementwise sum; both produce the array
# [[ 6.0  8.0]
#  [10.0 12.0]]
# print(x + y)
# print(np.add(x, y))
