#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests of the module *dhd.utils*."""

import pytest
import numpy as np
from shapely.geometry import LineString

from dhd import utils


def test_reverse_linestring():

    line1 = LineString([(0, 0), (1, 0), (2, 1), (3, 0)])
    line2 = LineString([(3, 0), (2, 1), (1, 0), (0, 0)])
    reverse_line = utils.reverse_linestring(line1)

    assert reverse_line == line2


def test_distance():

    p1 = (0, 0)
    p2 = (1, 0)
    d = utils.distance(p1, p2)

    assert d == 1


def test_get_list_transpose():

    l1 = [[0, 1], [1, 2], [2, 3], [3, 4]]
    l2 = [[0, 1, 2, 3], [1, 2, 3, 4]]
    lT = utils.get_list_transpose(l1)

    assert lT == l2


def test_get_moment():

    data = [0, 2, 4, 6]
    m1 = utils.get_moment(data, 1)
    m2 = utils.get_moment(data, 2)

    assert m1 == 3
    assert m2 == 14


def test_normalized_inner_product():

    x = np.array([1, 0, 1, 0, 1, 0, 1])
    y = np.array([1, 1, 2, 2, 2, 1, 1])
    d = utils.normalized_inner_product(x, y)

    assert d == 0.75
