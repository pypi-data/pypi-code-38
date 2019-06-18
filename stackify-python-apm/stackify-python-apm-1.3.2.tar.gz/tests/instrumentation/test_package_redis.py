import redis
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


class RedisInstrumentationTest(TestCase):
    def setUp(self):
        self.client = Client(CONFIG)
        register._cls_registers = {
            "stackifyapm.instrumentation.packages.redis.RedisInstrumentation",
            "stackifyapm.instrumentation.packages.redis.RedisPipelineInstrumentation",
        }
        self.cache = redis.Redis(host="127.0.0.1", port=1116)
        control.instrument()
        self.client.begin_transaction("transaction_test")

    def tearDown(self):
        control.uninstrument()

    def test_set_cache(self):
        self.cache.set("some_key", "Some value")
        self.assert_span(operation='set')

    def test_get_cache(self):
        self.cache.get("some_key")
        self.assert_span(operation='get')

    def test_pipeline_set(self):
        pipeline = self.cache.pipeline()
        pipeline.set("some_key", "Some value")
        pipeline.execute()
        self.assert_span(operation='SET')

    def test_pipeline_get(self):
        pipeline = self.cache.pipeline()
        pipeline.get("some_key")
        pipeline.execute()
        self.assert_span(operation='GET')

    def assert_span(self, operation):
        transaction = get_transaction()
        assert transaction
        assert transaction.get_spans()

        span = transaction.get_spans()[0]
        span_data = span.to_dict()

        assert span_data['reqBegin']
        assert span_data['reqEnd']
        assert span_data['transaction_id']
        assert span_data['call'] == 'cache.redis'
        assert span_data['props']
        assert span_data['props']['CATEGORY'] == 'Cache'
        assert span_data['props']['SUBCATEGORY'] == 'Execute'
        assert span_data['props']['COMPONENT_CATEGORY'] == 'Cache'
        assert span_data['props']['COMPONENT_DETAIL'] == 'Execute'
        assert span_data['props']['OPERATION'] == operation
        assert span_data['props']['CACHEKEY'] == 'some_key'
