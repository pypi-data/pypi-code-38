#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
import pandas as pd
import geopandas as gpd
import networkx as nx
from shapely.geometry import Point, LineString, MultiLineString
from shapely import ops

from dhd.logs import log
from dhd.utils import reverse_linestring
from dhd.exceptions import SourceError, NoMorePipe


def init_pipes(tst):
    """
    Convert the dataframe *tst* into its graph with source 'idA' and target 'idB'.

    *tst* must come with the columns 'geometry', 'weight', 'pA' and 'pB'. Two
    arguments ('load', 'n_sink') are added to the graph edges and set to 0.

    Parameters
    ----------
    tst: DataFrame
        DataFrame of the Terminal Steiner Tree.

    Returns
    -------
    Graph
        Graph of the Terminal Steiner Tree.

    """

    # construct the graph
    pipes = nx.from_pandas_edgelist(
        tst, source="idA", target="idB", edge_attr=["geometry", "weight", "pA", "pB"]
    )
    # initialize load and n_sink
    nx.set_edge_attributes(pipes, 0, "load")
    nx.set_edge_attributes(pipes, 0, "n_sink")

    return pipes


def init_terminals(terminals):
    """
    Initialize the dataframe of the terminals (*terminals*) by removing the
    columns '_id', '_geometry', '_weight' and adding the column 'connected' ;
    in-place.

    The 'connected' column is filled with booleans, True if the terminal is
    connected to the district heating network and false otherwise.

    Parameters
    ----------
    terminals: DataFrame
        Dataframe of the terminals as returned by the module *dhd.evolve*, namely
        with all possible connections.
    """

    terminals["connected"] = True
    for idx, terminal in terminals.iterrows():
        if len(terminal["_id"]) == 0:
            terminals.at[idx, "connected"] = False

    terminals.drop(columns=["_id", "_geometry", "_weight"], inplace=True)


def get_source_index(terminals):
    """
    Find the source index in the terminals dataframe.

    If there is no source or if it is not unique, an error is raised.

    Parameters
    ----------
    terminals: DataFrame
        Dataframe of the terminals.

    Returns
    -------
    string
        Index of the terminal dataframe referring to the unique source.
    """

    # check that there is a unique source
    sources = terminals.loc[terminals["kind"] == "source"]
    if len(sources) == 0:
        raise SourceError("No source in the system.")
    elif len(sources) > 1:
        raise SourceError("Impossible to treat more than one source.")
    else:
        idS = sources.index[0]

    return idS


def update_loads(shortest_path, pipes, terminal):
    """
    Update the loads of all pipes on the shortest path between the considered
    *terminal* and the source ; in-place.

    The attributes 'load' and 'n_sink' of each pipes on the path are
    respectively incremented by the load of the selected building and one.

    Parameters
    ----------
    shortest_path: list
        List of the nodes on the shortest path.
    pipes: DataFrame
        Dataframe of the TST.
    terminal: Series
        Row of the dataframe *terminals* describing the considered terminal.
    """

    for i in range(len(shortest_path) - 1):
        idA = shortest_path[i]
        idB = shortest_path[i + 1]
        pipes[idA][idB]["load"] += terminal["load"]
        pipes[idA][idB]["n_sink"] += 1


def add_terminal_to_pipes(pipes, terminal, idS):
    """
    Add the load of *terminal* to the dataframe *pipes* ; in-place.

    The shortest path between the source and *terminal* is first computed and
    then all pipes on the way are updated.

    Parameters
    ----------
    pipes: DataFrame
        Dataframe of the TST.
    terminal: Series
        Row of the dataframe *terminals* describing the considered terminal.
    idS: string
        Index of the dataframe *terminals* referring to the unique source.
    """

    idA = terminal.name
    shortest_path = nx.shortest_path(pipes, idS, idA, weight="weight")
    update_loads(shortest_path, pipes, terminal)


def pipes_to_dataframe(tst, pipes):

    pipes_ = tst.copy()
    pipes_["load"] = 0
    pipes_["n_sink"] = 0

    for idx, pipe_ in pipes_.iterrows():
        idA, idB = pipe_["idA"], pipe_["idB"]
        edge = pipes[idA][idB]
        pipes_.loc[idx, "load"] = edge["load"]
        pipes_.loc[idx, "n_sink"] = edge["n_sink"]

    return pipes_


