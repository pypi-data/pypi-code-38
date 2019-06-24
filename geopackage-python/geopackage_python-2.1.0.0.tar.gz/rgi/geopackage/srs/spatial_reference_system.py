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

from abc import abstractmethod, abstractproperty

from rgi.geopackage.core.spatial_ref_system_entry import SpatialReferenceSystemEntry


class SpatialReferenceSystem(SpatialReferenceSystemEntry):
    """
    The gpkg_spatial_ref_sys table includes the columns specified in SQL/MM (ISO 13249-3) [12]
     and shown in Spatial Ref Sys Table Definition below containing data that defines spatial
     reference systems.
    """

    @abstractmethod
    def __init__(self):
        super(SpatialReferenceSystem, self).__init__(srs_name=self.spatial_ref_sys_name,
                                                     srs_id=self.srs_identifier,
                                                     organization=self.srs_organization,
                                                     organization_coordsys_id=self.srs_organization_coordsys_id,
                                                     definition=self.srs_definition,
                                                     description=self.srs_description)

    @abstractproperty
    def spatial_ref_sys_name(self):
        """
            Human readable name of this SRS
            :return String
        """
        raise NotImplementedError()


    @abstractproperty
    def srs_identifier(self):
        """
        Unique identifier for each Spatial Reference System within a GeoPackage e.g. 4326
        :return: Integer
        """
        raise NotImplementedError()

    @abstractproperty
    def srs_organization(self):
        """
        Case-insensitive name of the defining organization e.g. EPSG or epsg
        :return: String
        """
        raise NotImplementedError()

    @abstractproperty
    def srs_organization_coordsys_id(self):
        """
        Numeric ID of the Spatial Reference System assigned by the organization
        :return: Integer
        """
        raise NotImplementedError()

    @abstractproperty
    def srs_definition(self):
        """
        Well-known Text Representation of the Spatial Reference System
        :return: String
        """
        raise NotImplementedError()

    @abstractproperty
    def srs_description(self):
        """
        Human readable description of this SRS
        :return: String
        """
        raise NotImplementedError()

    @staticmethod
    @abstractmethod
    def invert_y(z, y):
        """
        Inverts the Y tile value.

        Inputs:
        z -- the zoom level associated with the tile
        y -- the Y tile number

        Returns:
        The flipped tile value
        """
        raise NotImplementedError()


    @abstractmethod
    def get_coord(self,z,x,y):
        """
        Returns the coordinates (in units of the srs) of the bottom-left corner of the
        input tile.

        Inputs:
        z -- zoom level value for input tile
        x -- tile column (longitude) value for input tile
        y -- tile row (latitude) value for input tile
        """
        raise NotImplementedError()


    @staticmethod
    @abstractmethod
    def truncate(coord):
        """
        Formats a coordinate to within an acceptable degree of accuracy (i.e. 2
        decimal places for mercator).
        """
        raise NotImplementedError()

    @abstractmethod
    def pixel_x_size(self, z):
        """
        returns the width of the associated tile set's spatial reference system (SRS units per pixel) for the given
        zoom level

        :param z: the zoom level
        :type z: int
        :return: the width of the associated tile set's spatial reference system (SRS units per pixel)
        """
        raise NotImplementedError()

    @abstractmethod
    def pixel_y_size(self, z):
        """
        returns the height of the associated tile set's spatial reference system (SRS units per pixel) for the given
        zoom level

        :param z: the zoom level
        :type z: int
        :return: the height of the associated tile set's spatial reference system (SRS units per pixel)
        """
        raise NotImplementedError()

    @property
    @abstractmethod
    def tile_size(self):
        """
        The tile's width and height in pixels.
        :return: the tile's width/height in pixels
        """
        raise NotImplementedError()


