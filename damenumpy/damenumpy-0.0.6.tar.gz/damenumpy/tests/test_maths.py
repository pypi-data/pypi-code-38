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

class TestMaths(TestCase):
    def test_sum(self):
        x = np.array([[1,2],[3,4]])
        x2 = np.array([4, 6])
        x3 = np.array([4, 6])
        self.assertEqual(np.sum(x), 10)
        xres = x2 + x3
        self.assertTrue(np.array_equal(xres, [8, 12]))

    def test_substract(self):
        x2 = np.array([4, 6])
        x3 = np.array([4, 6])
        xres = x2 - x3
        xres2 = np.subtract(x2, x3)
        self.assertTrue(np.array_equal(xres, [0, 0]))
        self.assertTrue(np.array_equal(xres2, [0, 0]))

    def test_max(self):
        self.assertEqual(np.max([1, 2, 3, 4]), 4)

    def test_min(self):
        self.assertEqual(np.min([1, 2, 3, 4]), 1)

    def test_mean(self):
        self.assertEqual(np.mean([1, 2, 3, 4]), 2.5)

    def test_reject_outliers(self):
        m = 2
        data = [2,4,5,1,6,5,40]
        u = np.mean(data)
        s = np.std(data)
        filtered = [e for e in data if (u - 2 * s < e < u + 2 * s)]
        self.assertEqual([2, 4, 5, 1, 6, 5], filtered)

    def test_dot(self):
        v = np.array([9,10])
        w = np.array([11, 12])
        # Inner product of vectors; both produce 219
        self.assertEqual(np.dot(v, w), 219)

    def test_linspace(self):
        x = np.linspace(0, 10, num=11, endpoint=True)
        self.assertTrue(np.array_equal(x, np.array([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10])))
        y = np.linspace(0, 10, num=3, endpoint=True)
        self.assertTrue(np.array_equal(y, np.array([0, 5, 10])))

    def test_linalg(self):
        a = np.array([[1.0, 2.0], [3.0, 4.0]])
        y = np.array([[5.], [7.]])
        res = np.linalg.solve(a,y)
        self.assertTrue(np.array_equal(res, np.array([[-3.0], [4.0]])))

    def test_bincount(self):
        a = np.array([1, 1, 2])
        counts1 = np.bincount(a)
        self.assertTrue(np.array_equal(counts1, np.array([0, 2, 1])))
        b = np.array([1,2,3,1,2,1,1,1,3,2,2,1,7,7,7,7,7,7,7,7,7,7,7,7,7])
        counts2 = np.bincount(b)
        self.assertTrue(np.array_equal(counts2, np.array([0, 6, 4, 2, 0, 0, 0, 13])))

    def test_argmax(self): # moda
        arr = np.array([1,2,3,1,2,1,1,1])
        m = np.argmax(arr)
        self.assertTrue(1, m)
