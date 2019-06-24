#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests of the module *dhd.evolve*."""

import pytest
import numpy as np
import pandas as pd
import networkx as nx
from shapely.geometry import Point, LineString
import os

from dhd import evolve

from fixtures import load_pkl_evolve

# test functions
def test_remove_no_connection_terminals():

    terminals = pd.DataFrame(
        [["A", [0]], ["B", []], ["C", [1]]], columns=["index", "_id"]
    )
    terminals.set_index("index", inplace=True)
    tst_terminals = evolve.remove_no_connection_terminals(terminals)

    assert len(tst_terminals) == 2
    assert tst_terminals.loc["C", "_id"][0] == 1


def test_parameters_compatibility():

    n, n1, n2 = 10, 2, 5
    mutation_rate = 0.2

    assert evolve.parameters_compatibility(n, n1, n2, mutation_rate)


def test_dataframe_compatibility():

    vertices = pd.DataFrame(
        [["a", "b"], ["b", "c"], ["c", "d"]], columns=["idA", "idB"]
    )
    terminals1 = pd.DataFrame(
        [["A", ["a", "c"]], ["B", ["d"]]], columns=["index", "_id"]
    )
    terminals1.set_index("index", inplace=True)
    terminals2 = pd.DataFrame(
        [["A", ["a", "c"]], ["B", ["e"]]], columns=["index", "_id"]
    )
    terminals2.set_index("index", inplace=True)

    assert evolve.dataframe_compatibility(vertices, terminals1)
    with pytest.raises(evolve.IncompatibilityError):
        evolve.dataframe_compatibility(vertices, terminals2)


def test_connect_terminals():

    l1 = LineString([(0, 0), (2, 0)])
    l2 = LineString([(2, 0), (2, 1)])
    l3 = LineString([(2, 1), (4, 1)])
    l4 = LineString([(0, 1), (0, 0)])
    l5 = LineString([(4, 0), (4, 1)])
    l6 = LineString([(0, 1), (2, 1)])
    l7 = LineString([(4, 0), (2, 0)])
    vertices = pd.DataFrame(
        [["a", "b", l1, 2], ["b", "c", l2, 1], ["c", "d", l3, 2]],
        columns=["idA", "idB", "geometry", "weight"],
    )
    terminals = pd.DataFrame(
        [["A", ["a", "c"], [l4, l6], [0.5, 1]], ["B", ["b", "d"], [l7, l5], [1, 0.5]]],
        columns=["index", "_id", "_geometry", "_weight"],
    )
    terminals.set_index("index", inplace=True)
    genes1 = [0, 0]

    tst_vertices = evolve.connect_terminals(vertices, terminals, genes1)
    assert len(tst_vertices) == 5
    assert tst_vertices.loc[4, "idA"] == "B"


def test_get_terminal_steiner_tree():

    l1 = LineString([(0, 0), (2, 0)])
    l2 = LineString([(2, 0), (2, 1)])
    l3 = LineString([(2, 1), (4, 1)])
    l4 = LineString([(0, 1), (0, 0)])
    l5 = LineString([(4, 0), (4, 1)])
    l6 = LineString([(0, 1), (2, 1)])
    l7 = LineString([(4, 0), (2, 0)])
    vertices = pd.DataFrame(
        [["a", "b", l1, 2], ["b", "c", l2, 1], ["c", "d", l3, 2]],
        columns=["idA", "idB", "geometry", "weight"],
    )
    terminals = pd.DataFrame(
        [["A", ["a", "c"], [l4, l6], [0.5, 1]], ["B", ["b", "d"], [l7, l5], [1, 0.5]]],
        columns=["index", "_id", "_geometry", "_weight"],
    )
    terminals.set_index("index", inplace=True)
    genes1 = [0, 0]
    genes2 = [0, 1]
    genes3 = [1, 1]
    tst_vertices = evolve.connect_terminals(vertices, terminals, genes1)
    T = evolve.get_terminal_steiner_tree(tst_vertices, terminals)
    assert len(T.nodes()) == 4
    tst_vertices = evolve.connect_terminals(vertices, terminals, genes2)
    T = evolve.get_terminal_steiner_tree(tst_vertices, terminals)
    assert len(T.nodes()) == 6
    tst_vertices = evolve.connect_terminals(vertices, terminals, genes3)
    T = evolve.get_terminal_steiner_tree(tst_vertices, terminals)
    assert len(T.nodes()) == 4
    assert nx.is_connected(T)


