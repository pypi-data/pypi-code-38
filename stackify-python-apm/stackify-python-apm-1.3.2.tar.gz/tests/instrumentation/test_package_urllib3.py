import urllib3
from urllib3.response import HTTPResponse
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


class FP(object):
    close = True

    def isclosed(self):
        return self.close

    def read(self):
        self.close = False
        return ''

    def close(self):
        self.close = True


class Message(object):
    headers = []

    def items(self):
        pass


class UrlLib3InstrumentationTest(TestCase):
    def setUp(self):
        self.client = Client(CONFIG)
        register._cls_registers = {
            "stackifyapm.instrumentation.packages.urllib3.Urllib3Instrumentation",
        }

    def setUpSuccess(self):
        self.http_response = HTTPResponse(status=200, msg=Message())
        self.setUpContinue()

    def setUpFailed(self):
        self.http_response = HTTPResponse(status=400, msg=Message())
        self.setUpContinue()

    def setUpContinue(self):
        self.http_response._fp = FP()
        self.request_get = mock.patch('urllib3.connectionpool.HTTPConnectionPool._make_request')
        self.request_mock = self.request_get.start()
        self.request_mock.return_value = self.http_response
        control.instrument()
        self.client.begin_transaction("transaction_test")

    def tearDown(self):
        control.uninstrument()
        self.request_get.stop()

    def test_successful_get_request(self):
        self.setUpSuccess()

        http = urllib3.PoolManager()
        http.request('GET', 'http://www.python.org/')

        self.assert_span(method='GET', status=200)

    def test_unsuccessful_get_request(self):
        self.setUpFailed()

        http = urllib3.PoolManager()
        http.request('GET', 'http://www.python.org/')

        self.assert_span(method='GET', status=400)

    def test_successful_post_request(self):
        self.setUpSuccess()

        http = urllib3.PoolManager()
        http.request('POST', 'http://www.python.org/')

        self.assert_span(method='POST', status=200)

    def test_unsuccessful_post_request(self):
        self.setUpFailed()

        http = urllib3.PoolManager()
        http.request('POST', 'http://www.python.org/')

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
        assert span_data['call'] == 'ext.http.urllib3'
        assert span_data['props']
        assert span_data['props']['CATEGORY'] == 'Web External'
        assert span_data['props']['SUBCATEGORY'] == 'Execute'
        assert span_data['props']['COMPONENT_CATEGORY'] == 'Web External'
        assert span_data['props']['COMPONENT_DETAIL'] == 'Execute'
        assert span_data['props']['URL'] == 'http://www.python.org/'
        assert span_data['props']['STATUS'] == status
        assert span_data['props']['METHOD'] == method
