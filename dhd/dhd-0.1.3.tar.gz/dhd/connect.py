#!/usr/bin/env python
# -*- coding: utf-8 -*-


import pandas as pd
from shapely.geometry import Point, LineString
from shapely import ops
import numpy as np
import time
from collections import Counter

from dhd.logs import log
from dhd.utils import reverse_linestring, distance
from dhd.exceptions import GeometryError


def append_superpositions(superpositions, idx1, idx2):
    """
    Add indices *idx1* and *idx2* (associted to the new superposed sink) in the
    appropriate set of indices ; in-place.

    Parameters
    ----------
    superpositions: list
        List of sets. Each set arguments are the indices of the sinks located
        at a same location.
    idx1: int
        Index of the first superposed sink.
    idx2: int
        Index of the second superposed sink.
    """

    if len(superpositions) == 0:
        superpositions.append(set([idx1, idx2]))
    else:
        new_superposition = True
        for superposition in superpositions:
            if idx1 in superposition or idx2 in superposition:
                superposition.add(idx1)
                superposition.add(idx2)
                new_superposition = False
                break
        if new_superposition is True:
            superpositions.append(set([idx1, idx2]))


def order_superpositions(superpositions):
    """
    Put all superposition indices in one single list and remove one index from
    each superposition set.

    Parameters
    ----------
    superpositions: list
        List of sets. Each set arguments are the indices of the sinks located
        at a same location.

    Returns
    -------
    list
        List of indices associated to the rows to remove from the dataframe
        *sinks*.
    """

    indices = list()
    for superposition in superpositions:
        l = list(superposition)
        l.pop(0)
        indices += l

    return indices


def get_superpositions(sinks, epsilon):
    """
    Find the sets of sinks superpositions.

    Parameters
    ----------
    sinks: DataFrame
        Dataframe of the heating sinks.
    epsilon:
        Only sinks whose superposition area is larger than *epsilon* times the
        area of the smallest sink area are considered in superposition.

    Returns
    -------
    list
        List of sets. Each set arguments are the indices of the sinks located
        at a same location.
    """

    superpositions = []
    for idx1, sink1 in sinks.iterrows():
        for idx2, sink2 in sinks.iterrows():
            if idx2 < idx1:
                p1 = sink1["geometry"]
                p2 = sink2["geometry"]
                if p1.intersection(p2).area > epsilon * min(p1.area, p2.area):
                    append_superpositions(superpositions, idx1, idx2)

    return superpositions


def clean_superpositions(sinks, epsilon=0.01):
    """
    Remove superposed sinks.

    If multiple sink geometries are located at the same location (for example
    because of a bad time evolution documentation) only one of them is retained.

    Parameters
    ----------
    sinks: DataFrame
        Dataframe of the heating sinks.
    epsilon: float, optional
        Only sinks whose superposition area is larger than *epsilon* times the
        area of the smallest sink area are considered in superposition. Default
        is 0.01.

    Returns
    -------
    DataFrame
        Updated sinks dataframe.
    """

    sinks_ = sinks.reset_index(inplace=False)
    sinks_.columns = ["index"] + list(sinks_.columns[1:])
    superpositions = get_superpositions(sinks_, epsilon)
    indices = order_superpositions(superpositions)
    sinks_.drop(index=indices, inplace=True)

    if len(superpositions) > 0:
        text = "The following set of sinks were superposed: "
        for superposition in superpositions:
            text += "{}, ".format(superposition)
        text += "Only the first sink of each set is retained."
        log.warning(text)

    return sinks_.set_index("index", inplace=False)


def check_index_repetition(df):
    """
    Check that there is no repetition amongst the indices of the given dataframe.

    Parameters
    ----------
    df: DataFrame

    Returns
    -------
    bool
        True if the assertion is passed.
    """

    repetitions = {k: v for k, v in Counter(df.index).items() if v > 1}
    text = (
        "The following indices are repeated in the dataframe 'sinks' "
        "(index, # of occurences): {}"
    )
    assert len(repetitions) == 0, text.format(repetitions)

    return True


