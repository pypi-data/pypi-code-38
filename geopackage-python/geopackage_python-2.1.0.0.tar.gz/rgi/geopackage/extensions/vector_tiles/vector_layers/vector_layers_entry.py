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


class VectorLayersEntry(object):
    """
    The object that represents an entry to the GeoPackage Vector Layers Table (gpkgext_vt_layers)
    """

    def __init__(self,
                 table_name,
                 name,
                 description,
                 min_zoom,
                 max_zoom,
                 stylable_layer_set,
                 identifier=None):
        """
        Constructor

        :param identifier:primary key int identifier for the column id.  If None, a value will be assigned to it when
        added to the GeoPackage
        :type identifier: int, None

        :param table_name: vector tiles table_name matches in the gpkg_contents
        :type table_name: str

        :param name: name is the layer name
        :type name: str

        :param description: optional text description of layer
        :type description: str, None

        :param min_zoom: optional integer minimum zoom level
        :type min_zoom: str, None

        :param max_zoom: optional maximum zoom level
        :type max_zoom: str, None

        :param stylable_layer_set: optional styles set name that is a FK to the gpkgext_stylesheets styles_set name
        :type stylable_layer_set: str
        """

        self.table_name = table_name
        self.name = name
        self.description = description
        self.min_zoom = min_zoom
        self.max_zoom = max_zoom
        self.identifier = identifier
        self.stylable_layer_set = stylable_layer_set