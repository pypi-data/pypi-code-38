#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests of the module *dhd.connect*."""

import pytest
import geopandas as gpd
import pandas as pd
import numpy as np
import os
from shapely.geometry import Point, LineString, Polygon

from dhd import connect

from fixtures import load_pkl_connect


def test_append_superpositions():

    idx1, idx2 = "a", "b"
    s1 = []
    s2 = [{0, 1, 2}, {3, 4}]
    s3 = [{0, 1, 2}, {3, "a"}]
    connect.append_superpositions(s1, idx1, idx2)
    connect.append_superpositions(s2, idx1, idx2)
    connect.append_superpositions(s3, idx1, idx2)

    assert len(s1) == 1
    assert len(s2) == 3
    assert len(s3) == 2
    assert s1[0] == {"a", "b"}
    assert s2[2] == {"a", "b"}
    assert s3[1] == {3, "a", "b"}


def test_order_superpositions():

    s = [{0, 1, 2}, {3, 4}, {5, 6}]
    indices = connect.order_superpositions(s)

    assert indices == [1, 2, 4, 6]


def test_get_superpositions():

    p1 = Polygon([(0, 0), (1, 0), (1, 1), (0, 1)])
    p2 = Polygon([(2, 0), (3, 0), (3, 1), (2, 1)])
    p3 = Polygon([(0, 0.2), (1, 0.2), (1, 1.2), (0, 1.2)])
    p4 = Polygon([(2, 0.8), (3, 0.8), (3, 1.8), (2, 1.8)])
    sinks = pd.DataFrame([[p1], [p2], [p3], [p4]], columns=["geometry"])
    s1 = connect.get_superpositions(sinks, 0.5)
    s2 = connect.get_superpositions(sinks, 0.01)

    assert s1 == [{0, 2}]
    assert s2 == [{0, 2}, {1, 3}]

def test_clean_superpositions():

    p1 = Polygon([(0, 0), (1, 0), (1, 1), (0, 1)])
    p2 = Polygon([(2, 0), (3, 0), (3, 1), (2, 1)])
    p3 = Polygon([(5,5),(5,7),(7,8),(7,4)])
    p4 = Polygon([(-1,-1),(-2,-1),(-2,-3),(-1,-3)])
    sinks = pd.DataFrame([['a',p1],['b',p2],['c',p3],['d',p2],['e',p4]],\
                         columns=['index','geometry'])
    sinks.set_index('index', inplace=True, drop=True)
    sinks_ = connect.clean_superpositions(sinks)

    assert len(sinks_) == 4

def test_check_index_repetition():

    sinks1 = pd.DataFrame([["a"], ["b"], ["c"], ["d"], ["a"]], columns=["A"])
    sinks2 = sinks1.set_index("A", drop=True, inplace=False)

    assert connect.check_index_repetition(sinks1)
    with pytest.raises(AssertionError):
        connect.check_index_repetition(sinks2)


def test_check_data_structure(load_pkl_connect):

    sinks, streets, sources, barriers = load_pkl_connect
    ignore_index = True
    assert connect.check_data_structure(sinks, streets, sources, barriers, ignore_index)


def test_set_line_coordinates():

    line1, line2 = LineString([(0, 0), (1, 1)]), LineString([(0, 1), (2, 3)])
    df = pd.DataFrame([["a", line1], ["b", line2]], columns=["id", "geometry"])
    connect.set_line_coordinates(df)

    assert df.loc[0, "xA"] == 0
    assert {"xA", "yA", "xB", "yB"}.issubset(df.columns)


def test_connection_weight():

    line = LineString([(0, 0), (0, 1)])
    func = lambda x: x + 1

    weight = connect.connection_weight(line, func)
    assert weight == 2


def test_set_default_weight_to_length():

    line1, line2 = LineString([(0, 0), (0, 1)]), LineString([(0, 1), (2, 3)])
    df = pd.DataFrame([["a", line1], ["b", line2]], columns=["id", "geometry"])
    connect.set_default_weight_to_length(df)
    assert df.loc[0, "weight"] == 1


def test_init_vertices():

    line1, line2 = LineString([(0, 0), (0, 1)]), LineString([(0, 1), (2, 3)])
    df = pd.DataFrame(
        [["a", "c", line1], ["b", "d", line2]], columns=["idA", "idB", "geometry"]
    )

    vertices = connect.init_vertices(df)

    assert vertices.loc[0, "idE"] == "a_c"
    assert vertices.loc[0, "weight"] == 1
    assert vertices.loc[1, "yB"] == 3