def check_data_structure(sinks, streets, sources, barriers, ignore_index):
    """
    Ensure that the provided dataframes have the required structure.

    Parameters
    ----------
    streets: DataFrame
        Dataframe of the street network.
    sinks: DataFrame
        Dataframe of the heating sinks.
    sources: DataFrame
        Dataframe of the heating source(s).
    barriers: DataFrame
        Dataframe of the natural barriers.

    Returns
    -------
    bool
        True if the assertion are passed.
    """

    text1 = "The dataframe '{}' must contain a geometry column: 'geometry'."
    text2 = "The dataframe '{}' must contain two index columns: 'idA' and 'idB'."
    assert {"geometry"}.issubset(sinks.columns), text1.format("sinks")
    assert {"geometry"}.issubset(streets.columns), text1.format("streets")
    assert {"geometry"}.issubset(sources.columns), text1.format("sources")
    if barriers is not None:
        assert {"geometry"}.issubset(barriers.columns), text1.format("barriers")
    assert {"idA", "idB"}.issubset(streets.columns), text2.format("streets")
    if ignore_index is False:
        check_index_repetition(sinks)

    return True


def set_line_coordinates(vertices):
    """
    Add coordinates columns ('xA','xB','yA','yB') to the dataframe *vertices* ;
    in-place.

    The end node coordinates of each geometry (edge) of *vertices* are
    computed and  stored in their associated column (first end -> 'A', second
    end -> 'B').

    Parameters
    ----------
    vertices: DataFrame
        Dataframe of the vertices.
    """

    for idx, row in vertices.iterrows():
        coords = list(row["geometry"].coords)
        vertices.at[idx, "xA"] = coords[0][0]
        vertices.at[idx, "yA"] = coords[0][1]
        vertices.at[idx, "xB"] = coords[-1][0]
        vertices.at[idx, "yB"] = coords[-1][1]


def connection_weight(line, func):
    """
    Return the weight of the connection *line* according to weight function
    *func*.

    If *func* is None, the weight is set equal to the connection length.

    Parameters
    ----------
    line: LineString
        Geometry of the connection.
    func: function
        Function of the connection length returning its weight.

    Returns
    -------
    float
        Weight of the connection.
    """

    if func is None:
        weight = line.length
    else:
        weight = func(line.length)

    return weight


def set_default_weight_to_length(vertices):
    """
    Add weight column to the dataframe *vertices* with element equal to the
    length of the associated geometry ; in-place.

    Parameters
    ----------
    vertices: DataFrame
        Dataframe of the vertices.
    """

    for idx, vertex in vertices.iterrows():
        vertices.loc[idx, "weight"] = vertex["geometry"].length


def init_vertices(streets):
    """
    Initilization of the dataframe *vertices* from the input dataframe *streets*.

    Parameters
    ----------
    streets: DataFrame
        Dataframe of the street network.

    Returns
    -------
    DataFrame
        Dataframe of the vertices.
    """

    vertices = streets.copy()

    # set coordinates
    if not {"xA", "yA", "xB", "yB"}.issubset(vertices.columns):
        set_line_coordinates(vertices)

    # set weights
    if not "weight" in vertices.columns:
        set_default_weight_to_length(vertices)

    # set edges indices
    vertices["idE"] = [
        "{}_{}".format(vertex["idA"], vertex["idB"])
        for i, vertex in vertices.iterrows()
    ]

    text = "Initilization of the dataframe 'vertices' with {} rows."
    log.info(text.format(len(vertices)))

    return vertices


def get_terminals_indices(sources, sinks, ignore_index):
    """
    List the indices of the dataframe *terminals* from the dataframes *sources*
    and *sinks*.

    If *index* is True, use the indices of the dataframes, otherwise generate
    new indices.

    Parameters
    ----------
    sources: DataFrame
        Dataframe of the heating source(s).
    sinks: DataFrame
        Dataframe of the sinks.
    ignore_index: bool
        If False, use indices from the dataframes *sources* and *sinks*,
        otherwise generate new indices.

    Returns
    -------
    list
        List of the dataframe *terminals* indices.
    """

    indices1 = [str(i) + "S" for i in range(len(sources))]

    if ignore_index == False:
        indices2 = list(sinks.index)
    else:
        indices2 = [str(i) + "B" for i in range(len(sinks))]

    indices = indices1 + indices2

    return indices


