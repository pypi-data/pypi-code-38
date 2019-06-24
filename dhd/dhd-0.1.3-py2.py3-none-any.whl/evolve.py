#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
import pandas as pd
import networkx as nx
from networkx.algorithms.approximation.steinertree import steiner_tree
import random
import time
import multiprocessing
from functools import partial
from contextlib import contextmanager
from shapely.geometry import Point
import matplotlib.pyplot as plt

from dhd.logs import log
from dhd.utils import get_list_transpose, normalized_inner_product
from dhd.exceptions import IncompatibilityError, NoConnectionError


@contextmanager
def poolcontext(*args, **kwargs):
    pool = multiprocessing.Pool(*args, **kwargs)
    yield pool
    pool.terminate()


def remove_no_connection_terminals(terminals):
    """
    Remove terminals which cannot be connected to the district heating network.

    Parameters
    ----------
    terminals: DataFrame
        Dataframe of the terminals to connect to the graph.

    Returns
    -------
    DataFrame
        Updated *terminals* dataframe.
    """

    terminals = terminals.copy()

    count = 0
    for idx, terminal in terminals.iterrows():
        if len(terminal["_id"]) == 0:
            count += 1
            terminals.drop(index=idx, inplace=True)

    text = "{} terminals without connection removed."
    log.info(text.format(count))

    return terminals


def parameters_compatibility(n, n1, n2, mutation_rate):
    """
    Assert that the input parameters are compatible with eachother.

    Parameters
    ----------
    n: int
        Population size.
    n1: int
        Elite population size.
    n2: int
        Parent population size.
    mutation_rate: float
        Rate of genes mutation. Must belong to the open interval (0,1).

    Return
    ------
    bool
        True if the parameters are compatible.
    """

    assert n1 <= n, (
        "The elites population must me smaller than " "the whole population."
    )
    assert n2 <= n, (
        "The parents population must me smaller than " "the whole population."
    )
    assert 0 <= mutation_rate <= 1, (
        "The mutation rate must belong " "to the open interval (0,1)."
    )

    return True


def dataframe_compatibility(vertices, terminals):
    """
    Check the compatibility of the input dataframes.

    Parameters
    ----------
    vertices: DataFrame
        Dataframe of the street graph plus the connection nodes.
    terminals: DataFrame
        Dataframe of the terminals to connect to the graph.

    Returns
    -------
    bool
        True if the dataframes are compatible.
    """

    index = set(vertices.idA).union(set(vertices.idB))
    for idx, terminal in terminals.iterrows():
        for id in terminal["_id"]:
            if not id in index:
                text = (
                    "The terminal connection {} doesn't belong to the "
                    "vertices nodes."
                )
                raise IncompatibilityError(text.format(terminal.name))

    return True


def connect_terminals(vertices, terminals, genes):
    """
    Add the connections from *terminals* associated to the given *genes* to the
    graph *vertices*.

    Parameters
    ----------
    vertices : DataFrame
        Dataframe of the street graph plus the connection nodes.
    terminals : DataFrame
        Dataframe of the terminals to connect to the graph.
    genes : list
        List of terminal single connections of the considered configuration.

    Returns
    -------
    DataFrame
        Updated *vertices* dataframe.
    """

    tst_vertices = vertices.copy()
    n = len(tst_vertices)

    for i, a in enumerate(genes):

        terminal = terminals.iloc[i]
        tst_vertices.at[n + i, "idA"] = terminal.name
        tst_vertices.at[n + i, "idB"] = terminal["_id"][a]
        tst_vertices.at[n + i, "geometry"] = terminal["_geometry"][a]
        tst_vertices.at[n + i, "weight"] = terminal["_weight"][a]

    return tst_vertices


def get_terminal_steiner_tree(vertices, terminals):
    """
    Compute the Steiner Tree (TST by construction) associated to the updated
    graph *vertices* (with connection edges) of the considered configuration.

    Parameters
    ----------
    vertices: DataFrame
        Dataframe of the street graph plus the connection nodes concatenated with a single connection at each terminal.
    terminals: DataFrame
        Dataframe of the terminals to connect to the graph.

    Returns
    -------
    Graph
        Approximate Terminal Steiner Tree of the considered single connections
        configuration.
    """

    G = nx.from_pandas_edgelist(
        vertices, source="idA", target="idB", edge_attr=list(vertices.columns)
    )
    T = steiner_tree(G, terminal_nodes=list(terminals.index), weight="weight")

    return T


