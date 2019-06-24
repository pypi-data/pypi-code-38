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
import functools
import sqlite3
import threading
from sqlite3 import Cursor, connect, Connection


def synchronized(wrapped):
    """
    Ensures the method is executed completely before another thread calls the method.

    code taken from:
    https://stackoverflow.com/questions/29158282/how-to-create-a-synchronized-function-across-all-instances
    :param wrapped: the function to wrap (to be executed synchronously)
    :return: returns whatever the function would return
    """
    lock = threading.Lock()

    # in case you want locking information, uncomment to print
    # print (lock, id(lock))

    @functools.wraps(wrapped)
    def _wrap(*args, **kwargs):
        with lock:
            return wrapped(*args, **kwargs)

    return _wrap


def table_exists(cursor, table_name):
    """
    Checks if the table table_name exists in the database.
    returns true if the table exists in the database, false otherwise.

    :param cursor: the cursor to the database's connection
    :type cursor: Cursor
    :param table_name: the name of the table searching for
    :type table_name: str
    :return: true if the table exists, false otherwise
    :rtype: bool
    """
    cursor.execute("""
                       SELECT name 
                       FROM sqlite_master 
                       WHERE type='table' AND name=?;
                   """,
                   (table_name,))
    return bool(cursor.fetchone())


def row_id_exists(cursor, table_name, row_id):
    """

    :param cursor: the cursor to the database's connection
    :type cursor: Cursor

    :param table_name: the name of the table searching for
    :type table_name: str

    :param row_id: the integer value of the row in the table
    :type row_id: int

    :return: true if a row with the row_id given exists in the table, false otherwise
    :rtype: bool
    """
    if not table_exists(cursor=cursor,
                        table_name=table_name):
        return False

    cursor.execute("""SELECT 1 FROM "{table_name}" WHERE rowid = ?;"""
                   .format(table_name=table_name),
                   [row_id])

    return bool(cursor.fetchone())


def column_exists(cursor, table_name, column_name):
    """
    True if the column_name exists in the table table_name

    :param cursor: the cursor to the database's connection
    :type cursor: Cursor

    :param table_name: the name of the table with the column
    :type table_name: str

    :param column_name: the name of the column
    :type column_name: str

    :return: True if the column exists, false otherwise
    :rtype: bool
    """
    return columns_exists(cursor=cursor,
                          table_name=table_name,
                          column_names=[column_name])


def columns_exists(cursor,
                   table_name,
                   column_names):
    """
    True if ALL the column_name exists in the table table_name

    :param cursor: the cursor to the database's connection
    :type cursor: Cursor

    :param table_name: the name of the table with the column
    :type table_name: str

    :param column_names: the list of column names to verify exist in the table
    :type column_names: list of str

    :return: True if the column exists, false otherwise
    :rtype: bool
    """
    if table_exists(cursor=cursor,
                    table_name=table_name):
        cursor.execute("""
                        PRAGMA table_info("{table_name}")
                        """.format(table_name=table_name))
        columns_in_table = [row['name'] for row in cursor]
        return all(any(existing_column == column for existing_column in columns_in_table) for column in column_names)

    return False


def get_database_connection(file_path,
                            timeout=0.0):
    """
    Gets a Connection to an Sqlite Database

    :param timeout: the time in seconds application waits while trying to create a connection with SQL Server before
    terminating the attempt.
    :type timeout: float

    :param file_path: path to the sqlite database
    :type file_path: str

    :return: a connection to the database
    :rtype: Connection
    """
    db_connection = connect(database=file_path,
                            timeout=timeout)
    db_connection.row_factory = sqlite3.Row

    return db_connection


def select_all_query(cursor,
                     table_name):
    """
    Selects all entries in the given table

    :param cursor: the cursor to the database's connection
    :type cursor: Cursor

    :param table_name: the name of the table selecting the rows from
    :type table_name: str

    :return: rows returned from the query.
    :rtype: list of Row
    """

    # check if the table exists before querying for rows
    if not table_exists(cursor=cursor,
                        table_name=table_name):
        raise ValueError("Table must exist to select entries from it")

    cursor.execute("SELECT * FROM '{table_name}';"
                   .format(table_name=table_name))

    return cursor.fetchall()


