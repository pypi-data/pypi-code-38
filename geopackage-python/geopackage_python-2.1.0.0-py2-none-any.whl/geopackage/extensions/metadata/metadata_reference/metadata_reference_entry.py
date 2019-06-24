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
from rgi.geopackage.extensions.metadata.metadata_reference.reference_scope import ReferenceScope


class MetadataReferenceEntry(object):
    """
    The Metadata Reference object representation of an entry in the gpkg_metadata_reference table
    """

    def __init__(self,
                 reference_scope,
                 table_name,
                 column_name,
                 row_identifier,
                 file_identifier,
                 parent_identifier):
        """
        Constructor

        :param reference_scope: Lowercase metadata reference scope enum; one of 'geopackage', 'table', 'column', 'row',
        'row/col'
        :type reference_scope: ReferenceScope

        :param table_name: Name of the table to which this metadata reference applies, or NULL for referenceScope of
        'geopackage'
        :type table_name: str, None

        :param column_name: Name of the column to which this metadata reference applies; NULL for referenceScope of
        'geopackage','table' or 'row', or the name of a column in the tableName table for referenceScope of 'column' or
        'row/col'
        :type column_name: str, None

        :param row_identifier: NULL for referenceScope of 'geopackage', 'table' or 'column', or the rowed of a row
        record in the table_name table for referenceScope of 'row' or 'row/col'
        :type row_identifier: int, None

        :param file_identifier: gpkg_metadata table identifier column value for the metadata to which this
        gpkg_metadata_reference applies
        :type file_identifier: int

        :param parent_identifier: gpkg_metadata table identifier column value for the hierarchical parent gpkg_metadata
        for the gpkg_metadata to which this gpkg_metadata_reference applies, or NULL if file identifier forms the root
        of a metadata hierarchy
        :type parent_identifier: int, None
        """
        # check to make sure reference scope is not None
        if reference_scope is None:
            raise ValueError('reference_scope cannot be None.')

        # check to make sure the reference scope value is a valid value
        if reference_scope.value not in [reference_scope_enum.value for reference_scope_enum in ReferenceScope]:
            raise ValueError("Invalid md_scope value {scope}. Must be one of the following: {scopes}."
                             .format(scope=reference_scope,
                                     scopes=[reference_scope_enum.value for reference_scope_enum in ReferenceScope]))

        if reference_scope == ReferenceScope.GEOPACKAGE and table_name is not None:
            raise ValueError("Reference scopes of 'geopackage' must have None for the associated table name, and other "
                             "reference scope values must have non-null table names")  # requirement 72

        if not ReferenceScope.is_column_scope(reference_scope=reference_scope) and column_name is not None:
            raise ValueError("Reference scopes 'geopackage', 'table' or 'row' must have a None column name. Reference "
                             "scope values of 'column' or 'row/col' must have a non-null column name")  # Requirement 73

        if ReferenceScope.is_row_scope(reference_scope=reference_scope) and row_identifier is None:
            raise ValueError("Reference scopes of 'geopackage', 'table' or 'column' must have a None row identifier.  "
                             "Reference scopes of 'row' or 'row/col', must contain a reference to a row record in the "
                             "'{table}' table".format(table=table_name))  # Requirement 74

        if table_name is not None and len(table_name) == 0:
            raise ValueError('If the table_name is not None, it may not be empty')

        if column_name is not None and len(column_name) == 0:
            raise ValueError('If column_name is not None, it may not be empty')

        if file_identifier is None:
            raise ValueError('file_identifier may not be None')

        self.reference_scope = reference_scope
        self.table_name = table_name
        self.column_name = column_name
        self.row_identifier = row_identifier
        self.file_identifier = file_identifier
        self.parent_identifier = parent_identifier
