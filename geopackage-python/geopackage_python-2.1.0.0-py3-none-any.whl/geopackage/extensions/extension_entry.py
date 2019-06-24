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
EXTENSION_WRITE_ONLY_SCOPE = 'write-only'
EXTENSION_READ_WRITE_SCOPE = 'read-write'


class ExtensionEntry(object):
    """
    Extension: an object representation of an entry in the GeoPackage Extensions table
    """

    def __init__(self,
                 table_name,
                 column_name,
                 extension_name,
                 definition,
                 scope):
        """
        Constructor

        :rtype:
        :param table_name:Name of the table that requires the extension. When NULL,
               the extension is required for the entire GeoPackage. SHALL
               NOT be NULL when the column_name is not NULL
        :type table_name: str, None

        :param column_name:Name of the column that requires the extension. When NULL,
               the extension is required for the entire table
        :type column_name: str, None

        :param extension_name: The case sensitive name of the extension that is required,
                               in the form <author>_<extension_name> where <author>
                               indicates the person or organization that developed and
                               maintains the extension. The valid character set for
                               <author> is [a-zA-Z0-9]. The valid character set for
                               <extension_name> is [a-zA-Z0-9_]
        :type extension_name: str

        :param definition: Definition of the extension in the form specified by the
                           template in <a href=
                           "http://www.geopackage.org/spec/#extension_template">
                           GeoPackage Extension Template (Normative)</a> or reference
                           thereto.
        :type definition: str

        :param scope:  Indicates scope of extension effects on readers / writers:
                      "read-write" or "write-only" in lowercase.
        :type scope: str
        """
        super(ExtensionEntry, self).__init__()

        if column_name is not None and table_name is None:
            raise ValueError("Table name may not be None if column name is not None")  # Requirement 80

        if table_name is not None and len(table_name) == 0:
            raise ValueError("If table name is not None, it may not be empty")

        if column_name is not None and len(column_name) == 0:
            raise ValueError("If column name is not None, it may not be empty")

        if extension_name is None or len(extension_name) == 0:
            raise ValueError("Extension name may not be None or empty")

        if definition is None:
            raise ValueError("Definition may not be None")

        if scope is None:
            raise ValueError("Scope may not be None")

        if scope.lower() != EXTENSION_READ_WRITE_SCOPE and scope.lower() != EXTENSION_WRITE_ONLY_SCOPE:
            raise ValueError("Scope may only be {read_write} or {write_only}. Actual Value: {actual}"
                             .format(read_write=EXTENSION_READ_WRITE_SCOPE,
                                     write_only=EXTENSION_WRITE_ONLY_SCOPE,
                                     actual=scope))

        self.table_name = table_name
        self.column_name = column_name
        self.extension_name = extension_name
        self.definition = definition
        self.scope = scope.lower()
