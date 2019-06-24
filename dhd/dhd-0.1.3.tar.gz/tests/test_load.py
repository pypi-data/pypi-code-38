#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests of the module *dhd.load*."""

import pytest
import pandas as pd
import numpy as np
import os
import networkx as nx
from shapely.geometry import Point, LineString

from dhd import load


def get_test_tst1():

    p1, p2 = Point(0, 0), Point(0, 1)
    p3, p4 = Point(0, 2), Point(0, 3)
    p5, p6 = Point(-1, 2), Point(-1, 3)
    p7, p8 = Point(1, 2), Point(1, 3)
    l1 = LineString([p1, p2])
    l2 = LineString([p2, p3])
    l3 = LineString([p3, p4])
    l4 = LineString([p5, p3])
    l5 = LineString([p6, p4])
    l6 = LineString([p7, p3])
    l7 = LineString([p8, p4])
    tst = pd.DataFrame(
        [
            ["0S", "0R", l1, 3, p1, p2],
            ["0R", "1R", l2, 2, p2, p3],
            ["1R", "2R", l3, 2, p3, p4],
            ["0B", "1R", l4, 2, p5, p3],
            ["1B", "2R", l5, 2, p6, p4],
            ["2B", "1R", l6, 1, p7, p3],
            ["3B", "2R", l7, 0, p8, p4],
        ],
        columns=["idA", "idB", "geometry", "weight", "pA", "pB"],
    )

    return tst


def get_test_tst2():

    p1, p2 = Point(0, 0), Point(0, 1)
    p3, p4 = Point(0, 2), Point(0, 3)
    l1 = LineString([p1, p2])
    l2 = LineString([p2, p3])
    l3 = LineString([p3, p4])
    tst = pd.DataFrame(
        [
            ["0R", "1R", l2, 2, p2, p3],
            ["0S", "0R", l1, 2, p1, p2],
            ["1R", "0B", l3, 2, p3, p4],
        ],
        columns=["idA", "idB", "geometry", "weight", "pA", "pB"],
    )

    return tst


def get_test_terminals1():

    terminals = pd.DataFrame(
        [
            ["0S", "source", 0, [1], 2, 3],
            ["0B", "sink", 1, [1], 2, 3],
            ["1B", "sink", 2, [1], 2, 3],
            ["2B", "sink", 3, [1], 2, 3],
            ["3B", "sink", 4, [1], 2, 3],
        ],
        columns=["idA", "kind", "load", "_id", "_geometry", "_weight"],
    )
    terminals.set_index("idA", inplace=True)

    return terminals


def get_test_terminals2():

    terminals = pd.DataFrame(
        [["0S", "source", 0, [1], 2, 3], ["0B", "sink", 1, [1], 2, 3]],
        columns=["idA", "kind", "load", "_id", "_geometry", "_weight"],
    )
    terminals.set_index("idA", inplace=True)

    return terminals


def test_init_pipes():

    tst = get_test_tst1()
    pipes = load.init_pipes(tst)

    assert len(pipes.nodes()) == 8
    assert len(pipes.edges()) == 7
    assert pipes["1R"]["0B"]["weight"] == 2


def test_init_terminals():

    terminals = get_test_terminals1()
    terminals.loc["0B", "_id"].remove(1)
    load.init_terminals(terminals)
    assert len(terminals) == 5
    assert set(terminals.columns) == set(["kind", "load", "connected"])
    assert terminals.loc["0B", "connected"] == False


def test_get_source_index():

    terminals = pd.DataFrame(
        [
            ["0S", "source", 0],
            ["0B", "sink", 1],
            ["1B", "sink", 2],
            ["2B", "sink", 3],
            ["3B", "sink", 4],
        ],
        columns=["idA", "kind", "load"],
    )
    terminals.set_index("idA", inplace=True)

    assert load.get_source_index(terminals) == "0S"
    terminals.loc["0S", "kind"] = "sink"
    with pytest.raises(load.SourceError):
        load.get_source_index(terminals)


def test_update_loads():

    tst = get_test_tst1()
    terminals = get_test_terminals1()
    load.init_terminals(terminals)
    pipes = load.init_pipes(tst)
    terminal = terminals.loc["1B"]
    shortest_path = ["1B", "2R", "1R", "0R", "0S"]
    load.update_loads(shortest_path, pipes, terminal)

    assert pipes["0R"]["0S"]["load"] == 2
    assert pipes["1R"]["2B"]["load"] == 0


def test_add_terminal_to_pipes():

    tst = get_test_tst1()
    terminals = get_test_terminals1()
    load.init_terminals(terminals)
    pipes = load.init_pipes(tst)
    terminal = terminals.loc["1B"]
    idS = "0S"
    load.add_terminal_to_pipes(pipes, terminal, idS)

    assert pipes["0S"]["0R"]["load"] == 2
    assert pipes["2B"]["1R"]["load"] == 0


