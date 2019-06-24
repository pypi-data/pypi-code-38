#!/usr/bin/env python
# -*- coding: utf-8 -*-
import networkx as nx
import numpy as np
import geopandas as gpd
import matplotlib.pyplot as plt

from dhd.utils import get_moment


def plot_district_heating_network(pipelines, plot, loc="upper center"):
    """
    Plot the geometries of the district heating network on the plot interface.

    Parameters
    ----------
    pipeplines: GeoDataFrame
        Geodataframe of the district heating network.
    plot: dhd.plot.Plot
        Plot interface of the considered city.
    loc: tuple, optional
        Location of the legend box. Default is *loc* = 'upper center'.
    """

    label = "District Heating Network"
    kwargs = {"color": "black", "linewidth": 1.5}

    plot.add_geodataframe(pipelines, kwargs)
    plot.add_legend([kwargs["color"]], [label], "line", loc=loc)


def plot_terminals(terminals, plot, indices=None, loc="lower left"):
    """
    Plot the geometries of the sinks on the plot interface.

    The connected sinks are green and the disconnected sinks are red.

    Depending on the type of *indices* all geometries, a series of geometries or
    only one geometry are plotted.

    Parameters
    ----------
    terminals: GeoDataFrame
        Geodataframe of the terminals.
    plot: dhd.plot.Plot
        Plot interface of the considered city.
    indices: None or list or string, optional
        Indices of the sinks to plot. It may be a list or only one index. If
        None all geometries are plotted. Default is None.
    loc: tuple, optional
        Location of the legend box. Default is *loc* = 'lower left'.

    """

    if indices is None:
        gdf = gpd.GeoDataFrame(terminals)
    elif type(indices) == list:
        gdf = gpd.GeoDataFrame(terminals.loc[indices])
    else:
        gdf = gpd.GeoDataFrame(terminals.loc[[indices]])

    gdf = gdf.loc[gdf["kind"] == "sink"]
    gdf1 = gdf.loc[gdf["connected"] == True]
    gdf2 = gdf.loc[gdf["connected"] == False]

    colors = ["green", "red"]
    labels = ["connected", "disconnected"]
    kwargs1 = {"color": colors[0]}
    kwargs2 = {"color": colors[1]}

    plot.add_geodataframe(gdf1, kwargs1)
    plot.add_geodataframe(gdf2, kwargs2)
    plot.add_legend(colors, labels, "patch", loc=loc)


def get_connection_path(pipelines, id1, id2):
    """
    Find the path between two terminals and return the selection of the dataframe
    *pipeplines* referring to it.

    Parameters
    ----------
    pipelines: GeoDataFrame
        Geodataframe of the pipelines.
    id1: string
        Index of the first terminal.
    id2: string
        Index of the second terminal.

    Returns
    -------
    GeoDataFrame
        Selection of the dataframe *pipelines* referring to the connection path.
    """

    pipelines_ = pipelines.reset_index()
    graph = nx.from_pandas_edgelist(
        pipelines_, source="idA", target="idB", edge_attr=["weight", "index"]
    )
    path = nx.shortest_path(graph, id1, id2, weight="weight")

    indices = list()
    for i in range(len(path) - 1):
        idA = path[i]
        idB = path[i + 1]
        indices.append(graph[idA][idB]["index"])

    connection_path = pipelines.loc[indices]

    return connection_path


def get_column_statistics(df, key):
    """
    Compute the mean and the standard deviation of the data stored in the column
    *key* of the dataframe *df*.

    Parameters
    ----------
    df: DataFrame
    key: string
        Key of the column of interest.

    Returns
    -------
    float
        Mean of the data.
    float
        Standard deviation of the data.
    """

    data = list(df[key])
    m1 = get_moment(data, 1)
    m2 = get_moment(data, 2)

    mean = m1
    stddev = np.sqrt(m2 - m1 ** 2)

    return mean, stddev


def get_statistics(pipelines, keys=None):
    """
    Print the statistics (mean and standard deviation) of the different columns
    of the dataframe *pipelines*.

    Parameters
    ----------
    pipelines: GeoDataFrame
        Geodataframe of the pipelines.
    keys: list, optional
        List of the columns statistics to print. If None all the numeric columns
        are considered. Default is None.
    """

    if keys is None:
        keys = ["length", "weight", "load", "n_sink", "diameter"]

    print("Statistics of the pipelines:\n")
    for key in keys:
        mean, stddev = get_column_statistics(pipelines, key)
        text = "{}: mean = {} / standard deviation = {}.\n"
        print(text.format(key, mean, stddev))


def plot_distribution(pipelines, key, bins=20, color="C1"):
    """
    Plot the distribution of the data of the column *key* of the dataframe
    *pipelines* on a histogram.

    Parameters
    ----------
    pipelines: GeoDataFrame
        Geodataframe of the pipelines.
    key: string
        Key of the column of interest.
    bins: int, optional
        Number of bars in the histogram. Default is 20.
    color: string
        Color of the histogram. Default is 'C1'.
    """

    fig, ax = plt.subplots(figsize=(6, 4))

    data = [x for x in pipelines[key]]
    plt.hist(data, bins=bins, color=color)
    ax.set(xlabel=key, ylabel="# of occurences")

    plt.show()


def get_intersection_number(pipelines, terminals):
    """
    Compute the number of intersections in the district heating network.

    Parameters
    ----------
    pipelines: DataFrame
        Dataframe of the district heating network.
    terminals: DataFrame
        Dataframe of the terminals.

    Returns
    -------
    int
        Number of intersections.
    """

    sA = set(pipelines["idA"])
    sB = set(pipelines["idB"])
    s = sA.union(sB)
    n1 = len(s)
    n2 = len(terminals.loc[terminals["connected"] == True])
    n = n1 - n2

    return n
