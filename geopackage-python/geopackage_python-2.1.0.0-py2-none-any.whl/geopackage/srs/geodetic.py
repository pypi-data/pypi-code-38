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
    Steven D. Lander, Reinventing Geospatial Inc (RGi)
    Jenifer Cochran, Reinventing Geospatial Inc (RGi)
Date: 2018-11-11
   Requires: sqlite3, argparse
   Optional: Python Imaging Library (PIL or Pillow)
Credits:
  MapProxy imaging functions: http://mapproxy.org
  gdal2mb on github: https://github.com/developmentseed/gdal2mb

Version:
"""

from rgi.geopackage.srs.spatial_reference_system import SpatialReferenceSystem


class Geodetic(SpatialReferenceSystem):
    """
    Geodetic projection class that holds specific calculations and formulas for
    EPSG4326.
    """

    def pixel_x_size(self, z):
        """
        returns the width of the associated tile set's spatial reference system (SRS units per pixel) for the given
        zoom level

        :param z: the zoom level
        :type z: int
        :return: the width of the associated tile set's spatial reference system (SRS units per pixel)
        """
        return self.pixel_size(z)

    def pixel_y_size(self, z):
        """
        returns the height of the associated tile set's spatial reference system (SRS units per pixel) for the given
        zoom level

        :param z: the zoom level
        :type z: int
        :return: the height of the associated tile set's spatial reference system (SRS units per pixel)
        """
        return self.pixel_size(z)

    @property
    def tile_size(self):
        """
        The tile's width and height in pixels.
        :return: the tile's width/height in pixels
        """
        return self._tile_size

    spatial_ref_sys_name = "WGS 84"

    srs_identifier = 4326

    srs_organization = "epsg"

    srs_organization_coordsys_id = 4326

    srs_definition = """
                         PROJCS["WGS 84 / World Mercator",GEOGCS["WGS 84",
                         DATUM["WGS_1984",SPHEROID["WGS 84",6378137,298.257223563,
                         AUTHORITY["EPSG","7030"]],AUTHORITY["EPSG","6326"]],
                         PRIMEM["Greenwich",0,AUTHORITY["EPSG","8901"]],
                         UNIT["degree",0.01745329251994328,AUTHORITY["EPSG","9122"]],
                         AUTHORITY["EPSG","4326"]],UNIT["metre",1,AUTHORITY["EPSG","9001"]],
                         PROJECTION["Mercator_1SP"],PARAMETER["central_meridian",0],
                         PARAMETER["scale_factor",1],PARAMETER["false_easting",0],
                         PARAMETER["false_northing",0],AUTHORITY["EPSG","3395"],
                         AXIS["Easting",EAST],AXIS["Northing",NORTH]]
                     """

    srs_description = ""

    def __init__(self, tile_size=256):
        """
        Constructor
        """
        super(Geodetic, self).__init__()
        self.tile_size = tile_size
        self.resolution_factor = 360.0 / (self.tile_size)

    def pixel_size(self, zoom):
        """
        Return the size of a pixel in lat/long at the given zoom level

        z -- zoom level of the tile
        """
        return self.resolution_factor / 2 ** zoom

    def get_coord(self, z, x, y):
        """
        Return the coordinates (in lat/long) of the bottom left corner of
        the tile

        z -- zoom level for input tile
        x -- tile column
        y -- tile row
        """
        res = self.resolution_factor / 2 ** z
        return x * self.tile_size * res - 180, y * self.tile_size * res - 90

    @staticmethod
    def invert_y(z, y):
        """
        Return the inverted Y value of the tile

        z -- zoom level
        """
        if z == 0:
            return 0
        else:
            return (1 << (z - 1)) - y - 1

    @staticmethod
    def truncate(coord):
        """
        Formats a coordinate to an acceptable degree of accuracy (7 decimal
        places for Geodetic).
        """
        return '%.7f' % (int(coord * 10000000) / float(10000000))

    @tile_size.setter
    def tile_size(self, value):
        self._tile_size = value