def select_query(cursor,
                 table_name,
                 select_columns,
                 where_columns_dictionary):
    """
    Selects the columns from a given table.  Will handle None/NULL cases to build the query properly

    :param cursor: the cursor to the database's connection
    :type cursor: Cursor

    :param table_name: the name of the table selecting the rows from
    :type table_name: str

    :param select_columns: the columns names to select from the table
    :type select_columns: list of str
     (i.e.  ['table_name', 'column_name'] will select the columns 'table_name' and 'column_name' that will be in the
     row result)
    :param where_columns_dictionary: the column name as a key and the value the column you are searching for in a
    dictionary format

    (i.e.  {'column_name1': 'value_1',
            'column_name2': None }  This where clause will select all rows that meet this criteria. This will
            select the rows where column_name1 is equal to value_1 and column_name2 is NULL.

    :type where_columns_dictionary: dict [str, Union[str, bool, int, float, Binary, None]]

    :return: rows returned from the query. None will return if the query did not return any results matching the
    criteria
    :rtype: list of Row, None
    """

    # check if the table exists before querying for rows
    if not table_exists(cursor=cursor,
                        table_name=table_name):
        raise ValueError("Table must exist to select entries from it")

    # check to make sure all the column names are not None or Empty
    if any(column_name is None or len(column_name) == 0 for column_name in select_columns):
        raise ValueError("The column names cannot be None or empty")

    # create the query string
    query_string = "SELECT {columns} " \
                   "FROM '{table}' " \
                   "WHERE {where_clause};".format(columns=', '.join(["[{column_name}]".format(column_name=column)
                                                                     for column
                                                                     in select_columns]),
                                                  table=table_name,
                                                  where_clause=_build_where_clause(
                                                      where_columns_dictionary=where_columns_dictionary))

    # build the parameterized list (?)
    values = [value for __, value in where_columns_dictionary.items() if value is not None]

    cursor.execute(query_string, tuple(values))

    # return the results of the select query
    return cursor.fetchall()


def update_row(cursor,
               table_name,
               set_columns_dictionary,
               where_columns_dictionary):
    """
    Updates a row in a table.  Will properly handle the building of the SQL query for columns with null values.

    :param cursor: the cursor to the database's connection
    :type cursor: Cursor

    :param table_name: the name of the table updating the row from
    :type table_name: str

    :param set_columns_dictionary: the column name as a key and the value the column should be set to
    (i.e. {'column_name1': 'value_1',
           'column_name2': None,
           'column_name3': True}  where column_name1 should be updated to say 'value_1'
    :type set_columns_dictionary:  dict [str, object or None]

    :param where_columns_dictionary: the column name as a key and the value the column you are searching for in a
    dictionary format (to select the specific row to update)

    (i.e.  {'column_name1': 'value_1',
            'column_name2': None }  this where clause must uniquely select a row in the table to update. This will
            select the row where column_name1 is equal to value_1 and column_name2 is NULL.

    :type where_columns_dictionary: dict [str, str or None]
    """

    # check to see if the table exists
    if not table_exists(cursor=cursor,
                        table_name=table_name):
        raise ValueError("Table must exist to update entries")

    # check to make sure all the column names are not none or empty
    if any(len(column_name) == 0 or column_name is None for column_name, __ in set_columns_dictionary.items()):
        raise ValueError("The column names cannot be None or empty")

    # build the update query string (which accounts for None/NULL values
    query_string = "UPDATE '{table}' " \
                   "SET {columns} " \
                   "WHERE {where_clause};" \
        .format(columns=' = ?, '.join(["[{column_name}]".format(column_name=column)
                                       for column
                                       in set_columns_dictionary.keys()]) + ' = ? ',
                table=table_name,
                where_clause=_build_where_clause(where_columns_dictionary=where_columns_dictionary))

    # the parameterized values in the query (?)
    values = [value for value in set_columns_dictionary.values()] + \
             [value for value in where_columns_dictionary.values() if value is not None]

    # execute the query
    cursor.execute(query_string,
                   tuple(values))


def insert_row(cursor,
               table_name,
               sql_columns_list):
    """
    Inserts a new row into the table.  Will use the column values given in the sql_columns_list to determine what values
    correspond to which columns given.  This will not use the include_in_where_clause attribute in the sql_columns_list
    since there is no select statement being made.

    :param cursor: the cursor to the database's connection
    :type cursor: Cursor

    :param table_name: the name of the table updating the row from
    :type table_name: str

    :param sql_columns_list: the list of columns of interest for the sql query. This will be used to determine if the
    row needs to be inserted. Include in where clause will be ignored since there will be no searching for an existing
    row
    :type sql_columns_list:  list of SqlColumnQuery
    """

    # check to see if the table exists
    if not table_exists(cursor=cursor,
                        table_name=table_name):
        raise ValueError("Table must exist to update entries")

    insert_query = "INSERT INTO '{table_name}' " \
                   " ({column_names}) " \
                   "VALUES ({question_marks});".format(table_name=table_name,
                                                       column_names=', '.join(
                                                           ["[{column_name}]".format(column_name=column.column_name)
                                                            for column
                                                            in sql_columns_list]),
                                                       question_marks=', '.join(['?' for _ in sql_columns_list]))
    values = [column.column_value for column in sql_columns_list]

    cursor.execute(insert_query,
                   tuple(values))


