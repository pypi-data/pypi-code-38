import unittest
from arklibpy.database.ArkDBSQLite import *
import os


class ArkDBSQLiteTestCase(unittest.TestCase):
    def setUp(self):
        here = os.path.abspath(os.path.dirname(__file__))
        path = os.getcwd()
        self.db_ = ArkDBSQLite(
            db_config_file=os.path.join(here,'db_config_local_tester.txt'),
            db_filepath=path
        )
        self.table_ = "test_table"

    def tearDown(self):
        pass
        self.db_.remove_db_from_disk()

    def test_connection(self):
        self.db_.run_sql(f'DROP TABLE IF EXISTS {self.table_}')
        self.db_.run_sql(f'CREATE TABLE {self.table_} (str_col VARCHAR(20), int_col INT PRIMARY KEY)')

        self.db_.set_table(self.table_)
        temp = self.db_.get_query_value('int_col', 'SELECT int_col FROM test_table')
        self.assertIsNone(temp)

        rowid = self.db_.insert({"int_col": 1, "str_col": "test"})
        self.assertEqual(rowid, 1) # rowid starts with 1
        self.db_.insert({"int_col": 2, "str_col": "test"})
        self.db_.update(2, 'int_col', {"int_col": 5, "str_col": "test"})
        self.db_.delete(1, 'int_col')
        temp = self.db_.get_query_value('int_col', 'SELECT int_col FROM test_table')
        self.assertEqual(temp, 2)
        self.db_.update(2, 'int_col', {"str_col": "update test"})
        temp = self.db_.get_query_value('str_col', 'SELECT str_col FROM test_table')
        self.assertEqual(temp, 'update test')

    def test_create_table(self):
        table_desc = dict()
        table_desc['table_name'] = 'WORK_LIB'
        table_columns = list()
        table_columns.append({'name': 'idCELL', 'type': 'INT', 'property': 'NOT NULL'})
        table_columns.append({'name': 'CELL_PMOS_CNT', 'type': 'INT', 'property': 'NOT NULL'})
        table_columns.append({'name': 'CELL_NMOS_CNT', 'type': 'INT', 'property': 'NOT NULL'})
        table_columns.append({'name': 'CELL_NETLIST', 'type': 'VARCHAR(1000)', 'property': 'NULL'})
        table_columns.append({'name': 'CELL_BSF', 'type': 'VARCHAR(256)',
                              'property': "NULL"})
        table_columns.append({'name': 'CELL_NOTE', 'type': 'VARCHAR(1000)', 'property': 'NULL'})
        table_columns.append({'name': 'CELL_FAMILY', 'type': 'VARCHAR(1000)', 'property': 'NULL'})
        table_columns.append({'name': 'CELL_Schematic', 'type': 'VARCHAR(1000)', 'property': 'NULL'})
        table_columns.append({'name': 'CELL_BSF_UNIFIED', 'type': 'VARCHAR(256)',
                              'property': "NULL"})
        table_columns.append({'name': 'CELL_LEVEL', 'type': 'INT', 'property': 'NULL'})
        table_columns.append({'name': 'CELL_SIM_RESULT', 'type': 'INT', 'property': 'NULL'})
        table_columns.append({'name': 'CELL_BSF_weak', 'type': 'VARCHAR(256)',
                              'property': "NULL"})
        table_columns.append({'name': 'CELL_BSF_weak_UNIFIED', 'type': 'VARCHAR(256)',
                              'property': "NULL"})

        table_desc['table_columns'] = table_columns
        table_primary_keys = ['idCELL', 'CELL_PMOS_CNT']
        table_desc['table_pks'] = table_primary_keys

        self.db_.run_sql(f"DROP TABLE IF EXISTS {table_desc['table_name']}")
        self.db_.create_table(table_desc)
        self.assertTrue(self.db_.is_table_exist(table_desc['table_name']))

        # Creating the same table twice should fail
        self.assertFalse(self.db_.create_table(table_desc))

        # Force creating the same table twice should success
        self.assertTrue(self.db_.create_table(table_desc, True))

        # Clean up the test
        self.db_.run_sql(f"DROP TABLE {table_desc['table_name']}")


if __name__ == '__main__':
    unittest.main()
