from elasticsearch import VERSION
from elasticsearch import Elasticsearch
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


class ElasticSearchInstrumentationTest(TestCase):
    def setUp(self):
        self.client = Client(CONFIG)
        register._cls_registers = {
            "stackifyapm.instrumentation.packages.elasticsearch.ElasticsearchConnectionInstrumentation",
            "stackifyapm.instrumentation.packages.elasticsearch.ElasticsearchInstrumentation",
        }
        self.session = Elasticsearch(["127.0.0.1:1118"])

    def tearDown(self):
        control.uninstrument()
        self.session.indices.delete(index="*")

    def istrument_and_begin_transaction(self):
        control.instrument()
        self.client.begin_transaction("transaction_test")

    def create_doc(self, id=1):
        if VERSION[0] < 5:
            self.session.create("test", "doc", {"foo": "bar1"}, id)
        else:
            self.session.create("test", "doc", id, body={"foo": "bar1"})

    def test_ping(self):
        self.istrument_and_begin_transaction()

        self.session.ping()

        self.assert_span(method='HEAD', url='/')

    def test_info(self):
        self.istrument_and_begin_transaction()

        self.session.info()

        self.assert_span(method='GET', url='/')

    def test_create(self):
        self.istrument_and_begin_transaction()

        self.create_doc(id=1)

        self.assert_span(method='PUT', url='/test/doc/1/_create')

    def test_get(self):
        self.create_doc(id=2)
        self.istrument_and_begin_transaction()

        if VERSION[0] >= 6:
            self.session.get("test", "doc", 2)
        else:
            self.session.get("test", 2, "doc")

        self.assert_span(method='GET', url='/test/doc/2')

    def test_update(self):
        self.create_doc(id=3)
        self.istrument_and_begin_transaction()

        self.session.update("test", "doc", 3, {"doc": {"foo": "bar edit"}}, refresh=True)

        self.assert_span(method='POST', url='/test/doc/3/_update')

    def test_delete(self):
        self.create_doc(id=4)
        self.istrument_and_begin_transaction()

        self.session.delete(id=4, index="test", doc_type="doc")

        self.assert_span(method='DELETE', url='/test/doc/4')

    def test_exists(self):
        self.create_doc(id=5)
        self.istrument_and_begin_transaction()

        self.session.exists(id=5, index="test", doc_type="doc")

        self.assert_span(method='HEAD', url='/test/doc/5')

    def assert_span(self, method, url='/'):
        transaction = get_transaction()
        assert transaction
        assert transaction.get_spans()

        span = transaction.get_spans()[0]
        span_data = span.to_dict()

        assert span_data['reqBegin']
        assert span_data['reqEnd']
        assert span_data['transaction_id']
        assert span_data['call'] == 'db.elasticsearch'
        assert span_data['props']
        assert span_data['props']['CATEGORY'] == 'ElasticSearch'
        assert span_data['props']['SUBCATEGORY'] == 'Execute'
        assert span_data['props']['COMPONENT_CATEGORY'] == 'Web External'
        assert span_data['props']['COMPONENT_DETAIL'] == 'Execute'
        assert span_data['props']['METHOD'] == method
        assert span_data['props']['URL'] == url
