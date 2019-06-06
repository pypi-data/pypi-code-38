import unittest
import sys

import pytest
import requests
import requests_mock
from hamcrest import assert_that, instance_of, is_in, none, equal_to, is_
from jsonpickle import json

from sequoia import auth, http, error

if sys.version_info[0] == 2:
    import mock
    from mock import patch
else:
    from unittest import mock
    from unittest.mock import patch


class HttpExecutorTest(unittest.TestCase):

    def setUp(self):
        self.session_mock = requests.Session()
        self.adapter = requests_mock.Adapter()
        self.session_mock.mount('mock', self.adapter)

    @patch('requests.Session')
    def test_request_given_a_list_of_parameters_then_they_are_added_to_the_request(self, session_mock):
        # There is an issue where parameters won't be added to the request if the prefix does not start
        # with http https://bugs.launchpad.net/requests-mock/+bug/1518497. So request-mock can't be used here
        # to check parameters
        session_mock.request.return_value.url = 'mock://some_url'
        session_mock.request.return_value.status_code = 200
        session_mock.request.return_value.is_redirect = False

        http_executor = http.HttpExecutor(auth.Auth("client_id", "client_secret"), session=session_mock)
        http_executor.request("POST", "mock://some_url",
                              data='some data',
                              headers={'New-Header': 'SomeValue'},
                              params={'key1': 'value1'})

        session_mock.request.assert_called_with('POST', 'mock://some_url', allow_redirects=False, data='some data',
                                                headers=mock.ANY, params={'key1': 'value1'}, timeout=240)

    @staticmethod
    def match_request_text(request):
        return 'some data' in (request.text or '')

    def test_request_given_additional_headers_and_data_then_they_are_added_to_the_request(self):

        self.adapter.register_uri('POST', 'mock://some_url', text='{"key_1": "value_1"}',
                                  request_headers={'New-Header': 'SomeValue'},
                                  additional_matcher=HttpExecutorTest.match_request_text)

        http_executor = http.HttpExecutor(auth.Auth("client_id", "client_secret"), session=self.session_mock)
        response = http_executor.request("POST", "mock://some_url",
                                         headers={'New-Header': 'SomeValue'},
                                         data='some data')

        assert_that(response.data, equal_to({"key_1": "value_1"}))

    def test_request_given_get_method_and_an_unreachable_url_then_a_connectivity_error_should_be_raised(self):
        self.adapter.register_uri('GET', 'mock://some_url',
                                  exc=requests.exceptions.ConnectionError('some error desc'))

        http_executor = http.HttpExecutor(auth.Auth("client_id", "client_secret"), session=self.session_mock)

        with pytest.raises(error.ConnectionError) as sequoia_error:
            http_executor.request("GET", "mock://some_url")

        assert_that('some error desc', is_in(sequoia_error.value.args))
        assert_that(sequoia_error.value.cause, instance_of(requests.exceptions.ConnectionError))

    def test_request_given_server_returns_too_many_redirects_then_error_should_be_raised(self):
        self.adapter.register_uri('GET', 'mock://some_url',
                                  exc=requests.exceptions.TooManyRedirects('some error desc'))

        http_executor = http.HttpExecutor(auth.Auth("client_id", "client_secret"), session=self.session_mock)

        with pytest.raises(error.TooManyRedirects) as sequoia_error:
            http_executor.request("GET", "mock://some_url")

        assert_that('some error desc', is_in(sequoia_error.value.args))
        assert_that(sequoia_error.value.cause, instance_of(requests.exceptions.TooManyRedirects))

    def test_request_given_get_method_and_server_throw_connection_timeout_then_a_connection_error_should_be_raised(self):
        self.adapter.register_uri('GET', 'mock://some_url',
                                  exc=requests.exceptions.ConnectTimeout('some error desc'))

        http_executor = http.HttpExecutor(auth.Auth("client_id", "client_secret"), session=self.session_mock)

        with pytest.raises(error.ConnectionError) as sequoia_error:
            http_executor.request("GET", "mock://some_url")

        assert_that('some error desc', is_in(sequoia_error.value.args))
        assert_that(sequoia_error.value.cause, instance_of(requests.exceptions.ConnectionError))

    def test_request_given_get_method_and_server_throw_timeout_then_a_timeout_error_should_be_raised(self):
        self.adapter.register_uri('GET', 'mock://some_url',
                                  exc=requests.exceptions.Timeout('some error desc'))

        http_executor = http.HttpExecutor(auth.Auth("client_id", "client_secret"), session=self.session_mock)

        with pytest.raises(error.Timeout) as sequoia_error:
            http_executor.request("GET", "mock://some_url")

        assert_that('some error desc', is_in(sequoia_error.value.args))
        assert_that(sequoia_error.value.cause, instance_of(requests.exceptions.Timeout))

    def test_request_given_get_method_and_server_returns_an_error_code_then_that_error_should_be_populated(self):
        self.adapter.register_uri('GET', 'mock://test.com', text='some json value', status_code=403)

        http_executor = http.HttpExecutor(auth.Auth("client_id", "client_secret"), session=self.session_mock)

        with pytest.raises(error.HttpError) as sequoia_error:
            http_executor.request("GET", "mock://test.com")

        assert_that(sequoia_error.value.status_code, 403)
        assert_that(sequoia_error.value.message, 'some json value')
        assert_that(sequoia_error.value.cause, none())

    def test_request_given_post_method_and_server_returns_an_error_code_then_that_error_should_be_populated(self):
        self.adapter.register_uri('POST', 'mock://test.com', text='{"error": "some json value"}', status_code=403)

        http_executor = http.HttpExecutor(auth.Auth("client_id", "client_secret"), session=self.session_mock)

        with pytest.raises(error.HttpError) as sequoia_error:
            http_executor.request("POST", "mock://test.com")

        assert_that(sequoia_error.value.status_code, is_(403))
        assert_that(sequoia_error.value.message, is_({'error': 'some json value'}))
        assert_that(sequoia_error.value.cause, none())

    def test_request_given_server_returns_an_error_then_the_request_should_be_retried(self):

        json_response = '{"resp2": "resp2"}'

        self.adapter.register_uri('GET', 'mock://test.com', [{'text': 'resp1', 'status_code': 500},
                                                             {'text': json_response, 'status_code': 200}])

        http_executor = http.HttpExecutor(auth.Auth("client_id", "client_secret"), session=self.session_mock)

        response = http_executor.request("GET", "mock://test.com")

        assert_that(response.data, equal_to(json.loads(json_response)))

    def test_request_given_server_returns_an_error_then_the_request_should_be_retried_10_times_by_default(self):

        json_response = '{"resp2": "resp2"}'

        self.adapter.register_uri('GET', 'mock://test.com', [{'text': 'resp1', 'status_code': 500},
                                                             {'text': 'resp1', 'status_code': 500},
                                                             {'text': 'resp1', 'status_code': 500},
                                                             {'text': 'resp1', 'status_code': 500},
                                                             {'text': 'resp1', 'status_code': 500},
                                                             {'text': 'resp1', 'status_code': 500},
                                                             {'text': 'resp1', 'status_code': 500},
                                                             {'text': 'resp1', 'status_code': 500},
                                                             {'text': 'resp1', 'status_code': 500},
                                                             {'text': 'resp1', 'status_code': 500},
                                                             {'text': json_response, 'status_code': 200}])

        http_executor = http.HttpExecutor(auth.Auth("client_id", "client_secret"), session=self.session_mock)
        with pytest.raises(error.HttpError) as sequoia_error:
            http_executor.request("GET", "mock://test.com")

        assert_that(sequoia_error.value.status_code, is_(500))

    def test_request_given_server_returns_an_error_then_the_request_should_be_retried_configured_times_by_default(self):

        json_response = '{"resp2": "resp2"}'

        self.adapter.register_uri('GET', 'mock://test.com', [{'text': 'resp1', 'status_code': 500},
                                                             {'text': 'resp1', 'status_code': 500},
                                                             {'text': 'resp1', 'status_code': 500},
                                                             {'text': 'resp1', 'status_code': 500},
                                                             {'text': 'resp1', 'status_code': 500},
                                                             {'text': 'resp1', 'status_code': 500},
                                                             {'text': 'resp1', 'status_code': 500},
                                                             {'text': 'resp1', 'status_code': 500},
                                                             {'text': 'resp1', 'status_code': 500},
                                                             {'text': 'resp1', 'status_code': 500},
                                                             {'text': json_response, 'status_code': 200}])

        http_executor = http.HttpExecutor(auth.Auth("client_id", "client_secret"), session=self.session_mock,
                                          backoff_strategy={'interval': 0, 'max_tries': 11})
        response = http_executor.request("GET", "mock://test.com")

        assert_that(response.data, equal_to(json.loads(json_response)))

    def test_request_given_a_resource_name_for_a_request_then_it_should_be_returned_with_the_request_result(self):

        self.adapter.register_uri('GET', 'mock://test.com', status_code=200)

        http_executor = http.HttpExecutor(auth.Auth("client_id", "client_secret"), session=self.session_mock)

        resource_name_expected = 'resource_name_test'
        response = http_executor.request("GET", "mock://test.com", resource_name=resource_name_expected)

        assert_that(response.resource_name, equal_to(resource_name_expected))