def init_terminals(sources, sinks, ignore_index):
    """
    Initialization of the dataframe *terminals* from the input dataframes *sinks*
    and *sources*.

    Parameters
    ----------
    sources: DataFrame
        Dataframe of the heating source(s).
    sinks: DataFrame
        Dataframe of the sinks.
    ignore_index: bool
        If False, use indices from the dataframes *sources* and *sinks*,
        otherwise generate new indices.

    Returns
    -------
    DataFrame
        Dataframe of the terminals.
    """

    # construct DataFrame structure
    indices = get_terminals_indices(sources, sinks, ignore_index)
    columns = ["_id", "_weight", "_geometry"]
    terminals = pd.DataFrame(columns=columns, index=indices)

    # fill in with empty lists
    for column in columns:
        terminals[column] = None
        for idx in terminals.index:
            terminals.loc[idx, column] = list()

    # add columns
    terminals["geometry"] = list(sources["geometry"].append(sinks["geometry"]))
    terminals["kind"] = ["source"] * len(sources) + ["sink"] * len(sinks)
    if "load" in sinks.columns:
        list1 = [0] * len(sources)
        list2 = list(sinks["load"])
        terminals["load"] = list1 + list2

    text = "Initilization of the dataframe 'terminals' with {} rows."
    log.info(text.format(len(terminals)))

    return terminals


def get_nearest_point(series1, series2):
    """
    Get tuple coordinates of the orthogonal projections between the geometries
    of the two given Series.

    Parameters
    ----------
    series1: Series
        Series with a geometry key.
    series2: Series
        Series with a geometry key.

    Returns
    -------
    tuple
        Coordinates of the projection on *series1* geometry,
    tuple
        Coordinates of the projection on *series2* geometry.
    """

    p1, p2 = ops.nearest_points(series1["geometry"], series2["geometry"])
    p1, p2 = p1.coords[0], p2.coords[0]

    return p1, p2


def is_crossing_a_barrier(p1, p2, barriers):
    """
    Check if the two points *p1* and *p2* are on the same side of the list of
    barriers *barriers*.

    Parameters
    ----------
    p1: tuple
        Coordinates of the first point.
    p2: tuple
        Coordinates of the second point.
    barriers: DataFrame
        Dataframe of the natural barriers.

    Returns
    -------
    bool
        True if the line *p1*-*p2* crosses the *barriers* geometry, False
        otherwise.
    """

    l = LineString([p1, p2])
    intersection = True in set([barrier.intersects(l) for barrier in barriers])

    return intersection


def first_selection(vertices, terminal, R, barriers):
    """
    Select the orthogonal projection on the edges of *vertices* within the
    distance *R* from the geometry of *terminal*.

    If not None the geometric constraint *barriers* prevent any connection
    crossing it.

    Parameters
    ----------
    vertices: DataFrame
        Dataframe of the vertices.
    terminal: Series
        Row of the *terminal* dataframe.
    R: float
        Maximal connection length.
    barriers: DataFrame
        Dataframe of the natural barriers.

    Returns
    -------
    DataFrame
        Dataframe of the selected connections with columns:
            - 'idA': fist connection edge node index,
            - 'idB': second connection edge node index,
            - 'idE': connection edge index,
            - 'xT', 'yT': coordinates of the connection point on the terminal,
            - 'xC', 'yC': coordinates of the connection point on the vertex edge,
            - 'd': length of the connection.
    """

    # initialize the selection DataFrame
    columns = ["idA", "idB", "idE", "xT", "yT", "xC", "yC", "d"]
    selection = pd.DataFrame(columns=columns)

    # loop over all vertices
    for idx, vertex in vertices.iterrows():

        # get projection points on the terminal and the vertex
        p1, p2 = get_nearest_point(terminal, vertex)

        # check natural barrier crossing
        if barriers is not None:
            intersection = is_crossing_a_barrier(p1, p2, barriers["geometry"])
            if intersection:
                # text = 'Impossible to connect terminal {} to vertex {} because of '\
                #        'a natural barrier.'
                # log.debug(text.format(terminal.name, vertex['idE']))
                continue

        # check distance within R
        d = distance(p1, p2)
        if d < R:
            series = pd.Series(
                [
                    vertex["idA"],
                    vertex["idB"],
                    vertex["idE"],
                    p1[0],
                    p1[1],
                    p2[0],
                    p2[1],
                    d,
                ],
                index=columns,
            )
            selection = selection.append(series, ignore_index=True)

    return selection


