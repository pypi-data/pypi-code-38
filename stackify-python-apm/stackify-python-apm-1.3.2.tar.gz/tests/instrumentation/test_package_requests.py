import requests
from requests.models import Response
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


class RequestInstrumentationTest(TestCase):
    def setUp(self):
        self.client = Client(CONFIG)
        register._cls_registers = {
            "stackifyapm.instrumentation.packages.requests.RequestsInstrumentation",
        }

    def setUpSuccess(self):
        self.http_response = Response()
        self.http_response.status_code = 200
        self.setUpContinue()

    def setUpFailed(self):
        self.http_response = Response()
        self.http_response.status_code = 400
        self.setUpContinue()

    def setUpContinue(self):
        self.request_get = mock.patch('requests.adapters.HTTPAdapter.build_response')
        self.request_mock = self.request_get.start()
        self.request_mock.return_value = self.http_response
        control.instrument()
        self.client.begin_transaction("transaction_test")

    def tearDown(self):
        control.uninstrument()
        self.request_get.stop()

    def test_successful_get_request(self):
        self.setUpSuccess()

        requests.get('http://www.python.org/')

        self.assert_span(method='GET', status=200)

    def test_unsuccessful_get_request(self):
        self.setUpFailed()

        requests.get('http://www.python.org/')

        self.assert_span(method='GET', status=400)

    def test_successful_post_request(self):
        self.setUpSuccess()

        requests.post('http://www.python.org/')

        self.assert_span(method='POST', status=200)

    def test_unsuccessful_post_request(self):
        self.setUpFailed()

        requests.post('http://www.python.org/')

        self.assert_span(method='POST', status=400)

    def assert_span(self, method, status):
        transaction = get_transaction()
        assert transaction
        assert transaction.get_spans()

        span = transaction.get_spans()[0]
        span_data = span.to_dict()

        assert span_data['reqBegin']
        assert span_data['reqEnd']
        assert span_data['transaction_id']
        assert span_data['call'] == 'ext.http.requests'
        assert span_data['props']
        assert span_data['props']['CATEGORY'] == 'Web External'
        assert span_data['props']['SUBCATEGORY'] == 'Execute'
        assert span_data['props']['COMPONENT_CATEGORY'] == 'Web External'
        assert span_data['props']['COMPONENT_DETAIL'] == 'Execute'
        assert span_data['props']['URL'] == 'http://www.python.org/'
        assert span_data['props']['STATUS'] == status
        assert span_data['props']['METHOD'] == method
