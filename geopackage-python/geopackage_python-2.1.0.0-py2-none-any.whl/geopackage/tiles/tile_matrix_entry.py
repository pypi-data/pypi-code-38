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


class TileMatrixEntry(object):
    """
    Represents a row in the gpkg_tile_matrix Table
    """

    def __init__(self,
                 table_name,
                 zoom_level,
                 matrix_width,
                 matrix_height,
                 tile_width,
                 tile_height,
                 pixel_x_size,
                 pixel_y_size):
        """
        Constructor

        :param table_name:  Name of the tile set table that this tile matrix corresponds to
        :type table_name: str

        :param zoom_level:The zoom level of the associated tile set (0 <= zoomLevel <= max_level)
        :type zoom_level: int

        :param matrix_width:  The number of columns (>= 1) for this tile at this zoom level
        :type matrix_width: int

        :param matrix_height: The number of rows (>= 1) for this tile at this zoom level
        :type matrix_height: int

        :param tile_width:  The tile width in pixels (>= 1) at this zoom level
        :type tile_width: int

        :param tile_height: The tile height in pixels (>= 1) at this zoom level
        :type tile_height: int

        :param pixel_x_size: The width of the associated tile set's spatial reference system or default meters for an
        undefined geographic coordinate reference system (SRS id 0) (> 0) (SRS units per pixel)
        :type pixel_x_size: float

        :param pixel_y_size: The height of the associated tile set's spatial reference system or default meters for an
        undefined geographic coordinate reference system (SRS id 0) (> 0) (SRS units per pixel)
        :type pixel_y_size: float
        """

        self.table_name = table_name
        self.zoom_level = zoom_level
        self.matrix_width = matrix_width
        self.matrix_height = matrix_height
        self.tile_width = tile_width
        self.tile_height = tile_height
        self.pixel_x_size = pixel_x_size
        self.pixel_y_size = pixel_y_size
