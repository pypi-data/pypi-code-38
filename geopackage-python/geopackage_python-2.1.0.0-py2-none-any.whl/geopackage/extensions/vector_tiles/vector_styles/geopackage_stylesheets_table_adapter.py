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
from sqlite3 import Cursor

from rgi.geopackage.extensions.extension_entry import ExtensionEntry, EXTENSION_READ_WRITE_SCOPE
from rgi.geopackage.extensions.geopackage_extensions_table_adapter import GeoPackageExtensionsTableAdapter
from rgi.geopackage.extensions.vector_tiles.vector_layers.geopackage_vector_layers_table_adapter import GeoPackageVectorLayersTableAdapter
from rgi.geopackage.extensions.vector_tiles.vector_styles.styles_extension_constants import \
    GEOPACKAGE_STYLESHEETS_EXTENSION_NAME, STYLESHEETS_TILES_DEFINITION, GEOPACKAGE_STYLESHEETS_TABLE_NAME
from rgi.geopackage.extensions.vector_tiles.vector_styles.stylesheets_entry import StyleSheetsEntry
from rgi.geopackage.extensions.vector_tiles.vector_tiles_constants import GEOPACKAGE_VECTOR_LAYERS_TABLE_NAME
from rgi.geopackage.utility.sql_column_query import SqlColumnQuery
from rgi.geopackage.utility.sql_utility import table_exists, select_all_query, select_query, insert_or_update_row


