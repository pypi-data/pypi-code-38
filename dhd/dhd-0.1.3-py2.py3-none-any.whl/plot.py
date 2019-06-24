#!/usr/bin/env python
# -*- coding: utf-8 -*-

import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib


class Plot:
    """
    Class to define a visual interface representing the city and
    its constituent geometries.

    Parameters
    ----------
    streets: DataFrame, optional
        Dataframe of the streets network with a 'geometry' column. Default is
        None.
    buildings: DataFrame, optional
        Dataframe of all the city buildings with a 'geometry' column. Default is
        None.
    sources: DataFrame, optional
        Dataframe of the heating source(s) with a 'geometry' column. Default is
        None.
    barriers: DataFrame, optional
        Dataframe of the natural barriers with a 'geometry' column. Default is
        None.
    figsize: tuple
        Size of the figure framework. Default is *figsize* = (9,6).
    """

    def __init__(
        self, streets=None, buildings=None, sources=None, barriers=None, figsize=(9, 6)
    ):

        self.streets = self.init_streets(streets)
        self.buildings = self.init_buildings(buildings)
        self.sources = self.init_sources(sources)
        self.barriers = self.init_barriers(barriers)
        self.fig, self.ax = plt.subplots(figsize=figsize)
        self.plot()

    def init_streets(self, streets):
        """
        Initilization of the streets geodataframe if *streets* is not None.

        Parameters
        ----------
        streets: DataFrame
            Dataframe of the streets network with a 'geometry' column.

        Returns
        -------
        GeoDataFrame
            Geodataframe of the streets network.
        """
        if streets is None:
            return None
        else:
            return gpd.GeoDataFrame(streets)

    def init_buildings(self, buildings):
        """
        Initilization of the buildings geodataframe if *buildings* is not None.

        Parameters
        ----------
        buildings: DataFrame
            Dataframe of the buildings with a 'geometry' column.

        Returns
        -------
        GeoDataFrame
            Geodataframe of the buildings.
        """
        if buildings is None:
            return None
        else:
            return gpd.GeoDataFrame(buildings)

    def init_sources(self, sources):
        """
        Initilization of the sources geodataframe if *sources* is not None.

        Parameters
        ----------
        sources: DataFrame
            Dataframe of the sources with a 'geometry' column.

        Returns
        -------
        GeoDataFrame
            Geodataframe of the sources.
        """
        if sources is None:
            return None
        else:
            return gpd.GeoDataFrame(sources)

    def init_barriers(self, barriers):
        """
        Initilization of the barriers geodataframe if *barriers* is not None.

        Parameters
        ----------
        barriers: DataFrame
            Dataframe of the barriers with a 'geometry' column.

        Returns
        -------
        GeoDataFrame
            Geodataframe of the barriers.
        """
        if barriers is None:
            return None
        else:
            return gpd.GeoDataFrame(barriers)

    def reset_sources(self, sources):
        """
        Reset the class attribute *sources*.

        Parameters
        ----------
        sources: DataFrame
            Dataframe of the sources with a 'geometry' column.
        """

        self.sources = gpd.GeoDataFrame(sources)

    def reset_barriers(self, barriers):
        """
        Reset the class attribute *barriers*.

        Parameters
        ----------
        barriers: DataFrame
            Dataframe of the barriers with a 'geometry' column.
        """

        self.barriers = gpd.GeoDataFrame(barriers)

    def get_main_handles(self):
        """
        List the handles of the background geometries of the city for the
        interface legends.

        Returns
        -------
        list
            List of legend handles.
        """

        handles = (
            matplotlib.patches.Patch(
                color=plt.cm.tab10(5), label="buildings", alpha=0.8
            ),
            matplotlib.lines.Line2D(
                [], [], color="gray", linewidth=1, label="streets", alpha=0.8
            ),
            matplotlib.lines.Line2D(
                [],
                [],
                color=plt.cm.tab10(3),
                linewidth=1,
                Linestyle="--",
                alpha=0.8,
                label="natural barriers",
            ),
            matplotlib.lines.Line2D(
                [],
                [],
                color="black",
                marker="X",
                Linestyle="None",
                label="source(s)",
                alpha=0.8,
            ),
        )

        return handles

    def plot(self, loc="lower right"):
        """
        Plot the background geometries of the city which are provided.
        """

        if self.buildings is not None:
            self.buildings.plot(ax=self.ax, color=plt.cm.tab10(5), alpha=0.8)
        if self.streets is not None:
            self.streets.plot(ax=self.ax, linewidth=1, color="gray", alpha=0.8)
        if self.sources is not None:
            self.sources.plot(
                ax=self.ax, color="black", marker="X", markersize=30, alpha=0.8
            )
        if self.barriers is not None:
            self.barriers.plot(
                ax=self.ax,
                color=plt.cm.tab10(3),
                Linestyle="--",
                linewidth=1,
                alpha=0.8,
            )

        self.ax.axis("off")
        legend = plt.legend(handles=self.get_main_handles(), loc=loc)
        self.ax.add_artist(legend)
        plt.tight_layout()

    def clear(self):
        """
        Clear all the objects on the interface.
        """

        self.ax.clear()

    def reset(self, loc="lower right"):
        """
        Reset the interface with only the background geometries.
        """

        self.clear()
        self.plot(loc=loc)

    def get_handles(self, colors, labels, type):
        """
        Obtain the legend handles for the list of colors and labels.

        Parameters
        ----------
        colors: list
            List of colors.
        labels: list
            List of labels.
        type: string
            Type of legend handle. It may be 'pach', 'line' or 'point.'

        Returns
        -------
        list
            List of legend handles.
        """

        if type == "patch":
            handles = [
                matplotlib.patches.Patch(color=color, label=label)
                for color, label in zip(colors, labels)
            ]
        elif type == "line":
            handles = [
                matplotlib.lines.Line2D([], [], color=color, label=label)
                for color, label in zip(colors, labels)
            ]
        elif type == "point":
            handles = [
                matplotlib.lines.Line2D(
                    [],
                    [],
                    color=color,
                    label=label,
                    marker="o",
                    markersize=5,
                    Linestyle="None",
                )
                for color, label in zip(colors, labels)
            ]
        else:
            text = "type must either be 'patch', 'point' or 'line'."
            raise TypeError(text)

        return handles

    def add_geodataframe(self, gdf, kwargs={'color':'C1'}, centroid=False):
        """
        Add the geometries of the geodataframe *gdf* to the interface.

        Parameters
        ----------
        gdf: GeoDataFrame
            Geodataframe of the objects to represent visually.
        kwargs: dict, optional
            Arguments of the geopandas plot function. Default is {'color':'C1'}.
        centroid: bool
            If True only the centroid of the geometries is represented.
        """

        if centroid is True:
            gdf = gdf["geometry"].centroid

        gdf.plot(ax=self.ax, **kwargs)

    def add_legend(self, colors, labels, type, loc="best"):
        """
        Add a legend to the interface.

        Parameters
        ----------
        colors: list
            List of colors.
        labels: list
            List of labels.
        type: string
            Type of legend handle. It may be 'pach', 'line' or 'point'.
        loc: tuple, optional
            Location of the legend box. Default is *loc* = (0,1).
        """
        handles = self.get_handles(colors, labels, type)
        legend = plt.legend(handles=handles, loc=loc)
        self.ax.add_artist(legend)