def load_the_pipes(tst, terminals):
    """
    Define a dataframe of the pipes (edges) of the TST with loads associated to
    the number of served sinks and the served heating load.

    Parameters
    ----------
    tst: DataFrame
        DataFrame of the TST as returned by the module *dhd.evolve*.
    terminals: DataFrame
        Dataframe of the terminals as returned by the module *dhd.evolve*, namely
        with all possible connections.

    Returns
    -------
    DataFrame
        Dataframe of the TST with the edges loads.
    """

    pipes = init_pipes(tst)
    init_terminals(terminals)
    idS = get_source_index(terminals)
    for idx, terminal in terminals.loc[terminals["connected"] == True].iterrows():
        add_terminal_to_pipes(pipes, terminal, idS)

    pipes = pipes_to_dataframe(tst, pipes)

    return pipes


def init_pipelines():
    """
    Initialize the dataframe *pipelines* used to store the pipelines, namely the
    merged pipes of identical load.

    Returns
    -------
    DataFrame
        Empty dataframe with columns 'idA', 'idB', 'length', 'weight',
        'geometry', 'load', 'n_sink', 'pA', 'pB'.
    """

    pipelines = pd.DataFrame(
        columns=[
            "idA",
            "idB",
            "length",
            "weight",
            "geometry",
            "load",
            "n_sink",
            "pA",
            "pB",
        ]
    )

    return pipelines


def select_pipes(pipes):
    """
    Select pipes which have the same load as the first pipe of the dataframe
    *pipes*.

    Parameters
    ----------
    pipes: DataFrame
        Dataframe of the TST pipes.

    Returns
    -------
    DataFrame
        Dataframe of the selected pipes (same load as the first pipe).
    """

    load = pipes.at[0, "load"]
    pipes_selection = pipes.loc[pipes["load"] == load].copy()

    return pipes_selection


def remove_pipes(pipes, pipes_selection):
    """
    Remove the selected pipes (*pipes_selection*) from the dataframe *pipes* ;
    in-place

    Parameters
    ----------
    pipes: DataFrame
        Dataframe of the TST pipes.
    pipes_selection:
        Dataframe of the selected pipes (same load as the first pipe).
    """

    pipes.drop(index=pipes_selection.index, inplace=True)
    pipes.reset_index(inplace=True, drop=True)


def get_first_end(pipes_selection):
    """
    Find an end node of one of the pipelines to build with the pipes from
    *pipes_selection*.

    Look for a node which occurs only once amongst the ends of the pipes of
    *pipes_selection*. If this node is match to the label 'A' ('B') *reverse* is
    set to True (False).

    Parameters
    ----------
    pipes_selection:
        Dataframe of the selected pipes (same load as the first pipe).

    Returns
    -------
    int
        Index of the dataframe *pipes_selection* referring to the end node.
    bool
        True (False) if the node is at the 'A' ('B') end.
    """

    # list of all the node coordinates (shapely Point)
    points = list(pipes_selection["pB"]) + list(pipes_selection["pA"])

    for idx, pipe in pipes_selection.iterrows():

        # count number of appearence of the same node
        countA, countB = 0, 0
        for point in points:
            if point == pipe["pA"]:
                countA += 1
            if point == pipe["pB"]:
                countB += 1

        if countA == 1:
            reverse = False
            break

        if countB == 1:
            reverse = True
            break

    return idx, reverse


def add_next_pipe(ordered_pipes, pipe, reverse):
    """
    Append *pipe* to the dataframe *ordered_pipes* ; in-place.

    Parameters
    ----------
    ordered_pipes: DataFrame
        Dataframe of the pipes belonging to the same pipeline disposed from one
        pipeline end to the other.
    pipe: Series
        Row of the TST dataframe *pipes* corresponding to the pipe to append.
    reverse: bool
        True if the pipe LineString must be inversed.
    """

    n = len(ordered_pipes)
    ordered_pipes.loc[n] = pipe
    if reverse == True:

        ordered_pipes.at[n, "idA"] = pipe["idB"]
        ordered_pipes.at[n, "idB"] = pipe["idA"]
        ordered_pipes.at[n, "pA"] = pipe["pB"]
        ordered_pipes.at[n, "pB"] = pipe["pA"]
        ordered_pipes.at[n, "geometry"] = reverse_linestring(pipe["geometry"])


