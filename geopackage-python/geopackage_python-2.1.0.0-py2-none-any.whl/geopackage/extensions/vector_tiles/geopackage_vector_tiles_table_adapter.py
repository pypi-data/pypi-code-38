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
from abc import abstractmethod, abstractproperty
from sqlite3 import Cursor, Binary

from rgi.geopackage.extensions.extension_entry import ExtensionEntry, EXTENSION_READ_WRITE_SCOPE
from rgi.geopackage.extensions.geopackage_extensions_table_adapter import GeoPackageExtensionsTableAdapter
from rgi.geopackage.extensions.vector_tiles.vector_fields.geopackage_vector_fields_table_adapter import GeoPackageVectorFieldsTableAdapter
from rgi.geopackage.extensions.vector_tiles.vector_layers.geopackage_vector_layers_table_adapter import GeoPackageVectorLayersTableAdapter
from rgi.geopackage.extensions.vector_tiles.vector_layers.vector_layers_entry import VectorLayersEntry
from rgi.geopackage.extensions.vector_tiles.vector_tiles_constants import VECTOR_TILES_DEFINITION
from rgi.geopackage.tiles.geopackage_abstract_tiles_table_adapter import GeoPackageAbstractTilesTableAdapter
from rgi.geopackage.tiles.geopackage_tiles_table_adapter import GeoPackageTilesTableAdapter


class GeoPackageVectorTilesTableAdapter(ExtensionEntry, GeoPackageAbstractTilesTableAdapter):
    """
    Abstract class representation of the GeoPackage Vector Tiles Extension.

    Represents the GeoPackage Vector Tiles extension. Defines the requirements for encoding the tile_data column
    in pyramid-user-data tables in a vector-tile format (rather than raster ie jpeg, png).  Also defines the
    relational tables needed for vector tiles on top of the gpkg_tile_matrix and gpkg_tile_matrix_set. Registers
    the extension in the GeoPackage Extensions table as well.
    """

    def __init__(self,
                 vector_tiles_table_name):
        super(GeoPackageVectorTilesTableAdapter, self).__init__(table_name=vector_tiles_table_name,
                                                                column_name='tile_data',
                                                                # name depends if mapbox or geojson
                                                                extension_name=self.extension_name,
                                                                definition=VECTOR_TILES_DEFINITION,
                                                                scope=EXTENSION_READ_WRITE_SCOPE)
        self.vector_tiles_table_name = vector_tiles_table_name

    @staticmethod
    def create_default_tiles_tables(cursor):
        """
        Creates the related tables required for storing tiles: gpkg_tile_matrix, gpkg_tile_matrix_set

        :param cursor: the cursor to the GeoPackage database's connection
        :type cursor: Cursor
        """
        # create the default tiles tables
        GeoPackageTilesTableAdapter.create_default_tiles_tables(cursor=cursor)
        GeoPackageVectorLayersTableAdapter.create_vector_layers_table(cursor=cursor)
        GeoPackageVectorFieldsTableAdapter.create_vector_fields_table(cursor=cursor)
        GeoPackageExtensionsTableAdapter.insert_or_update_extensions_row(cursor=cursor,
                                                                         extension=GeoPackageVectorFieldsTableAdapter())
        GeoPackageExtensionsTableAdapter.insert_or_update_extensions_row(cursor=cursor,
                                                                         extension=GeoPackageVectorLayersTableAdapter())

    def insert_or_update_vector_tiles_table(self,
                                            cursor,
                                            vector_tiles_content):
        """
        Adds all the default tables needed to add a vector-tiles table. It also registers the extension as well.

        :param cursor: the cursor to the GeoPackage database's connection
        :type cursor: Cursor

        :param vector_tiles_content: the vector tiles content information
        :type vector_tiles_content: VectorTilesContentEntry
        """
        GeoPackageVectorTilesTableAdapter.create_default_tiles_tables(cursor=cursor)
        # create the tiles table but with a vector-tiles data type
        GeoPackageTilesTableAdapter.create_pyramid_user_data_table(cursor=cursor,
                                                                   tiles_content=vector_tiles_content)

        # register the extension
        # add the vector-tiles table extension
        GeoPackageExtensionsTableAdapter.insert_or_update_extensions_row(cursor=cursor,
                                                                         extension=self)

    @classmethod
    def insert_or_update_tile_data(cls,
                                   cursor,
                                   table_name,
                                   zoom_level,
                                   tile_column,
                                   tile_row,
                                   tile_data):
        """
        Inserts or updates row in the pyramid user data table with the table_name provided.

        :param cursor: the cursor to the GeoPackage database's connection
        :type cursor: Cursor

        :param table_name: Tile Pyramid User Data Table Name
        :type table_name: str

        :param zoom_level:  0 <= zoom_level <= max_level for table_name
        :type zoom_level: int

        :param tile_column:  0 to tile_matrix matrix_width - 1
        :type tile_column: int

        :param tile_row: 0 to tile_matrix matrix_height - 1
        :type tile_row: int

        :param tile_data: vector-tile encoded Binary data
        :type tile_data: Binary
        """
        super(GeoPackageVectorTilesTableAdapter, cls).insert_or_update_tile_data(cursor=cursor,
                                                                                 table_name=table_name,
                                                                                 zoom_level=zoom_level,
                                                                                 tile_column=tile_column,
                                                                                 tile_row=tile_row,
                                                                                 tile_data=tile_data)

        cls.insert_vector_layers_and_fields_from_tile_data(cursor=cursor,
                                                           tile_data=tile_data,
                                                           table_name=table_name)

    @classmethod
    def insert_or_update_tile_data_bulk(cls,
                                        cursor,
                                        table_name,
                                        tiles):
        """
        Inserts or updates rows in the pyramid user data table with the table_name provided.

        :param cursor: the cursor to the GeoPackage database's connection
        :type cursor: Cursor

        :param table_name: Tile Pyramid User Data Table Name
        :type table_name: str

        :param tiles: the tiles to update or insert into the tile pyramid user data table
        :type tiles: list of TileDataInformation
        """
        super(GeoPackageVectorTilesTableAdapter, cls).insert_or_update_tile_data_bulk(cursor=cursor,
                                                                                      table_name=table_name,
                                                                                      tiles=tiles)
        for tile in tiles:
            cls.insert_vector_layers_and_fields_from_tile_data(cursor=cursor,
                                                               tile_data=tile.tile_data,
                                                               table_name=table_name)

    @staticmethod
    @abstractmethod
    def insert_vector_layers_and_fields_from_tile_data(cursor,
                                                       tile_data,
                                                       table_name):
        # type: (Cursor, Binary, str) -> tuple[list[VectorLayersEntry], list[VectorFieldsEntry]]
        """
        Reads the tile_data and extracts the layers and fields information from the tile.

        :param cursor: the cursor to the GeoPackage database's connection
        :type cursor: Cursor

        :param tile_data: the tile_data
        :type tile_data: Binary

        :param table_name: the name of the table this tile_data belongs to
        :type table_name: str

        :returns: tuple where the first value is the list of VectorLayerEntry values and the second value is
        the list of VectorFieldsEntry values.
        :rtype: (list of VectorLayersEntry, list of VectorFieldsEntry)
        """
        raise NotImplementedError()

    @abstractproperty
    def extension_name(self):
        """
        The Name of the Extension

        :return: the name of the extension
        :rtype: str
        """
        raise NotImplementedError
