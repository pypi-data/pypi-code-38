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

VECTOR_TILES_EXTENSION_NAME = "im_vector_tiles"  # type: str
"""
GeoPackage Vector Tiles Extension name
"""

VECTOR_TILES_DEFINITION = "https://portal.opengeospatial.org/wiki/pub/VectorTilesPilot/ConvertDocsOutputVTP/VTP/VTPGPKG12.pdf"  # type: str
"""
GeoPackage Vector Tiles Extension definition
"""

GEOPACKAGE_VECTOR_FIELDS_TABLE_NAME = "gpkgext_vt_fields"  # type: str
"""
GeoPackage Vector Tiles relational table for Vector Tiles fields Name. gpkgext_vt_fields
"""

GEOPACKAGE_VECTOR_LAYERS_TABLE_NAME = "gpkgext_vt_layers"  # type: str
"""
GeoPackage Vector Tiles relational table for Vector Tiles layers Name. gpkgext_vt_layers
"""

VECTOR_TILES_DATA_TYPE = "vector-tiles" # type: str
"""GeoPackage Vector Tiles data_type in the gpkg_contents table"""
