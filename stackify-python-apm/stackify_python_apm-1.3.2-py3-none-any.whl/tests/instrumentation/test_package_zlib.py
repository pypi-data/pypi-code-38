import zlib
from unittest import TestCase

from stackifyapm.base import Client
from stackifyapm.instrumentation import register
from stackifyapm.instrumentation import control
from stackifyapm.traces import get_transaction

CONFIG = {
    "SERVICE_NAME": "service_name",
    "ENVIRONMENT": "production",
    "HOSTNAME": "sample_host",
    "FRAMEWORK_NAME": "framework",
    "FRAMEWORK_VERSION": "1.0",
    "APPLICATION_NAME": "sample_application",
    "BASE_DIR": "path/to/application/",
}


class ZLibInstrumentationTest(TestCase):

    def setUp(self):
        self.client = Client(CONFIG)
        register._cls_registers = {
            "stackifyapm.instrumentation.packages.zlib.ZLibInstrumentation",
        }

    def tearDown(self):
        control.uninstrument()

    def test_compress(self):
        control.instrument()
        self.client.begin_transaction("Test for begin transaction")

        zlib.compress(b'Compressing Data')
        self.assert_span(operation='compress')

    def test_decompress(self):
        compressed_data = zlib.compress(b'ZLib Sample Data')
        control.instrument()
        self.client.begin_transaction("transaction_test")

        zlib.decompress(compressed_data)
        self.assert_span(operation='decompress')

    def assert_span(self, operation):
        transaction = get_transaction()
        assert transaction
        assert transaction.get_spans()

        span = transaction.get_spans()[0]
        span_data = span.to_dict()

        assert span_data['reqBegin']
        assert span_data['reqEnd']
        assert span_data['transaction_id']
        assert span_data['call'] == 'compression.zlib'
        assert span_data['props']
        assert span_data['props']['CATEGORY'] == 'Compression'
        assert span_data['props']['SUBCATEGORY'] == 'Compression'
        assert span_data['props']['COMPONENT_CATEGORY'] == 'Compression'
        assert span_data['props']['COMPONENT_DETAIL'] == 'Compression'
        assert span_data['props']['OPERATION'] == operation