def remove_pipe_from_pipes_selection(pipes_selection, idx):
    """
    Remove the pipe of index *idx* from the dataframe of pipes of equal load ;
    in-place.

    Parameters
    ----------
    pipes_selection: DataFrame
        Dataframe of the selected pipes (same load as the first pipe).
    idx: int
        Index of the pipe to remove.
    """

    pipes_selection.drop(index=[idx], inplace=True)
    pipes_selection.reset_index(inplace=True, drop=True)


def find_next_pipe(pipes_selection, ordered_pipes):
    """
    Find the pipe connected to the 'B' node of the last pipe of the dataframe
    *ordered_pipes* from the dataframe *pipes_selection*.

    Parameters
    ----------
    pipes_selection: DataFrame
        Dataframe of the selected pipes (same load as the first pipe).
    ordered_pipes: DataFrame
        Dataframe of the pipes belonging to the same pipeline disposed from one
        pipeline end to the other.

    Returns
    -------
    int
        Index of the next pipe.
    Series
        Row of the dataframe *pipes_selection* of the next pipe.
    bool
        True if the pipe LineString must be reversed.
    """

    idB = ordered_pipes.loc[len(ordered_pipes) - 1, "idB"]

    reverse = False
    pipe = pipes_selection.loc[pipes_selection["idA"] == idB]
    if len(pipe) == 0:
        reverse = True
        pipe = pipes_selection.loc[pipes_selection["idB"] == idB]
        if len(pipe) == 0:
            raise NoMorePipe

    idx = pipe.index[0]
    pipe = pipe.iloc[0]

    return idx, pipe, reverse


def get_ordered_pipes(pipes_selection):
    """
    Classify the selected pipes (rows of *pipes_selection*) from the one
    pipeline end to the other.

    Parameters
    ----------
    pipes_selection: DataFrame
        Dataframe of the selected pipes (same load as the first pipe).

    Returns
    -------
    DataFrame
        Dataframe of the pipes belonging to the same pipeline disposed from one
        pipeline end to the other.
    """

    ordered_pipes = pd.DataFrame(columns=pipes_selection.columns)

    idx, reverse = get_first_end(pipes_selection)
    pipe = pipes_selection.loc[idx]
    remove_pipe_from_pipes_selection(pipes_selection, idx)
    add_next_pipe(ordered_pipes, pipe, reverse)

    while True:
        try:
            idx, pipe, reverse = find_next_pipe(pipes_selection, ordered_pipes)
            remove_pipe_from_pipes_selection(pipes_selection, idx)
            add_next_pipe(ordered_pipes, pipe, reverse)
        except NoMorePipe:
            break

    return ordered_pipes


def get_pipeline_geometry(ordered_pipes):
    """
    Merge the geomteries of the pipes belonging to the same pipeline into a
    unique LineString geometry.

    Parameters
    ----------
    ordered_pipes: DataFrame
        Dataframe of the pipes belonging to the same pipeline disposed from one
        pipeline end to the other.

    Returns
    -------
    LineString
        Geometry of the pipeline.
    """

    lines = [pipe["geometry"] for i, pipe in ordered_pipes.iterrows()]
    line = MultiLineString(lines)
    line = ops.linemerge(line)

    return line


def stick_ordered_pipes(ordered_pipes):
    """
    Merge all pipes of a pipeline.

    Parameters
    ----------
    ordered_pipes: DataFrame
        Dataframe of the pipes belonging to the same pipeline disposed from one
        pipeline end to the other.

    Returns
    -------
    Series
        Row of the dataframe *pipelines* with information on the pipeline to add.
    """

    n = len(ordered_pipes)
    idA = ordered_pipes.at[0, "idA"]
    idB = ordered_pipes.at[n - 1, "idB"]
    pA = ordered_pipes.at[0, "pA"]
    pB = ordered_pipes.at[n - 1, "pB"]
    weight = ordered_pipes["weight"].sum()
    line = get_pipeline_geometry(ordered_pipes)
    length = line.length
    load = ordered_pipes.at[0, "load"]
    n_sink = ordered_pipes.at[0, "n_sink"]

    pipeline = pd.Series(
        [idA, idB, length, weight, line, load, n_sink, pA, pB],
        index=[
            "idA",
            "idB",
            "length",
            "weight",
            "geometry",
            "load",
            "n_sink",
            "pA",
            "pB",
        ],
    )

    return pipeline


