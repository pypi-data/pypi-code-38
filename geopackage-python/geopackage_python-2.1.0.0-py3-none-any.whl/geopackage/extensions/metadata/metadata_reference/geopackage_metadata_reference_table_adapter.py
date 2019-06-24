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
from rgi.geopackage.extensions.extension_entry import ExtensionEntry, EXTENSION_READ_WRITE_SCOPE
from rgi.geopackage.extensions.geopackage_extensions_table_adapter import GeoPackageExtensionsTableAdapter
from rgi.geopackage.extensions.metadata.metadata_reference.metadata_reference_entry import MetadataReferenceEntry
from rgi.geopackage.extensions.metadata.metadata_reference.reference_scope import ReferenceScope
from rgi.geopackage.utility.sql_utility import table_exists, column_exists, row_id_exists, select_all_query

GEOPACKAGE_METADATA_REFERENCE_TABLE_NAME = "gpkg_metadata_reference"
GEOPACKAGE_METADATA_EXTENSION_NAME = 'gpkg_metadata'
GEOPACKAGE_METADATA_EXTENSION_DEFINITION = 'http://www.geopackage.org/spec121/#extension_metadata'


class GeoPackageMetadataReferenceTableAdapter(ExtensionEntry):
    """
    GeoPackage Metadata Reference Subsystem extension representation
    """

    def __init__(self):
        super(GeoPackageMetadataReferenceTableAdapter, self).__init__(table_name=GEOPACKAGE_METADATA_REFERENCE_TABLE_NAME,
                                                                      column_name=None,
                                                                      scope=EXTENSION_READ_WRITE_SCOPE,
                                                                      definition=GEOPACKAGE_METADATA_EXTENSION_DEFINITION,
                                                                      extension_name=GEOPACKAGE_METADATA_EXTENSION_NAME)

    @staticmethod
    def create_metadata_reference_table(cursor):
        """
        Creates the gpkg_metadata table and registers the table as an extension to the GeoPackage
        see http://www.geopackage.org/spec121/#metadata_table_table_definition

        :param cursor: the cursor to the GeoPackage database's connection
        :type cursor: Cursor
        """
        # create the metadata table
        cursor.execute("""
                         CREATE TABLE IF NOT EXISTS {table_name}
                                      (reference_scope TEXT     NOT NULL,                                                -- Lowercase metadata reference scope; one of 'geopackage', 'table','column', 'row', 'row/col'
                                       table_name      TEXT,                                                             -- Name of the table to which this metadata reference applies, or NULL for reference_scope of 'geopackage'
                                       column_name     TEXT,                                                             -- Name of the column to which this metadata reference applies; NULL for reference_scope of 'geopackage','table' or 'row', or the name of a column in the table_name table for reference_scope of 'column' or 'row/col'
                                       row_id_value    INTEGER,                                                          -- NULL for reference_scope of 'geopackage', 'table' or 'column', or the rowed of a row record in the table_name table for reference_scope of 'row' or 'row/col'
                                       timestamp       DATETIME NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')), -- timestamp value in ISO 8601 format as defined by the strftime function '%Y-%m-%dT%H:%M:%fZ' format string applied to the current time
                                       md_file_id      INTEGER  NOT NULL,                                                -- gpkg_metadata table id column value for the metadata to which this gpkg_metadata_reference applies
                                       md_parent_id    INTEGER,                                                          -- gpkg_metadata table id column value for the hierarchical parent gpkg_metadata for the gpkg_metadata to which this gpkg_metadata_reference applies, or NULL if md_file_id forms the root of a metadata hierarchy
                          CONSTRAINT crmr_mfi_fk FOREIGN KEY (md_file_id) REFERENCES gpkg_metadata(id),
                          CONSTRAINT crmr_mpi_fk FOREIGN KEY (md_parent_id) REFERENCES gpkg_metadata(id));
                       """.format(table_name=GEOPACKAGE_METADATA_REFERENCE_TABLE_NAME))

        # register extension in the extensions table
        if GEOPACKAGE_METADATA_REFERENCE_TABLE_NAME not in \
                [extension.table_name for extension in GeoPackageExtensionsTableAdapter.get_all_extensions(cursor=cursor)]:
            GeoPackageExtensionsTableAdapter.insert_or_update_extensions_row(cursor=cursor, extension=GeoPackageMetadataReferenceTableAdapter())

    @staticmethod
    def insert_or_update_metadata_reference_row(cursor,
                                                metadata_reference):
        """
        Inserts or updates the metadata reference entry into gpkg_metadata_reference table.

        :param cursor: the cursor to the GeoPackage database's connection
        :type cursor: Cursor

        :param metadata_reference:  The MetadataReference entry to insert into the gpkg_metadata_reference table
        :type metadata_reference: MetadataReferenceEntry
        """

        if metadata_reference.table_name is not None and not table_exists(cursor=cursor,
                                                                          table_name=metadata_reference.table_name):
            raise ValueError("The metadata reference table_name value references a non-existent table: {table}.  The "
                             "table must exist in the GeoPackage".format(table=metadata_reference.table_name))

        if metadata_reference.column_name is not None and not column_exists(cursor=cursor,
                                                                            table_name=metadata_reference.table_name,
                                                                            column_name=metadata_reference.column_name):
            raise ValueError("The metadata reference column_name value references a column named {column} which does "
                             "not exist in table {table}".format(column=metadata_reference.column_name,
                                                                 table=metadata_reference.table_name))

        if metadata_reference.row_identifier is not None and not row_id_exists(cursor=cursor,
                                                                               table_name=metadata_reference.table_name,
                                                                               row_id=metadata_reference.row_identifier):
            raise ValueError("The metadata reference row_id value {row_id} row does not exist in table {table}"
                             .format(row_id=metadata_reference.row_identifier,
                                     table=metadata_reference.table_name))

        if not table_exists(cursor=cursor, table_name=GEOPACKAGE_METADATA_REFERENCE_TABLE_NAME):
            GeoPackageMetadataReferenceTableAdapter.create_metadata_reference_table(cursor=cursor)

        cursor.execute("""
                         INSERT INTO gpkg_metadata_reference (reference_scope,
                                                              table_name,
                                                              column_name,
                                                              row_id_value,
                                                              timestamp,
                                                              md_file_id,
                                                              md_parent_id)
                         VALUES (?, ?, ?, ?, strftime('%Y-%m-%dT%H:%M:%fZ','now'), ?, ?);
                       """.format(table_name=GeoPackageMetadataReferenceTableAdapter), (metadata_reference.reference_scope.value,
                                                                                        metadata_reference.table_name,
                                                                                        metadata_reference.column_name,
                                                                                        metadata_reference.row_identifier,
                                                                                        metadata_reference.file_identifier,
                                                                                        metadata_reference.parent_identifier))


    @staticmethod
    def get_all_metadata_references(cursor):
        """
        Returns all the rows in the gpkg_metadata_reference table

        :param cursor: the cursor to the GeoPackage database's connection
        :type cursor: Cursor

        :return  all the rows in the gpkg_metadata_reference table
        :rtype: list of MetadataReferenceEntry
        """
        if not table_exists(cursor=cursor, table_name=GEOPACKAGE_METADATA_REFERENCE_TABLE_NAME):
            return []

        # select all the rows
        rows = select_all_query(cursor=cursor,
                                table_name=GEOPACKAGE_METADATA_REFERENCE_TABLE_NAME)
        # get the results
        return [MetadataReferenceEntry(reference_scope=ReferenceScope.from_text(row['reference_scope']),
                                       table_name=row['table_name'],
                                       column_name=row['column_name'],
                                       row_identifier=row['row_id_value'],
                                       file_identifier=row['md_file_id'],
                                       parent_identifier=row['md_parent_id']) for row in rows]
