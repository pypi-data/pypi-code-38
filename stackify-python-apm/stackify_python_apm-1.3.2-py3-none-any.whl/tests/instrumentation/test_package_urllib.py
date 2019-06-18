import urllib
from unittest import TestCase
try:
    from unittest import mock
except Exception:
    import mock

from stackifyapm.base import Client
from stackifyapm.traces import get_transaction
from stackifyapm.instrumentation import register
from stackifyapm.instrumentation import control
from stackifyapm.utils.compat import PY3

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


class UrllibInstrumentationTest(TestCase):
    def setUp(self):
        self.client = Client(CONFIG)
        register._cls_registers = {
            "stackifyapm.instrumentation.packages.urllib.UrllibInstrumentation",
        }

    def setUpSuccess(self):
        self.http_response = HttpResponseMock(200)
        self.setUpContinue()

    def setUpFailed(self):
        self.http_response = HttpResponseMock(404)
        self.setUpContinue()

    def setUpContinue(self):
        if PY3:
            self.openurl = mock.patch('urllib.request.urlopen')
        else:
            self.openurl = mock.patch('urllib.urlopen')

        self.openurl_mock = self.openurl.start()
        self.openurl_mock.return_value = self.http_response

    def tearDown(self):
        control.uninstrument()
        self.openurl.stop()

    def test_successful_request(self):
        self.setUpSuccess()
        control.instrument()
        self.client.begin_transaction("transaction_test")

        if PY3:
            urllib.request.urlopen('http://www.python.org/')
        else:
            urllib.urlopen('http://www.python.org/')

        self.assert_span(status=200)

    def test_unsuccessful_request(self):
        self.setUpFailed()
        control.instrument()
        self.client.begin_transaction("transaction_test")

        if PY3:
            urllib.request.urlopen('http://www.python.org/')
        else:
            urllib.urlopen('http://www.python.org/')

        self.assert_span(status=404)

    def assert_span(self, status):
        transaction = get_transaction()
        assert transaction
        assert transaction.get_spans()

        span = transaction.get_spans()[0]
        span_data = span.to_dict()

        assert span_data['reqBegin']
        assert span_data['reqEnd']
        assert span_data['transaction_id']
        assert span_data['call'] == 'ext.http.urllib'
        assert span_data['props']
        assert span_data['props']['CATEGORY'] == 'Web External'
        assert span_data['props']['SUBCATEGORY'] == 'Execute'
        assert span_data['props']['COMPONENT_CATEGORY'] == 'Web External'
        assert span_data['props']['COMPONENT_DETAIL'] == 'Execute'
        assert span_data['props']['URL'] == 'http://www.python.org/'
        assert span_data['props']['STATUS'] == status