def test_get_tree_weight():

    l1 = LineString([(0, 0), (2, 0)])
    l2 = LineString([(2, 0), (2, 1)])
    l3 = LineString([(2, 1), (4, 1)])
    l4 = LineString([(0, 1), (0, 0)])
    l5 = LineString([(4, 0), (4, 1)])
    l6 = LineString([(0, 1), (2, 1)])
    l7 = LineString([(4, 0), (2, 0)])
    vertices = pd.DataFrame(
        [["a", "b", l1, 2], ["b", "c", l2, 1], ["c", "d", l3, 2]],
        columns=["idA", "idB", "geometry", "weight"],
    )
    terminals = pd.DataFrame(
        [["A", ["a", "c"], [l4, l6], [0.5, 1]], ["B", ["b", "d"], [l7, l5], [1, 0.5]]],
        columns=["index", "_id", "_geometry", "_weight"],
    )
    terminals.set_index("index", inplace=True)
    args = [vertices, terminals]
    genes1 = [0, 0]
    genes2 = [0, 1]
    individual1 = [0, genes1]
    individual2 = [0, genes2]

    weight, genes = evolve.get_tree_weight(individual1, args)
    assert weight == 3.5
    weight, genes = evolve.get_tree_weight(individual2, args)
    assert weight == 6


def test_get_configuration_number_exponent():

    allele_number = range(1, 10)
    configuration_number_exponent = evolve.get_configuration_number_exponent(
        allele_number
    )

    assert configuration_number_exponent == 5


def set_allele_number():

    terminals = pd.DataFrame(
        [
            ["A", ["a", "c"]],
            ["B", ["b"]],
            ["C", ["b"]],
            ["D", ["b", "d", "e"]],
            ["E", ["b", "d", "a", "e"]],
        ],
        columns=["index", "_id"],
    )
    terminals.set_index("index", inplace=True)
    allele_number = evolve.set_allele_number(terminals)
    assert allele_number == [2, 1, 1, 3, 4]
    terminals.loc["B", "_id"] = []
    with pytest.raises(evolve.NoConnectionError):
        evolve.set_allele_number(terminals)


def test_init_individual_genes():

    allele_number = [1, 2, 1, 3]
    genes = evolve.init_individual_genes(allele_number)

    assert len(genes) == 4
    assert type(genes[3]) == int
    assert genes[0] == 0
    assert 0 <= genes[1] <= 1


def test_init_population_genes():

    allele_number = [1, 2, 3]
    n = 10
    population = evolve.init_population_genes(n, allele_number)

    assert len(population) == 10
    assert population[0][1][0] == 0


def test_get_statistics():

    population = [[i, None] for i in range(10)]
    mean, stddev = evolve.get_statistics(population)

    assert round(mean, 2) == round(4.5, 2)
    assert round(stddev, 2) == round(np.sqrt(8.25), 2)


def test_individual_mutation():

    individual = [None, [0, 0, 0, 0]]
    allele_number = [1, 2, 1, 3]
    mutation_rate = 1

    mutation = evolve.individual_mutation(
        individual, allele_number, mutation_rate, inbred=False
    )
    assert len(mutation[1]) == 4
    assert mutation[1][0] == 0
    assert mutation[1][1] == 1


def test_select_random_parents():

    parents1 = [[0, [0]], [1, [1]], [2, [2]], [3, [3]], [4, [4]]]
    parents2 = [[0, [0]], [0, [0]], [0, [0]], [0, [0]], [0, [0]]]

    mum, dad, inbred = evolve.select_random_parents(parents1)
    assert inbred == False
    mum, dad, inbred = evolve.select_random_parents(parents2)
    assert inbred == True
    assert mum[1] == [0]


def test_procreate():

    mum = [None, [0, 1, 0, 1, 0, 1]]
    dad = [None, [1, 0, 1, 0, 1, 0]]
    child = evolve.procreate(mum, dad)

    assert len(child[1]) == 6
    assert child[1][2] == 0 or child[1][2] == 1


def test_reproduction():

    parents = [[0, [0, 0]], [1, [0, 1]], [2, [1, 0]], [3, [1, 1]]]
    allele_number = [2, 2]
    mutation_rate = 0.5
    child = evolve.reproduction(parents, allele_number, mutation_rate)

    assert len(child[1]) == 2
    assert child[0] == None
    assert child[1][0] == 0 or child[1][0] == 1


