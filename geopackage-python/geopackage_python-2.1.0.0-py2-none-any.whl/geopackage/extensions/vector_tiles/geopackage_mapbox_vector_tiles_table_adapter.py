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

import mapbox_vector_tile

from rgi.geopackage.extensions.geopackage_extensions_table_adapter import GeoPackageExtensionsTableAdapter
from rgi.geopackage.extensions.vector_tiles.geopackage_vector_tiles_table_adapter import GeoPackageVectorTilesTableAdapter
from rgi.geopackage.extensions.vector_tiles.vector_fields.geopackage_vector_fields_table_adapter import GeoPackageVectorFieldsTableAdapter
from rgi.geopackage.extensions.vector_tiles.vector_fields.vector_fields_entry import VectorFieldType, \
    VectorFieldsEntry
from rgi.geopackage.extensions.vector_tiles.vector_layers.geopackage_vector_layers_table_adapter import GeoPackageVectorLayersTableAdapter
from rgi.geopackage.extensions.vector_tiles.vector_layers.vector_layers_entry import VectorLayersEntry
from sqlite3 import Cursor, Binary

GEOPACKAGE_MAPBOX_VECTOR_TILES_EXTENSION_NAME = "im_vector_tiles_mapbox"


class GeoPackageMapBoxVectorTilesTableAdapter(GeoPackageVectorTilesTableAdapter):
    """
        GeoPackage Tiles MapBox encoded vector tiles extension. Represents the im_vector_tiles_mapbox extension. Creates
        vector-tile pyramid user data tables where the tile_data column is encoded in Google Protocol Buffer as defined
        by MVT https://github.com/mapbox/vector-tile-spec/blob/master/2.1/vector_tile.proto
    """

    def __init__(self,
                 vector_tiles_table_name):
        """
        Constructor

        :param vector_tiles_table_name: the name of the Vector-tiles table (pyramid-user-data table) that will
        have the vector-tiles encoded in Google Protocol Buffer format.
        """
        super(GeoPackageMapBoxVectorTilesTableAdapter, self).__init__(vector_tiles_table_name)

    @staticmethod
    def insert_vector_layers_and_fields_from_tile_data(cursor,
                                                       tile_data,
                                                       table_name):
        """
        Adds the vector layers and fields found in the tile_data object.  In Google Protocol Buffer (MVT) format,
        the layers and fields are found within the data. This will decode the Google Protocol Buffer encoed data
        and add the necessary values to the appropriate tables

        :param cursor: the cursor to the GeoPackage database's connection
        :type cursor: Cursor

        :param tile_data: The vector-tile encoded in Google Protocol Buffer (MVT)
        :type tile_data: Binary

        :param table_name: the name of the vector-tiles table the data is associated with
        :type table_name: str

        :rtype (list of VectorLayersEntry, list of VectorFieldsEntry)
        """
        # Use the mapbox vector tiles to decode the data
        decoded_data = mapbox_vector_tile.decode(tile_data)
        # create the lists of layers and fields created
        vector_layers_entries = list()
        layer_field_dictionary = dict()

        # go through each layer to find the layers
        for layer, values in decoded_data.items():
            layer_entry = VectorLayersEntry(table_name=table_name,
                                            name=layer,
                                            description="",
                                            min_zoom=None,
                                            max_zoom=None,
                                            stylable_layer_set=None)

            # add the layer to the GeoPackage. It is important to add it bc the Fields need to have a layer_id
            # to create the vector field entry in the GeoPackage
            vector_layers_entries.append(layer_entry)
            if layer_entry.name not in layer_field_dictionary:
                layer_field_dictionary[layer_entry.name] = set()
            # iterate through each feature's properties to extract the fields
            for feature in values.get('features'):
                for key, item in feature.get('properties').items():
                    # figure out from the value what type of field it is (boolean, string, number)
                    vector_field_type = VectorFieldType.convert_string_value_to_vector_field_type(item)
                    # create the vector fields entry
                    fields_entry = VectorFieldsEntry(layer_id=None,
                                                     name=key,
                                                     field_type=vector_field_type)
                    # don't add to list if repeated
                    if not any(field for field in layer_field_dictionary[layer_entry.name]
                               if field.name == fields_entry.name and field.type == fields_entry.type):
                        layer_field_dictionary[layer_entry.name].add(fields_entry)
        # add the vector layers to the geopackage
        GeoPackageVectorLayersTableAdapter.insert_vector_layers_entries_bulk(cursor=cursor,
                                                                             vector_layers_entries=vector_layers_entries)

        for layer_name, vector_fields_entries in layer_field_dictionary.items():
            GeoPackageVectorFieldsTableAdapter.insert_or_update_vector_field_entries_in_bulk(cursor=cursor,
                                                                                             vector_tiles_table_name=table_name,
                                                                                             vector_layer_name=layer_name,
                                                                                             vector_field_entries=vector_fields_entries)

    extension_name = GEOPACKAGE_MAPBOX_VECTOR_TILES_EXTENSION_NAME

    @classmethod
    def create_pyramid_user_data_table(cls,
                                       cursor,
                                       tiles_content):
        """
        Creates the vector-tile pyramid user data table with tile_data encoded with Google Protocol Buffer format
        (MVT).  It will also register the extension in the GeoPackage.

        :param cursor: the cursor to the GeoPackage database's connection
        :type cursor: Cursor

        :param tiles_content: The TileSet entry in the gpkg_contents table describing the vector-tiles in the GeoPackage
        :type tiles_content: VectorTilesContentEntry
        """
        GeoPackageMapBoxVectorTilesTableAdapter.create_default_tiles_tables(cursor=cursor)

        super(GeoPackageMapBoxVectorTilesTableAdapter, cls).create_pyramid_user_data_table(cursor=cursor,
                                                                                           tiles_content=tiles_content)
        # add the table to the extensions table
        GeoPackageExtensionsTableAdapter.insert_or_update_extensions_row(cursor=cursor,
                                                                         extension=
                                                             GeoPackageMapBoxVectorTilesTableAdapter(tiles_content.table_name))
