#!/usr/bin/env python
# -*- coding: utf-8 -*-

from shapely.geometry import Point
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt

from dhd.logs import log


def get_streets_selection(streets, p, R):
    """
    Select the streets from the dataframe *streets* within the distance *R* from
    the given point *p*.

    Parameters
    ----------
    streets: DataFrame
        Dataframe of the streets network.
    p: Point or tuple
        Coordinates of the given point.
    R: float, optional
        Maximal distance from the point so that a street is selected.

    Returns
    -------
    DataFrame
        Dataframe of the selected streets with indices from the dataframe
        *streets*.
    """

    index = list()
    for idx, street in streets.iterrows():
        line = street["geometry"]
        d = line.distance(p)
        if d < R:
            index.append(idx)

    streets_selection = streets.loc[index]

    return streets_selection


def plot_streets(streets_selection, plot):
    """
    Plot the selected streets on the axes of the *plot* instance together
    with a legend.

    Parameters
    ----------
    streets_selection: DataFrame
        Dataframe of the streets close enough to the considered point.
    plot: dhd.plot.Plot
        Plot instance associated to the considered city.
    """

    i = 0
    labels = list()
    colors = list()

    for idx, street_selection in streets_selection.iterrows():

        color = plt.cm.Dark2(i)
        labels.append("index: {}".format(idx))
        colors.append(color)
        kwargs = {"color": color, "linewidth": 2}
        i += 1

        gdf = gpd.GeoDataFrame([street_selection])
        plot.add_geodataframe(gdf, kwargs)

    plot.add_legend(colors, labels, "line", loc="upper left")


def find_streets_mutiple_points(streets, points, R=1, plot=None):
    """
    Find the streets within the distance *R* from the given list of points *points*.

    Plot the selection of streets on the axes of the *dhd.plot.Plot* instance
    *plot* if provided.

    Parameters
    ----------
    streets: DataFrame
        Dataframe of the streets network.
    points: list of Point or tuple
        Coordinates of the given points.
    R: float, optional
        Maximal distance from the point so that a street is selected. Default is
        1 meter.
    plot: dhd.plot.Plot, optional
        Plot instance associated to the considered city. Default is None.

    Returns
    -------
    DataFrame
        Dataframe of the selected streets with indices from the dataframe
        *streets*.
    """

    streets_selection = []
    for p in points:
        streets_selection.append(find_streets(streets, p, R=R))
        # plot points
        if plot is not None:
            plot_point(p, plot)

    streets_selection = gpd.GeoDataFrame(pd.concat(streets_selection))     
    
    # plot streets
    if plot is not None:        
        plot_streets(streets_selection, plot)

    return streets_selection


def find_streets(streets, p, R=1, plot=None):
    """
    Find the streets within the distance *R* from the given point *p*.

    Plot the selection of streets on the axes of the *dhd.plot.Plot* instance
    *plot* if provided.

    Parameters
    ----------
    streets: DataFrame
        Dataframe of the streets network.
    p: Point or tuple
        Coordinates of the given point.
    R: float, optional
        Maximal distance from the point so that a street is selected. Default is
        1 meter.
    plot: dhd.plot.Plot, optional
        Plot instance associated to the considered city. Default is None.

    Returns
    -------
    DataFrame
        Dataframe of the selected streets with indices from the dataframe
        *streets*.
    """

    try:
        x, y = p
        p = Point(x, y)
    except TypeError:
        text = "'point' must either be x/y coordinates or Point geometry."
        assert type(p) == Point, text

    streets_selection = get_streets_selection(streets, p, R)

    text = "{} streets found within {} meters of the point {}."
    log.info(text.format(len(streets_selection), R, p))

    if plot is not None:
        plot_point(p, plot)
        plot_streets(streets_selection, plot)

    return streets_selection