def remove_point(selection, idmin, r):
    """
    Remove connections within distance *r* from the closest connection of index
    *idmin* ; in-place.

    Parameters
    ----------
    selection: DataFrame
        Dataframe of the connections selected by *dhd.connect.first_selection*.
    idmin: int
        Index of the connection having the smallest distance *d* in *selection*.
    r: float
        Minimal distance between two connections to the same terminal.
    """

    # coordinates of the closest connection
    p1 = (selection.at[idmin, "xC"], selection.at[idmin, "yC"])

    # list of labels of connection to remove
    labels = []
    for i, point in selection.iterrows():
        # coordinates of the tested connection
        p2 = [point["xC"], point["yC"]]
        d = distance(p1, p2)
        if d < r:
            labels.append(i)

    # drop connection too close to p1
    selection.drop(index=labels, inplace=True)
    selection.reset_index(inplace=True, drop=True)


def second_selection(selection, r):
    """
    Improve selection quality by removing connections within the distance *d*
    from each other.

    Parameters
    ----------
    selection: DataFrame
        Dataframe of the connections selected by *dhd.connect.first_selection*.
    r: float
        Minimal distance between two conections to the same terminal.

    Returns
    -------
    DataFrame
        Dataframe of the possible connections to the considered terminal. The
        columns are identical to those of *selection*.
    """

    # initialize DataFrame
    connections = pd.DataFrame(columns=list(selection.keys()))

    # remove connections from 'selection' and store them in 'connections' if
    # distance criterion fulfilled until 'selection' is emplty
    while True:
        idmin = np.array(selection["d"]).argmin()
        connections = connections.append(selection.loc[idmin], ignore_index=True)
        remove_point(selection, idmin, r)
        if len(selection) == 0:
            break

    return connections


def split_line(l, p, eps=0.1):
    """
    Split the LineString *l* in two at a the Point *p* on the line.

    Parameters
    ----------
    l: LineString
        Vertex edge to split at the connection point.
    p: Point
        Connection point on the vertex edge.
    eps: float, optional
        Distance under which two points are considered identical. Default is
        0.1 m.

    Returns
    -------
    LineString
        Geometry of the first line,
    LineString
        Geometry of the second line.
    """

    # check that 'p' belongs to 'l'.
    if l.distance(p) > eps:
        text = "The point {} must lie on the line {}."
        raise GeometryError(text.format(p, l))

    # get LineString coordinates
    coords = list(l.coords)
    n = len(coords)

    # find first segment coordinates
    coords1 = [coords[0]]
    for i in range(n - 1):
        p1, p2 = coords[i], coords[i + 1]
        line = LineString([p1, p2])
        # check that p is not on the line segment
        if line.distance(p) > eps:
            coords1.append(p2)
        else:
            coords1.append(p.coords[0])
            break

    # find second segment coordinates
    coords2 = [p.coords[0]]
    for j in range(i + 1, n):
        coords2.append(coords[j])

    # coordinates to LineString
    line1 = LineString(coords1)
    line2 = LineString(coords2)

    return line1, line2


def sort_lines(line1, line2, coords):
    """
    Sort *line1* and *line2* such that the first line has either its first points
    equal to *coords* or its last point equal to *coords*.

    Parameters
    ----------
    line1: LineString
        Geometry of the first line of the splitted edge.
    line2: LineString
        Geometry of the second line of the splitted edge.
    coords: tuple
        Coordinates of the edge end 'A'.

    Returns
    -------
    LineString
        Line with one end equal to the edge end 'A',
    LineString
        Line with one end equal to the edge end 'B'.
    """

    coords1 = list(line1.coords)
    coords2 = list(line2.coords)

    if coords == coords1[0]:
        lineA, lineB = line1, line2
    elif coords == coords2[-1]:
        lineA, lineB = reverse_linestring(line2), reverse_linestring(line1)
    else:
        raise GeometryError("The point {} correspond to none of the line ends.")

    return lineA, lineB


def find_vertex(vertices, connection):
    """
    Find which vertex of *vertices* corresponds to *connection*.

    Parameters
    ----------
    vertices: DataFrame
        Dataframe of the vertices.
    connection: Series
        Row of the dataframe *connections* obtained with the function
        *dhd.connect.second_selection*.

    Returns
    -------
    Series
        Series of the dataframe *vertices* corresponding to *connection*.
    """

    vertex = vertices.loc[vertices["idE"] == connection["idE"]].iloc[0]

    return vertex


