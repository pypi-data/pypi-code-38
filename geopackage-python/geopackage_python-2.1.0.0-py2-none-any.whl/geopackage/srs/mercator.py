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

from math import pi, atan, sinh, degrees, log, tan

from rgi.geopackage.srs.abstract_mercator import AbstractMercator


class Mercator(AbstractMercator):
    """
    Mercator projection class that holds specific calculations and formulas
    for EPSG3857.
    """

    spatial_ref_sys_name = "WGS 84 / Pseudo-Mercator"

    srs_identifier = 3857

    srs_organization = "epsg"

    srs_organization_coordsys_id = 3857

    srs_definition = """
                        PROJCS["WGS 84 / Pseudo-Mercator",GEOGCS["WGS 84",DATUM["WGS_1984"
                        ,SPHEROID["WGS 84",6378137,298.257223563,AUTHORITY["EPSG","7030"]]
                        ,AUTHORITY["EPSG","6326"]],PRIMEM["Greenwich",0,AUTHORITY["EPSG",
                        "8901"]],UNIT["degree",0.0174532925199433,AUTHORITY["EPSG","9122"]]
                        ,AUTHORITY["EPSG","9122"]]AUTHORITY["EPSG","4326"]],PROJECTION[
                        "Mercator_1SP"],PARAMETER["central_meridian",0],PARAMETER[
                        "scale_factor",1],PARAMETER["false_easting",0],PARAMETER[
                        "false_northing",0],UNIT["metre",1,AUTHORITY["EPSG","9001"]],AXIS[
                        "X",EAST],AXIS["Y",NORTH]
                    """

    srs_description= ""

    def __init__(self, tile_size=256):
        """
        Constructor
        """
        super(Mercator, self).__init__(tile_size)
        # self.tile_size = tile_size
        # self.radius = 6378137
        # self.origin_shift = pi * self.radius
        # self.initial_resolution = 2 * self.origin_shift / self.tile_size

    @staticmethod
    def tile_to_lat_lon(z, x, y):
        """
        Returns the lat/lon coordinates of the bottom-left corner of the input
        tile.

        Inputs:
        z -- zoom level value for input tile
        x -- tile column (longitude) value for input tile
        y -- tile row (latitude) value for input tile
        """
        n = 2.0 ** z
        lon = x / n * 360.0 - 180.0
        lat_rad = atan(sinh(pi * (2 * y / n - 1)))
        # lat_rad = math.atan(math.sinh(math.pi * (1 - 2 * y / n)))
        lat = degrees(lat_rad)
        return lat, lon

    def tile_to_meters(self, z, x, y):
        """
        Returns the meter coordinates of the bottom-left corner of the input
        tile.

        Inputs:
        z -- zoom level value for input tile
        x -- tile column (longitude) value for input tile
        y -- tile row (latitude) value for input tile
        """
        # Mercator Upper left, add 1 to both x and y to get Lower right
        lat, lon = self.tile_to_lat_lon(z, x, y)
        meters_x = lon * self.origin_shift / 180.0
        meters_y = log(tan((90 + lat) * pi / 360.0)) / \
                   (pi / 180.0)
        meters_y = meters_y * self.origin_shift / 180.0
        return meters_x, meters_y