def multiply_streets_weight(streets, indices, ratios):
    """
    Multiply the weights of the rows of the dataframe *streets* with the given
    indices by the given ratios ; in-place.

    *indices* and *ratios* may either be singlets of lists.

    Parameters
    ----------
    streets: DataFrame
        Dataframe of the streets network.
    indices: int or list
        Index (or indices) of the street(s) which weight shall be changed.
    ratios: float or list
        Number(s) by which the associated street weight is multiplied and then
        replaced.
    """

    if type(indices) == list:
        text = "The lists 'indices' and 'ratios' must have the same length."
        assert len(indices) == len(ratios), text

        for index, ratio in zip(indices, ratios):
            streets.loc[index, "weight"] *= ratio

    elif type(indices) == int:
        streets.loc[indices, "weight"] *= ratios

    else:
        text = (
            "'indices' and 'ratios' must either be numbers or lists of "
            "numbers (int respectively float)."
        )
        raise TypeError(text)


def replace_streets_weight(streets, indices, weights):
    """
    Replace the weights of the rows of the dataframe *streets* with the given
    indices by the given weights ; in-place.

    *indices* and *weights* may either be singlets of lists.

    Parameters
    ----------
    streets: DataFrame
        Dataframe of the streets network.
    indices: int or list
        Index (or indices) of the street(s) which weight shall be changed.
    weights: float or list
        Number(s) by which the associated street weight are replaced.
    """

    if type(indices) == list:
        text = "The lists 'indices' and 'weights' must have the same length."
        assert len(indices) == len(weights), text

        for index, weight in zip(indices, weights):
            streets.loc[index, "weight"] = weight

    elif type(indices) == int:
        streets.loc[indices, "weight"] = weights

    else:
        text = (
            "'indices' and 'weights' must either be numbers or lists of "
            "numbers (int respectively float)."
        )
        raise TypeError(text)


def get_sinks_selection(sinks, p, R):
    """
    Select the sinks from the dataframe *sinks* within the distance *R* from
    the given point *p*.

    Parameters
    ----------
    sinks: DataFrame
        Dataframe of the sinks.
    p: Point or tuple
        Coordinates of the given point.
    R: float, optional
        Maximal distance from the point so that a street is selected.

    Returns
    -------
    DataFrame
        Dataframe of the selected sinks with indices from the dataframe
        *sinks*.
    """

    index = list()
    for idx, sink in sinks.iterrows():
        object = sink["geometry"]
        d = object.distance(p)
        if d < R:
            index.append(idx)

    sinks_selection = sinks.loc[index]

    return sinks_selection


def plot_sinks(sinks_selection, plot):
    """
    Plot the selected sinks centroids on the axes of the *plot* instance together
    with a legend.

    Parameters
    ----------
    sinks_selection: DataFrame
        Dataframe of the sinks close enough to the considered point.
    plot: dhd.plot.Plot
        Plot instance associated to the considered city.
    """

    i = 0
    labels = list()
    colors = list()

    for idx, sink_selection in sinks_selection.iterrows():

        color = plt.cm.Dark2(i)
        labels.append("index: {}".format(idx))
        colors.append(color)
        kwargs = {"color": color, "markersize": 20}
        i += 1

        gdf = gpd.GeoDataFrame([sink_selection])
        plot.add_geodataframe(gdf, kwargs, centroid=True)

    plot.add_legend(colors, labels, "point", loc="upper left")


def plot_point(p, plot):
    """

    """
    # TODO: add doc
    kwargs = {'color': 'black', 'marker': '+', 'markersize': 20}
    gdf = gpd.GeoDataFrame([[p]], columns=['geometry'])
    plot.add_geodataframe(gdf, kwargs)


def find_sinks(sinks, p, R=1, plot=None):
    """
    Find the sinks within the distance *R* from the given point *p*.

    Plot the selection of sinks on the axes of the *dhd.plot.Plot* instance
    *plot* if provided.

    Parameters
    ----------
    sinks: DataFrame
        Dataframe of the sinks.
    p: Point or tuple
        Coordinates of the given point.
    R: float, optional
        Maximal distance from the point so that a street is selected. Default is
        1 meter.
    plot: dhd.plot.Plot, optional
        Plot instance associated to the considered city. Default is None.

    Returns
    -------
    DataFrame
        Dataframe of the selected sinks with indices from the dataframe
        *sinks*.
    """

    try:
        x, y = p
        p = Point(x, y)
    except TypeError:
        text = "'point' must either be x/y coordinates or Point geometry."
        assert type(p) == Point, text

    sinks_selection = get_sinks_selection(sinks, p, R)

    text = "{} sinks found within {} meters of the point {}."
    log.info(text.format(len(sinks_selection), R, p))

    if plot is not None:
        plot_point(p, plot)
        plot_sinks(sinks_selection, plot)

    return sinks_selection