def test_pipes_to_dataframe():

    tst = pd.DataFrame([["a", "b"], ["c", "d"]], columns=["idA", "idB"])
    pipes = nx.Graph()
    pipes.add_edges_from([("b", "a"), ("c", "d")])
    nx.set_edge_attributes(pipes, 0, "load")
    nx.set_edge_attributes(pipes, 0, "n_sink")
    pipes["a"]["b"]["load"] = 1
    pipes["a"]["b"]["n_sink"] = 1
    pipes["c"]["d"]["load"] = 10
    pipes["c"]["d"]["n_sink"] = 2
    pipes = load.pipes_to_dataframe(tst, pipes)

    assert pipes.loc[0, "idA"] == "a"
    assert pipes.loc[1, "idA"] == "c"
    assert pipes.loc[0, "load"] == 1
    assert pipes.loc[1, "load"] == 10


def test_load_the_pipes():

    tst = get_test_tst1()
    terminals = get_test_terminals1()
    pipes = load.load_the_pipes(tst, terminals)

    assert len(pipes) == 7
    assert set(pipes.columns) == set(
        ["idA", "idB", "geometry", "weight", "pA", "pB", "load", "n_sink"]
    )
    assert pipes.loc[0, "load"] == 10


def test_init_pipelines():

    pipelines = load.init_pipelines()

    assert len(pipelines) == 0
    assert set(pipelines.columns) == set(
        ["idA", "idB", "length", "weight", "geometry", "load", "n_sink", "pA", "pB"]
    )


def test_select_pipes():

    tst = get_test_tst1()
    terminals = get_test_terminals1()
    pipes = load.load_the_pipes(tst, terminals)
    pipes_selection = load.select_pipes(pipes)

    assert len(pipes_selection) == 2


def test_remove_pipes():

    tst = get_test_tst1()
    terminals = get_test_terminals1()
    pipes = load.load_the_pipes(tst, terminals)
    pipes_selection = load.select_pipes(pipes)
    load.remove_pipes(pipes, pipes_selection)

    assert len(pipes) == 5


def test_get_first_end():

    tst = get_test_tst1()
    terminals = get_test_terminals1()
    pipes = load.load_the_pipes(tst, terminals)
    pipes_selection = load.select_pipes(pipes)
    idx, reverse = load.get_first_end(pipes_selection)
    assert idx == 0
    assert reverse == False
    pA, pB = pipes_selection.at[0, "pA"], pipes_selection.at[0, "pB"]
    pipes_selection.at[0, "pA"], pipes_selection.at[0, "pB"] = pB, pA
    idx, reverse = load.get_first_end(pipes_selection)
    assert reverse == True


def test_add_next_pipe():

    tst = get_test_tst1()
    terminals = get_test_terminals1()
    pipes = load.load_the_pipes(tst, terminals)
    pipes_selection = load.select_pipes(pipes)
    ordered_pipes = pd.DataFrame(columns=pipes_selection.columns)
    pipe = pipes_selection.loc[0]
    load.add_next_pipe(ordered_pipes, pipe, False)
    load.add_next_pipe(ordered_pipes, pipe, True)
    assert len(ordered_pipes) == 2
    assert ordered_pipes.loc[0, "idA"] == pipe["idA"]
    assert ordered_pipes.loc[1, "idA"] == pipe["idB"]


def test_remove_pipe_from_pipes_selection():

    tst = get_test_tst1()
    terminals = get_test_terminals1()
    pipes = load.load_the_pipes(tst, terminals)
    pipes_selection = load.select_pipes(pipes)
    load.remove_pipe_from_pipes_selection(pipes_selection, 0)

    assert len(pipes_selection) == 1
    assert pipes_selection.loc[0, "idA"] == "0R"


def test_find_next_pipe():

    tst = get_test_tst1()
    terminals = get_test_terminals1()
    pipes = load.load_the_pipes(tst, terminals)
    pipes_selection = load.select_pipes(pipes)
    ordered_pipes = pipes_selection.loc[pipes_selection["idA"] == "0S"]
    idx, pipe, reverse = load.find_next_pipe(pipes_selection, ordered_pipes)

    assert idx == 1
    assert pipe["idB"] == "1R"
    assert reverse == False


def test_get_ordered_pipes_set1():

    tst = get_test_tst1()
    terminals = get_test_terminals1()
    pipes = load.load_the_pipes(tst, terminals)
    pipes_selection = load.select_pipes(pipes)
    ordered_pipes = load.get_ordered_pipes(pipes_selection)

    assert len(ordered_pipes) == 2
    assert ordered_pipes.loc[0, "idB"] == ordered_pipes.loc[1, "idA"]


def test_get_ordered_pipes_set2():

    tst = get_test_tst2()
    terminals = get_test_terminals2()
    pipes = load.load_the_pipes(tst, terminals)
    pipes_selection = load.select_pipes(pipes)
    ordered_pipes = load.get_ordered_pipes(pipes_selection)

    assert len(ordered_pipes) == 3
    assert ordered_pipes.loc[0, "idB"] == ordered_pipes.loc[1, "idA"]


