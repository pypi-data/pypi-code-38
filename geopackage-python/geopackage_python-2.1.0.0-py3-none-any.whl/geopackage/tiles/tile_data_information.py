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

Authors:
    Jenifer Cochran, Reinventing Geospatial Inc (RGi)
Date: 2018-11-11
   Requires: sqlite3, argparse
   Optional: Python Imaging Library (PIL or Pillow)
Credits:
  MapProxy imaging functions: http://mapproxy.org
  gdal2mb on github: https://github.com/developmentseed/gdal2mb

Version:
"""


class TileDataInformation(object):
    """
    Represents tile data of a single tile with a given x,y,z coordinate
    """

    def __init__(self,
                 tile_column,
                 tile_row,
                 tile_zoom,
                 tile_data):
        """
        Constructor
        Note: The tile row and tile column must be of upper left origin.

        :param tile_row: the y coordinate of the tile. 0 to tile_matrix matrix_height - 1
        :type tile_row: int

        :param tile_column: the x coordinate of the tile.  0 to tile_matrix matrix_width - 1
        :type tile_column: int

        :param tile_zoom: the zoom level of the tile (z coordinate)
        :type tile_zoom: int

        :param tile_data: the tile data encoded in JPEG, PNG, MapBox Vector Tile (.pbf), or GeoJSON
        :type tile_data: Binary
        """

        if tile_zoom < 0:
            raise ValueError("tile zoom must be greater than or equal to 0.")
        if tile_row < 0:
            raise ValueError("tile row must be greater than or equal to 0.")
        if tile_column < 0:
            raise ValueError("tile column must be greater than or equal to 0.")
        if tile_data is None:
            raise ValueError("tile data cannot be None.")

        self.zoom_level = tile_zoom
        self.tile_row = tile_row
        self.tile_column = tile_column
        self.tile_data = tile_data