def construct_pipeline(pipes_selection):
    """
    Find the pipes belonging to the same pipeline in the dataframe
    *pipes_selection* and stick them together to form a pipeline.

    Parameters
    ----------
    pipes_selection: DataFrame
        Dataframe of the selected pipes (same load as the first pipe).

    Returns
    -------
    Series
        Row of the dataframe *pipelines* with information on the pipeline to add.
    """

    ordered_pipes = get_ordered_pipes(pipes_selection)
    pipeline = stick_ordered_pipes(ordered_pipes)

    return pipeline


def add_pipelines(pipelines, pipes):
    """
    Select pipes belonging to the same pipeline, construct the pipelines and add
    them to the dataframe *pipelines* ; in-place.

    Once the pipes have been selected they are removed from the dataframe *pipes*.

    Its is possible to select and construct multiple pipelines if they have the
    same load.

    Parameters
    ----------
    pipelines: DataFrame
        Dataframe of the TST pipelines.
    pipes: DataFrame
        Dataframe of the TST pipes.
    """

    pipes_selection = select_pipes(pipes)
    remove_pipes(pipes, pipes_selection)
    while len(pipes_selection) > 0:
        pipeline = construct_pipeline(pipes_selection)
        pipelines.loc[len(pipelines)] = pipeline


def order_geometries(pipes):
    """
    Inverse all edges geometry which direction is opposite to its associated
    edge end coordinates 'pA' and 'pB' ; in-place.

    Parameters
    ----------
    pipes: DataFrame
        Dataframe of the TST pipes.
    """

    for i, pipe in pipes.iterrows():
        if not pipe["pA"].xy[0][0] == pipe["geometry"].xy[0][0]:
            line = reverse_linestring(pipe["geometry"])
            pipes.at[i, "geometry"] = line


def get_diameter_function(unit, rho, cp, vmax, dT):
    """
    Define the standard diameter function, which returns the diameter of a
    pipeline depending on its heating load.

    Parameters
    ----------
    unit: string, optional
        Unit of the load power: 'kW' for kilowatts or 'W' for watts. Default is
        'kW'.
    rho: float, optional
        Mass density of the pipelines liquid in [kg/m^3]. Default is 1000.
    cp: float, optional
        Isobaric heat capacity of the pipelines liquide in [kJ/kg/K]. Default is
        4.18.
    vmax: float, optional
        Design flow velocity in [m/s]. Default is 2.
    dT: float, optional
        Temperature difference between the supply and return pipe networks if
        [K]. Default is 30.

    Returns
    -------
    function
        Diameter function which returns the diameter of a pipeline depending on
        its heating load.
    """

    if unit == "kW":
        func = lambda power: 2 * np.sqrt(power / (np.pi * rho * vmax * cp * dT))
    elif unit == "W":
        func = lambda power: 2 * np.sqrt(power / 1000 / (np.pi * rho * vmax * cp * dT))
    else:
        raise SyntaxError("'unit' must either be 'kW' or 'W'.")

    return func


def set_diameter(
    pipelines, diameter_function=None, unit="kW", rho=1000, cp=4.18, vmax=2, dT=30
):
    """
    Compute the diameters of the pipelines according to a function depending on
    its heating load ; in-place.

    If not provided the standard relation

    .. math::
        P [kW] = \dot{m} [kg/s]\: c_p[kJ/kg/K]\: \Delta T[K]

    is used to define the diameter function.

    Parameters
    ----------
    diameter_function: function
        Function of a pipeline heating load returning its diameter. If not
        specified the standard function from *dhd.load.get_diameter_function* is
        used. Default is None.
    unit: string, optional
        Unit of the load power: 'kW' for kilowatts or 'W' for watts. Default is
        'kW'.
    rho: float, optional
        Mass density of the pipelines liquid in [kg/m^3]. Default is 1000.
    cp: float, optional
        Isobaric heat capacity of the pipelines liquide in [kJ/kg/K]. Default is
        4.18.
    vmax: float, optional
        Design flow velocity in [m/s]. Default is 2.
    dT: float, optional
        Temperature difference between the supply and return pipe networks if
        [K]. Default is 30.
    """

    if diameter_function is None:
        diameter_function = get_diameter_function(unit, rho, cp, vmax, dT)

    pipelines["diameter"] = 0
    for idx, pipeline in pipelines.iterrows():
        diameter = diameter_function(pipeline["load"])
        pipelines.loc[idx, "diameter"] = diameter