def multiply_sinks_load(sinks, indices, ratios):
    """
    Multiply the loads of the rows of the dataframe *sinks* with the given
    indices by the given ratios ; in-place.

    *indices* and *ratios* may either be singlets of lists.

    Parameters
    ----------
    sinks: DataFrame
        Dataframe of the sinks.
    indices: int or list
        Index (or indices) of the sink(s) which load shall be changed.
    ratios: float or list
        Number(s) by which the associated sinks load is multiplied and then
        replaced.
    """

    # TODO: add case where indices are list but ratios are int (numpy ?)

    if type(indices) == list:
        text = "The lists 'indices' and 'ratios' must have the same length."
        assert len(indices) == len(ratios), text

        for index, ratio in zip(indices, ratios):
            sinks.loc[index, "load"] *= ratio

    elif type(indices) == int:
        sinks.loc[indices, "load"] *= ratios

    else:
        text = (
            "'indices' and 'ratios' must either be numbers or lists of "
            "numbers (int respectively float)."
        )
        raise TypeError(text)


def replace_sinks_load(sinks, indices, loads):
    """
    Replace the loads of the rows of the dataframe *sinks* with the given
    indices by the given loads ; in-place.

    *indices* and *loads* may either be singlets of lists.

    Parameters
    ----------
    sinks: DataFrame
        Dataframe of the sinks.
    indices: int or list
        Index (or indices) of the sink(s) which load shall be changed.
    loads: float or list
        Number(s) by which the associated sinks load are replaced.
    """

    if type(indices) == list:
        text = "The lists 'indices' and 'loads' must have the same length."
        assert len(indices) == len(loads), text

        for index, load in zip(indices, loads):
            sinks.loc[index, "load"] = load

    elif type(indices) == int:
        sinks.loc[indices, "load"] = loads

    else:
        text = (
            "'indices' and 'loads' must either be numbers or lists of "
            "numbers (int respectively float)."
        )
        raise TypeError(text)


def add_streets():
    """TODO"""


def add_sinks(sinks, sinks_to_add, ignore_index=True):
    """
    Add new sinks to the dataframe *sinks*.

    Parameters
    ----------
    sinks: DataFrame
        Dataframe of the sinks.
    sinks_to_add: DataFrame
        Dataframe of the sinks to add.
    ignore_index: bool, optional
        If True, reset the indices to integers, else use the indices provided.
        Default is True.

    Returns
    -------
    DataFrame
        Appended dataframe of the sinks.
    """

    sinks_ = sinks.append(sinks_to_add, ignore_index=ignore_index)

    return sinks_


def remove_streets(streets, index):
    """
    Remove streets to the dataframe *streets*.

    Parameters
    ----------
    streets: DataFrame
        Dataframe of the streets.
    index: list
        List of indices of the streets to remove.

    Returns
    -------
    DataFrame
        Updated dataframe of the streets.
    """

    streets_ = streets.drop(index=index, inplace=False)
    streets_.reset_index(inplace=True)

    return streets_


def remove_sinks(sinks, index, ignore_index=True):
    """
    Remove sinks to the dataframe *sinks*.

    Parameters
    ----------
    sinks: DataFrame
        Dataframe of the sinks.
    index: list
        List of indices of the sinks to remove.
    ignore_index: bool, optional
        If True, reset the indices to integers, else use the indices provided.
        Default is True.

    Returns
    -------
    DataFrame
        Updated dataframe of the sinks.
    """

    sinks_ = sinks.drop(index=index, inplace=False)

    if ignore_index is True:
        sinks_.reset_index(inplace=True)

    return sinks_