def insert_or_update_row(cursor,
                         table_name,
                         sql_columns_list):
    """
    Inserts a new row into the database IF no single row is returned from the select query peformed first.  Based on
    the sql_columns_list, a select query will be performed to see if a single row from the database is returned that
    would match the search. If no rows are returned or if multiple rows are returned, an insertion will be performed.

    If a single row is returned, that row will be updated with the new values in the sql_columns_list.

    :param cursor: the cursor to the database's connection
    :type cursor: Cursor

    :param table_name: the name of the table updating the row from
    :type table_name: str

    :param sql_columns_list: the list of columns of interest for the sql query. This will be used to determine if the
    row needs to be updated (to use the columns with the where clause to check if it already exists) or if the row
    needs to be inserted with the information.  The columns for the where clause need to ensure that the row it
    queries for is unique.  Using the PK for the table is recommended! Or if a unique constraint is added to the table
    ensure that all columns that are part of that unique constraint are marked with "include_in_where_clause"
    :type sql_columns_list:  list of SqlColumnQuery
    """
    existing_row = select_query(cursor=cursor,
                                table_name=table_name,
                                select_columns=[column.column_name
                                                for column
                                                in sql_columns_list
                                                if column.include_in_select_clause],
                                where_columns_dictionary={column.column_name: column.column_value
                                                          for column
                                                          in sql_columns_list
                                                          if column.include_in_where_clause})

    if existing_row is None or len(existing_row) > 1 or len(existing_row) == 0:
        # Insert new row
        insert_row(cursor=cursor,
                   table_name=table_name,
                   sql_columns_list=sql_columns_list)
    else:
        # update row
        update_row(cursor=cursor,
                   table_name=table_name,
                   set_columns_dictionary={column.column_name: column.column_value
                                           for column
                                           in sql_columns_list
                                           if column.include_in_set_clause},
                   where_columns_dictionary={column.column_name: column.column_value
                                             for column
                                             in sql_columns_list
                                             if column.include_in_where_clause})


def delete_row(cursor,
               table_name,
               sql_columns_list):
    """
    Deletes a single row from the table given.

    :param cursor: the cursor to the database's connection
    :type cursor: Cursor

    :param table_name: the name of the table updating the row from
    :type table_name: str

    :param sql_columns_list: the list of columns of interest for the sql delete query. This will be used to determine if
    the row needs to be deleted (to use the columns with the where clause to check if it a row exists or multiple rows
    exist). The columns for the where clause need to ensure that the row it queries for is unique.  Using the PK for the
    table is recommended! Or if a unique constraint is added to the table  ensure that all columns that are part of that
     unique constraint are marked with "include_in_where_clause"
    :type sql_columns_list:  list of SqlColumnQuery
    """
    where_dictionary = {column.column_name: column.column_value
                        for column
                        in sql_columns_list
                        if column.include_in_where_clause}

    delete_query = "DELETE FROM '{table_name}' " \
                   "WHERE {where_clause};".format(table_name=table_name,
                                                  where_clause=_build_where_clause(
                                                      where_columns_dictionary=where_dictionary))
    # build the parameterized list (?)
    values = [value for __, value in where_dictionary.items() if value is not None]

    cursor.execute(delete_query, values)


def delete_rows(cursor,
                table_name,
                sql_columns_list):
    """
    Deletes all rows from the table given that matches the where condition.

    :param cursor: the cursor to the database's connection
    :type cursor: Cursor

    :param table_name: the name of the table updating the row from
    :type table_name: str

    :param sql_columns_list: the list of columns of interest for the sql delete query. This will be used to determine if
    the row needs to be deleted (to use the columns with the where clause to check if it a row exists or multiple rows
    exist). Ensure that all columns that are part of that are being searched for are marked with
    "include_in_where_clause"
    :type sql_columns_list:  list of SqlColumnQuery
    """
    where_dictionary = {column.column_name: column.column_value
                        for column
                        in sql_columns_list
                        if column.include_in_where_clause}

    delete_query = "DELETE FROM '{table_name}' " \
                   "WHERE {where_clause};".format(table_name=table_name,
                                                  where_clause=_build_where_clause(
                                                      where_columns_dictionary=where_dictionary))

    # build the parameterized list (?)
    values = [value for __, value in where_dictionary.items() if value is not None]

    cursor.execute(delete_query, values)


def _build_where_clause(where_columns_dictionary):
    """
    Builds the where portion of the SQL query to account for None values
    : :param where_columns_dictionary: the column name as a key and the value the column you are searching for in a
    dictionary format (to select the specific row to update)

    (i.e.  {'column_name1': 'value_1',
            'column_name2': None }  this where clause must uniquely select a row in the table to update. This will
            select the row where column_name1 is equal to value_1 and column_name2 is NULL.

    :type where_columns_dictionary: dict [str, str or None]
    :return: the where clause properly built to account for None values as a string
    """
    return ' AND '.join("[{column_name}] = ? ".format(column_name=key)
                        if value is not None
                        else "[{column_name}] IS NULL ".format(column_name=key)
                        for key, value
                        in where_columns_dictionary.items())