def get_tree_weight(individual, args):
    """
    Find the approximate Steiner Tree associated to the genes of the given
    *individual* and compute its weight.

    Parameters
    ----------
    individual: tuple = float, list
        Individual weight and genes. The weight has not yet been computed and is
        None.
    args: tuple = Dataframe, DataFrame
        Dataframes *vertices* and *terminals*.

    Returns
    -------
    tuple = float, list
        Individual with the updated weight associated to its genes.
    """

    vertices, terminals = args
    weigth, genes = individual

    # add rows associated to the connections
    tst_vertices = connect_terminals(vertices, terminals, genes)
    # compute Steiner tree
    T = get_terminal_steiner_tree(tst_vertices, terminals)
    # graph -> DataFrame
    df = nx.to_pandas_edgelist(T)
    # get total weight
    weight = sum(list(df["weight"]))

    individual = (weight, genes)

    return individual


def get_configuration_number_exponent(allele_number):
    """
    Compute the approximate *log10* of the total number of connection
    configurations.

    Parameters
    ----------
    allele_number: list
        List of the number of possible connections at each terminal.

    Returns
    -------
    int
        Integer approximation of the *log10* of the total number of connection
        configurations.
    """

    configuration_number_exponent = 0

    for A in allele_number:
        if A == 0:
            raise NoConnectionError("At least one terminal has no connection.")
        else:
            configuration_number_exponent += np.log10(A)

    return int(configuration_number_exponent)


def set_allele_number(terminals):
    """
    Counts the number of possible connection at each terminal.

    Parameters
    ----------
    terminals: DataFrame
        Dataframe of the terminals to connect to the graph.

    Returns
    -------
    list
        List of the number of possible connections at each terminal.
    """

    allele_number = [len(terminal["_id"]) for idx, terminal in terminals.iterrows()]

    configuration_number_exponent = get_configuration_number_exponent(allele_number)

    text = (
        "Discrete vector space of dimension d={} and total number of "
        "configuration 10^{} initialized."
    )
    log.info(text.format(len(allele_number), configuration_number_exponent))

    return allele_number


def init_individual_genes(allele_number):
    """
    Generate a random genes list.

    Parameters
    ----------
    allele_number: list
        List of the number of possible connections at each terminal.

    Returns
    -------
    list
        List of terminal single connections.
    """

    genes = [random.randint(0, A - 1) for A in allele_number]

    return genes


def init_population_genes(n, allele_number):
    """
    Generate random genes for the *n* individuals of the population according to
    the possible connections at each terminal *allele_number*.

    Parameters
    ----------
    n: int
        Population size.
    allele_number: list
        List of the number of possible connections at each terminal.

    Returns
    -------
    list
        List of *n* individual tuples (weight=None, genes).
    """

    population = [(None, init_individual_genes(allele_number)) for k in range(n)]

    return population


def get_statistics(population):
    """
    Get population weights mean and standard deviation.

    Parameters
    ----------
    population: list
        List of individual tuples (weight, genes).

    Returns
    -------
    float
        Mean of the population weights.
    float
        Standard deviation of the population weigths.
    """

    p = 1 / len(population)
    M1 = sum([p * weight for weight, genes in population])
    M2 = sum([p * weight ** 2 for weight, genes in population])
    V = M2 - M1 ** 2

    if V < 0:
        text = "Negative variance ({}) of the population weights."
        log.debug(text.format(V))

    return M1, np.sqrt(V)


def individual_mutation(individual, allele_number, mutation_rate, inbred=False):
    """
    Genes mutation of the given *individual*.

    Each gene is randomly mutated with probability *mutation_rate*.

    Parameters
    ----------
    individual: tuple = float, list
        Tuple of the individual weight and genes.
    allele_number: list
        List of the number of possible connections at each terminal.
    mutation_rate: float
        Rate of genes mutation. Must belong to the open interval (0,1).
    inbred: bool, optional
        True if the two parents are identical. Default is False

    Returns
    -------
    tuple = float, list
        Individual with weight reset to None and mutated genes.
    """

    # get weight and genes
    weight, genes = individual
    genes_ = genes.copy()

    count = 0
    for i, A in enumerate(allele_number):
        x = random.random()
        if x <= mutation_rate and A > 1:
            allele_set = set(range(A)) - set([genes_[i]])
            genes_[i] = random.sample(allele_set, 1)[0]
            count += 1

    if count == 0 and inbred:
        log.info("Inbred procreation lead to identical individual.")

    return (None, genes_)


