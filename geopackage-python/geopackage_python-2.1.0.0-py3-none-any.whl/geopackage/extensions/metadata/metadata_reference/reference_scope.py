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
from enum import Enum


class ReferenceScope(Enum):
    """
    Every gpkg_metadata_reference table reference scope column value SHALL be one of 'geopackage', 'table', 'column',
    'row', 'row/col' in lowercase.

    see "http://www.geopackage.org/spec/#_requirement-71"
    """

    """The Reference Scope is of the entire GeoPackage"""
    GEOPACKAGE = 'geopackage'

    """The Reference Scope is of a single Table"""
    TABLE = 'table'

    """The Reference Scope is of a column"""
    COLUMN = 'column'

    """The Reference Scope is of a row"""
    ROW = 'row'

    """The Reference Scope is of a row or a column"""
    ROW_COL = 'row/col'

    @staticmethod
    def is_row_scope(reference_scope):
        """
        Returns true if the ReferenceScope is of type 'row' or 'row/col', false otherwise

        :param reference_scope: the reference scope to check
        :type reference_scope: ReferenceScope

        :return true if the ReferenceScope is of type 'row' or 'row/col', false otherwise
        :rtype: bool
        """

        return reference_scope == ReferenceScope.ROW or reference_scope == ReferenceScope.ROW_COL

    @staticmethod
    def is_column_scope(reference_scope):
        """
        Returns true if the ReferenceScope is of type 'column' or 'row/col', false otherwise

        :param reference_scope: the reference scope to check
        :type reference_scope: ReferenceScope

        :return true if the ReferenceScope is of type 'column' or 'row/col', false otherwise
        :rtype: bool
        """

        return reference_scope == ReferenceScope.COLUMN or reference_scope == ReferenceScope.ROW_COL

    @staticmethod
    def from_text(text):
        """
        ReferenceScope representation of the text supplied, if none match, an error will be thrown

        :param text: the string value of an ReferenceScope (i.e. 'geopackage')
        :type text: str

        :return: ReferenceScope representation of the text supplied
        :rtype: ReferenceScope
        """
        if text.lower() == ReferenceScope.GEOPACKAGE.value:
            return ReferenceScope.GEOPACKAGE
        if text.lower() == ReferenceScope.TABLE.value:
            return ReferenceScope.TABLE
        if text.lower() == ReferenceScope.COLUMN.value:
            return ReferenceScope.COLUMN
        if text.lower() == ReferenceScope.ROW.value:
            return ReferenceScope.ROW
        if text.lower() == ReferenceScope.ROW_COL.value:
            return ReferenceScope.ROW_COL

        raise ValueError("No ReferenceScope that matches {text}".format(text=text))
