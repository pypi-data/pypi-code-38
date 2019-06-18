import sqlite3
from unittest import TestCase

from stackifyapm.base import Client
from stackifyapm.traces import get_transaction
from stackifyapm.traces import set_transaction
from stackifyapm.traces import Transaction
from stackifyapm.instrumentation import register
from stackifyapm.instrumentation import control
from stackifyapm.instrumentation.packages.sqlite import SQLiteConnectionProxy

CONFIG = {
    "SERVICE_NAME": "service_name",
    "ENVIRONMENT": "production",
    "HOSTNAME": "sample_host",
    "FRAMEWORK_NAME": "framework",
    "FRAMEWORK_VERSION": "1.0",
    "APPLICATION_NAME": "sample_application",
    "BASE_DIR": "path/to/application/",
}


class SQLiteInstrumentationTest(TestCase):
    def setUp(self):
        self.client = Client(CONFIG)
        register._cls_registers = {
            "stackifyapm.instrumentation.packages.sqlite.SQLiteInstrumentation",
        }

        self.conn = sqlite3.connect(":memory:")
        self.cursor = self.conn.cursor()
        self.cursor.execute("CREATE TABLE testdb (id integer, username text)")

    def tearDown(self):
        self.cursor.execute("DROP TABLE testdb")

    def test_connect(self):
        control.instrument()
        self.client.begin_transaction("transaction_test")

        sqlite3.connect(":memory:")

        assert_span(
            call='db.sqlite.connect',
            subcategory='Connect',
            component_category='Database',
            component_detail='Open Connection',
        )

    def test_execute(self):
        control.instrument()
        self.client.begin_transaction("transaction_test")

        self.cursor.execute('INSERT INTO testdb VALUES (1, "JayR")')

        assert_span(
            call='db.sqlite.sql',
            subcategory='Execute',
            component_category='DB Query',
            component_detail='Execute SQL Query',
            sql='INSERT INTO testdb VALUES (1, "JayR")',
        )

    def test_execute_many(self):
        control.instrument()
        self.client.begin_transaction("transaction_test")

        self.cursor.executemany("INSERT INTO testdb VALUES (?, ?)", ((2, "Elmo"), (3, "Matt")))

        assert_span(
            call='db.sqlite.sql',
            subcategory='Executemany',
            component_category='DB Query',
            component_detail='Execute SQL Query',
            sql='INSERT INTO testdb VALUES (?, ?)',
        )


class MockSqlProxyBase(object):
    def execute(self, *args, **kwargs):
        pass

    def executemany(self, *args, **kwargs):
        pass


class SQLiteConnectionProxyTest(TestCase):
    def setUp(self):
        client = Client(CONFIG)
        transaction = Transaction("request", None, meta_data=client.get_meta_data())
        set_transaction(transaction)

    def tearDown(self):
        get_transaction(clear=True)

    def test_execute(self):
        sqlite_proxy = SQLiteConnectionProxy(MockSqlProxyBase())

        sqlite_proxy.execute('SELECT * FROM test')

        assert_span(
            call='db.sqlite.sql',
            subcategory='Execute',
            component_category='DB Query',
            component_detail='Execute SQL Query',
            sql='SELECT * FROM test',
        )

    def test_execute_with_params(self):
        sqlite_proxy = SQLiteConnectionProxy(MockSqlProxyBase())

        sqlite_proxy.execute('INSERT INTO test VALUES (?, ?)', ('foo', 'bar'))

        assert_span(
            call='db.sqlite.sql',
            subcategory='Execute',
            component_category='DB Query',
            component_detail='Execute SQL Query',
            sql='INSERT INTO test VALUES (?, ?)',
        )

    def test_executemany(self):
        sqlite_proxy = SQLiteConnectionProxy(MockSqlProxyBase())

        sqlite_proxy.executemany('SELECT * FROM test')

        assert_span(
            call='db.sqlite.sql',
            subcategory='Executemany',
            component_category='DB Query',
            component_detail='Execute SQL Query',
            sql='SELECT * FROM test',
        )

    def test_executemany_with_params(self):
        sqlite_proxy = SQLiteConnectionProxy(MockSqlProxyBase())

        sqlite_proxy.executemany('INSERT INTO test VALUES (?, ?)', [('foo', 'bar'), ('bar', 'foo')])

        assert_span(
            call='db.sqlite.sql',
            subcategory='Executemany',
            component_category='DB Query',
            component_detail='Execute SQL Query',
            sql='INSERT INTO test VALUES (?, ?)',
        )


def assert_span(call, subcategory, component_category, component_detail, sql=None):
    transaction = get_transaction()
    assert transaction
    assert transaction.get_spans()

    span = transaction.get_spans()[0]
    span_data = span.to_dict()

    assert span_data['reqBegin']
    assert span_data['reqEnd']
    assert span_data['transaction_id']
    assert span_data['call'] == call
    assert span_data['props']
    assert span_data['props']['CATEGORY'] == 'Database'
    assert span_data['props']['SUBCATEGORY'] == subcategory
    assert span_data['props']['COMPONENT_CATEGORY'] == component_category
    assert span_data['props']['COMPONENT_DETAIL'] == component_detail
    if sql:
        assert span_data['props']['SQL'] == sql