def select_random_parents(parents):
    """
    Randomly select two parents from the parent population.

    If the two parents are identical the procreation is classified as 'inbred'.

    Parameters
    ----------
    parents: list
        Parents population.

    Returns
    -------
    tuple = float, list
        First parent individual.
    tuple = float, list
        second parent individual.
    bool
        True if the two parents are identical.
    """

    # loop to encourage diversity mating
    n = 10
    for i in range(n):
        mum, dad = random.sample(parents, 2)
        if not mum[0] == dad[0]:
            break

    # check inbred procreation
    if i == n - 1:
        inbred = True
    else:
        inbred = False

    return mum, dad, inbred


def procreate(mum, dad):
    """
    Gene mixing of the two parent individuals.

    Each gene of the children is either the one of its dad or its mum, with equal
    probability.

    Parameters
    ----------
    mum: tuple = float, list
        First parent individual.
    dad: tuple = float, list
        Second parent individual.

    Returns
    -------
    tuple = float, list
        Child individual with weight=None and a mixing of its parents genes.
    """

    child = (None, [])
    for i in range(len(mum[1])):
        x = random.randint(0, 1)
        if x == 0:
            child[1].append(mum[1][i])
        else:
            child[1].append(dad[1][i])

    return child


def reproduction(parents, allele_number, mutation_rate):
    """
    Production of a new individual out of the set of parents.

    Two parents are first selected, then mated and finally the child is mutated.

    Parameters
    ----------
    parents: list
        Parents population.
    allele_number: list
        List of the number of possible connections at each terminal.
    mutation_rate: float
        Rate of genes mutation. Must belong to the open interval (0,1).

    Returns
    -------
    tuple = float, list
        Child individual with weight=None and a mixing of its parents genes
        followed by a mutation.
    """

    mum, dad, inbred = select_random_parents(parents)
    child = procreate(mum, dad)
    child = individual_mutation(child, allele_number, mutation_rate, inbred)

    return child


def get_next_generation(elites, parents, n1, n, allele_number, mutation_rate):
    """
    Generate the next generation from the *elites* and *parents* populations.

    Parameters
    ----------
    elites: list
        Elites population.
    parents: list
        Parents population.
    n1: int
        Elites population size.
    n: int
        Population size.
    allele_number: list
        List of the number of possible connections at each terminal.
    mutation_rate: float
        Rate of genes mutation. Must belong to the open interval (0,1).

    Returns
    -------
    list
        List of individuals constituting the new generation.
    """

    elite_mutations = [
        individual_mutation(elite, allele_number, mutation_rate) for elite in elites
    ]
    children = [
        reproduction(parents, allele_number, mutation_rate) for i in range(n - n1)
    ]
    population = elite_mutations + children

    return population


def select_elites_and_parents(population, elites, n1, n2):
    """
    Select the new elites and parents from the whole *population* and old
    *elites*.

    Parameters
    ----------
    population: list
        List of individuals constituting the population.
    elites: list
        Elites population.
    n1: int
        Elites population size.
    n2: int
        Parents population size.

    Returns
    -------
    list
        New elites population.
    list
        New parents population.
    """

    noitalupop = get_list_transpose(population)

    if elites is None:
        sample = noitalupop
    else:
        setile = get_list_transpose(elites)
        sample = [noitalupop[0] + setile[0], noitalupop[1] + setile[1]]

    # sort the weight and get their index
    index = sorted(range(len(sample[0])), key=lambda k: sample[0][k])
    # sort the individuals
    elites = [(sample[0][i], sample[1][i]) for i in index[0:n1]]
    parents = [(sample[0][i], sample[1][i]) for i in index[0:n2]]

    return elites, parents


def init_evolution_dataframe(N, save_population):
    """
    Initilization of the dataframe to save the population evolution.

    Parameters
    ----------
    N: int
        Number of generation.
    save_population: bool
        True if each generation population must be saved.

    Returns
    -------
    DataFrame
        Dataframe of the population evolution.
    """

    if save_population:
        columns = ["weight", "mean", "stddev", "genes", "population"]
    else:
        columns = ["weight", "mean", "stddev", "genes"]

    evolution = pd.DataFrame(columns=columns, index=range(N))

    return evolution


