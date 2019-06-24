#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests of the module *dhd.modify*."""

import pytest
from shapely.geometry import Point, LineString
import pandas as pd

from dhd import modify


def get_test_streets():

    la = LineString([(-2, -1), (2, -1)])
    lb = LineString([(-2, 0), (2, 0)])
    lc = LineString([(-2, 1), (2, 1)])
    lA = LineString([(-1, -2), (-1, 2)])
    lB = LineString([(0, -2), (0, 2)])
    lC = LineString([(1, -2), (1, 2)])

    streets = pd.DataFrame(
        [
            ["a1", "a2", la, 1],
            ["b1", "b2", lb, 2],
            ["c1", "c2", lc, 3],
            ["A1", "A2", lA, 4],
            ["B1", "B2", lB, 5],
            ["C1", "C2", lC, 6],
        ],
        columns=["idA", "idB", "geometry", "weight"],
    )

    return streets


def get_test_sinks():

    p1, p2, p3 = Point(-1, -1), Point(0, -1), Point(1, -1)
    p4, p5, p6 = Point(-1, 0), Point(0, 0), Point(1, 0)
    p7, p8, p9 = Point(-1, 1), Point(0, 1), Point(1, 1)

    sinks = pd.DataFrame(
        [
            [p1, 1],
            [p2, 2],
            [p3, 3],
            [p4, 4],
            [p5, 5],
            [p6, 6],
            [p7, 7],
            [p8, 8],
            [p9, 9],
        ],
        columns=["geometry", "load"],
    )

    return sinks


def test_get_streets_selection():

    streets = get_test_streets()
    p = Point(0.5, 0.5)
    R1, R2 = 1, 0.1
    streets_selection1 = modify.get_streets_selection(streets, p, R1)
    streets_selection2 = modify.get_streets_selection(streets, p, R2)

    assert len(streets_selection1) == 4
    assert len(streets_selection2) == 0


def test_find_streets():

    streets = get_test_streets()
    p = Point(0.5, 0.5)
    R1, R2 = 1, 0.1
    streets_selection1 = modify.find_streets(streets, p, R1)
    streets_selection2 = modify.find_streets(streets, p, R2)

    assert len(streets_selection1) == 4
    assert len(streets_selection2) == 0


def test_multiply_streets_weight_singlet():

    streets = get_test_streets()
    indices = 2
    ratios = 2.5
    modify.multiply_streets_weight(streets, indices, ratios)

    assert streets.loc[2, "weight"] == 7.5


def test_multiply_streets_weight_list():

    streets = get_test_streets()
    indices = [2, 4]
    ratios = [2.5, 0.5]
    modify.multiply_streets_weight(streets, indices, ratios)

    assert streets.loc[2, "weight"] == 7.5
    assert streets.loc[4, "weight"] == 2.5


def test_replace_streets_weight_singlet():

    streets = get_test_streets()
    indices = 2
    weights = 2.5
    modify.replace_streets_weight(streets, indices, weights)

    assert streets.loc[2, "weight"] == 2.5


def test_replace_streets_weight_list():

    streets = get_test_streets()
    indices = [2, 4]
    weights = [2.5, 0.5]
    modify.replace_streets_weight(streets, indices, weights)

    assert streets.loc[2, "weight"] == 2.5
    assert streets.loc[4, "weight"] == 0.5


def test_get_sinks_selection():

    sinks = get_test_sinks()
    p = Point(0.5, 0.5)
    R1, R2 = 1, 0.1
    sinks_selection1 = modify.get_sinks_selection(sinks, p, R1)
    sinks_selection2 = modify.get_sinks_selection(sinks, p, R2)

    assert len(sinks_selection1) == 4
    assert len(sinks_selection2) == 0


def test_find_sinks():

    sinks = get_test_sinks()
    p = Point(0.5, 0.5)
    R1, R2 = 1, 0.1
    sinks_selection1 = modify.find_sinks(sinks, p, R1)
    sinks_selection2 = modify.find_sinks(sinks, p, R2)

    assert len(sinks_selection1) == 4
    assert len(sinks_selection2) == 0


def test_multiply_sinks_load_singlet():

    sinks = get_test_sinks()
    indices = 2
    ratios = 2.5
    modify.multiply_sinks_load(sinks, indices, ratios)

    assert sinks.loc[2, "load"] == 7.5


def test_multiply_sinks_load_list():

    sinks = get_test_sinks()
    indices = [2, 4]
    ratios = [2.5, 0.5]
    modify.multiply_sinks_load(sinks, indices, ratios)

    assert sinks.loc[2, "load"] == 7.5
    assert sinks.loc[4, "load"] == 2.5


def test_replace_sinks_load_singlet():

    sinks = get_test_sinks()
    indices = 2
    loads = 2.5
    modify.replace_sinks_load(sinks, indices, loads)

    assert sinks.loc[2, "load"] == 2.5


def test_replace_sinks_load_list():

    sinks = get_test_sinks()
    indices = [2, 4]
    loads = [2.5, 0.5]
    modify.replace_sinks_load(sinks, indices, loads)

    assert sinks.loc[2, "load"] == 2.5
    assert sinks.loc[4, "load"] == 0.5


def test_add_sinks():

    sinks = get_test_sinks()
    p1, p2 = Point(0, 3), Point(0, 4)
    sinks_to_add = pd.DataFrame(
        [["A", p1, 1], ["B", p2, 2]], columns=["index", "geometry", "load"]
    )
    sinks_to_add.set_index("index", inplace=True)
    sinks1 = modify.add_sinks(sinks, sinks_to_add, ignore_index=True)
    sinks2 = modify.add_sinks(sinks, sinks_to_add, ignore_index=False)

    assert len(sinks1) == len(sinks2) == 11
    assert sinks1.loc[10, "load"] == sinks2.loc["B", "load"] == 2


def test_remove_streets():

    streets = get_test_streets()
    index = [1, 4]
    streets = modify.remove_streets(streets, index)

    assert len(streets) == 4
    assert streets.loc[2, "weight"] == 4


def test_remove_sinks():

    sinks = get_test_sinks()
    sinks["index"] = ["a", "b", "c", "d", "e", "f", "g", "h", "i"]
    sinks.set_index("index", inplace=True)
    index = ["a", "f"]
    sinks1 = modify.remove_sinks(sinks, index, ignore_index=True)
    sinks2 = modify.remove_sinks(sinks, index, ignore_index=False)

    assert len(sinks1) == len(sinks2) == 7
    assert sinks1.loc[5, "load"] == sinks2.loc["h", "load"] == 8