def get_connection_coordinates(connection, vertex):
    """
    Get the coordinates of the different points of the connection.

    The vertex edges end are labeled 'A' and 'B', the terminal is labeld 'T' and
    the connection point on the vertex edge is labeled 'C'.

    Parameters
    ----------
    connection: Series
        Row of the dataframe *connections* obtained from the function
        *dhd.connect.second_selection*. It contains all the information on the
        terminal to be connected.
    vertex: Series
        Row of the dataframe *vertices*. It contains all the information on the
        edge to be connected.

    Returns
    -------
    dict
        Dictionary of the four point tuple coordinates with keys: 'A', 'B', 'T'
        and 'C'.
    """

    coords = dict()
    coords["T"] = (connection["xT"], connection["yT"])
    coords["C"] = (connection["xC"], connection["yC"])
    coords["A"] = (vertex["xA"], vertex["yA"])
    coords["B"] = (vertex["xB"], vertex["yB"])

    return coords


def get_connection_distances(coords):
    """
    Measure the distances between the points 'A' and 'C' and the points 'B' and
    'C' from the dictionary *coords*.

    Parameters
    ----------
    coords: dict
        Tuple coordinates of the connection edge ends ('A' and 'B'), the terminal
        ('T') and the connection point on the vertex edge ('C').

    Returns
    -------
    dict
        Dictionary of the two distances ('A'-'C' and 'B'-'C') with keys 'A' and
        'B'.
    """

    d = dict()
    d["A"] = distance(coords["A"], coords["C"])
    d["B"] = distance(coords["B"], coords["C"])

    return d


def get_connection_index(connection, terminal, d):
    """
    Find if the connection 'C' lies on the edge 'A'-'B', on the edge end 'A' or
    on the edge end 'B' and return the associted connection index.

    Parameters
    ----------
    connection: Series
        Row of the dataframe *connections* obtained from the function
        *dhd.connect.second_selection*.
    terminal: Series
        Row of the dataframe *terminals*.
    d: dict
        Dictionary of the distances between the connection and the edge ends.

    Returns
    -------
    bool
        True if 'C' lies on 'A'-'B', False otherwise.
    str
        Index of the connection 'C': index of 'A' if 'C'='A', index of 'B' if
        'C'='B', concatenation of the *terminal* index and the *connection*
        index otherwise.
    """

    # if connection on the first edge end (A)
    if d["A"] == 0:
        idC = connection["idA"]
        on_edge = False
    # if connection on the second edge end (B)
    elif d["B"] == 0:
        idC = connection["idB"]
        on_edge = False
    # if connection inbetween the edge ends (A,B)
    else:
        idC = "{}_{}".format(terminal.name, connection.name)
        on_edge = True

    return on_edge, idC


def add_connection_to_terminal(terminal, coords, idC, func):
    """
    Append the connection list of *terminal* with connection of coordinates
    *coords* and index 'idC' ; in-place.

    Parameters
    ----------
    terminal: Series
        Row of the *terminals* dataframe.
    coords: dict
        Tuple coordinates of the connection edge ends ('A' and 'B'), the terminal
        ('T') and the connection point on the vertex edge ('C').
    idC: str
        Index of the new connection.
    func: function
        Function of the connection length returning its weight.
    """

    # get connection geometry
    line = LineString([coords["T"], coords["C"]])
    # append terminal lists
    terminal["_geometry"].append(line)
    terminal["_id"].append(idC)
    terminal["_weight"].append(connection_weight(line, func))


def new_edge_weight(vertex, line):
    """
    Compute the weight of the splitted edge of geometry *line* and original
    vertex row *vertex*.

    Parameters
    ----------
    vertex: Series
        Row of the dataframe *vertices*.
    line: LineString
        One of the two geometries of the splitted edge.

    Returns
    -------
    float
        Weight of the new vertex.
    """

    return vertex["weight"] * line.length / vertex["geometry"].length


