#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests of the module *dhd.city*."""

import pytest
import pandas as pd
import networkx as nx
from shapely.geometry import Point, LineString, Polygon
from copy import deepcopy

from dhd import city

# class instance
name = "Vevey, Switzerland"
vevey = city.City(name)

# initilization functions
def get_test_graph():

    G = nx.Graph()
    G.add_nodes_from([1, 2, 3, 4, 5, 6])
    G.add_edges_from([(1, 2), (2, 3), (3, 4), (3, 6), (2, 5), (5, 6)])
    G.node[1]["x"], G.node[1]["y"] = 0, 0
    G.node[2]["x"], G.node[2]["y"] = 1, 0
    G.node[3]["x"], G.node[3]["y"] = 2, 0
    G.node[4]["x"], G.node[4]["y"] = 4, 0
    G.node[5]["x"], G.node[5]["y"] = 1, 1
    G.node[6]["x"], G.node[6]["y"] = 2, 2
    nx.set_edge_attributes(G, None, "geometry")

    return G


# test functions
def test_init():

    assert vevey.name == name
    assert vevey.sources is None
    assert vevey.barriers is None
    assert type(vevey.graph) == nx.MultiDiGraph
    assert set(vevey.buildings.columns) == set(["load", "geometry"])


def test_simplify_graph():

    graph = vevey.simplify_graph()

    assert type(graph) == nx.Graph


def test_reset_sources():

    vevey_ = deepcopy(vevey)
    sources = Point(0, 0)
    vevey_.reset_sources(sources)

    assert vevey_.sources == sources


def test_reset_barriers():

    vevey_ = deepcopy(vevey)
    barriers = LineString([(0, 0), (1, 1)])
    vevey_.reset_barriers(barriers)

    assert vevey_.barriers == barriers


def test_init_streets():

    graph = get_test_graph()
    streets = vevey.init_streets(graph)

    assert len(streets) == 6
    assert set(streets.columns) == set(["idA", "idB", "geometry"])
    assert streets.loc[1, "idA"] == 2


def test_complete_geometries():

    graph = get_test_graph()
    streets = vevey.init_streets(graph)
    vevey.complete_geometries(streets, graph)

    assert streets.loc[0, "geometry"].length == 1
    assert streets.loc[4, "geometry"].length == 2


def test_set_geometries_order():

    graph = get_test_graph()
    streets = vevey.init_streets(graph)
    vevey.complete_geometries(streets, graph)
    streets.loc[0, "geometry"] = LineString([(1, 0), (0, 0)])
    vevey.set_geometries_order(streets, graph)
    assert streets.loc[0, "geometry"] == LineString([(0, 0), (1, 0)])
    with pytest.raises(city.GeometryError):
        streets.loc[0, "geometry"] = LineString([(1, 0), (0, 1)])
        vevey.set_geometries_order(streets, graph)


def test_set_indices():

    streets = pd.DataFrame([[1, 2], [4, 5]], columns=["idA", "idB"])
    vevey.set_indices(streets)
    assert streets.loc[0, "idA"] == "1R"


def test_set_streets_weight():

    graph = get_test_graph()
    streets = vevey.init_streets(graph)
    vevey.complete_geometries(streets, graph)
    vevey.set_streets_weight(streets)

    assert streets.loc[0, "weight"] == 1


def test_get_streets():

    streets = vevey.get_streets()

    assert set(streets.columns) == set(["idA", "idB", "geometry", "weight"])
    assert streets.loc[0, "geometry"].length == streets.loc[0, "weight"]
    assert streets.loc[0, "idA"] == "0R"


def test_get_load_from_area():

    area = 10
    load = vevey.get_load_from_area(area)

    assert load == 2.5


def test_set_buildings_load():

    p = Polygon([(0, 0), (2, 0), (2, 2), (0, 2)])
    buildings = pd.DataFrame([[p]], columns=["geometry"])
    vevey.set_buildings_load(buildings)

    assert buildings.loc[0, "load"] == 1


def test_select_sinks():

    min_area = 1e3
    sinks = vevey.select_sinks(min_area)

    is_working = True
    for idx, sink in sinks.iterrows():
        if sink["load"] < min_area:
            is_working = False

    assert set(sinks.columns) == set(["geometry", "load"])
    assert is_working is True


def test_init_sources():

    sources = [Point(0, 0), Point(1, 1)]
    sources = vevey.init_sources(sources)

    assert len(sources) == 2
    assert sources.loc[0, "geometry"] == Point(0, 0)


def test_get_sources():

    sources1 = Point(0, 0)
    sources2 = [Point(0, 0), Point(1, 1)]
    with pytest.raises(city.SourceError):
        vevey.get_sources()
    vevey.reset_sources(sources1)
    sources = vevey.get_sources()
    assert len(sources) == 1
    assert sources.loc[0, "geometry"] == Point(0, 0)
    vevey.reset_sources(sources2)
    sources = vevey.get_sources()
    assert len(sources) == 2
    assert sources.loc[0, "geometry"] == Point(0, 0)


def test_init_barriers():

    line1 = LineString([(0, 0), (10, 0)])
    line2 = LineString([(5, 5), (5, -5)])
    barriers = [line1, line2]
    barriers = vevey.init_barriers(barriers)

    assert len(barriers) == 2
    assert barriers.loc[0, "geometry"] == line1


def test_get_barriers():

    line1 = LineString([(0, 0), (10, 0)])
    line2 = LineString([(5, 5), (5, -5)])
    barriers = [line1, line2]
    with pytest.raises(city.BarrierError):
        vevey.get_barriers()
    vevey.reset_barriers(barriers)
    barriers = vevey.get_barriers()
    assert len(barriers) == 2
    assert barriers.loc[0, "geometry"] == line1
