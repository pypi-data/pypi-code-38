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

class TestBasics(TestCase):

    def test_indexing(self):
        b = np.array([[1,2,3],[4,5,6]])   # Create a rank 2 array
        self.assertEqual(b[0, 0], 1)
        self.assertEqual(b[0, 1], 2)
        self.assertEqual(b[1, 0], 4)

    def test_shape(self):
        b = np.array([[1,2,3],[4,5,6]])   # Create a rank 2 array
        self.assertEqual((2, 3), b.shape)

    def test_sum(self):
        x = np.array([[1,2],[3,4]])
        x2 = np.array([4, 6])
        x3 = np.array([4, 6])
        self.assertEqual(np.sum(x), 10)

    def test_sum_zero(self):
        x = np.zeros((2, 2))
        res = np.sum(x)
        self.assertEqual(res, 0)

    def test_equal(self):
        self.assertTrue(np.array_equal([1, 2], [1, 2]))
        self.assertTrue(np.array_equal(np.array([1, 2]), np.array([1, 2])))

    def test_zeros(self):
        x = np.zeros((3, 3))
        self.assertTrue(np.array_equal(x, np.array([[0, 0, 0], [0, 0, 0], [0, 0, 0]])))

    def test_ones(self):
        x = np.ones((2, 2))
        self.assertTrue(np.array_equal(x, np.array([[1, 1], [1, 1]])))

    def test_full(self):
        x = np.full((2, 2), 7)
        self.assertTrue(np.array_equal(x, np.array([[7, 7], [7, 7]])))

    def test_eye(self):
        x = np.eye(3)
        self.assertTrue(np.array_equal(x, np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]])))

    def test_bool_array(self):
        a = np.array([[1,2], [3, 4], [5, 6]])
        bool_idx = (a > 2)  # Find the elements of a that are bigger than 2;
                    # this returns a numpy array of Booleans of the same
                    # shape as a, where each slot of bool_idx tells
                    # whether that element of a is > 2.
        self.assertEqual(bool_idx[0, 0], False)
        self.assertEqual(bool_idx[0, 1], False)
        self.assertEqual(bool_idx[1, 0], True)
        self.assertEqual(bool_idx[1, 1], True)

    def test_tile(self):
        v = np.array([1, 0, 1])
        vv = np.tile(v, (4, 1))  # Stack 4 copies of v on top of each other
        self.assertTrue(np.array_equal(vv, np.array([[1, 0, 1], [1, 0, 1], [1, 0, 1], [1, 0, 1]])))

    def test_empty_like(self):
        x = np.array([[1,2,3], [4,5,6], [7,8,9], [10, 11, 12]])
        v = np.array([1, 0, 1])
        y = np.empty_like(x)   # Create an empty matrix with the same shape as x
        # Add the vector v to each row of the matrix x with an explicit loop
        for i in range(4):
            y[i, :] = x[i, :] + v
        self.assertTrue(np.array_equal(np.array([[2, 2, 4], [5, 5, 7], [8, 8, 10], [11, 11, 13]]), y))

    def test_transpose(self):
        a = np.array([[1, 2], [3, 4]])
        self.assertTrue(np.array_equal(np.array([[1, 3], [2, 4]]), a.transpose()))
