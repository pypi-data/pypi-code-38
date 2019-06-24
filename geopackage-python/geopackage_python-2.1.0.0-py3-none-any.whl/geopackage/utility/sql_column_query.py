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

Authors:
    Jenifer Cochran, Reinventing Geospatial Inc (RGi)
Date: 2018-11-11
   Requires: sqlite3, argparse
   Optional: Python Imaging Library (PIL or Pillow)
Credits:
  MapProxy imaging functions: http://mapproxy.org
  gdal2mb on github: https://github.com/developmentseed/gdal2mb

Version:
"""


class SqlColumnQuery(object):
    """
    A helper object to perform SQL queries in a more generic way.  This is extensively used in sql_utility to perform
    row updates, insertions, or selections generically. This class was created to better handle None values in those
    queries.  This gives the SQL query enough information to perform the operation.

    """
    def __init__(self,
                 column_name,
                 column_value,
                 include_in_where_clause=True,
                 include_in_select_clause=True,
                 include_in_set_clause=True):
        """
        Constructor
        :param column_name: the name of the column
        :type column_name: str

        :param column_value: the value the column should be
        :type column_value: object, None, str, int, float, Binary

        :param include_in_where_clause: whether this should be in the SQL WHERE clause statement or not
        :type include_in_where_clause: bool

        :param include_in_select_clause: whether this column should be included in the SQL SELECT portion of the
        statement to be returned
        :type include_in_select_clause: bool

        :param include_in_set_clause: whether this column should be included in the SQL SET portion if an update row
        occurs
        """
        self.column_name = column_name
        self.column_value = column_value
        self.include_in_where_clause = include_in_where_clause
        self.include_in_select_clause = include_in_select_clause
        self.include_in_set_clause = include_in_set_clause