def update_edges(vertices, connection, vertex, coords, idC, func):
    """
    Update the graph edges in *vertices* according to the new *connection* on
    the considered *vertex* ; in-place.

    This function is only called when the parent edge is splitted in two child
    edges. The parent edge is removed and the child edges are appended.

    Parameters
    ----------
    vertices: DataFrame
        Dataframe of the vertices.
    connection: Series
        Row of the dataframe *connections* obtained with the function
        *dhd.connect.second_selection*.
    vertex: Series
        Row of the dataframe *vertices*.
    coords: dict
        Tuple coordinates of the connection edge ends ('A' and 'B'), the terminal
        ('T') and the connection point on the vertex edge ('C').
    idC: str
        Index of the new connection.
    func: function
        Function of the connection length returning its weight.
    """

    # columns of 'vertices'
    columns = ["idA", "idB", "idE", "geometry", "weight", "xA", "yA", "xB", "yB"]
    # edge nodes indices
    idA, idB = connection["idA"], connection["idB"]
    # split edge (A,B) in two geometries
    line1, line2 = split_line(vertex["geometry"], Point(coords["C"]))
    lineA, lineB = sort_lines(line1, line2, coords["A"])
    # remove edge (A,B)
    vertices.drop(index=vertex.name, inplace=True)
    vertices.reset_index(inplace=True, drop=True)
    # new row for the edge (A, C)
    seriesA = pd.Series(
        [
            idA,
            idC,
            "{}_{}".format(idA, idC),
            lineA,
            new_edge_weight(vertex, lineA),
            coords["A"][0],
            coords["A"][1],
            coords["C"][0],
            coords["C"][1],
        ],
        index=columns,
    )
    vertices.loc[len(vertices)] = seriesA
    # new row for the edge (C, B)
    seriesB = pd.Series(
        [
            idC,
            idB,
            "{}_{}".format(idC, idB),
            lineB,
            new_edge_weight(vertex, lineB),
            coords["C"][0],
            coords["C"][1],
            coords["B"][0],
            coords["B"][1],
        ],
        index=columns,
    )
    vertices.loc[len(vertices)] = seriesB


def update_graph(vertices, terminal, connections, func):
    """
    Add the possible *connections* to the given *terminal* into the dataframe
    *vertices* ; in-place.

    The list associated to the given *terminal* in the dataframe *terminals* are
    appended by each possible connection. Also the rows of the dataframe
    *vertices* are modified to coincide with the new graph when a connection
    occurs on a parent edge splitted in two child edges.

    Parameters
    ----------
    vertices: DataFrame
        Dataframe of the vertices.
    vertex: Series
        Row of the dataframe *vertices*.
    connections: DataFrame
        Dataframe of the possible connections to the considered terminal,
        obtained from the function *dhd.connect.second_selection*.
    func: function
        Function of the connection length returning its weight.
    """

    # loop over all selected possible connections
    for idx, connection in connections.iterrows():
        # select the edge to be connected
        vertex = find_vertex(vertices, connection)
        # coordinates of the edge ends
        coords = get_connection_coordinates(connection, vertex)
        # distances A-C and B-C
        d = get_connection_distances(coords)
        # type of connection & connection index
        on_edge, idC = get_connection_index(connection, terminal, d)
        # append connection list
        add_connection_to_terminal(terminal, coords, idC, func)
        # update 'vertices'
        if on_edge:
            update_edges(vertices, connection, vertex, coords, idC, func)


def connect_terminal(vertices, terminal, barriers, R, r, func):
    """
    Span the graph to find the possible connections to the given *terminal* and
    then update the dataframes *vertices* and *terminals* accordingly ; in-place.

    Parameters
    ----------
    vertices: DataFrame
        Dataframe of the vertices.
    terminal: Series
        Row of the dataframe *terminal*.
    barriers: DataFrame
        Dataframe of the natural barriers.
    R: float
        Maximal connection length.
    r: float
        Minimal distance between two connections to the same terminal.
    func: function
        Function of the connection length returning its weight.
    """

    # select the possible connection around the given 'terminal'
    selection = first_selection(vertices, terminal, R, barriers)
    # if no possible connection
    if len(selection) == 0:
        if terminal["kind"] == "source":
            text = (
                "Impossible to connect the source {}. It is too far from "
                "the network."
            )
            log.error(text.format(terminal.name))
        else:
            text = "Impossible to connect terminal {}."
            log.info(text.format(terminal.name))

    else:
        # remove possible connections to close to each other
        connections = second_selection(selection, r)
        # update 'vertices' and 'terminals'
        update_graph(vertices, terminal, connections, func)