def get_nominal_diameter(pipe_catalogue, diameter, DN, ID):
    """
    Compute the nominal diameter associated to a metric diameter according to
    the provided catalogue.

    The metric diameter predicted by the module is matched to the nominal pipe
    with the minimal superior inner diameter.

    Parameters
    ----------
    pipelines: DataFrame
        Dataframe of the TST pipelines.
    pipe_catalogue: DataFrame
        Catalogue of the nominal pipe size. It must at least contain a column
        of nominal diameters (*DN*) and a column of inner diameters (*ID*).
    DN: string
        Name of the nominal diameter column.
    ID: string
        Name of the inner diameter column.
    """

    d = 1000 * diameter

    nominal_diameter = None
    for idx, pipe in pipe_catalogue.iterrows():
        if d <= pipe[ID]:
            nominal_diameter = pipe_catalogue.at[idx, DN]
            break

    return nominal_diameter


def set_nominal_diameter(pipelines, pipe_catalogue, DN="DN", ID="ID"):
    """
    Add a column of nominal diameters to the pipelines dataframe.

    The metric diameter predicted by the module is matched to the nominal pipe
    with the minimal superior inner diameter as listed in the dataframe
    *pipe_catalogue*.

    Parameters
    ----------
    pipe_catalogue: DataFrame
        Catalogue of the nominal pipe size. It must at least contain a column
        of nominal diameters (*DN*) and a column of inner diameters (*ID*).
    diameter: float
        Metric diameter predicted by the module.
    DN: string, optional
        Name of the nominal diameter column. Default is 'DN'.
    ID: string, optional
        Name of the inner diameter column. Default is 'ID'.
    """

    pipelines["nominal_diameter"] = 0
    for idx, pipeline in pipelines.iterrows():
        diameter = pipeline["diameter"]
        nominal_diameter = get_nominal_diameter(pipe_catalogue, diameter, DN, ID)
        pipelines.loc[idx, "nominal_diameter"] = nominal_diameter
        if nominal_diameter is None:
            text = (
                "The pipeline {} diameter exceeds the range of the given " "catalogue."
            )
            log.info(text.format(idx))


def check_neighbor_terminals(pipelines, terminals):

    terminals_id = set(terminals.index)
    for idx, pipeline in pipelines.iterrows():
        idA, idB = pipeline["idA"], pipeline["idB"]
        if (idA in terminals_id) and (idB in terminals_id):
            text = (
                "The neighbour terminals {} and {} have the same load. This "
                "lead to the omission of a pipeline intersection. Please "
                "alter slightly one of the two loads to solve the issue. "
                "You can use the function 'dhd.modify.replace_sinks_load'."
            )
            log.info(text.format(idA, idB))


def load_the_pipelines(tst, terminals):
    """
    Function to class the pipes into pipelines and store them in a dataframe.

    A pipeline is a series of pipes connecting two droppings (sinks or
    intersections). All the pipes of a pipeline share the same *load* and
    serve the same number of sikns *n_sink*. The length (weight) of a pipeline
    are given by the sum of the length (weight) of its constituent pipes.

    Parameters
    ----------
    tst: DataFrame
        DataFrame of the Terminal Steiner Tree.
    terminals: DataFrame
        Dataframe of the terminals.

    Returns
    -------
    pipelines: GeoDataFrame
        Dataframe of the TST pipelines with the following structure:
            * INDEX: Integers.
            * COLUMNS:
                - 'idA': first pipeline end node index,
                - 'idB': second pipeline end node index,
                - 'pA': coordinates (shapely Point) of the node 'idA',
                - 'pB': coordinates (shapely Point) of the node 'idB',
                - 'length': pipeline length,
                - 'weight': pipeline weight,
                - 'load': heating load served by the pipeline,
                - 'n_sink': number of buildings served by the pipeline,
                - 'geometry': pipeline geometry.
    """

    # initialize the pipelines DataFrame
    pipelines = init_pipelines()

    pipes = load_the_pipes(tst, terminals)
    order_geometries(pipes)
    # loop over the pipes to store them in the pipelines
    while len(pipes) > 0:
        add_pipelines(pipelines, pipes)

    check_neighbor_terminals(pipelines, terminals)

    # DataFrame -> GeoDataFrame
    pipelines = gpd.GeoDataFrame(pipelines)

    return pipelines
