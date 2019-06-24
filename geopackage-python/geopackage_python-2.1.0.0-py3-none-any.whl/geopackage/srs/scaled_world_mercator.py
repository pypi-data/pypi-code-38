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
from math import log, tan, pi, sin

from rgi.geopackage.srs.abstract_mercator import AbstractMercator


class ScaledWorldMercator(AbstractMercator):
    """
    Scaled World Mercator projection class that holds specific calculations
    and formulas for EPSG9804/9805 projection proposed by NGA Craig Rollins.
    """

    spatial_ref_sys_name = "WGS 84 / Scaled World Mercator"

    srs_identifier = 9804

    srs_organization = "epsg"

    srs_organization_coordsys_id = 9804

    srs_definition = """
                         PROJCS["unnamed",GEOGCS["WGS 84",
                         DATUM["WGS_1984",SPHEROID["WGS 84",6378137,298.257223563,
                         AUTHORITY["EPSG","7030"]],AUTHORITY["EPSG","6326"]],
                         PRIMEM["Greenwich",0],UNIT["degree",0.0174532925199433],
                         AUTHORITY["EPSG","4326"]],PROJECTION["Mercator_1SP"],
                         PARAMETER["central_meridian",0],
                         PARAMETER["scale_factor",0.803798909747978],
                         PARAMETER["false_easting",0],
                         PARAMETER["false_northing",0],
                         UNIT["metre",1,AUTHORITY["EPSG","9001"]]]
                     """

    srs_description = ""

    def __init__(self):
        """
        Constructor
        """
        super(ScaledWorldMercator, self).__init__()

    @staticmethod
    def pixel_size(z):
        """
        Calculates the pixel size for a given zoom level.
        """
        return 125829.12 / 2 ** z

    @staticmethod
    def lat_to_northing(lat):
        """
        Convert a latitude to a northing
                      /    / pi   phi \   / 1 - e sin(phi) \ e/2 \
        y(phi) = R ln| tan| --- + ---  | |  --------------  |     |
                      \    \ 4     2  /   \ 1 + e sin(phi) /     /
        """
        r = 6378137.0 * 0.857385503731176
        e = 0.081819190842621
        return r * log(tan((pi / 2 + lat) / 2) * ((1 - e * sin(lat)) /
                                                  (1 + e * sin(lat))) ** (e / 2))

    @staticmethod
    def tile_to_lat_lon(z, x, y):
        """
        Returns the lat/lon coordinates of the bottom-left corner of the input
        tile. Finds the value numerically (using the secant method). A scale
        factor has been added specifically for scaled world mercator.

        Inputs:
        z -- zoom level value for input tile
        x -- tile column value for input tile
        y -- tile row value for input tile
        """
        n = 2.0 ** z
        r = 6378137.0 * 0.857385503731176
        lon = x / n * 360.0 - 180.0
        my = (y - 2 ** (z - 1)) * r * pi * 2 / 2 ** z

        def f(phi):
            return ScaledWorldMercator.lat_to_northing(phi) - my

        lat = 0.0
        oldLat = 1.0
        diff = 1.0
        while abs(diff) > 0.0001:
            newLat = lat - f(lat) * (lat - oldLat) / (f(lat) - f(oldLat))
            if newLat > 1.4849969713855238:
                newLat = 1.4849969713855238
            elif newLat < -1.4849969713855238:
                newLat = -1.4849969713855238
            oldLat = lat
            lat = newLat
            diff = lat - oldLat
        lat = lat * 180.0 / pi
        return lat, lon

    def tile_to_meters(self, z, x, y):
        """
        Returns the meter coordinates of the bottom-left corner of the input
        tile. A scale factor has been added to the longitude meters
        calculation.

        Inputs:
        z -- zoom level value for input tile
        x -- tile column (longitude) value for input tile
        y -- tile row (latitude) value for input tile
        """
        lat, lon = self.tile_to_lat_lon(z, x, y)
        meters_x = lon * (pi * (6378137.0 * 0.857385503731176)) / 180.0
        meters_y = self.lat_to_northing(lat * pi / 180.0)
        # Instituting a 2 decimal place round to ensure accuracy
        return meters_x, round(meters_y, 2)
