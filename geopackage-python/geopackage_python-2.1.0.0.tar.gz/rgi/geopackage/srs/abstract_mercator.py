#!/usr/bin/python2.7
"""
Copyright (C) 2014 Reinventing Geospatial, Inc.

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>,
or write to the Free Software Foundation, Inc., 59 Temple Place -
Suite 330, Boston, MA 02111-1307, USA.

Author: Jenifer Cochran, Reinventing Geospatial Inc (RGi)
Date: 2018-11-11
   Requires: sqlite3, argparse
   Optional: Python Imaging Library (PIL or Pillow)
Credits:
  MapProxy imaging functions: http://mapproxy.org
  gdal2mb on github: https://github.com/developmentseed/gdal2mb

Version:
"""

from abc import abstractmethod
from math import pi

from rgi.geopackage.srs.spatial_reference_system import SpatialReferenceSystem


class AbstractMercator(SpatialReferenceSystem):
    """
     Base Class for any Mercator projection classes.  Sets-up the commonalities for the other Mercator projections
     such as Ellipsoidal, scaled world mercator, or Psuedo-Mercator.
    """

    @property
    def tile_size(self):
        """
        The tile's width and height in pixels.
        :return: the tile's width/height in pixels
        """
        return self._tile_size

    @tile_size.setter
    def tile_size(self, value):
        self._tile_size = value

    def __init__(self, tile_size=256):
        """
        Constructor
        """
        super(AbstractMercator, self).__init__()
        self.tile_size = tile_size
        self.radius = 6378137
        self.origin_shift = pi * self.radius
        self.initial_resolution = 2 * self.origin_shift / self.tile_size

    @staticmethod
    def invert_y(z, y):
        """
        Inverts the Y tile value.

        Inputs:
        z -- the zoom level associated with the tile
        y -- the Y tile number

        Returns:
        The flipped tile value
        """
        return (1 << z) - y - 1

    def get_coord(self, z, x, y):
        """
        Returns the coordinates (in meters) of the bottom-left corner of the
        input tile.

        Inputs:
        z -- zoom level value for input tile
        x -- tile column (longitude) value for input tile
        y -- tile row (latitude) value for input tile
        """
        return self.tile_to_meters(z, x, y)

    @staticmethod
    def truncate(coord):
        """
        Formats a coordinate to within an acceptable degree of accuracy (2
        decimal places for mercator).
        """
        return '%.2f' % (int(coord * 100) / float(100))

    def pixel_x_size(self, z):
        """
        returns the width of the associated tile set's spatial reference system (SRS units per pixel) for the given
        zoom level

        :param z: the zoom level
        :type z: int
        :return: the width of the associated tile set's spatial reference system (SRS units per pixel)
        """
        return AbstractMercator.pixel_size(z)

    def pixel_y_size(self, z):
        """
        returns the height of the associated tile set's spatial reference system (SRS units per pixel) for the given
        zoom level

        :param z: the zoom level
        :type z: int
        :return: the height of the associated tile set's spatial reference system (SRS units per pixel)
        """
        return AbstractMercator.pixel_size(z)

    @staticmethod
    def pixel_size(z):
        """
        Returns the pixel resolution of the input zoom level.

        Inputs:
        z -- zoom level value for the input tile
        """
        # 156543.033928041 is the pixel resolution in meters at zoom level 0
        return 156543.033928041 / 2 ** z

    @abstractmethod
    def tile_to_meters(self, z, x, y):
        """
        Determines the coordinate in meters for the specified tile.

        :param z: zoom level for the tile
        :type z: int
        :param x: the tile_row coordinate of the tile
        :type x: int
        :param y: the tile_column coordiante of the tile
        :type y: int
        """
        raise NotImplementedError()

    @staticmethod
    @abstractmethod
    def tile_to_lat_lon(z, x, y):
        """
         Determines the coordinate in decimal degrees for the specified tile.

        :param z: zoom level for the tile
        :type z: int
        :param x: the tile_row coordinate of the tile
        :type x: int
        :param y: the tile_column coordiante of the tile
        :type y: int
        """
        raise NotImplementedError()