def test_get_pipeline_geometry():

    l1 = LineString([(0, 0), (0, 1)])
    l2 = LineString([(0, 1), (1, 1)])
    l3 = LineString([(1, 1), (1, 0)])
    l = LineString([(0, 0), (0, 1), (1, 1), (1, 0)])
    ordered_pipes = pd.DataFrame([[l1], [l2], [l3]], columns=["geometry"])
    line = load.get_pipeline_geometry(ordered_pipes)

    assert line == l


def test_stick_ordered_pipes():

    tst = get_test_tst1()
    terminals = get_test_terminals1()
    pipes = load.load_the_pipes(tst, terminals)
    pipes_selection = load.select_pipes(pipes)
    ordered_pipes = load.get_ordered_pipes(pipes_selection)
    pipeline = load.stick_ordered_pipes(ordered_pipes)

    assert pipeline["idA"] == "0S"
    assert pipeline["idB"] == "1R"
    assert pipeline["pA"] == Point(0, 0)
    assert pipeline["pB"] == Point(0, 2)


def test_construct_pipeline():

    tst = get_test_tst1()
    terminals = get_test_terminals1()
    pipes = load.load_the_pipes(tst, terminals)
    pipes_selection = load.select_pipes(pipes)
    pipeline = load.construct_pipeline(pipes_selection)

    assert pipeline["idA"] == "0S"
    assert pipeline["idB"] == "1R"
    assert pipeline["pA"] == Point(0, 0)
    assert pipeline["pB"] == Point(0, 2)


def test_add_pipelines_set1():

    tst = get_test_tst1()
    terminals = get_test_terminals1()
    pipes = load.load_the_pipes(tst, terminals)
    pipelines = load.init_pipelines()
    load.add_pipelines(pipelines, pipes)

    assert len(pipes) == 5
    assert len(pipelines) == 1
    assert pipelines.loc[0, "geometry"].length == 2
    assert pipelines.loc[0, "load"] == 10


def test_add_pipelines_set2():

    tst = get_test_tst2()
    terminals = get_test_terminals2()
    pipes = load.load_the_pipes(tst, terminals)
    pipelines = load.init_pipelines()
    load.add_pipelines(pipelines, pipes)

    assert len(pipes) == 0
    assert len(pipelines) == 1
    assert pipelines.loc[0, "geometry"].length == 3
    assert pipelines.loc[0, "load"] == 1


def test_get_diameter_function():

    f_kW = load.get_diameter_function("kW", 1, 1, 1, 1)
    f_W = load.get_diameter_function("W", 1, 1, 1, 1)

    assert f_kW(np.pi) == 2
    assert f_W(1000 * np.pi) == 2


def test_set_diameter():

    func = lambda x: x ** 2
    diameter_kW = 2 * np.sqrt(40 / (np.pi * 1000 * 2 * 4.18 * 30))
    diameter_W = 2 * np.sqrt(40 / 1000 / (np.pi * 1000 * 2 * 4.18 * 30))
    pipelines = pd.DataFrame([[40], [2]], columns=["load"])
    load.set_diameter(pipelines)
    assert pipelines.loc[0, "diameter"] == diameter_kW
    load.set_diameter(pipelines, unit="W")
    assert pipelines.loc[0, "diameter"] == diameter_W
    load.set_diameter(pipelines, func)
    assert pipelines.loc[1, "diameter"] == 4


def test_get_nominal_diameter():

    pipe_catalogue = pd.DataFrame(
        [[0, 1], [1, 12], [2, 53], [3, 78], [4, 96], [5, 123]], columns=["DN", "ID"]
    )
    nominal_diameter1 = load.get_nominal_diameter(pipe_catalogue, 0.056, "DN", "ID")
    nominal_diameter2 = load.get_nominal_diameter(pipe_catalogue, 0.096, "DN", "ID")
    nominal_diameter3 = load.get_nominal_diameter(pipe_catalogue, 1, "DN", "ID")

    assert nominal_diameter1 == 3
    assert nominal_diameter2 == 4
    assert nominal_diameter3 == None


def test_set_nominal_diameter():

    pipelines = pd.DataFrame([[0.002], [0.053], [0.021], [0.095]], columns=["diameter"])
    pipe_catalogue = pd.DataFrame(
        [[0, 1], [1, 12], [2, 53], [3, 78], [4, 96], [5, 123]], columns=["DN", "ID"]
    )
    load.set_nominal_diameter(pipelines, pipe_catalogue)

    assert set(pipelines.columns) == {"diameter", "nominal_diameter"}
    assert pipelines.at[2, "nominal_diameter"] == 2


def test_load_the_pipelines_set1():

    tst = get_test_tst1()
    terminals = get_test_terminals1()
    pipelines = load.load_the_pipelines(tst, terminals)

    assert len(pipelines) == 6
    assert pipelines.loc[0, "load"] == 10


def test_load_the_pipelines_set2():

    tst = get_test_tst2()
    terminals = get_test_terminals2()
    pipelines = load.load_the_pipelines(tst, terminals)

    assert len(pipelines) == 1
    assert pipelines.loc[0, "load"] == 1
