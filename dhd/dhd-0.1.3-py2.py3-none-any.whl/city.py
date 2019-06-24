#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module defining the class *City* which allows to obtain information from Open
Street Map (OSM) about the street network and the buildings geometries of a
given city.

This information is organised in the dataframe structures used by the module
*dhd.connect*.

A selection of the buildings to be connected to the district heating network is
proposed on an area criterium.
"""

import osmnx as ox
import networkx as nx
import pandas as pd
from shapely.geometry import Point, LineString

from dhd.logs import log
from dhd.utils import reverse_linestring
from dhd.exceptions import SourceError, BarrierError, GeometryError

ox.config(use_cache=True)


class City:
    """
    Class to define a city with the geometry of its buildings and streets.
    Sources and natural barriers may also be considered if provided as shapely
    objects.

    Parameters
    ----------
    name: string
        Name of the city to load.
    sources: list, optional
        List of the heating source(s) as shapely Point geometries. Default is
        None.
    barriers: list, optional
        List of the natural barriers as shapely LineString geometries. Default
        is None.
    """

    def __init__(self, name, sources=None, barriers=None):
        """Constructor of the *City* class."""

        self.name = name
        self.sources = sources
        self.barriers = barriers
        self.graph = self.set_graph()
        self.buildings = self.set_buildings()

    def set_graph(self):
        """
        Load the street network from OSM and save it as a MultiDiGraph.

        Returns
        -------
        MultiDiGraph
        """

        multidigraph = ox.graph_from_place(
            self.name, network_type="drive", simplify=True
        )
        multidigraph = ox.project_graph(multidigraph)

        return multidigraph

    def simplify_graph(self):
        """
        Turn the MultiDiGraph of the street network to a simple Graph and reset
        its nodes label to integers.

        Return
        ------
        Graph
        """

        graph = nx.Graph(self.graph)
        graph = nx.convert_node_labels_to_integers(graph)

        return graph

    def reset_sources(self, sources):
        """
        Reset the list of shapely Point used to define the source(s).

        Parameters
        ----------
        sources: list
            List of the heating source(s) as shapely Point geometries. Default
            is None.
        """

        self.sources = sources

    def reset_barriers(self, barriers):
        """
        Reset the list of shapely LineString used to define the natural
        barriers(s).

        Parameters
        ----------
        barriers: list, optional
            List of the natural barriers as shapely LineString geometries. Default
            is None.
        """

        self.barriers = barriers

    @staticmethod
    def init_streets(graph):
        """
        Convert the street *graph* to a DataFrame with source and target labels
        'idA' and 'idB'.

        All arguments but 'idA', 'idB' and 'geometry' are dropped.

        Parameters
        ----------
        graph: Graph
            Graph of the street network.

        Returns
        -------
        DataFrame
            Dataframe of the street network.
        """

        streets = nx.to_pandas_edgelist(graph, source="idA", target="idB")
        columns = ["idA", "idB", "geometry"]
        labels = list(set(streets.keys()) - set(columns))
        streets.drop(labels=labels, axis=1, inplace=True)

        return streets

    @staticmethod
    def complete_geometries(streets, graph):
        """
        Create a LineString geometry for edges without geometry ; in-place.

        The LineString is a single line matching the coordinates of the two edge
        ends.

        Parameters
        ----------
        streets: DataFrame
            Dataframe of the street network.
        graph: Graph
            Graph of the street network.
        """

        nodes = graph.nodes(data=True)

        for i, street in streets.iterrows():
            if not type(street["geometry"]) == LineString:
                idA, idB = street["idA"], street["idB"]
                xA, yA = nodes[idA]["x"], nodes[idA]["y"]
                xB, yB = nodes[idB]["x"], nodes[idB]["y"]
                line = LineString([(xA, yA), (xB, yB)])
                streets.at[i, "geometry"] = line

    @staticmethod
    def set_geometries_order(streets, graph):
        """
        Reverse alle edges (LineString) not pointing in the right direction ;
        in-place.

        The streets network *streets* is modified so that the edge between two
        nodes always point from 'idA' to 'idB'.

        Parameters
        ----------
        streets: DataFrame
            Dataframe of the street network.
        graph: Graph
            Graph of the street network.
        """

        nodes = graph.nodes(data=True)

        for i, street in streets.iterrows():

            idA, idB = street["idA"], street["idB"]

            line = street["geometry"]
            x1, y1 = line.coords[0]
            x2, y2 = line.coords[-1]
            xA, yA = nodes[idA]["x"], nodes[idA]["y"]
            xB, yB = nodes[idB]["x"], nodes[idB]["y"]

            if x1 == xA and y1 == yA and x2 == xB and y2 == yB:
                pass
            elif x1 == xB and y1 == yB and x2 == xA and y2 == yA:
                line = reverse_linestring(line)
                streets.at[i, "geometry"] = line
            else:
                text = "The edge end coordinates don't match the nodes coordinates."
                raise GeometryError(text)

    @staticmethod
    def set_indices(streets):
        """
        Set indices of the streets dataframe *streets* ; in-place.
        """

        for i, street in streets.iterrows():
            idA = "{}R".format(street["idA"])
            idB = "{}R".format(street["idB"])
            streets.loc[i, "idA"] = idA
            streets.loc[i, "idB"] = idB

    @staticmethod
    def set_streets_weight(streets):
        """
        Set the streets weight equal to theirt length ; in-place.
        """

        streets["weight"] = None
        for i, street in streets.iterrows():
            weight = street["geometry"].length
            streets.at[i, "weight"] = weight

    def get_streets(self):
        """
        Store the streets network in a dataframe and return it.

        Returns
        -------
        streets: DataFrame
            Dataframe of the street network with the following structure:
                * INDEX: Integers.
                * COLUMNS:
                    - 'idA': index of the edge first node,
                    - 'idB': index of the edge second node,
                    - 'geometry': LineString edge geometry,
                    - 'weight': weight (length) of the edge.
        """

        graph = self.simplify_graph()
        streets = self.init_streets(graph)
        self.complete_geometries(streets, graph)
        self.set_geometries_order(streets, graph)
        self.set_indices(streets)
        self.set_streets_weight(streets)

        return streets

    def init_buildings(self):
        """
        Load the geometries (Polygons) of the buildings of the considered city.

        The geometries are projected on the CRS used for the street network. All
        attributes but 'geometry' are dropped.

        Returns
        -------
        DataFrame
            Dataframe of the buildings of the city.
        """

        n, e = ox.graph_to_gdfs(self.graph, nodes=True, edges=True)
        crs = e.crs
        buildings = ox.footprints_from_place(self.name)
        buildings = buildings.to_crs(crs=crs)
        buildings = buildings.reset_index()
        columns = ["geometry"]
        labels = list(set(buildings.keys()) - set(columns))
        buildings.drop(labels=labels, axis=1, inplace=True)

        return buildings

    @staticmethod
    def get_load_from_area(area):

        kWh_per_area = 100  # kWh/m^2/year
        full_power_hours = 2000  # full power equivalent number of hours per year
        level_number = 5  # number of levels
        load = area * kWh_per_area / full_power_hours * level_number

        return load

    def set_buildings_load(self, buildings):
        """
        Set the building load equal to its area ; in-place.

        Parameters
        ----------
        buildings: DataFrame
            Dataframe of the buildings of the city
        """
        area = buildings["geometry"].apply(lambda x: x.area)
        buildings["load"] = self.get_load_from_area(area)

    def set_buildings(self):
        """
        Store the buildings geometries in a dataframe and return it.

        Returns
        -------
        buildings: DataFrame
            Dataframe of the buildings of the city with the following structure:
                * INDEX: Integers.
                * COLUMNS:
                    - 'geometry': Polygon geometry of the building,
                    - 'load': heating load of the building (building area).
        """

        buildings = self.init_buildings()
        self.set_buildings_load(buildings)

        return buildings

    def select_sinks(self, min_load=0):
        """
        Select the sinks to be connected to the distrcit heating network.

        Only buildings with area larger than *min_area* are selected.

        Parameters
        ----------
        min_load: float, optional
            Buildings with a load larger than *min_load* ([kW]) are selected
            to be connected to the district heating network. Default is 0.

        Returns
        -------
        sinks: DataFrame
            Dataframe of the selected buildings (sinks) with the following structure:
                * INDEX: Integers.
                * COLUMNS:
                    - 'geometry': Polygon geometry of the building (sink),
                    - 'load': heating load of the building (building area).
        """

        sinks = self.buildings.loc[self.buildings.load > min_load]
        sinks.reset_index(inplace=True, drop=True)

        return sinks

    @staticmethod
    def init_sources(sources):
        """
        Store the source(s) (*sources*) in a dataframe with unique column
        'geometry' for the shapely Point of the source.

        Parameters
        ----------
        sources: list
            List of shapely Points representing the source(s) coordinates.

        Returns
        -------
        DataFrame
            DataFrame of the heating source(s).
        """

        count = 0
        for source in sources:
            if not type(source) == Point:
                raise SourceError("{} is not a shapely Point.".format(source))
            count += 1
        log.info("{} source(s) initialized.".format(count))

        sources = pd.DataFrame(sources, columns=["geometry"])

        return sources

    def get_sources(self):
        """
        Store the source(s) (*City.sources*) in a dataframe with unique column
        'geometry' for the shapely Point of the source and return it.

        If *City.sources* is None or not a valid type (list of shapely Points),
        the exception *SourceError* is raised.

        Returns
        -------
        sources: DataFrame
            Dataframe of the heating source(s) with the following structure:
                * INDEX: Integers.
                * COLUMNS:
                    - 'geometry': Point geometry of the source.
        """

        sources = self.sources

        if sources is None:
            raise SourceError("No source provided.")
        elif type(sources) == Point:
            sources = [sources]
        elif type(sources) == list:
            pass
        else:
            text = "'sources' must either be None or a list of Point."
            raise SourceError(text)

        sources = self.init_sources(sources)

        return sources

    @staticmethod
    def init_barriers(barriers):
        """
        Store the barriers (*barriers*) in a dataframe with unique column
        'geometry' for the shapely LineString of the barrier.

        Parameters
        ----------
        barriers: list
            List of shapely LineString representing the barriers coordinates.

        Returns
        -------
        DataFrame
            DataFrame of the barriers.
        """

        count = 0
        for line in barriers:
            if not type(line) == LineString:
                text = "{} is not a shapely LineString."
                raise BarrierError(text.format(line))
            count += 1
        log.info("{} barriers(s) initialized.".format(count))

        barriers = pd.DataFrame(barriers, columns=["geometry"])

        return barriers

    def get_barriers(self):
        """
        Store the barriers (*City.barriers*) in a dataframe with unique column
        'geometry' for the shapely LineString of the barrier and return it.

        The barriers may be any constraint impossible to cross when connecting
        the sinks/sources to the heating network (rivers, railways,...).

        If *City.barriers* is None or not a valid type (list of shapely LineStrings),
        the exception *BarrierError* is raised.

        Returns
        -------
        sources: DataFrame
            Dataframe of the heating source(s) with the following structure:
                * INDEX: Integers.
                * COLUMNS:
                    - 'geometry': Point geometry of the source.
        """

        barriers = self.barriers

        if barriers is None:
            raise BarrierError("No barrier provided.")
        elif type(barriers) == LineString:
            barriers = [barriers]
        elif type(barriers) == list:
            pass
        else:
            text = "'barriers' must either be None or a list of LineString."
            raise SourceError(text)

        barriers = self.init_barriers(barriers)

        return barriers