def test_get_next_generation():

    elites = [[0, [0, 0]], [0, [1, 1]]]
    parents = [[0, [0, 0]], [1, [0, 1]], [2, [1, 0]], [3, [1, 1]]]
    allele_number = [2, 2]
    n1 = 2
    n = 8
    mutation_rate = 1
    population = evolve.get_next_generation(
        elites, parents, n1, n, allele_number, mutation_rate
    )

    assert len(population) == 8
    assert population[0][1] == [1, 1]


def test_select_elites_and_parents():

    population = [[i, None] for i in range(20)]
    elites = [[100 + i, None] for i in range(5)]
    n1 = 5
    n2 = 10
    elites, parents = evolve.select_elites_and_parents(population, elites, n1, n2)

    assert len(elites) == 5
    assert len(parents) == 10
    assert parents[9][0] == 9


def test_init_evolution_dataframe():

    N = 10
    evolution1 = evolve.init_evolution_dataframe(N, True)
    evolution2 = evolve.init_evolution_dataframe(N, False)

    assert list(evolution1.index) == list(evolution2.index) == list(range(N))
    assert list(evolution1.columns) == [
        "weight",
        "mean",
        "stddev",
        "genes",
        "population",
    ]
    assert list(evolution2.columns) == ["weight", "mean", "stddev", "genes"]


def test_save_generation():

    N = 10
    evolution = evolve.init_evolution_dataframe(N, True)
    elites = [[1, [0, 0]], [2, [0, 1]]]
    population = [
        [1, [0, 0]],
        [2, [0, 1]],
        [3, [1, 0]],
        [6, [1, 1]],
        [4, [2, 0]],
        [5, [2, 1]],
    ]
    evolve.save_generation(0, evolution, population, elites, True)

    assert evolution.at[0, "weight"] == 1
    assert evolution.at[0, "genes"] == [0, 0]
    assert round(evolution.at[0, "mean"], 2) == round(21.0 / 6, 2)


def test_run_evolution(load_pkl_evolve):

    vertices, terminals = load_pkl_evolve

    evolution = evolve.run_evolution(vertices, terminals, 5, n=16, n1=2, n2=8)
    terminals_ = evolve.remove_no_connection_terminals(terminals)

    assert len(evolution) == 5
    assert evolution.at[0, "weight"] >= evolution.at[4, "weight"]
    assert len(evolution.at[4, "genes"]) == len(terminals_)


def test_get_best_individual():

    evolution = pd.DataFrame(
        [[1, 2, 3], [4, 5, 6]], columns=["weight", "genes", "stddev"]
    )
    genes = evolve.get_best_individual(evolution)

    assert genes == 5


def test_get_best_terminal_steiner_tree(load_pkl_evolve):

    vertices, terminals = load_pkl_evolve

    evolution = evolve.run_evolution(vertices, terminals, 5, n=16, n1=2, n2=8)
    genes = evolve.get_best_individual(evolution)
    tst = evolve.get_best_terminal_steiner_tree(vertices, terminals, evolution)
    w1 = tst["weight"].sum()
    w2 = evolution.at[len(evolution) - 1, "weight"]

    assert np.abs(w2 - w1) / (w2 + w1) < 0.001


def test_set_nodes_coordinates():

    l1 = LineString([(0, 0), (1, 0)])
    l2 = LineString([(1, 0), (1, 1)])
    l3 = LineString([(1, 1), (0, 1)])
    l4 = LineString([(0, 1), (0, 0)])
    tst = pd.DataFrame(
        [["a", "b", l1], ["b", "c", l2], ["c", "d", l3], ["d", "a", l4]],
        columns=["idA", "idB", "geometry"],
    )
    evolve.set_nodes_coordinates(tst)

    assert tst.loc[0, "pA"] == Point(0, 0)
    assert tst.loc[2, "pB"] == Point(0, 1)


def test_get_genes_variation():

    evolution = pd.DataFrame(
        [[1, [1, 0, 1]], [2, [0, 1, 1]], [3, [0, 1, 1]], [4, [1, 1, 1]]],
        columns=["weight", "genes"],
    )
    genes_variation = evolve.get_genes_variation(evolution)

    assert genes_variation == [0.5, 1, 2 / np.sqrt(6)]