def save_generation(i, evolution, population, elites, save_population):
    """
    Update the *evolution* dataframe with the informations on the current
    generation ; in-place.

    Parameters
    ----------
    i: int
        Generation number.
    evolution: DataFrame
        Dataframe of the population evolution.
    population: list
        List of individuals constituting the population.
    elites: list
        Elites population.
    save_population: bool
        True if the each generation population must be saved.
    """

    elites_ = elites.copy()
    population_ = population.copy()

    mean, stddev = get_statistics(population)
    evolution.at[i, "weight"] = elites_[0][0]
    evolution.at[i, "mean"] = mean
    evolution.at[i, "stddev"] = stddev
    evolution.at[i, "genes"] = elites_[0][1]
    if save_population:
        evolution.at[i, "population"] = population_


def run_evolution(
    vertices,
    terminals,
    N,
    n=64,
    n1=8,
    n2=32,
    mutation_rate=0.1,
    save_population=False,
    pool_number=6,
):
    """
    Evolves a sample of *n* configurations of single terminal connections seeking
    for the lowest Terminal Steiner Tree (TST) weight.

    The algorithm swipes the space of single connections

    .. math::
        V = \otimes_{i=0}^{d-1} \:\: \{0,\cdots,A_i-1\}

    namely the discrete space of dimension d = *# of terminals* with each direction
    spanned by the integers between 0 and A_i, with A_i = *# of
    possible connection to terminal i*.

    A set a *n* vectors is first chosen randomly and then evolved through the
    configuration space generation after generation. At each generation, the *n2*
    best individuals (*parents*) reproduce amongst themselves as couples. These
    *n-n1* children as well as the *n1* best individual (*elites*) of the
    previous generation then undergo a gene mutation of parameter *mutation_rate*.

    Parameters
    ----------
    vertices: DataFrame
        Dataframe of the street graph plus the connection nodes.
    terminals: DataFrame
        Dataframe of the terminals to connect to the graph.
    N: int
        Number of generation.
    n: int
        Population size.
    n1: int
        Elite population size.
    n2: int
        Parent population size.
    mutation_rate: float
        Rate of genes mutation. Must belong to the open interval (0,1).
    save_population: bool
        True if each generation population must be saved.
    pool_number: int, optional
        Number of processes working in parallel. Default is 6.

    Returns
    -------
    evolution: DataFrame
        Dataframe of the population evolution with the following structure:
            * INDEX: generation integers from 0 to *N*-1.
            * COLUMNS:
                - 'weight': weight of the best individual,
                - 'mean': mean weight of the population,
                - 'stddev': standard deviation of the population weights,
                - 'genes': genes of the best individual,
                - 'population': whole population weights and genes (only if
                  *save_population* is True).
    """

    assert parameters_compatibility(n, n1, n2, mutation_rate)
    terminals = remove_no_connection_terminals(terminals)
    assert dataframe_compatibility(vertices, terminals)

    # list the possible connection number of each leaf
    allele_number = set_allele_number(terminals)
    # generate initial random vector
    population = init_population_genes(n, allele_number)
    # initialize the storing lists
    evolution = init_evolution_dataframe(N, save_population)

    args = (vertices, terminals)
    elites = None
    # evolution
    for i in range(N):

        tic = time.time()
        # multiprocessing computation of weights of the Steiner trees associated
        # to each vector of the current generation
        with poolcontext(processes=pool_number) as pool:
            population = pool.map(partial(get_tree_weight, args=args), population)

        # select elites and parents by sorting the population
        elites, parents = select_elites_and_parents(population, elites, n1, n2)
        save_generation(i, evolution, population, elites, save_population)
        # prepare next generation
        population = get_next_generation(
            elites, parents, n1, n, allele_number, mutation_rate
        )

        tac = time.time()

        text = "generation {} / {} completed in {} seconds. Current best weight: {}"
        log.info(text.format(i + 1, N, round(tac - tic, 2), evolution.at[i, "weight"]))

    return evolution


