import unittest
import logging
from io import StringIO
from os import path
import sqlite3
from dativa.tools import SqlClient
import os
import re


logger = logging.getLogger("dativa.tools.sql.tests")


class SqlTest(unittest.TestCase):

    def setUp(self):

        self.base_path = "{0}/test_data/sqlclient/".format(
            path.dirname(path.abspath(__file__)))

        # set up the SQL Lite database
        self.connection = sqlite3.connect(":memory:")

        # enable log capture
        self.log_stream = StringIO()
        sql_logger = logging.getLogger("dativa.tools.sql_client")
        sql_logger.setLevel(logging.DEBUG)
        handler = logging.StreamHandler(self.log_stream)
        handler.setFormatter(logging.Formatter('%(message)s'))
        sql_logger.addHandler(handler)

    def test_execute_df(self):
        sql = SqlClient(self.connection)
        sql.execute_query("{0}create_table.sql".format(self.base_path))

        df = sql.execute_query_to_df("SELECT * FROM test")

        self.assertEqual(df.iloc[0, 0], 'bee bee')
        self.assertEqual(df.iloc[0, 1], 374)
        self.assertEqual(df.shape, (1, 2))
        self.assertEqual(self.log_stream.getvalue()[-16:], "1 rows affected\n")

    def test_execute_df_replace(self):
        sql = SqlClient(self.connection)
        sql.execute_query("{0}create_table.sql".format(self.base_path),
                          replace={"bee bee": "boo boo"})

        df = sql.execute_query_to_df("SELECT * FROM test;")

        self.assertEqual(df.iloc[0, 0], 'boo boo')
        self.assertEqual(df.iloc[0, 1], 374)
        self.assertEqual(df.shape, (1, 2))

        df = sql.execute_query_to_df(
            "UPDATE test set name='' WHERE name = 'boo boo';SELECT * FROM test WHERE name ='';")

        self.assertEqual(df.iloc[0, 0], '')
        self.assertEqual(df.iloc[0, 1], 374)
        self.assertEqual(df.shape, (1, 2))
        self.assertEqual(self.log_stream.getvalue()[-16:], "1 rows affected\n")

        df = sql.execute_query_to_df("UPDATE test set name='baa' WHERE name = '';SELECT * FROM test WHERE name ='';")

        self.assertEqual(df.shape, (0, 0))
        self.assertEqual(self.log_stream.getvalue()[-20:], "No results returned\n")

    def test_execute_csv(self):
        sql = SqlClient(self.connection)
        sql.execute_query("{0}create_table.sql".format(self.base_path))

        sql.execute_query_to_csv("SELECT * FROM test", "{0}sql_test_output.csv".format(self.base_path))

        with open("{0}sql_test_output.csv".format(self.base_path)) as file_out:
            with open("{0}sql_test_input.csv".format(self.base_path)) as file_in:
                self.assertEqual(file_out.read(), file_in.read())

        sql.execute_query_to_csv("SELECT * FROM test", "{0}sql_test_output.csv".format(self.base_path), append=True)

        with open("{0}sql_test_output.csv".format(self.base_path)) as file_out:
            with open("{0}sql_test_input_append.csv".format(self.base_path)) as file_in:
                self.assertEqual(file_out.read(), file_in.read())

        sql.execute_query_to_csv("SELECT * FROM test", "{0}sql_test_output.csv".format(self.base_path))

        with open("{0}sql_test_output.csv".format(self.base_path)) as file_out:
            with open("{0}sql_test_input.csv".format(self.base_path)) as file_in:
                self.assertEqual(file_out.read(), file_in.read())

    def test_exception(self):
        sql = SqlClient(self.connection)
        try:
            sql.execute_query("{0}file_not_found.sql".format(self.base_path))
        except OSError:
            self.assertTrue(True)
            return

        self.assertTrue(False)

    def test_log_params(self):

        sql = SqlClient(self.connection)

        sql_log_file = os.path.join(self.base_path, "sql_log.log")

        sql.execute_query(os.path.join(self.base_path, "query_file.sql"),
                          parameters={'f_names': ('John', 'Terry', 'Eric', 'Terry', 'Michael', 'Graham'),
                                      'last_name': 'Chapman'},
                          dry_run=True,
                          archive_query=sql_log_file)

        reference = """SELECT top 10 * from pythons

where first_name in ('John', 'Terry', 'Eric', 'Terry', 'Michael', 'Graham')

or last_name = 'Chapman';
"""
        with open(sql_log_file) as f:
            self.assertTrue(re.match(r'-- Ran query on: \d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}', f.readline()))
            self.assertEqual("-- Parameters: {'f_names': ('John', 'Terry', 'Eric', 'Terry', 'Michael', 'Graham'), 'last_name': 'Chapman'}\n",
                             f.readline())
            self.assertEqual(reference, f.read())