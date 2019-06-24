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
import json
from sqlite3 import Cursor, Binary

from rgi.geopackage.extensions.geopackage_extensions_table_adapter import GeoPackageExtensionsTableAdapter
from rgi.geopackage.extensions.vector_tiles.geopackage_vector_tiles_table_adapter import GeoPackageVectorTilesTableAdapter
from rgi.geopackage.extensions.vector_tiles.vector_fields.geopackage_vector_fields_table_adapter import GeoPackageVectorFieldsTableAdapter
from rgi.geopackage.extensions.vector_tiles.vector_fields.vector_fields_entry import VectorFieldsEntry, VectorFieldType
from rgi.geopackage.extensions.vector_tiles.vector_layers.geopackage_vector_layers_table_adapter import GeoPackageVectorLayersTableAdapter
from rgi.geopackage.extensions.vector_tiles.vector_layers.vector_layers_entry import VectorLayersEntry

GEOPACKAGE_GEOJSON_VECTOR_TILES_EXTENSION_NAME = "im_vector_tiles_geojson"


class GeoPackageGeoJSONVectorTilesTableAdapter(GeoPackageVectorTilesTableAdapter):
    """
    GeoPackage Tiles GeoJSON encoded vector tiles extension. Represents the im_vector_tiles_geojson extension.  Creates
    vector-tile pyramid user data tables where the tile_data column is encoded in GeoJSON
    """

    def __init__(self,
                 vector_tiles_table_name):
        """
        Constructor

        :param vector_tiles_table_name: The table name of the vector-tiles table that has GeoJSON encoding for the
        tile_data column
        """
        super(GeoPackageGeoJSONVectorTilesTableAdapter, self).__init__(vector_tiles_table_name)

    @classmethod
    def create_pyramid_user_data_table(cls,
                                       cursor,
                                       tiles_content):
        """
        Creates the vector-tile pyramid user data table with tile_data encoded in GeoJSON format. It will also register
        the extension in the GeoPackage.

        :param cursor: the cursor to the GeoPackage database's connection
        :type cursor: Cursor

        :param tiles_content: The TileSet entry in the gpkg_contents table describing the vector-tiles in the GeoPackage
        :type tiles_content: VectorTilesContentEntry
        """
        GeoPackageGeoJSONVectorTilesTableAdapter.create_default_tiles_tables(cursor=cursor)

        super(GeoPackageGeoJSONVectorTilesTableAdapter, cls).create_pyramid_user_data_table(cursor=cursor,
                                                                                            tiles_content=tiles_content)

        GeoPackageExtensionsTableAdapter.insert_or_update_extensions_row(cursor=cursor,
                                                                         extension=
                                                             GeoPackageGeoJSONVectorTilesTableAdapter(tiles_content.table_name))

    extension_name = GEOPACKAGE_GEOJSON_VECTOR_TILES_EXTENSION_NAME

    @staticmethod
    def insert_vector_layers_and_fields_from_tile_data(cursor,
                                                       tile_data,
                                                       table_name):
        """
        Reads the vector tiles data and extracts the Vector Layers and Fields from the GeoJSON encoded data.

        :param cursor: the cursor to the GeoPackage database's connection
        :type cursor: Cursor

        :param tile_data: the GeoJSON data to extract the information from
        :type tile_data: Binary

        :param table_name: the vector tiles layer name
        :type table_name: str

        :rtype (list of VectorLayersEntry, list of VectorFieldsEntry)
        """

        vector_layers_entries = []
        vector_fields_entries = set()
        # in GeoJSON the entire GeoJSON is considered the layer
        layer_entry = VectorLayersEntry(table_name=table_name,
                                        name=table_name,
                                        description="",
                                        min_zoom=None,
                                        max_zoom=None,
                                        stylable_layer_set=None)

        # add the layer to the GeoPackage. It is important to add it bc the Fields need to have a layer_id
        # to create the vector field entry in the GeoPackage
        GeoPackageVectorLayersTableAdapter.insert_or_update_vector_tile_layer_entry(cursor=cursor,
                                                                                    vector_tile_layer_entry=layer_entry)
        vector_layers_entries.append(layer_entry)

        data = json.loads(tile_data)
        for feature in data['features']:
            for json_property in feature['properties']:
                value = feature['properties'][json_property]
                vector_field_entry = VectorFieldsEntry(layer_id=layer_entry.identifier,
                                                       name=json_property,
                                                       field_type=VectorFieldType.convert_string_value_to_vector_field_type(
                                                           value))
                # don't need to add it if it is a duplicate
                if not any(field for field in vector_fields_entries
                           if field.name == vector_field_entry.name
                              and field.type == vector_field_entry.type):
                    vector_fields_entries.add(vector_field_entry)

        GeoPackageVectorFieldsTableAdapter.insert_or_update_vector_field_entries_in_bulk(cursor=cursor,
                                                                                         vector_tiles_table_name=table_name,
                                                                                         vector_layer_name=table_name,
                                                                                         vector_field_entries=vector_fields_entries)