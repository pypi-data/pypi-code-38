import stackify
from unittest import TestCase
try:
    from unittest import mock
except Exception:
    import mock

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


class HttpResponseMock(object):

    def __init__(self, code):
        self.code = code


class StackifyInstrumentationTest(TestCase):
    def setUp(self):
        self.client = Client(CONFIG)
        stackify_config = {
            "name": "test_log",
            "application": "Test App",
            "environment": "Test",
            "api_key": "some_key",
            "api_url": "https://some.api.com",
        }
        self.logger = stackify.getLogger(**stackify_config)
        register._cls_registers = {
            "stackifyapm.instrumentation.packages.stackify.StackifyInstrumentation",
        }
        control.instrument()
        self.client.begin_transaction("transaction_test")

    def tearDown(self):
        control.uninstrument()

    @mock.patch('stackify.http.HTTPClient.POST')
    def test_log_span(self, stackify_http_post_mock):
        self.logger.error('Some Error!')

        assert stackify_http_post_mock.called
        self.assert_span()

    @mock.patch('stackify.handler.StackifyListener.handle')
    @mock.patch('stackify.http.HTTPClient.POST')
    def test_log_msg_should_contain_trans_id_and_log_id(self, stackify_http_post_mock, stackify_handle_mock):
        self.logger.error('Some Error!')

        assert stackify_handle_mock.called
        assert hasattr(stackify_handle_mock.call_args_list[0][0][0], 'trans_id')
        assert hasattr(stackify_handle_mock.call_args_list[0][0][0], 'log_id')
        self.assert_span()

    def assert_span(self):
        transaction = get_transaction()
        assert transaction
        assert transaction.get_spans()

        span = transaction.get_spans()[0]
        span_data = span.to_dict()

        assert span_data['reqBegin']
        assert span_data['reqEnd']
        assert span_data['transaction_id']
        assert span_data['call'] == 'stackify.log'
        assert span_data['props']
        assert span_data['props']['CATEGORY'] == 'Stackify'
        assert span_data['props']['SUBCATEGORY'] == 'Log'
        assert span_data['props']['ID']
