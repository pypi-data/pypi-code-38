from tormor.main_script import script
import click
from click.testing import CliRunner
from click.exceptions import UsageError
from tormor.connections import Connection
from tormor.commands import BOOTSTRAP_SQL
import pytest

class TestScript():
    def setup(self):
        self.runner = CliRunner()
        self.conn = Connection('postgresql://localhost/tormordb')
        self.conn.execute("DROP TABLE IF EXISTS migration")
        self.conn.execute("DROP TABLE IF EXISTS module ")
        self.conn.execute(BOOTSTRAP_SQL)

    def teardown(self):
        self.runner = None
        self.conn.execute("DROP TABLE migration")
        self.conn.execute("DROP TABLE module")
        self.conn.close()

    def test_script_to_invalid_command(self):
        result = self.runner.invoke(script, ['--xyz'])
        assert result.exit_code == click.UsageError.exit_code

    def test_script_to_migrate(self):
        self.conn.execute('''INSERT INTO module(name) VALUES ('customer')''')
        self.conn.execute('''INSERT INTO module(name) VALUES ('employee')''')
        self.conn.execute('''INSERT INTO module(name) VALUES ('product')''')
        self.runner.invoke(script, ['-h', 'localhost', '-d', 'tormordb', 'migrate'])
        result = self.conn.fetch("SELECT * FROM migration")
        actual_result = set(record.get("module_name") for record in result)
        self.conn.execute("DROP TABLE customer")
        self.conn.execute("DROP TABLE employee")
        self.conn.execute("DROP TABLE product")
        expected_result = {"customer", "employee", "product"}
        assert actual_result == expected_result

    def test_script_to_dry_migrate(self):
        self.conn.execute('''INSERT INTO module(name) VALUES ('customer')''')
        self.conn.execute('''INSERT INTO module(name) VALUES ('employee')''')
        self.conn.execute('''INSERT INTO module(name) VALUES ('product')''')
        self.conn.execute('''INSERT INTO module(name) VALUES ('department')''')
        result = self.runner.invoke(script, ['-h', 'localhost', '-d', 'tormordb', 'migrate', '--dry-run'])

    def test_script_to_include(self):
        self.runner.invoke(script, ['-h', 'localhost', '-d', 'tormordb', 'include', 'tormor/tests/script_file.txt'])
        result = self.conn.fetch("SELECT name FROM module GROUP BY name ORDER BY name")
        actual_result = [x['name'] for x in result]
        assert ["customer", "employee", "product"] == actual_result
    
    def test_script_to_include_without_file(self):
        result = self.runner.invoke(script, ['-h', 'localhost', '-d', 'tormordb', 'include'])
        assert result.exit_code == click.UsageError.exit_code

    def test_script_to_enable_modules(self):
        self.runner.invoke(script, ['-h', 'localhost', '-d', 'tormordb', 'enable-modules', 'module1', 'module2'])
        result = self.conn.fetch("SELECT name FROM module")
        actual_result = set(record.get("name") for record in result)
        assert "module1" in actual_result and "module2" in actual_result

    def test_script_to_enable_modules_without_name(self):
        result = self.runner.invoke(script, ['-h', 'localhost', '-d', 'tormordb', 'enable-modules'])
        assert result.exit_code == click.UsageError.exit_code

    def test_script_to_execute_sql(self):
        self.runner.invoke(script, ['-h', 'localhost', '-d', 'tormordb', 'sql', 'tormor/tests/Schema/customer/01_customer.sql'])
        result = self.conn.fetch("SELECT * FROM customer")
        actual_result = set(record.get("name") for record in result)
        expected_result = {"Customer1", "Customer2", "Customer3"}
        self.conn.execute("DROP TABLE customer")
        assert actual_result == expected_result

    def test_script_to_execute_sql_no_file(self):
        result = self.runner.invoke(script, ['-h', 'localhost', '-d', 'tormordb', 'sql'])
        assert result.exit_code == click.UsageError.exit_code