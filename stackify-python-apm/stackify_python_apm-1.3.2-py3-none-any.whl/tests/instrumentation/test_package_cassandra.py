from unittest import TestCase

from cassandra.cluster import Cluster
from cassandra.query import SimpleStatement

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


class CassandraInstrumentationTest(TestCase):
    def setUp(self):
        self.client = Client(CONFIG)
        register._cls_registers = {
            "stackifyapm.instrumentation.packages.cassandra.CassandraInstrumentation",
        }
        self.cluster = Cluster(["localhost"], port=1111)

    def tearDown(self):
        control.uninstrument()

    def setUpQuery(self):
        self.session = self.cluster.connect()
        self.session.execute("CREATE KEYSPACE IF NOT EXISTS testkeyspace WITH REPLICATION = { 'class' : 'SimpleStrategy' ,'replication_factor' : 1 }")
        self.session.execute("USE testkeyspace;")
        self.session.execute("CREATE TABLE IF NOT EXISTS testkeyspace.users ( id UUID PRIMARY KEY, name text);")

    def istrument_and_begin_transaction(self):
        control.instrument()
        self.client.begin_transaction("transaction_test")

    def test_connect(self):
        self.istrument_and_begin_transaction()

        self.cluster.connect()

        self.assert_span(call='db.cassandra.connect', category='Cassandra', subcategory='Connect')

    def test_select_query_string(self):
        self.setUpQuery()
        self.istrument_and_begin_transaction()

        self.session.execute("SELECT name from users")

        self.assert_span(call='db.cassandra.query', category='Cassandra', subcategory='Execute', sql='SELECT name from users')

    def test_select_simple_statement(self):
        self.setUpQuery()
        self.istrument_and_begin_transaction()

        self.session.execute(SimpleStatement("SELECT name from users"))

        self.assert_span(call='db.cassandra.query', category='Cassandra', subcategory='Execute', sql='SELECT name from users')

    def test_select_prepared_statement(self):
        self.setUpQuery()
        self.istrument_and_begin_transaction()

        self.session.execute(self.session.prepare("SELECT name from users"))

        self.assert_span(call='db.cassandra.query', category='Cassandra', subcategory='Execute', sql='SELECT name from users')

    def assert_span(self, call, category, subcategory, sql=None):
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
        assert span_data['props']['CATEGORY'] == category
        assert span_data['props']['SUBCATEGORY'] == subcategory
        if sql:
            assert span_data['props']['SQL'] == 'SELECT name from users'
