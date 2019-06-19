from tormor.connections import Connection
from tormor.commands import execute_sql_file, migrate, include, enable_modules
import asyncpg
from asyncpg.exceptions import InvalidCatalogNameError, UndefinedTableError
import pytest
import asyncio
from tormor.exceptions import ModuleNotPresent

SQL_TO_CREATE_INSERT_MANY_MODULES = '''
    CREATE TABLE module(
        name text NOT NULL,
        CONSTRAINT module_pk PRIMARY KEY(name));
    INSERT INTO module(name)
        VALUES('Module1'); 
    INSERT INTO module(name)
        VALUES('Module2');
    INSERT INTO module(name)
        VALUES('Module3');
'''

def test_connection_working():
    conn = Connection('postgresql://localhost/tormordb')
    conn.close()

def test_connection_not_working():
    with pytest.raises(InvalidCatalogNameError):
        conn = Connection('postgresql://localhost/tormordb_none')
        conn.close()

class TestConnection:
    def setup(self):
        self.conn = Connection('postgresql://localhost/tormordb')
        self.conn.execute("DROP TABLE IF EXISTS module")
        self.conn.execute(SQL_TO_CREATE_INSERT_MANY_MODULES)

    def teardown(self):
        self.conn.execute("DROP TABLE module")
        self.conn.close()

    def test_fetch(self):     
        result = self.conn.fetch("SELECT name FROM module")
        expected_result = {"Module1", "Module2", "Module3"}
        actual_result = set(record.get("name") for record in result)
        assert actual_result == expected_result

    def test_load_module(self):
        actual_result = self.conn.load_modules()
        expected_result = {'Module1', 'Module2', 'Module3'}
        assert actual_result == expected_result

    def test_assert_module_exist(self):
        self.conn.assert_module("Module1")
    
    def test_assert_module_not_exist(self):
        with pytest.raises(ModuleNotFoundError):
            self.conn.assert_module("none")

    def test_transaction_rollback(self):
        with pytest.raises(UndefinedTableError):
            result = self.conn.fetch("SELECT name FROM module_none")