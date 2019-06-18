import pymssql
from unittest import TestCase

from stackifyapm.base import Client
from stackifyapm.traces import get_transaction
from stackifyapm.instrumentation import register
from stackifyapm.instrumentation import control


CONFIG = {
    "SERVICE_NAME": "service_name",
    "ENVIRONMENT": "production",
    "HOSTNAME": "sample_host",
    "FRAMEWORK_NAME": "framework",
    "FRAMEWORK_VERSION": "1.0",
    "APPLICATION_NAME": "sample_application",
    "BASE_DIR": "path/to/application/",
}


class MSSQLInstrumentationTest(TestCase):
    def setUp(self):
        self.client = Client(CONFIG)
        register._cls_registers = {
            "stackifyapm.instrumentation.packages.pymssql.PyMSSQLInstrumentation",
        }

        self.params = {
            'database': 'test',
            'password': 'Qwert12345!',
            'user': 'SA',
            'host': '127.0.0.1',
            'port': 1115
        }

        self.conn = pymssql.connect(**self.params)
        self.cursor = self.conn.cursor()

        self.cursor.execute("CREATE TABLE testdb(id INT, name VARCHAR(30));")
        self.conn.commit()

    def tearDown(self):
        control.uninstrument()
        self.cursor.execute("DROP TABLE testdb;")
        self.conn.commit()

    def test_execute(self):
        control.instrument()
        self.client.begin_transaction("transaction_test")

        self.conn = pymssql.connect(**self.params)
        self.cursor = self.conn.cursor()
        self.cursor.execute("SELECT * FROM testdb WHERE name LIKE 'JayR'")
        self.conn.commit()

        transaction = get_transaction()
        assert transaction
        assert transaction.get_spans()

        span = transaction.get_spans()[0]
        span_data = span.to_dict()

        assert span_data['reqBegin']
        assert span_data['reqEnd']
        assert span_data['transaction_id']
        assert span_data['call'] == 'db.pymssql.sql'
        assert span_data['props']
        assert span_data['props']['CATEGORY'] == 'Database'
        assert span_data['props']['SUBCATEGORY'] == 'Execute'
        assert span_data['props']['COMPONENT_CATEGORY'] == 'DB Query'
        assert span_data['props']['COMPONENT_DETAIL'] == 'Execute SQL Query'
        assert span_data['props']['PROVIDER'] == 'pymssql'
        assert span_data['props']['SQL'] == 'SELECT * FROM testdb WHERE name LIKE \'JayR\''
