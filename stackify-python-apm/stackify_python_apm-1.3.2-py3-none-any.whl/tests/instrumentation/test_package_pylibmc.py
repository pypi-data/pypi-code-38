from unittest import TestCase
from unittest import SkipTest

try:
    import pylibmc
except Exception:
    raise SkipTest('Skipping due to version incompatibility')

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


class PyLibMCInstrumentationTest(TestCase):
    def setUp(self):
        self.client = Client(CONFIG)
        register._cls_registers = {
            "stackifyapm.instrumentation.packages.pylibmc.PyLibMcInstrumentation",
        }
        self.cache = pylibmc.Client(["127.0.0.1:1117"], binary=True, behaviors={"tcp_nodelay": True, "ketama": True})
        control.instrument()
        self.client.begin_transaction("transaction_test")

    def tearDown(self):
        control.uninstrument()

    def test_set_cache(self):
        self.cache.set("some_key", "Some value")
        self.assert_span(operation='set', key='some_key')

    def test_get_cache(self):
        self.cache.get("some_key")
        self.assert_span(operation='get', key='some_key')

    def test_set_multi(self):
        self.cache.set_multi({"foo": "1", "bar": "2"})
        self.assert_span(operation='set_multi', key=['foo', 'bar'])

    def test_get_multi(self):
        self.cache.get_multi(['foo', 'bar'])
        self.assert_span(operation='get_multi', key=['foo', 'bar'])

    def assert_span(self, operation, key):
        transaction = get_transaction()
        assert transaction
        assert transaction.get_spans()

        span = transaction.get_spans()[0]
        span_data = span.to_dict()

        assert span_data['reqBegin']
        assert span_data['reqEnd']
        assert span_data['transaction_id']
        assert span_data['call'] == 'cache.memcached'
        assert span_data['props']
        assert span_data['props']['CATEGORY'] == 'Cache'
        assert span_data['props']['SUBCATEGORY'] == 'Execute'
        assert span_data['props']['COMPONENT_CATEGORY'] == 'Cache'
        assert span_data['props']['COMPONENT_DETAIL'] == 'Execute'
        assert span_data['props']['OPERATION'] == operation
        assert set(span_data['props']['CACHEKEY']) == set(key)