def connect_terminals(
    streets,
    sinks,
    sources,
    barriers=None,
    R=75,
    r=25,
    ignore_index=False,
    connection_weight_function=None,
):
    """
    Construct the dataframes *vertices* and *terminals* needed for the district
    heating design evolutive algorithm in the module *dhd.evolve*.

    The original street graph is enlarged with the connection nodes between the
    terminals and the graph edges. All the possible connection edges are stored
    in *terminals*.

    Parameters
    ----------
    streets: DataFrame
        Dataframe of the street network with the following structure:

        * INDEX: Integers.
        * COLUMNS:

            - 'idA': index of the first edge end (A),
            - 'idB': index of the second edge end (B),
            - 'geometry': shapely LineString of the edge between A and B (it
              must go from A to B).
            - 'weight': edge weight (optional, if not specified the edge
              length is used instead).
            - ...

    sinks: DataFrame
        Dataframe of the heating sinks with mandatory structure:

        * INDEX: If *index* is True, set of indices disjoint from the set of
          indices of *sources*. Otherwise the indices are generated.
        * COLUMNS:

            - 'geometry': shapely geometry of the sink,
            - 'load': heating load of the sink (optional, if not specified
              the module *dhd.load* cannot be used.)
            - ...

    sources: DataFrame
        Dataframe of the heating source(s) of the district heating network with
        the following structure:

        * INDEX: If *index* is True, set of indices disjoint from the set of
          indices of *sinks*. Otherwise the indices are generated.
        * COLUMNS:

            - 'geometry': shapely geometry of the source.
            - ...

    barriers: DataFrame, optional
        Dataframe of the natural barriers (railways, rivers,...) which cannot be
        crossed when connecting a sink to the heating network. Default is None.
        The dataframe must have the following structure:

        * INDEX: Integers.
        * COLUMNS:

            - 'geometry': shapely LineString of the barrier.
            - ...

    R: float, optional
        Maximal connection length. Default is 50 m.
    r: float, optional
        Minimal distance between two connections to the same terminal. Default is
        20 m.
    ignore_index: bool, optional
        If False, use indices from the dataframes *sources* and *sinks*,
        otherwise generate new indices. Default is True. Note
        that the indices of *sinks* and the indices of *sources* must be two
        disjoint set.
    connection_weight_function: function, optional
        Function of the connection length returning its weight. If None the
        weight is set equal to the length. Default is None.

    Returns
    -------
    vertices: DataFrame
        Dataframe of the street network plus the possible connection nodes to
        the terminals with the following structure:

        * INDEX: Integers
        * COLUMNS:

            - 'idA': first node index (from *streets*),
            - 'idB': second node index (from *streets*),
            - 'idE': edge index,
            - 'xA', 'yA': first node coordinates,
            - 'xB', 'yB': second node coordinates,
            - 'geometry': edge geometry (shapely LineString),
            - 'weight': edge weight,
            - ... additional columns from *streets*.

    terminals: DataFrame
        Dataframe of the terminals to connect to the streets network and their
        possible connections with the following structure:

        * INDEX: If *index* is True, indices from *sources* and *sinks*,
          generated indices : ['0S',...,'NS','0B',...,'MB'] for N sources
          and M sinks.
        * COLUMNS:

            - '_id': list of the possible connections indices,
            - '_weight': list of the possible connections weights,
            - '_geometry': list of the possible connections geometries,
            - 'geometry': geometry of the terminal,
            - 'kind': terminal kind ('source' or 'sink'),
            - 'load': terminal heating load (only if provided in *sinks*).

    """

    tic = time.time()
    check_data_structure(sinks, streets, sources, barriers, ignore_index)
    sinks = clean_superpositions(sinks)
    # initialize the dataframes 'vertices' and 'terminals'
    vertices = init_vertices(streets)
    terminals = init_terminals(sources, sinks, ignore_index)

    # connect the terminals
    for idx, terminal in terminals.iterrows():
        connect_terminal(vertices, terminal, barriers, R, r, connection_weight_function)

    tac = time.time()

    text = "Initilization of the vertices and terminals dataframes in {} seconds."
    log.info(text.format(round(tac - tic, 2)))

    return vertices, terminals
