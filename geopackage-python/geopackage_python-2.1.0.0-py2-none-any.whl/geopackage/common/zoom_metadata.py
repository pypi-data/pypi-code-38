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
class ZoomMetadata(object):
    """Return an object containing metadata about a given zoom level."""

    @property
    def zoom(self):
        """Return the zoom level of this metadata object."""
        return self.__zoom

    @zoom.setter
    def zoom(self, value):
        """Set the zoom level of this metadata object."""
        self.__zoom = value

    @property
    def min_tile_col(self):
        """Return the minimum tile column of this metadata object."""
        return self.__min_tile_col

    @min_tile_col.setter
    def min_tile_col(self, value):
        """Set the minimum tile column of this metadata object."""
        self.__min_tile_col = value

    @property
    def max_tile_col(self):
        """Return the maximum tile column of this metadata object."""
        return self.__max_tile_col

    @max_tile_col.setter
    def max_tile_col(self, value):
        """Set the maximum tile column of this metadata object."""
        self.__max_tile_col = value

    @property
    def min_tile_row(self):
        """Return the minimum tile row of this metadata object."""
        return self.__min_tile_row

    @min_tile_row.setter
    def min_tile_row(self, value):
        """Set the minimum tile row of this metadata object."""
        self.__min_tile_row = value

    @property
    def max_tile_row(self):
        """Return the maximum tile row of this metadata object."""
        return self.__max_tile_row

    @max_tile_row.setter
    def max_tile_row(self, value):
        """Set the maximum tile row of this metadata object."""
        self.__max_tile_row = value

    @property
    def min_x(self):
        """Return the minimum x coordinate of the bounding box."""
        return self.__min_x

    @min_x.setter
    def min_x(self, value):
        """Set the minimum x coordinate of the bounding box."""
        self.__min_x = value

    @property
    def max_x(self):
        """Return the maximum x coordinate of the bounding box."""
        return self.__max_x

    @max_x.setter
    def max_x(self, value):
        """Set the maximum x coordinate of the bounding box."""
        self.__max_x = value

    @property
    def min_y(self):
        """Return the minimum y coordinate of the bounding box."""
        return self.__min_y

    @min_y.setter
    def min_y(self, value):
        """Set the minimum y coordinate of the bounding box."""
        self.__min_y = value

    @property
    def max_y(self):
        """Return the maximum y coordinate of the bounding box."""
        return self.__max_y

    @max_y.setter
    def max_y(self, value):
        """Set the maximum y coordinate of the bounding box."""
        self.__max_y = value

    @property
    def matrix_width(self):
        """Number of tiles wide this matrix should be."""
        # return (self.__matrix_width if hasattr(self, 'matrix_width') else None)
        return self.__matrix_width or None

    @matrix_width.setter
    def matrix_width(self, value):
        """Set the number of tiles wide this matrix should be."""
        self.__matrix_width = value

    @property
    def matrix_height(self):
        """Number of tiles high this matrix should be."""
        return self.__matrix_height or None

    @matrix_height.setter
    def matrix_height(self, value):
        """Set the number of tiles high this matrix should be."""
        self.__matrix_height = value