def test_get_terminals_indices():

    df1 = pd.DataFrame([[1, 2, 3], [4, 5, 6]], index=["a", "b"])
    df2 = pd.DataFrame([[6, 5, 4], [3, 2, 1]], index=["c", "d"])

    indices1 = connect.get_terminals_indices(df1, df2, False)
    indices2 = connect.get_terminals_indices(df1, df2, True)

    assert indices1[2] == "c"
    assert indices2[2] == "0B"


def test_init_terminals():

    p0, p1, p2 = Point(0, 0), Point(1, 1), Point(5, 5)
    df1 = pd.DataFrame([[p0]], columns=["geometry"])
    df2 = pd.DataFrame([[p1, 1], [p2, 2]], columns=["geometry", "load"])

    terminals = connect.init_terminals(df1, df2, True)

    assert terminals.loc["0B", "geometry"] == p1
    assert terminals.loc["1B", "load"] == 2
    terminals.loc["0S", "_id"].append(2)
    assert terminals.loc["0S", "_id"][0] == 2


def test_get_nearest_point():

    point = Point(0, 0)
    line = LineString([(1, -1), (-1, -1)])
    s1 = pd.Series([point], index=["geometry"])
    s2 = pd.Series([line], index=["geometry"])

    # projection of the point on the line
    p1, p2 = connect.get_nearest_point(s1, s2)
    assert p1 == (0, 0)
    assert p2 == (0, -1)


def test_is_crossing_a_barrier():

    lines = [LineString([(0, 0), (0, 10)])]
    p1, p2 = (-1, 5), (1, 5)
    # check if the line between p1 and p2 intersects the list of lines
    intersection = connect.is_crossing_a_barrier(p1, p2, lines)
    assert intersection == True


def test_first_selection():

    # unit square
    vertices = gpd.GeoDataFrame(
        [
            [0, 1, "0_1", LineString([(0, 0), (0, 1)])],
            [1, 2, "1_2", LineString([(0, 1), (1, 1)])],
            [2, 3, "2_3", LineString([(1, 1), (1, 0)])],
            [3, 0, "3_0", LineString([(1, 0), (0, 0)])],
        ],
        columns=["idA", "idB", "idE", "geometry"],
    )

    # point at the square center and far away
    terminals = gpd.GeoDataFrame(
        [[Point(0.5, 0.5)], [Point(10, 10)]], columns=["geometry"]
    )

    # vertical line crossing the right side of the square
    barriers = gpd.GeoDataFrame(
        [[LineString([(0.8, -1), (0.8, 2)])]], columns=["geometry"]
    )

    terminal1 = terminals.iloc[0]
    terminal2 = terminals.iloc[1]
    # connection to the center of each side of the square
    selection1 = connect.first_selection(vertices, terminal1, 1, None)
    # no connection on the right side because of the barrier
    selection2 = connect.first_selection(vertices, terminal1, 1, barriers)
    # no connection (point to far)
    selection3 = connect.first_selection(vertices, terminal2, 1, None)

    assert len(selection1) == 4
    assert len(selection2) == 3
    assert len(selection3) == 0


def test_remove_point():

    # save square coordinates in DataFrame
    selection = pd.DataFrame([[0, 0], [0, 1], [1, 1], [1, 0]], columns=["xC", "yC"])
    # remove all corners but the opposite one
    df = selection.copy()
    connect.remove_point(df, 0, 1.2)
    assert len(df) == 1
    # # remove only the source point (idmin=0)
    df = selection.copy()
    connect.remove_point(df, 0, 0.5)
    assert len(df) == 3
    # # remove all points
    df = selection.copy()
    connect.remove_point(df, 0, 2)
    assert len(df) == 0


def test_second_selection():

    selection1 = pd.DataFrame(
        [[0, 0, 1], [0, 1, 2], [1, 1, 3], [1, 0, 4]], columns=["xC", "yC", "d"]
    )
    selection2 = connect.second_selection(selection1, 1.2)

    assert len(selection2) == 2


def test_split_line():

    # construct line
    l = LineString([(0, 0), (0, 1), (5, 1), (7, 7)])
    # p1 on the line, p2 not on the line
    p1, p2 = Point(3, 1), Point(3, 2)
    # split l in two around p1
    line1, line2 = connect.split_line(l, p1)
    assert line1.length == 4
    with pytest.raises(connect.GeometryError):
        # impossible to split the line around p2
        connect.split_line(l, p2)


def test_sort_lines():

    # construct line
    l = LineString([(0, 0), (0, 1), (5, 1), (7, 7)])
    # p on the line
    p1 = Point(3, 1)
    # split l in two around p
    coords = (7, 7)
    line1, line2 = connect.split_line(l, p1)
    lineA, lineB = connect.sort_lines(line1, line2, coords)
    assert lineB == LineString([(3, 1), (0, 1), (0, 0)])


