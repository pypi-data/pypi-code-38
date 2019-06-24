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

from rgi.geopackage.extensions.extension_entry import ExtensionEntry
from rgi.geopackage.utility.sql_column_query import SqlColumnQuery
from rgi.geopackage.utility.sql_utility import table_exists, column_exists, select_query, insert_or_update_row, \
    select_all_query

GEOPACKAGE_EXTENSIONS_TABLE_NAME = "gpkg_extensions"


class GeoPackageExtensionsTableAdapter(object):
    """
    'Extensions' subsystem of the GeoPackage implementation
    """

    @staticmethod
    def create_extensions_table(cursor):
        """
         Creates the GeoPackage Extensions table

        :param cursor: the cursor to the GeoPackage database's connection
        :type cursor: Cursor
        """
        cursor.execute("""
                       CREATE TABLE IF NOT EXISTS {table_name}
                       (table_name     TEXT,          -- Name of the table that requires the extension. When NULL, the extension is required for the entire GeoPackage. SHALL NOT be NULL when the column_name is not NULL
                        column_name    TEXT,          -- Name of the column that requires the extension. When NULL, the extension is required for the entire table
                        extension_name TEXT NOT NULL, -- The case sensitive name of the extension that is required, in the form <author>_<extension_name>
                        definition     TEXT NOT NULL, -- Definition of the extension in the form specified by the template in GeoPackage Extension Template (Normative) or reference thereto
                        scope          TEXT NOT NULL, -- Indicates scope of extension effects on readers / writers: read-write or write-only in lowercase
                        CONSTRAINT ge_tce UNIQUE (table_name, column_name, extension_name))
                     """.format(table_name=GEOPACKAGE_EXTENSIONS_TABLE_NAME))

    @staticmethod
    def insert_or_update_extensions_row(cursor,
                                        extension):
        """
        Adds an extension to the GeoPackage extensions table. Will create the extensions table if it does not exist

        :param cursor: the cursor to the GeoPackage database's connection
        :type cursor: Cursor

        :param extension: an Extension entry in the gpkg_extensions table
        :type extension: ExtensionEntry
        """
        if not table_exists(cursor, GEOPACKAGE_EXTENSIONS_TABLE_NAME):
            GeoPackageExtensionsTableAdapter.create_extensions_table(cursor)

        if extension.table_name is not None and not table_exists(cursor=cursor, table_name=extension.table_name):
            raise ValueError("Extension's table_name is not None and it does not exist in the GeoPackage.  The "
                             "table_name must exist before adding it to the extensions table")

        if extension.column_name is not None and not column_exists(cursor=cursor,
                                                                   table_name=extension.table_name,
                                                                   column_name=extension.column_name):
            raise ValueError("Extension's column_name is not None and table {table_name} does not have a column named "
                             "{column_name}.".format(table_name=extension.table_name,
                                                     column_name=extension.column_name))
        # sqlite does not check uniqueness if any values are null, therefore we have to check ourselves
        # to avoid duplicates
        insert_or_update_row(cursor=cursor,
                             table_name=GEOPACKAGE_EXTENSIONS_TABLE_NAME,
                             sql_columns_list=[SqlColumnQuery(column_name='table_name',
                                                              column_value=extension.table_name),
                                               SqlColumnQuery(column_name='column_name',
                                                              column_value=extension.column_name),
                                               SqlColumnQuery(column_name='extension_name',
                                                              column_value=extension.extension_name),
                                               SqlColumnQuery(column_name='definition',
                                                              column_value=extension.definition,
                                                              include_in_where_clause=False),
                                               SqlColumnQuery(column_name='scope',
                                                              column_value=extension.scope,
                                                              include_in_where_clause=False)])

    @staticmethod
    def get_all_extensions(cursor):
        """
        Returns a list of Extension objects that represent the entries in GeoPackage Extensions Table

        :param cursor: the cursor to the GeoPackage database's connection
        :type cursor: Cursor

        :return a list of Extension objects that are in the GeoPackage Extensions table
        :rtype: list of ExtensionEntry
        """

        if not table_exists(cursor, GEOPACKAGE_EXTENSIONS_TABLE_NAME):
            return []

        # select all the rows
        rows = select_all_query(cursor=cursor,
                                table_name=GEOPACKAGE_EXTENSIONS_TABLE_NAME)

        return [ExtensionEntry(table_name=row["table_name"],
                               column_name=row["column_name"],
                               extension_name=row["extension_name"],
                               definition=row["definition"],
                               scope=row["scope"]) for row in rows]

    @classmethod
    def get_extensions_with_table_name(cls,
                                       cursor,
                                       table_name):

        """
        Returns a list of Extension objects that represent the entries in GeoPackage Extensions Table whose table_name
        value matches the one given

        :param table_name: the value to search for in the table_name column
        :type table_name: str

        :param cursor: the cursor to the GeoPackage database's connection
        :type cursor: Cursor

        :return a list of Extension objects that are in the GeoPackage Extensions table
        :rtype: list of ExtensionEntry
        """

        if not table_exists(cursor, GEOPACKAGE_EXTENSIONS_TABLE_NAME):
            return []

        # select all the rows
        rows = select_query(cursor=cursor,

                            table_name=GEOPACKAGE_EXTENSIONS_TABLE_NAME,
                            select_columns=['table_name',
                                            'column_name',
                                            'extension_name',
                                            'definition',
                                            'scope'],
                            where_columns_dictionary={'table_name': table_name})

        return [ExtensionEntry(table_name=row["table_name"],
                               column_name=row["column_name"],
                               extension_name=row["extension_name"],
                               definition=row["definition"],
                               scope=row["scope"]) for row in rows]

    @classmethod
    def has_extension(cls, cursor, extension):
        """
        Returns True if the GeoPackage has the extension, False otherwise

        :param cursor: the cursor to the GeoPackage database's connection
        :type cursor: Cursor

        :param extension: an Extension entry in the gpkg_extensions table to check if it exists or not
        :type extension: ExtensionEntry

        :return  Returns True if the GeoPackage has the extension, False otherwise
        :rtype: bool
        """

        if not table_exists(cursor, GEOPACKAGE_EXTENSIONS_TABLE_NAME):
            return False

        # select all the rows
        rows = select_query(cursor=cursor,
                            table_name=GEOPACKAGE_EXTENSIONS_TABLE_NAME,
                            select_columns=['table_name', 'column_name', 'extension_name', 'definition', 'scope'],
                            where_columns_dictionary={'table_name': extension.table_name,
                                                      'column_name': extension.column_name,
                                                      'extension_name': extension.extension_name})

        return rows is not None and len(rows) > 0
