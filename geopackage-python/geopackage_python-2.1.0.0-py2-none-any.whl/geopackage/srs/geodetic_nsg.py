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


class GeodeticNSG(SpatialReferenceSystem):
    """
        Geodetic projection for the NSG profile. Has methods to calculate world bound tile matrices and
        properties to return world bounds x and y values for EPSG:4326. This is used for the absolute
        tiling scheme required by the NSG Profile for GeoPackages. This was just different enough  from the standard
        Geodetic profile to warrant a separate class.

        note: because NSG requires 2 tiles at the top level, much of the math for resolution and pixel size changes
        depending on axis. this is reflected in x and y methods. As a practice, X generally denotes Longitude and Y
        denotes latitude.

        All NSG projections need these fields/methods.
    """

    spatial_ref_sys_name = "WGS 84 Geographic 2D"

    srs_identifier = 4326

    srs_organization = "epsg"

    srs_organization_coordsys_id = 4326

    srs_definition = """GEOGCS["WGS 84",DATUM["WGS_1984",SPHEROID["WGS 84",6378137, 298.257223563,AUTHORITY["EPSG","7030"]], 
        AUTHORITY["EPSG", "6326"]], PRIMEM["Greenwich",0,AUTHORITY["EPSG","8901"]], UNIT["degree",0.0174532925199433, 
        AUTHORITY["EPSG","9122"]], 
        AUTHORITY["EPSG","4326"]]"""

    srs_description = "Horizontal component of 3D system. Used by the GPS satellite navigation system and for NATO military geodetic surveying."

    @property
    def tile_size(self):
        """
        The tile's width and height in pixels.
        :return: the tile's width/height in pixels
        """
        return self._tile_size

    def __init__(self, tile_size=256):
        """
        Constructor
        """
        super(GeodeticNSG, self).__init__()
        self.tile_size = tile_size
        self.resolution_factor = 360.0 / (self.tile_size * 2)
        self.resolution_factor_y = 180.0 / self.tile_size

    @staticmethod
    def invert_y(z, y):
        """
        Return the inverted Y value of the tile - for nsg we dont subtract an additional tile.

        z -- zoom level
        """
        if z == 0:
            return 0
        else:
            return (1 << z) - y - 1

    @property
    def bounds(self):
        """
        Returns bounds of the world in the form min_x, min_y, max_x, max_y. with X being longitude and Y
        being Latitude. useful for tile and resolution factor calculations
        Returns:
            min_x - -180
            min_y - -90
            max_x - 180
            max_y -90
        """
        return -180.00, -90.00, 180.00, 90.00

    def pixel_x_size(self, zoom):
        """
        Return the size of an x pixel in longitude degrees at the given zoom level

        z -- zoom level of the tile
        """
        return self.resolution_factor / 2 ** zoom

    def pixel_y_size(self, zoom):
        """
        Return the size of an x pixel in longitude degrees at the given zoom level

        z -- zoom level of the tile
        """
        return self.resolution_factor_y / 2 ** zoom

    def get_coord(self, z, x, y):
        """
        Return the coordinates (in lat/long) of the bottom left corner of
        the tile

        z -- zoom level for input tile
        x -- tile column
        y -- tile row
        """
        return x * self.tile_size * self.pixel_x_size(z) - 180, \
               y * self.tile_size * self.pixel_y_size(z) - 90

    @staticmethod
    def get_matrix_size(zoom):
        """
        Returns tile matrix size of the world bounds at the given level. used for NSG profile calculations
        Args:
            zoom: zoom level to return the tile matrix size of

        Returns:
            x - tile matrix width
            y - tile matrix height
        """
        x = 2 ** (zoom + 1)
        y = 2 ** zoom
        return x, y

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