def test_find_vertex():

    df = pd.DataFrame([["a", 1], ["b", 2], ["c", 3]], columns=["idE", "x"])
    s = pd.Series(["b"], index=["idE"])

    vertex = connect.find_vertex(df, s)
    assert vertex["x"] == 2
    assert vertex.name == 1


def test_get_connection_coordinates():

    s1 = pd.Series([0, 0, 5, 5], index=["xT", "yT", "xC", "yC"])
    s2 = pd.Series([5, 2, 5, 7], index=["xA", "yA", "xB", "yB"])
    coords = connect.get_connection_coordinates(s1, s2)

    assert coords["T"] == (0, 0)
    assert coords["C"] == (5, 5)
    assert coords["A"] == (5, 2)
    assert coords["B"] == (5, 7)


def test_get_connection_distances():

    # connection edge (T-C)
    s1 = pd.Series([0, 0, 5, 5], index=["xT", "yT", "xC", "yC"])
    # vertex edge (A-B)
    s2 = pd.Series([5, 2, 5, 7], index=["xA", "yA", "xB", "yB"])
    coords = connect.get_connection_coordinates(s1, s2)
    d = connect.get_connection_distances(coords)

    assert d["A"] == 3
    assert d["B"] == 2


def test_get_connection_index():

    connections = pd.DataFrame(
        [["a", "b", 0, 0, 1, 0], ["c", "d", 0, 0, -1, -1]],
        columns=["idA", "idB", "xT", "yT", "xC", "yC"],
    )
    vertices = pd.DataFrame(
        [["a", "b", 1, -1, 1, 1], ["b", "c", 1, 1, 1, -1], ["c", "d", 1, -1, -1, -1]],
        columns=["idA", "idB", "xA", "yA", "xB", "yB"],
    )
    p0, p1, p2 = Point(0, 0), Point(1, 1), Point(5, 5)
    df1 = pd.DataFrame([[p0]], columns=["geometry"])
    df2 = pd.DataFrame([[p1], [p2]], columns=["geometry"])
    terminals = connect.init_terminals(df1, df2, True)

    connection = connections.loc[0]
    vertex = vertices.loc[0]
    terminal = terminals.loc["0S"]
    coords = connect.get_connection_coordinates(connection, vertex)
    d = connect.get_connection_distances(coords)
    on_edge, idC = connect.get_connection_index(connection, terminal, d)

    assert on_edge == True
    assert idC == "0S_0"

    connection = connections.loc[1]
    vertex = vertices.loc[2]
    terminal = terminals.loc["0S"]
    coords = connect.get_connection_coordinates(connection, vertex)
    d = connect.get_connection_distances(coords)
    on_edge, idC = connect.get_connection_index(connection, terminal, d)

    assert on_edge == False
    assert idC == "d"


def test_add_connection_to_terminal():

    p0, p1, p2 = Point(0, 0), Point(1, 1), Point(5, 5)
    df1 = pd.DataFrame([[p0]], columns=["geometry"])
    df2 = pd.DataFrame([[p1], [p2]], columns=["geometry"])
    terminals = connect.init_terminals(df1, df2, True)
    coords = {"T": (0, 0), "C": (5, 5), "A": (5, 2), "B": (5, 7)}
    connect.add_connection_to_terminal(terminals.loc["0S"], coords, "idC", None)

    assert len(terminals) == 3
    assert terminals.loc["0S", "_id"] == ["idC"]
    assert terminals.loc["0S", "_weight"] == [np.sqrt(50)]


def test_new_edge_weight():

    l = LineString([(0, 0), (0, 5), (5, 5), (5, 0)])
    p = Point(0, 5)
    l1, l2 = connect.split_line(l, p)
    lA, lB = connect.sort_lines(l1, l2, (0, 0))

    vertex = pd.Series([l, 9], index=["geometry", "weight"])
    weight = connect.new_edge_weight(vertex, lA)

    assert weight == 3


def test_update_edges():

    l = LineString([(5, 2), (5, 7)])
    columns = ["idA", "idB", "idE", "geometry", "weight", "xA", "yA", "xB", "yB"]
    vertices = pd.DataFrame([["a", "b", "a_b", l, 10, 5, 2, 5, 7]], columns=columns)
    connection = pd.Series(["a", "b"], index=["idA", "idB"])
    vertex = vertices.loc[0]
    coords = {"T": (0, 0), "C": (5, 5), "A": (5, 2), "B": (5, 7)}
    idC = "c"
    connect.update_edges(vertices, connection, vertex, coords, idC, None)

    assert len(vertices) == 2
    assert vertices.loc[0, "idA"] == "a"
    assert vertices.loc[1, "weight"] == 4


