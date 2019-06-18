from unittest import TestCase

from stackifyapm.utils.wsgi import get_headers
from stackifyapm.utils.wsgi import get_environ
from stackifyapm.utils.wsgi import get_host


class GetHeadersTest(TestCase):

    def test_should_return_nothing_given_invalid_data(self):
        invalid_data = {'SOME_KEY': 'SOME_VALUE'}

        headers = get_headers(invalid_data)

        assert dict(headers) == {}

    def test_should_return_generator_with_valid_data(self):
        valid_custom_data = {'HTTP_SOME_KEY': 'HTTP_SOME_VALUE'}

        headers = get_headers(valid_custom_data)

        assert dict(headers) == {'some-key': 'HTTP_SOME_VALUE'}

    def test_should_return_generator_with_valid_headers(self):
        valid_headers = {'CONTENT_TYPE': 'application/json'}

        headers = get_headers(valid_headers)

        assert dict(headers) == {'content-type': 'application/json'}


class GetEnvironTest(TestCase):

    def test_should_return_nothing_given_invalid_data(self):
        invalid_data = {'SOME_KEY': 'SOME_VALUE'}

        environ = get_environ(invalid_data)

        assert dict(environ) == {}

    def test_should_return_valid_data(self):
        valid_data = {
            "REMOTE_ADDR": "remote address",
            "SERVER_NAME": "server name",
            "SERVER_PORT": "server port",
        }

        environ = get_environ(valid_data)

        assert dict(environ) == {
            "REMOTE_ADDR": "remote address",
            "SERVER_NAME": "server name",
            "SERVER_PORT": "server port",
        }

    def test_should_only_return_expected_data(self):
        valid_data = {
            "REMOTE_ADDR": "remote address",
            "SERVER_NAME": "server name",
            "SERVER_PORT": "server port",
            "CUSTOM_KEY1": "value1",
            "CUSTOM_KEY2": "value2",
        }

        environ = get_environ(valid_data)

        assert dict(environ) == {
            "REMOTE_ADDR": "remote address",
            "SERVER_NAME": "server name",
            "SERVER_PORT": "server port",
        }


class GetHostTest(TestCase):
    def test_should_return_http_with_x_forwarded_host(self):
        data = {
            "wsgi.url_scheme": "http",
            "HTTP_X_FORWARDED_HOST": "some.host.name:80",
        }

        host = get_host(data)

        assert host == "some.host.name"

    def test_should_return_https_with_x_forwarded_host(self):
        data = {
            "wsgi.url_scheme": "https",
            "HTTP_X_FORWARDED_HOST": "some.host.name:443",
        }

        host = get_host(data)

        assert host == "some.host.name"

    def test_should_return_http_with_http_host(self):
        data = {
            "wsgi.url_scheme": "http",
            "HTTP_HOST": "some.host.name:80",
        }

        host = get_host(data)

        assert host == "some.host.name"

    def test_should_return_https_with_http_host(self):
        data = {
            "wsgi.url_scheme": "https",
            "HTTP_HOST": "some.host.name:443",
        }

        host = get_host(data)

        assert host == "some.host.name"

    def test_should_return_http_given_no_http_host_header(self):
        data = {
            "wsgi.url_scheme": "http",
            "SERVER_NAME": "some.host.name",
            "SERVER_PORT": "80"
        }

        host = get_host(data)

        assert host == "some.host.name"

    def test_should_return_https_given_no_http_host_header(self):
        data = {
            "wsgi.url_scheme": "https",
            "SERVER_NAME": "some.host.name",
            "SERVER_PORT": "443"
        }

        host = get_host(data)

        assert host == "some.host.name"