class GeoPackageStylesheetsTableAdapter(ExtensionEntry):
    """
    Represents the GeoPackage Stylesheets table (gpkgext_stylesheets). This was built off of a pre-liminary schema.
    Schema could be subject to change. Document is located on OGC website:
     https://portal.opengeospatial.org/wiki/pub/VectorTilesPilot/ConvertDocsOutputVTP/VTP/VTPExtension.pdf
    """

    def __init__(self):
        super(GeoPackageStylesheetsTableAdapter, self).__init__(table_name=GEOPACKAGE_STYLESHEETS_TABLE_NAME,
                                                                column_name=None,
                                                                extension_name=GEOPACKAGE_STYLESHEETS_EXTENSION_NAME,
                                                                definition=STYLESHEETS_TILES_DEFINITION,
                                                                scope=EXTENSION_READ_WRITE_SCOPE)

    @staticmethod
    def create_stylesheets_table(cursor):
        """
        Creates the gpkgext_stylesheets table

        :param cursor: the cursor to the GeoPackage database's connection
        :type cursor: Cursor
        """

        cursor.execute("""
                         CREATE TABLE IF NOT EXISTS {table_name}
                         (id          INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,  -- auto generated primary key
                          styles_set  TEXT NOT NULL,                               -- a style set name that groups a set of stylesheets. FK to the stylable_layer_set column in {vector_layers_table_name}
                          style       TEXT NOT NULL,                               -- name of the style (i.e. 'day', 'night', 'default')
                          format      TEXT NOT NULL,                               -- style encoding format
                          stylesheet  BLOB NOT NULL,                               -- style encoding itself
                          title       TEXT,                                        -- optional title for the style
                          description TEXT,                                        -- optional description of the style
                          CONSTRAINT fk_styles_set  FOREIGN KEY (styles_set) REFERENCES {vector_layers_table_name} (stylable_layer_set),
                          UNIQUE(style, format, styles_set));
                       """.format(table_name=GEOPACKAGE_STYLESHEETS_TABLE_NAME,
                                  vector_layers_table_name=GEOPACKAGE_VECTOR_LAYERS_TABLE_NAME))

        # register the extension
        GeoPackageExtensionsTableAdapter.insert_or_update_extensions_row(cursor=cursor,
                                                                         extension=GeoPackageStylesheetsTableAdapter())

    @staticmethod
    def get_all_stylesheet_entries(cursor):
        """
        Returns a list of Stylesheet entries that exist in the GeoPackage's gpkgext_stylesheets table
        :param cursor: the cursor to the GeoPackage database's connection
        :type cursor: Cursor

        :return a list of Stylesheet entries that exist in the GeoPackage's gpkgext_stylesheets table
        :rtype: list of StyleSheetsEntry
        """
        if not table_exists(cursor, GEOPACKAGE_STYLESHEETS_TABLE_NAME):
            return []

        # select all the rows
        rows = select_all_query(cursor=cursor,
                                table_name=GEOPACKAGE_STYLESHEETS_TABLE_NAME)

        return [StyleSheetsEntry(styles_set=row['styles_set'],
                                 style=row['style'],
                                 style_format=row['format'],
                                 stylesheet=row['stylesheet'],
                                 title=row['title'],
                                 description=row['description'],
                                 identifier=row['id']) for row in rows]

    @staticmethod
    def get_all_stylesheet_entries_for_tile_set(cursor,
                                                vector_tiles_table_name):
        """
        Returns a list of Stylesheet entries that exist in the GeoPackage's gpkgext_stylesheets table

        :param vector_tiles_table_name: the name of the vector_tiles table to get the style sheets for.
        :type vector_tiles_table_name: str

        :param cursor: the cursor to the GeoPackage database's connection
        :type cursor: Cursor

        :return a list of Stylesheet entries that exist in the GeoPackage's gpkgext_stylesheets table
        :rtype: list of StyleSheetsEntry
        """
        if not table_exists(cursor, GEOPACKAGE_STYLESHEETS_TABLE_NAME):
            raise ValueError("The table {table} does not exist.".format(table=GEOPACKAGE_STYLESHEETS_TABLE_NAME))

        if not GeoPackageVectorLayersTableAdapter.table_exists(cursor=cursor):
            raise ValueError("The table '{table}' does not exist or does not have the correct columns."
                             .format(table=GEOPACKAGE_VECTOR_LAYERS_TABLE_NAME))

        sql_query = """
                     SELECT * 
                     FROM {styles_table}
                     WHERE styles_set
                     IN (SELECT stylable_layer_set 
                         FROM {vector_layers_name}
                         WHERE table_name = ?);
                    """.format(styles_table=GEOPACKAGE_STYLESHEETS_TABLE_NAME,
                               vector_layers_name=GEOPACKAGE_VECTOR_LAYERS_TABLE_NAME)

        cursor.execute(sql_query, (vector_tiles_table_name,))

        return [StyleSheetsEntry(styles_set=row['styles_set'],
                                 style=row['style'],
                                 style_format=row['format'],
                                 stylesheet=row['stylesheet'],
                                 title=row['title'],
                                 description=row['description'],
                                 identifier=row['id']) for row in cursor.fetchall()]

    @staticmethod
    def get_all_stylesheet_entries_by_layer_name_and_table_name(cursor,
                                                                layer_name,
                                                                vector_tiles_table_name):
        """
        Returns any Stylesheet Entries whose layer column value matches the layer_name and vector_tiles_table_name
        parameter.

        :param vector_tiles_table_name: the name of the vector tiles table to get the entry value from
        :type vector_tiles_table_name: str

        :param cursor: the cursor to the GeoPackage database's connection
        :type cursor: Cursor

        :param layer_name: the name value in the gpkgext_vt_layers that references a specific layer the stylesheet
        applies to
        :type layer_name: str

        :return a list of Stylesheet entries that exist in the GeoPackage's gpkgext_stylesheets table that match the
        layer_identifier provided
        :rtype: list of StyleSheetsEntry
        """

        if not table_exists(cursor, GEOPACKAGE_STYLESHEETS_TABLE_NAME):
            raise ValueError("The table {table} does not exist.".format(table=GEOPACKAGE_STYLESHEETS_TABLE_NAME))

        if not GeoPackageVectorLayersTableAdapter.table_exists(cursor=cursor):
            raise ValueError("The table '{table}' does not exist or does not have the correct columns."
                             .format(table=GEOPACKAGE_VECTOR_LAYERS_TABLE_NAME))

        sql_query = """
                     SELECT * 
                     FROM {styles_table}
                     WHERE styles_set
                     IN (SELECT stylable_layer_set 
                         FROM {vector_layers_name}
                         WHERE table_name = ? AND name = ?);
                    """.format(styles_table=GEOPACKAGE_STYLESHEETS_TABLE_NAME,
                               vector_layers_name=GEOPACKAGE_VECTOR_LAYERS_TABLE_NAME)

        cursor.execute(sql_query,
                       (vector_tiles_table_name, layer_name))

        return [StyleSheetsEntry(styles_set=row['styles_set'],
                                 style=row['style'],
                                 style_format=row['format'],
                                 stylesheet=row['stylesheet'],
                                 title=row['title'],
                                 description=row['description'],
                                 identifier=row['id']) for row in cursor.fetchall()]

    @staticmethod
    def get_all_style_sheets_by_styles_set(cursor,
                                           styles_set):
        """
        Retrieves the all the StyleSheetsEntry whose styles_set value is matches the one given from the Vector Tiles
        Stylesheet Table (gpkgext_stylesheets)

        :param cursor: the cursor to the GeoPackage database's connection
        :type cursor: Cursor

        :param styles_set: the styles_set name to retrieve
        :type styles_set: str

        :rtype: list of StyleSheetsEntry
        """
        if not table_exists(cursor, GEOPACKAGE_STYLESHEETS_TABLE_NAME):
            raise ValueError("The table {table} does not exist.".format(table=GEOPACKAGE_STYLESHEETS_TABLE_NAME))

        rows = select_query(cursor=cursor,
                            table_name=GEOPACKAGE_STYLESHEETS_TABLE_NAME,
                            select_columns=['id',
                                            'styles_set',
                                            'style',
                                            'format',
                                            'stylesheet',
                                            'title',
                                            'description'],
                            where_columns_dictionary={'styles_set': styles_set})

        return [StyleSheetsEntry(styles_set=row['styles_set'],
                                 style=row['style'],
                                 style_format=row['format'],
                                 stylesheet=row['stylesheet'],
                                 title=row['title'],
                                 description=row['description'],
                                 identifier=row['id']) for row in rows]

    @staticmethod
    def insert_or_update_stylesheet_entry(cursor,
                                          stylesheet_entry):
        """
        Adds an entry to the Vector Tiles Stylesheets Table (gpkgext_stylesheets) with the values given

        :param cursor: the cursor to the GeoPackage database's connection
        :type cursor: Cursor

        :param stylesheet_entry: the stylesheet entry to be added to the table
        :type stylesheet_entry: StyleSheetsEntry

        :return Updated StyleSheetsEntry with the id value updated if needed
        """
        if not table_exists(cursor, GEOPACKAGE_STYLESHEETS_TABLE_NAME):
            GeoPackageStylesheetsTableAdapter.create_stylesheets_table(cursor=cursor)

        # TODO validate layer_id if not none? check to make sure it references a value in the gpkgext_vt_layers table

        # if user did not provide an id for the row to insert/update use the unique clause (styles_set, style, and
        # format) should be unique to see if the row needs to be inserted or updated
        if stylesheet_entry.identifier is None:
            insert_or_update_row(cursor=cursor,
                                 table_name=GEOPACKAGE_STYLESHEETS_TABLE_NAME,
                                 sql_columns_list=[SqlColumnQuery(column_name='id',
                                                                  column_value=stylesheet_entry.identifier,
                                                                  include_in_where_clause=False,
                                                                  include_in_set_clause=False),
                                                   SqlColumnQuery(column_name='styles_set',
                                                                  column_value=stylesheet_entry.styles_set),
                                                   SqlColumnQuery(column_name='style',
                                                                  column_value=stylesheet_entry.style),
                                                   SqlColumnQuery(column_name='format',
                                                                  column_value=stylesheet_entry.style_format),
                                                   SqlColumnQuery(column_name='stylesheet',
                                                                  column_value=stylesheet_entry.stylesheet,
                                                                  include_in_where_clause=False),
                                                   SqlColumnQuery(column_name='title',
                                                                  column_value=stylesheet_entry.title,
                                                                  include_in_where_clause=False),
                                                   SqlColumnQuery(column_name='description',
                                                                  column_value=stylesheet_entry.description,
                                                                  include_in_where_clause=False)])
        # if the user did provide an id for the row, use that to determine whether to update or insert the row (if
        # it exists in the table or not)
        else:
            insert_or_update_row(cursor=cursor,
                                 table_name=GEOPACKAGE_STYLESHEETS_TABLE_NAME,
                                 sql_columns_list=[SqlColumnQuery(column_name='id',
                                                                  column_value=stylesheet_entry.identifier),
                                                   SqlColumnQuery(column_name='styles_set',
                                                                  column_value=stylesheet_entry.styles_set,
                                                                  include_in_where_clause=False),
                                                   SqlColumnQuery(column_name='style',
                                                                  column_value=stylesheet_entry.style,
                                                                  include_in_where_clause=False),
                                                   SqlColumnQuery(column_name='format',
                                                                  column_value=stylesheet_entry.style_format,
                                                                  include_in_where_clause=False),
                                                   SqlColumnQuery(column_name='stylesheet',
                                                                  column_value=stylesheet_entry.stylesheet,
                                                                  include_in_where_clause=False),
                                                   SqlColumnQuery(column_name='title',
                                                                  column_value=stylesheet_entry.title,
                                                                  include_in_where_clause=False),
                                                   SqlColumnQuery(column_name='description',
                                                                  column_value=stylesheet_entry.description,
                                                                  include_in_where_clause=False)])

        # TODO update the layer entry with the stylesheet number???

        stylesheet_entry.identifier = select_query(cursor=cursor,
                                                   select_columns=['id'],
                                                   table_name=GEOPACKAGE_STYLESHEETS_TABLE_NAME,
                                                   where_columns_dictionary={'styles_set': stylesheet_entry.styles_set,
                                                                     'style': stylesheet_entry.style,
                                                                     'format': stylesheet_entry.style_format,
                                                                     'stylesheet': stylesheet_entry.stylesheet,
                                                                     'description': stylesheet_entry.description,
                                                                     'title': stylesheet_entry.title})[0]['id']

        return stylesheet_entry