def test_update_graph():

    l1 = LineString([(5, 2), (5, 7)])
    l2 = LineString([(5, 7), (8, 7)])
    l3 = LineString([(8, 7), (8, 9)])
    columns1 = ["idA", "idB", "idE", "geometry", "weight", "xA", "yA", "xB", "yB"]
    vertices = pd.DataFrame(
        [
            ["a", "b", "a_b", l1, 10, 5, 2, 5, 7],
            ["b", "c", "b_c", l2, 15, 5, 7, 8, 7],
            ["c", "d", "c_d", l3, 20, 8, 7, 8, 9],
        ],
        columns=columns1,
    )

    p0, p1, p2 = Point(0, 0), Point(1, 1), Point(5, 5)
    df1 = pd.DataFrame([[p0]], columns=["geometry"])
    df2 = pd.DataFrame([[p1], [p2]], columns=["geometry"])
    terminals = connect.init_terminals(df1, df2, True)
    terminal = terminals.loc["0S"]

    columns2 = ["idA", "idB", "idE", "xT", "yT", "xC", "yC", "d"]
    connections = pd.DataFrame(
        [
            ["a", "b", "a_b", 0, 0, 5, 5, np.sqrt(50)],
            ["c", "d", "c_d", 0, 0, 8, 8, np.sqrt(128)],
        ],
        columns=columns2,
    )

    connect.update_graph(vertices, terminal, connections, None)

    assert len(vertices) == 5
    assert vertices.loc[4, "weight"] == 10
    assert terminals.loc["0S", "_id"] == ["0S_0", "0S_1"]


def test_connect_terminal():

    l1 = LineString([(0, 0), (0, 1)])
    l2 = LineString([(0, 1), (1, 1)])
    l3 = LineString([(1, 1), (1, 0)])
    l4 = LineString([(1, 0), (0, 0)])
    columns1 = ["idA", "idB", "idE", "geometry", "weight", "xA", "yA", "xB", "yB"]
    vertices = pd.DataFrame(
        [
            ["a", "b", "a_b", l1, 1, 0, 0, 0, 1],
            ["b", "c", "b_c", l2, 2, 0, 1, 1, 1],
            ["c", "d", "c_d", l3, 1, 1, 1, 1, 0],
            ["d", "e", "d_e", l4, 2, 1, 0, 0, 0],
        ],
        columns=columns1,
    )

    p0, p1 = Point(0.1, 0.2), Point(0.3, 0.9)
    df1 = pd.DataFrame([[p0]], columns=["geometry"])
    df2 = pd.DataFrame([[p1]], columns=["geometry"])
    terminals = connect.init_terminals(df1, df2, True)
    terminal1 = terminals.loc["0S"]
    terminal2 = terminals.loc["0B"]

    barriers = gpd.GeoDataFrame(
        [[LineString([(0.8, -1), (0.8, 2)])]], columns=["geometry"]
    )

    connect.connect_terminal(vertices, terminal1, barriers, 0.5, 2, None)
    assert len(vertices) == 5
    assert terminals.loc["0S", "_id"] == ["0S_0"]
    connect.connect_terminal(vertices, terminal2, barriers, 2, 0.35, None)
    assert len(vertices) == 7
    assert terminals.loc["0B", "_id"] == ["0B_0", "0S_0", "0B_2"]


def test_connect_terminals_default(load_pkl_connect):

    sinks, streets, sources, barriers = load_pkl_connect

    vertices, terminals = connect.connect_terminals(
        streets, sinks, sources, barriers, ignore_index=True
    )
    assert len(vertices) == 198
    assert len(terminals) == 9
    assert vertices.loc[23, "idE"] == "13R_90R"
    assert terminals.loc["5B", "_id"] == ["23R", "5B_1"]


def test_connect_terminals_index(load_pkl_connect):

    sinks, streets, sources, barriers = load_pkl_connect

    indices1 = ["{}s".format(i) for i in range(len(sources))]
    indices2 = ["{}b".format(i) for i in range(len(sinks))]
    sources["index"] = indices1
    sinks["index"] = indices2
    sources.set_index("index", inplace=True)
    sinks.set_index("index", inplace=True)
    vertices, terminals = connect.connect_terminals(
        streets, sinks, sources, barriers, ignore_index=False
    )

    assert len(vertices) == 198
    assert len(terminals) == 9
    assert vertices.loc[23, "idE"] == "13R_90R"
    assert terminals.loc["5b", "_id"] == ["5b_0", "74R", "5b_2"]


def test_connect_terminals_connection_weight_function(load_pkl_connect):

    sinks, streets, sources, barriers = load_pkl_connect

    func = lambda x: 100
    vertices, terminals = connect.connect_terminals(
        streets,
        sinks,
        sources,
        barriers,
        ignore_index=True,
        connection_weight_function=func,
    )

    assert terminals.loc["0S", "_weight"][0] == 100
