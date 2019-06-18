import django
from django.conf import settings
from django.http import QueryDict
from unittest import TestCase
try:
    from unittest import mock
except Exception:
    import mock

from stackifyapm.contrib.flask.utils import get_data_from_exception
from stackifyapm.contrib.flask.utils import get_data_from_request
from stackifyapm.contrib.flask.utils import get_data_from_response
from tests.contrib.django.fixtures.testapp.settings import TEST_SETTINGS


class SomeFile(object):
    filename = 'f1'


class RequestMock(object):
    method = 'POST'
    environ = {
        "REMOTE_ADDR": "remote_address",
        "SERVER_NAME": "server_name",
        "SERVER_PORT": "server_port",
    }
    is_secure = False
    cookies = 'some_cookies'
    url = 'http://www.some_url.com'
    content_type = None

    def __init__(self, content_type=None, get_data=None):
        self.content_type = content_type
        self.get_data = get_data
        self.form = QueryDict('foo=bar')


class GetDataFromRequestTest(TestCase):
    def setUp(self):
        # mock setup logging so it will not log any traces
        self.setup_logging = mock.patch('stackifyapm.conf.setup_logging')
        self.setup_logging.start()

        if not settings.configured:
            settings.configure(**TEST_SETTINGS)
            django.setup()

    def tearDown(self):
        self.setup_logging.stop()

    def test_with_post_json_request_and_captured_body_false(self):
        request = RequestMock(content_type='json/application')
        request.get_data = lambda as_text=False: 'some_request_data'

        request_data = get_data_from_request(request, capture_body=False)

        self.assert_request_data(request_data, body='[REDACTED]')

    def test_with_post_json_request_and_captured_body_true(self):
        request = RequestMock(content_type='json/application')
        request.get_data = lambda as_text=False: 'some_request_data'

        request_data = get_data_from_request(request, capture_body=True)

        self.assert_request_data(request_data, body='some_request_data')

    def test_with_post_urlencoded_data_and_captured_body_false(self):
        request = RequestMock(content_type='application/x-www-form-urlencoded')

        request_data = get_data_from_request(request, capture_body=False)

        self.assert_request_data(request_data, body='[REDACTED]')

    def test_with_post_urlencoded_data_and_captured_body_true(self):
        request = RequestMock(content_type='application/x-www-form-urlencoded')

        request_data = get_data_from_request(request, capture_body=True)

        self.assert_request_data(request_data, body={'foo': 'bar'})

    def test_with_post_multi_part_form_data_and_captured_body_false(self):
        request = RequestMock(content_type='multipart/form-data')

        request_data = get_data_from_request(request, capture_body=False)

        self.assert_request_data(request_data, body='[REDACTED]')

    def test_with_post_multi_part_form_data_and_captured_body_true(self):
        request = RequestMock(content_type='multipart/form-data')

        request_data = get_data_from_request(request, capture_body=True)

        self.assert_request_data(request_data, body={'foo': 'bar'})

    def test_with_post_json_request_and_get_data_raised_exception(self):
        request = RequestMock(content_type='json/application')
        request.get_data = lambda as_text=False: 1 // 0

        request_data = get_data_from_request(request, capture_body=True)

        self.assert_request_data(request_data, body=None)

    def assert_request_data(self, request_data, body):
        assert request_data['method'] == 'POST'
        assert request_data['socket']['encrypted'] is False
        assert request_data['socket']['remote_address'] == 'remote_address'
        assert request_data['env']['REMOTE_ADDR'] == 'remote_address'
        assert request_data['env']['SERVER_NAME'] == 'server_name'
        assert request_data['env']['SERVER_PORT'] == 'server_port'
        assert request_data['headers'] == {}
        assert request_data['url']['full'] == 'http://www.some_url.com'
        assert request_data['url']['hostname'] == 'www.some_url.com'
        assert request_data['url']['pathname'] == ''
        assert request_data['url']['protocol'] == 'http:'
        if body:
            assert request_data['body'] == body


class ResponseMock(object):
    pass


class GetDataFromResponse(TestCase):
    def setUp(self):
        # mock setup logging so it will not log any traces
        self.setup_logging = mock.patch('stackifyapm.conf.setup_logging')
        self.setup_logging.start()

        if not settings.configured:
            settings.configure(**TEST_SETTINGS)
            django.setup()

    def tearDown(self):
        self.setup_logging.stop()

    def test_with_empty_response(self):
        response = ResponseMock()

        response_data = get_data_from_response(response)

        assert response_data == {}

    def test_with_status_code(self):
        response = ResponseMock()
        response.status_code = 200

        response_data = get_data_from_response(response)

        assert response_data == {'status_code': 200}

    def test_with_status_(self):
        response = ResponseMock()
        response.status = 200

        response_data = get_data_from_response(response)

        assert response_data == {'status_code': 200}

    def test_with_code(self):
        response = ResponseMock()
        response.status = 200

        response_data = get_data_from_response(response)

        assert response_data == {'status_code': 200}

    def test_with_headers(self):
        response = ResponseMock()
        response.headers = QueryDict('foo=bar')

        response_data = get_data_from_response(response)

        assert response_data == {'headers': {'foo': 'bar'}}


class GetDataFromException(TestCase):
    def test_should_return_500(self):
        exception_data = get_data_from_exception()

        assert exception_data == {'status_code': 500}