def get_best_individual(evolution):
    """
    Select the best connections configuration of the whole evolution.

    Parameters
    ----------
    evolution: DataFrame
        Dataframe of the population evolution.

    Returns
    -------
    List of the genes (connection configuration) of the best individual.
    """

    N = len(evolution)
    genes = evolution.loc[N - 1, "genes"]

    return genes

def get_best_terminal_steiner_tree(vertices, terminals, evolution):
    """
    Find the TST dataframe with the smallest weight from those computed during
    the evolution.

    Parameters
    ----------
    vertices: DataFrame
        Dataframe of the street graph plus the connection nodes.
    terminals: DataFrame
        Dataframe of the terminals to connect to the graph.
    evolution: DataFrame
        Dataframe of the population evolution.

    Returns
    -------
    tst: DataFrame
        Dataframe of the best computed TST with the following structure:
            * INDEX: Integers.
            * COLUMNS:
                - 'idA': first vertex end node index,
                - 'idB': second vertex end node index,
                - 'pA': coordinates (shapely Point) of the node 'idA',
                - 'pB': coordinates (shapely Point) of the node 'idB',
                - 'weight': vertex weight,
                - 'geometry': vertex geometry.
    """

    genes = get_best_individual(evolution)
    tst_terminals = remove_no_connection_terminals(terminals)
    tst_vertices = connect_terminals(vertices, tst_terminals, genes)
    tst = get_terminal_steiner_tree(tst_vertices, tst_terminals)
    tst = nx.to_pandas_edgelist(tst, source="idA", target="idB")
    set_nodes_coordinates(tst)
    tst.drop(columns=["xA", "yA", "xB", "yB", "idE"], inplace=True)

    return tst


def set_nodes_coordinates(tst):
    """
    Find all TST nodes coordinates and save them as shapely Points ; in-place.

    The key 'pA' ('pB') correspond to the first (last) shapely Point of the edge
    geometry.

    Parameters
    ----------
    tst: DataFrame
        DataFrame of the TST edges.
    """

    tst["pA"] = None
    tst["pB"] = None

    for i, edge in tst.iterrows():

        line = edge["geometry"].xy
        pA = Point(line[0][0], line[1][0])
        pB = Point(line[0][-1], line[1][-1])
        tst.at[i, "pA"] = pA
        tst.at[i, "pB"] = pB


def get_genes_variation(evolution):
    """
    Measure the "distance" between each following pair of best genes.

    The distance is defined as the cosine of the angle between the two considered
    gene vectors. The closer the returned number is to one, the less variation.


    Parameters
    ----------
    evolution: DataFrame
        Dataframe of the population evolution.

    Returns
    -------
    list
        List of number between 0 and 1 representing the distance between each
        following genes pairs.
    """

    genes = evolution["genes"]
    n = len(genes)

    genes_variation = list()
    for i in range(1, n):
        gene1 = np.array(genes[i - 1])
        gene2 = np.array(genes[i])
        d = normalized_inner_product(gene1, gene2)
        genes_variation.append(d)

    return genes_variation


def show_evolution_statistics(evolution):
    """
    Plot the evolution of the best weight, the mean weight, the standard
    deviation and the genes variations.

    The gene variation is defined as the cosine of the angle between the best
    gene of a generation and the best gene of its previous generation. The number
    lies between 0 and 1. The closer iit is to 0, the more mutation there is.

    Parameters
    ----------
    evolution: DataFrame
        Dataframe of the population evolution.
    """

    genes_variation = get_genes_variation(evolution)

    fig, ax = plt.subplots(3, figsize=(9, 12))

    ax[0].plot(
        evolution["weight"], marker="o", Linestyle="--", color="C0", label="best weight"
    )
    ax[0].plot(
        evolution["mean"], marker="o", Linestyle="--", color="C1", label="mean weight"
    )
    ax[0].set_xlabel("generation number", fontsize=14)
    ax[0].set_ylabel("TST weight", fontsize=14)
    ax[0].legend(loc="best", fontsize=14)
    ax[1].plot(evolution["stddev"], marker="o", Linestyle="--", color="C0")
    ax[1].set_xlabel("generation number", fontsize=14)
    ax[1].set_ylabel("TST standard deviation", fontsize=14)
    ax[2].plot(genes_variation, marker="o", Linestyle="--", color="C0")
    ax[2].set_xlabel("generation number", fontsize=14)
    ax[2].set_ylabel("best gene variation", fontsize=14)

    plt.show()
