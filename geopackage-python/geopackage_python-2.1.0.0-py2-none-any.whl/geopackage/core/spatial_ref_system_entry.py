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


class SpatialReferenceSystemEntry(object):
    """
    An object representing an entry in the gpkg_spatial_ref_sys Table
    """

    def __init__(self,
                 srs_name,
                 srs_id,
                 organization,
                 organization_coordsys_id,
                 definition,
                 description):
        """
        Constructor

        :param srs_name:  Human readable name of this SRS
        :type srs_name: str

        :param srs_id: Unique identifier for each Spatial Reference System within a GeoPackage e.g. 4326
        :type srs_id: int

        :param organization: Case-insensitive name of the defining organization e.g. EPSG or epsg
        :type organization: str

        :param organization_coordsys_id: Numeric ID of the Spatial Reference System assigned by the organization
        :type organization_coordsys_id: int

        :param definition: Well-known Text Representation of the Spatial Reference System
        :type definition: str

        :param description: Human readable description of this SRS
        :type description: str
        """
        self.srs_name = srs_name
        self.organization = organization
        self.organization_coordsys_id = organization_coordsys_id
        self.srs_id = srs_id
        self.definition = definition
        self.description = description
