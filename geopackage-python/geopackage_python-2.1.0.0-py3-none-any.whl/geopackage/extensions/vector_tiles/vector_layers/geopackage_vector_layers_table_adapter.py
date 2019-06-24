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
from rgi.geopackage.core.geopackage_core_table_adapter import GEOPACKAGE_CONTENTS_TABLE_NAME
from rgi.geopackage.extensions.extension_entry import ExtensionEntry, EXTENSION_READ_WRITE_SCOPE
from rgi.geopackage.extensions.vector_tiles.vector_layers.vector_layers_entry import VectorLayersEntry
from rgi.geopackage.extensions.vector_tiles.vector_tiles_constants import GEOPACKAGE_VECTOR_LAYERS_TABLE_NAME, \
    VECTOR_TILES_EXTENSION_NAME, VECTOR_TILES_DEFINITION
from rgi.geopackage.extensions.vector_tiles.vector_styles.styles_extension_constants import \
    GEOPACKAGE_STYLESHEETS_TABLE_NAME
from rgi.geopackage.utility.sql_column_query import SqlColumnQuery

from rgi.geopackage.utility.sql_utility import select_query, select_all_query, insert_or_update_row, \
    columns_exists, table_exists


class GeoPackageVectorLayersTableAdapter(ExtensionEntry):
    """
    Represents the GeoPackage Vector Layers table (gpkgext_vt_layers)
    """

    def __init__(self):
        super(GeoPackageVectorLayersTableAdapter, self).__init__(table_name=GEOPACKAGE_VECTOR_LAYERS_TABLE_NAME,
                                                                 column_name=None,
                                                                 scope=EXTENSION_READ_WRITE_SCOPE,
                                                                 extension_name=VECTOR_TILES_EXTENSION_NAME,
                                                                 definition=VECTOR_TILES_DEFINITION)

    @classmethod
    def create_vector_layers_table(cls,
                                   cursor):
        """
        Creates the Vector Tiles Layers Table (gpkgext_vt_layers)

        :param cursor: the cursor to the GeoPackage database's connection
        :type cursor: Cursor
        """

        cursor.execute("""
                             CREATE TABLE IF NOT EXISTS {table_name}
                             (id                    INTEGER PRIMARY KEY AUTOINCREMENT, -- primary key
                              table_name            TEXT NOT NULL,                     -- table_name matches in the gpkg_contents
                              name                  TEXT NOT NULL,                     -- name is layer name
                              description           TEXT,                              -- optional text description
                              minzoom               INTEGER,                           -- optional integer minimum zoom level
                              maxzoom               INTEGER,                           -- optional maximum zoom level
                              stylable_layer_set    TEXT,                              -- optional stylable_layer_set value that is a FK to the {style_sheet_table} table
                              CONSTRAINT fk_gpkg_con_tbl_name FOREIGN KEY (table_name) REFERENCES {gpkg_contents}(table_name),
                              CONSTRAINT fk_gpkgext_stylsheets_style_set FOREIGN KEY (stylable_layer_set) REFERENCES {style_sheet_table}(layer_set),
                               UNIQUE (table_name, name)
                             );
                           """.format(table_name=GEOPACKAGE_VECTOR_LAYERS_TABLE_NAME,
                                      gpkg_contents=GEOPACKAGE_CONTENTS_TABLE_NAME,
                                      style_sheet_table=GEOPACKAGE_STYLESHEETS_TABLE_NAME))

    @classmethod
    def _convert_rows_to_vector_layers_entry(cls,
                                             rows):
        """
        Convert a list of Row objects to a list of VectorLayersEntry objects.

        :param rows: row entries to convert to a list of VectorLayersEntry objects
        :type rows: list of Row

        :rtype: list of VectorLayersEntry
        """
        return [VectorLayersEntry(table_name=row['table_name'],
                                  name=row['name'],
                                  description=row['description'],
                                  min_zoom=row['minzoom'],
                                  max_zoom=row['maxzoom'],
                                  stylable_layer_set=row['stylable_layer_set'],
                                  identifier=row['id'])
                for row in rows]

    @classmethod
    def _get_all_table_columns(cls):
        """
        Return the list of the column names in this table

        :rtype: list of str
        """
        return ['id', 'table_name', 'name', 'minzoom', 'maxzoom', 'description', 'stylable_layer_set']

    @classmethod
    def _get_insert_or_update_sql_column_query(cls,
                                               vector_tile_layer_entry):
        """

        Return the list of SqlColumnQuery objects that are needed to insert or update a row in the GeoPackage

        :param vector_tile_layer_entry: the vector tile layer entry to be added to the GeoPackage
        :type vector_tile_layer_entry: VectorLayersEntry

        :rtype: list of SqlColumnQuery
        """

        return [SqlColumnQuery(column_name='table_name',
                               column_value=vector_tile_layer_entry.table_name),
                SqlColumnQuery(column_name='name',
                               column_value=vector_tile_layer_entry.name),
                SqlColumnQuery(column_name='description',
                               column_value=vector_tile_layer_entry.description,
                               include_in_where_clause=False),
                SqlColumnQuery(column_name='minzoom',
                               column_value=vector_tile_layer_entry.min_zoom,
                               include_in_where_clause=False),
                SqlColumnQuery(column_name='maxzoom',
                               column_value=vector_tile_layer_entry.max_zoom,
                               include_in_where_clause=False),
                SqlColumnQuery(column_name='stylable_layer_set',
                               column_value=vector_tile_layer_entry.stylable_layer_set,
                               include_in_where_clause=False)]

    @classmethod
    def table_exists(cls,
                     cursor):
        """
        Return true if the table exists with all the expected columns for the GeoPackage Vector Layers, false otherwise

        :param cursor: the cursor to the GeoPackage database's connection
        :type cursor: Cursor
        """

        return columns_exists(cursor=cursor,
                              table_name=GEOPACKAGE_VECTOR_LAYERS_TABLE_NAME,
                              column_names=cls._get_all_table_columns())

    @classmethod
    def get_all_vector_layers_entries(cls,
                                      cursor):
        """
        Returns a list of Vector Layer entries that exist in the GeoPackage's gpkgext_vt_layers table

        :param cursor: the cursor to the GeoPackage database's connection
        :type cursor: Cursor

        :return a list of Vector Layer entries that exist in the GeoPackage's gpkgext_vt_layers table
        :rtype: list of VectorLayersEntry
        """
        if not cls.table_exists(cursor):
            raise ValueError("Table {table_name} does not exist or does not have all the appropriate columns. "
                             "Expected columns: {columns}."
                             .format(table_name=GEOPACKAGE_VECTOR_LAYERS_TABLE_NAME,
                                     columns=cls._get_all_table_columns()))

        # select all the rows
        rows = select_all_query(cursor=cursor,
                                table_name=GEOPACKAGE_VECTOR_LAYERS_TABLE_NAME)

        return cls._convert_rows_to_vector_layers_entry(rows=rows)

    @classmethod
    def get_vector_layer_entries_by_table_name(cls,
                                               cursor,
                                               vector_tiles_table_name):
        """
        Returns any Vector Layer Entries whose table_name column value matches the vector_tiles_table_name parameter.

        :param cursor: the cursor to the GeoPackage database's connection
        :type cursor: Cursor

        :param vector_tiles_table_name: the table_name of the vector tiles table that the entries in the vector
        layer table should match
        :type vector_tiles_table_name: str

        :return: Returns any Vector Layer Entries whose table_name column value matches the vector_tiles_table_name
        parameter.
        :rtype: list of VectorLayersEntry
        """
        if not cls.table_exists(cursor):
            raise ValueError("Table {table_name} does not exist or does not have all the appropriate columns. "
                             "Expected columns: {columns}."
                             .format(table_name=GEOPACKAGE_VECTOR_LAYERS_TABLE_NAME,
                                     columns=cls._get_all_table_columns()))

        # select all the rows
        rows = select_query(cursor=cursor,
                            table_name=GEOPACKAGE_VECTOR_LAYERS_TABLE_NAME,
                            select_columns=cls._get_all_table_columns(),
                            where_columns_dictionary={'table_name': vector_tiles_table_name})

        # get the results
        return cls._convert_rows_to_vector_layers_entry(rows=rows)

    @classmethod
    def get_vector_layer_entries_by_table_name_and_layer_name(cls,
                                                              cursor,
                                                              vector_tiles_table_name,
                                                              layer_name):
        """
        Returns any Vector Layer Entries whose table_name column value matches the vector_tiles_table_name parameter and
        the layer_name parameter.

        :param layer_name: the name of the layer
        :type layer_name: str

        :param cursor: the cursor to the GeoPackage database's connection
        :type cursor: Cursor

        :param vector_tiles_table_name: the table_name of the vector tiles table that the entries in the vector
        layer table should match
        :type vector_tiles_table_name: str

        :return: Returns any Vector Layer Entries whose table_name column value matches the vector_tiles_table_name
        parameter and layer_name parameter
        :rtype: VectorLayersEntry
        """
        if not cls.table_exists(cursor):
            raise ValueError("Table {table_name} does not exist or does not have all the appropriate columns. "
                             "Expected columns: {columns}."
                             .format(table_name=GEOPACKAGE_VECTOR_LAYERS_TABLE_NAME,
                                     columns=cls._get_all_table_columns()))

        # select all the rows
        rows = select_query(cursor=cursor,
                            table_name=GEOPACKAGE_VECTOR_LAYERS_TABLE_NAME,
                            select_columns=cls._get_all_table_columns(),
                            where_columns_dictionary={'table_name': vector_tiles_table_name,
                                                      'name': layer_name})

        # get the results
        layer_entries = cls._convert_rows_to_vector_layers_entry(rows=rows)
        # there cannot be more than one entry due to the unique constraint of table_name to layer name
        return layer_entries[0] if len(layer_entries) == 1 else None

    @classmethod
    def insert_or_update_vector_tile_layer_entry(cls,
                                                 cursor,
                                                 vector_tile_layer_entry):
        """
        Adds an entry to the Vector Tiles Layers Table (gpkgext_vt_layers) with the values given. To update a given
        row, the table_name and name columns must be equivalent to what already exists in the table. The id value
        is ignored for updates.

        :param cursor: the cursor to the GeoPackage database's connection
        :type cursor: Cursor

        :param vector_tile_layer_entry: the vector tile layer entry to be added to the table
        :type vector_tile_layer_entry: VectorLayersEntry

        :return Updated VectorLayerEntry with the id value populated
        """
        if not cls.table_exists(cursor):
            cls.create_vector_layers_table(cursor=cursor)

        sql_columns_list = cls._get_insert_or_update_sql_column_query(vector_tile_layer_entry=
                                                                      vector_tile_layer_entry)
        insert_or_update_row(cursor=cursor,
                             table_name=GEOPACKAGE_VECTOR_LAYERS_TABLE_NAME,
                             sql_columns_list=sql_columns_list)

        where_dictionary = dict((column.column_name, column.column_value) for column in sql_columns_list)
        # get the id value
        vector_tile_layer_entry.identifier = select_query(cursor=cursor,
                                                          select_columns=['id'],
                                                          table_name=GEOPACKAGE_VECTOR_LAYERS_TABLE_NAME,
                                                          where_columns_dictionary=where_dictionary)[0]['id']

        # set the layer id
        return vector_tile_layer_entry

    @classmethod
    def insert_vector_layers_entries_bulk(cls,
                                          cursor,
                                          vector_layers_entries):
        """
        Adds all the entries to the Vector Tiles Layers Table (gpkgext_vt_layers) with the values given. (id value
        is ignored)

        :param cursor: the cursor to the GeoPackage database's connection
        :type cursor: Cursor

        :param vector_layers_entries: the vector tile layer entry to be added to the table
        :type vector_layers_entries: list of VectorLayersEntry

        :return Updated VectorLayerEntries with the id value populated
        """

        if not table_exists(cursor=cursor,
                            table_name=GEOPACKAGE_VECTOR_LAYERS_TABLE_NAME):
            raise ValueError("Cannot add row to {table} because it does not exist"
                             .format(table=GEOPACKAGE_VECTOR_LAYERS_TABLE_NAME))

        # id value is populated based on the unique constraint in the gpkg_vt_layers table (table_name, name)
        # this will make sure a proper replace is called if need be
        vector_layer_query = """
                              INSERT OR REPLACE INTO "{table_name}"
                                  (id,
                                   table_name, 
                                   description, 
                                   name, 
                                   minzoom,
                                   maxzoom,
                                   stylable_layer_set)
                              VALUES ((SELECT id FROM {table_name} WHERE table_name = ? AND name = ?), ?,?,?,?,?,?);
                          """.format(table_name=GEOPACKAGE_VECTOR_LAYERS_TABLE_NAME)
        cursor.executemany(vector_layer_query, tuple([(vector_layer_entry.table_name,
                                                       vector_layer_entry.name,
                                                       vector_layer_entry.table_name,
                                                       vector_layer_entry.description,
                                                       vector_layer_entry.name,
                                                       vector_layer_entry.min_zoom,
                                                       vector_layer_entry.max_zoom,
                                                       vector_layer_entry.stylable_layer_set)
                                                      for vector_layer_entry
                                                      in vector_layers_entries]))
