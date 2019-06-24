#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests of the module *dhd.features*."""

import pytest
import pandas as pd

from dhd import features


def test_get_connection_path():

    pipelines = pd.DataFrame(
        [["a", "b", 1], ["b", "c", 2], ["b", "d", 3], ["d", "e", 4], ["d", "f", 5]],
        columns=["idA", "idB", "weight"],
    )
    connection_path = features.get_connection_path(pipelines, "a", "f")

    assert len(connection_path) == 3
    assert set(connection_path.index) == set([0, 2, 4])
    assert connection_path.loc[2, "weight"] == 3


def test_get_column_statistics():

    df = pd.DataFrame([[1, 0], [-1, 2], [1, 0], [-1, 2]], columns=["a", "b"])
    mean_a, stddev_a = features.get_column_statistics(df, "a")
    mean_b, stddev_b = features.get_column_statistics(df, "b")

    assert mean_a == 0
    assert mean_b == 1
    assert stddev_a == 1
    assert stddev_b == 1


def test_get_intersection_number():

    pipelines = pd.DataFrame(
        [["a", "b", 1], ["b", "c", 2], ["b", "d", 3], ["d", "e", 4], ["d", "f", 5]],
        columns=["idA", "idB", "weight"],
    )
    terminals = pd.DataFrame(
        [[True], [True], [False], [True], [True]],
        index=["a", "c", "g", "e", "f"],
        columns=["connected"],
    )
    intersection_number = features.get_intersection_number(pipelines, terminals)

    assert intersection_number == 2
