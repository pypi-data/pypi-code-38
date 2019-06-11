# -*- coding: utf-8 -*-

# Copyright (c) 2019, Brandon Nielsen
# All rights reserved.
#
# This software may be modified and distributed under the terms
# of the BSD license.  See the LICENSE file for details.

import unittest
import operator

import numpy as np

from decimal import Decimal
from numpytimebuilder.util import apply_duration, decimal_split, decompose

class TestUtil(unittest.TestCase):
    def test_decompose(self):
        testtuples = (((0, 0, 0, 0),
                       (np.timedelta64(0, 'D'),
                        np.timedelta64(0, 'h'),
                        np.timedelta64(0, 'm'),
                        np.timedelta64(0, 's'),
                        np.timedelta64(0, 'ms'),
                        np.timedelta64(0, 'us'),
                        np.timedelta64(0, 'ns'),
                        np.timedelta64(0, 'ps'),
                        np.timedelta64(0, 'fs'),
                        np.timedelta64(0, 'as'))),
                      ((Decimal('1.5'), 0, 0, 0),
                       (np.timedelta64(1, 'D'),
                        np.timedelta64(12, 'h'),
                        np.timedelta64(0, 'm'),
                        np.timedelta64(0, 's'),
                        np.timedelta64(0, 'ms'),
                        np.timedelta64(0, 'us'),
                        np.timedelta64(0, 'ns'),
                        np.timedelta64(0, 'ps'),
                        np.timedelta64(0, 'fs'),
                        np.timedelta64(0, 'as'))),
                      ((0, Decimal('1.5'), 0, 0),
                       (np.timedelta64(0, 'D'),
                        np.timedelta64(1, 'h'),
                        np.timedelta64(30, 'm'),
                        np.timedelta64(0, 's'),
                        np.timedelta64(0, 'ms'),
                        np.timedelta64(0, 'us'),
                        np.timedelta64(0, 'ns'),
                        np.timedelta64(0, 'ps'),
                        np.timedelta64(0, 'fs'),
                        np.timedelta64(0, 'as'))),
                      ((0, 0, Decimal('1.5'), 0),
                       (np.timedelta64(0, 'D'),
                        np.timedelta64(0, 'h'),
                        np.timedelta64(1, 'm'),
                        np.timedelta64(30, 's'),
                        np.timedelta64(0, 'ms'),
                        np.timedelta64(0, 'us'),
                        np.timedelta64(0, 'ns'),
                        np.timedelta64(0, 'ps'),
                        np.timedelta64(0, 'fs'),
                        np.timedelta64(0, 'as'))),
                      ((0, 0, 0, Decimal('1.200300400500600700')),
                       (np.timedelta64(0, 'D'),
                        np.timedelta64(0, 'h'),
                        np.timedelta64(0, 'm'),
                        np.timedelta64(1, 's'),
                        np.timedelta64(200, 'ms'),
                        np.timedelta64(300, 'us'),
                        np.timedelta64(400, 'ns'),
                        np.timedelta64(500, 'ps'),
                        np.timedelta64(600, 'fs'),
                        np.timedelta64(700, 'as'))),
                      ((Decimal('1.2'), Decimal('3.4'),
                        Decimal('4.5'), Decimal('6.7')),
                       (np.timedelta64(1, 'D'),
                        np.timedelta64(8, 'h'),
                        np.timedelta64(16, 'm'),
                        np.timedelta64(36, 's'),
                        np.timedelta64(700, 'ms'),
                        np.timedelta64(0, 'us'),
                        np.timedelta64(0, 'ns'),
                        np.timedelta64(0, 'ps'),
                        np.timedelta64(0, 'fs'),
                        np.timedelta64(0, 'as'))))

        for testtuple in testtuples:
            result = decompose(*testtuple[0])
            self.assertEqual(result, testtuple[1])

    def test_apply_duration(self):
        testtuples = (((np.datetime64('1981-01-01'),
                        (np.timedelta64(1, 'D'),),
                        operator.add),
                       np.datetime64('1981-01-02')),
                      ((np.datetime64('1981-01-01T00:00:00'),
                        (np.timedelta64(1, 'D'),
                         np.timedelta64(2, 'h')),
                        operator.add),
                       np.datetime64('1981-01-02T02:00:00')),
                      ((np.datetime64('1981-01-01T00:00:00'),
                        (np.timedelta64(1, 'D'),
                         np.timedelta64(2, 'h'),
                         np.timedelta64(3, 'm')),
                        operator.add),
                       np.datetime64('1981-01-02T02:03:00')),
                      ((np.datetime64('1981-01-01T00:00:00'),
                        (np.timedelta64(1, 'D'),
                         np.timedelta64(2, 'h'),
                         np.timedelta64(3, 'm'),
                         np.timedelta64(4, 's')),
                        operator.add),
                       np.datetime64('1981-01-02T02:03:04')),
                      ((np.datetime64('1981-01-01T00:00:00'),
                        (np.timedelta64(1, 'D'),
                         np.timedelta64(2, 'h'),
                         np.timedelta64(3, 'm'),
                         np.timedelta64(4, 's'),
                         np.timedelta64(567, 'ms')),
                        operator.add),
                       np.datetime64('1981-01-02T02:03:04.567')),
                      ((np.datetime64('1981-01-01T00:00:00'),
                        (np.timedelta64(1, 'D'),
                         np.timedelta64(2, 'h'),
                         np.timedelta64(3, 'm'),
                         np.timedelta64(4, 's'),
                         np.timedelta64(567, 'ms'),
                         np.timedelta64(891, 'us')),
                        operator.add),
                       np.datetime64('1981-01-02T02:03:04.567891')),
                      ((np.datetime64('1981-01-01T00:00:00'),
                        (np.timedelta64(1, 'D'),
                         np.timedelta64(2, 'h'),
                         np.timedelta64(3, 'm'),
                         np.timedelta64(4, 's'),
                         np.timedelta64(567, 'ms'),
                         np.timedelta64(891, 'us'),
                         np.timedelta64(234, 'ns')),
                        operator.add),
                       np.datetime64('1981-01-02T02:03:04.567891234')),
                      ((np.datetime64('1981-01-01T00:00:00'),
                        (np.timedelta64(1, 'D'),
                         np.timedelta64(2, 'h'),
                         np.timedelta64(3, 'm'),
                         np.timedelta64(4, 's'),
                         np.timedelta64(567, 'ms'),
                         np.timedelta64(891, 'us'),
                         np.timedelta64(234, 'ns'),
                         np.timedelta64(567, 'ps')),
                        operator.add),
                       np.datetime64('1981-01-02T02:03:04.567891234567')),
                      ((np.datetime64('1981-01-01T00:00:00'),
                        (np.timedelta64(1, 'D'),
                         np.timedelta64(2, 'h'),
                         np.timedelta64(3, 'm'),
                         np.timedelta64(4, 's'),
                         np.timedelta64(567, 'ms'),
                         np.timedelta64(891, 'us'),
                         np.timedelta64(234, 'ns'),
                         np.timedelta64(567, 'ps'),
                         np.timedelta64(891, 'fs')),
                        operator.add),
                       np.datetime64('1981-01-02T02:03:04.567891234567891')),
                      ((np.datetime64('1981-01-01T00:00:00'),
                        (np.timedelta64(1, 'D'),
                         np.timedelta64(2, 'h'),
                         np.timedelta64(3, 'm'),
                         np.timedelta64(4, 's'),
                         np.timedelta64(567, 'ms'),
                         np.timedelta64(891, 'us'),
                         np.timedelta64(234, 'ns'),
                         np.timedelta64(567, 'ps'),
                         np.timedelta64(891, 'fs'),
                         np.timedelta64(234, 'as')),
                        operator.add),
                       np.datetime64('1981-01-02'
                                     'T02:03:04.567891234567891234')),
                      #Verify no switch to datetime resolution
                      ((np.datetime64('1981-01-01'),
                        (np.timedelta64(1, 'D'),
                         np.timedelta64(2, 'h')),
                        operator.add),
                       np.datetime64('1981-01-02')),
                      ((np.datetime64('1981-01-01'),
                        (np.timedelta64(1, 'D'),
                         np.timedelta64(2, 'h'),
                         np.timedelta64(3, 'm')),
                        operator.add),
                       np.datetime64('1981-01-02')),
                      ((np.datetime64('1981-01-01'),
                        (np.timedelta64(1, 'D'),
                         np.timedelta64(2, 'h'),
                         np.timedelta64(3, 'm'),
                         np.timedelta64(4, 's')),
                        operator.add),
                       np.datetime64('1981-01-02')),
                      ((np.datetime64('1981-01-01'),
                        (np.timedelta64(1, 'D'),
                         np.timedelta64(2, 'h'),
                         np.timedelta64(3, 'm'),
                         np.timedelta64(4, 's'),
                         np.timedelta64(567, 'ms')),
                        operator.add),
                       np.datetime64('1981-01-02')),
                      ((np.datetime64('1981-01-01'),
                        (np.timedelta64(1, 'D'),
                         np.timedelta64(2, 'h'),
                         np.timedelta64(3, 'm'),
                         np.timedelta64(4, 's'),
                         np.timedelta64(567, 'ms'),
                         np.timedelta64(891, 'us')),
                        operator.add),
                       np.datetime64('1981-01-02')),
                      ((np.datetime64('1981-01-01'),
                        (np.timedelta64(1, 'D'),
                         np.timedelta64(2, 'h'),
                         np.timedelta64(3, 'm'),
                         np.timedelta64(4, 's'),
                         np.timedelta64(567, 'ms'),
                         np.timedelta64(891, 'us'),
                         np.timedelta64(234, 'ns')),
                        operator.add),
                       np.datetime64('1981-01-02')),
                      ((np.datetime64('1981-01-01'),
                        (np.timedelta64(1, 'D'),
                         np.timedelta64(2, 'h'),
                         np.timedelta64(3, 'm'),
                         np.timedelta64(4, 's'),
                         np.timedelta64(567, 'ms'),
                         np.timedelta64(891, 'us'),
                         np.timedelta64(234, 'ns'),
                         np.timedelta64(567, 'ps')),
                        operator.add),
                       np.datetime64('1981-01-02')),
                      ((np.datetime64('1981-01-01'),
                        (np.timedelta64(1, 'D'),
                         np.timedelta64(2, 'h'),
                         np.timedelta64(3, 'm'),
                         np.timedelta64(4, 's'),
                         np.timedelta64(567, 'ms'),
                         np.timedelta64(891, 'us'),
                         np.timedelta64(234, 'ns'),
                         np.timedelta64(567, 'ps'),
                         np.timedelta64(891, 'fs')),
                        operator.add),
                       np.datetime64('1981-01-02')),
                      ((np.datetime64('1981-01-01'),
                        (np.timedelta64(1, 'D'),
                         np.timedelta64(2, 'h'),
                         np.timedelta64(3, 'm'),
                         np.timedelta64(4, 's'),
                         np.timedelta64(567, 'ms'),
                         np.timedelta64(891, 'us'),
                         np.timedelta64(234, 'ns'),
                         np.timedelta64(567, 'ps'),
                         np.timedelta64(891, 'fs'),
                         np.timedelta64(234, 'as')),
                        operator.add),
                       np.datetime64('1981-01-02')))

        for testtuple in testtuples:
            result = apply_duration(*testtuple[0])
            self.assertEqual(result, testtuple[1])

    def test_decimal_split(self):
        result = decimal_split(Decimal(1))
        self.assertEqual(result, (Decimal(1), Decimal(0)))

        result = decimal_split(Decimal('1.1'))
        self.assertEqual(result, (Decimal(1), Decimal('0.1')))

        result = decimal_split(Decimal('10.0'))
        self.assertEqual(result, (Decimal(10), Decimal(0)))

        result = decimal_split(Decimal('11.1'))
        self.assertEqual(result, (Decimal(11), Decimal('0.1')))

        result = decimal_split(Decimal(-1))
        self.assertEqual(result, (Decimal(-1), Decimal(0)))

        result = decimal_split(Decimal('-1.1'))
        self.assertEqual(result, (Decimal(-1), Decimal('-0.1')))

        result = decimal_split(Decimal('-10.0'))
        self.assertEqual(result, (Decimal(-10), Decimal(0)))

        result = decimal_split(Decimal('-11.1'))
        self.assertEqual(result, (Decimal(-11), Decimal('-0.1')))
