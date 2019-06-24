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

from math import pi, log, tan, sin

from rgi.geopackage.srs.abstract_mercator import AbstractMercator


class EllipsoidalMercator(AbstractMercator):
    """
    Ellipsoidal Mercator projection class that holds specific calculations and
    formulas for EPSG3395.
    """

    spatial_ref_sys_name = "WGS 84 / World Mercator"

    srs_identifier = 3395

    srs_organization = "epsg"

    srs_organization_coordsys_id = 3395

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

    srs_description = " "

    def __init__(self):
        """
        Constructor
        """
        super(EllipsoidalMercator, self).__init__()

    @staticmethod
    def lat_to_northing(lat):
        """
        Convert a latitude to a northing
                      /    / pi   phi \   / 1 - e sin(phi) \ e/2 \
        y(phi) = R ln| tan| --- + ---  | |  --------------  |     |
                      \    \ 4     2  /   \ 1 + e sin(phi) /     /
        """
        r = 6378137.0
        e = 0.081819190842621
        return r * log(tan((pi / 2 + lat) / 2) * ((1 - e * sin(lat)) /
                                                  (1 + e * sin(lat))) ** (e / 2))

    @staticmethod
    def tile_to_lat_lon(z, x, y):
        """
        Returns the lat/lon coordinates of the bottom-left corner of the input
        tile. Finds the value numerically (using the secant method).

        Inputs:
        z -- zoom level value for input tile
        x -- tile column value for input tile
        y -- tile row value for input tile
        """
        n = 2.0 ** z
        lon = x / n * 360.0 - 180.0
        my = (y - 2 ** (z - 1)) * 6378137 * pi * 2 / 2 ** z

        def f(phi):
            return EllipsoidalMercator.lat_to_northing(phi) - my

        lat = 0.0
        oldLat = 1.0
        diff = 1.0
        while abs(diff) > 0.0001:
            newLat = lat - f(lat) * (lat - oldLat) / (f(lat) - f(oldLat))
            if newLat > 1.48499697138:
                newLat = 1.48499697138
            elif newLat < -1.48499697138:
                newLat = -1.48499697138
            oldLat = lat
            lat = newLat
            diff = lat - oldLat
        lat = lat * 180.0 / pi
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
        lat, lon = self.tile_to_lat_lon(z, x, y)
        meters_x = lon * self.origin_shift / 180.0
        meters_y = self.lat_to_northing(lat * pi / 180.0)
        return meters_x, meters_y
