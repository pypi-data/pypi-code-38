import unittest
import json
import yaml

from unittest.mock import patch

from ..config import EvolvConfig
from ..request import EvolvRequest
from ..collections import METAMODELS


def mocked_request(*args, **kwargs):
    """
    Mocks a good response from a request.
    """
    class MockResponse:
        def __init__(self, json_data, status_code, headers={'Content-Type': 'application/json'}):
            self.json_data = json_data
            self.status_code = status_code
            self.headers = headers

            if json_data:
                self.content = json.dumps(json_data).encode()
            else:
                self.content = b''

        def json(self):
            return self.json_data

        @property
        def ok(self):
            if self.status_code < 400:
                return True
            return False

    return MockResponse({'test': 1}, 200)


def mocked_request_bad_response(*args, **kwargs):
    """
    Mocks a bad response from a request.
    """
    class MockResponse:
        def __init__(self, json_data, status_code):
            self.json_data = json_data
            self.status_code = status_code

            if json_data:
                self.content = json.dumps(json_data).encode()
            else:
                self.content = b''

        def json(self):
            return self.json_data

        @property
        def ok(self):
            if self.status_code < 400:
                return True
            return False

    return MockResponse(None, 401)


class TestEvolvRequest(unittest.TestCase):
    """
    Tests the EvolvRequest class.
    """
    API_KEY = 'xx_test_xx'
    API_DOMAIN = 'test.evolv.ai'
    API_VERSION = 'v1'
    METAMODEL_ID = 'test1'
    ACCOUNT_ID = 'test_account'

    def test_create_instance(self):
        """
        Tests the creation of a EvolvRequest instance.
        """
        config = EvolvConfig(api_key=self.API_KEY)
        requester = EvolvRequest(config)

        self.assertIsInstance(requester, EvolvRequest)

    def test_request_path(self):
        """
        Tests the api request path builder.
        """
        config = EvolvConfig(
            api_domain=self.API_DOMAIN,
            api_key=self.API_KEY,
            api_version=self.API_VERSION
        )
        requester = EvolvRequest(config)
        path = requester.request_path(METAMODELS, account_id=self.ACCOUNT_ID)
        self.assertEqual(path, 'https://{}/{}/accounts/{}/metamodels'.format(self.API_DOMAIN, self.API_VERSION,
                                                                             self.ACCOUNT_ID))

        path = requester.request_path(METAMODELS, entity_id=self.METAMODEL_ID, account_id=self.ACCOUNT_ID)
        self.assertEqual(path, 'https://{}/{}/accounts/{}/metamodels/{}'.format(self.API_DOMAIN, self.API_VERSION,
                                                                                self.ACCOUNT_ID, self.METAMODEL_ID))

        path = requester.request_path(METAMODELS, entity_id=self.METAMODEL_ID, account_id=self.ACCOUNT_ID,
                                      content_only=True)
        self.assertEqual(path, 'https://{}/{}/accounts/{}/metamodels/{}/content'.format(self.API_DOMAIN,
                                                                                        self.API_VERSION,
                                                                                        self.ACCOUNT_ID,
                                                                                        self.METAMODEL_ID))

        query = {'query': 'test'}
        path = requester.request_path(METAMODELS, account_id=self.ACCOUNT_ID, query=query)
        self.assertEqual(path, 'https://{}/{}/accounts/{}/metamodels{}'.format(self.API_DOMAIN,
                                                                               self.API_VERSION,
                                                                               self.ACCOUNT_ID,
                                                                               '?query=test'))

    @patch('evolvclient.request.requests.get', side_effect=mocked_request)
    def test_get_method(self, mock_get):
        """
        Tests a get request to the experiment api.
        """
        config = EvolvConfig(
            api_domain=self.API_DOMAIN,
            api_key=self.API_KEY,
            api_version=self.API_VERSION
        )
        requester = EvolvRequest(config)

        response = requester.get(METAMODELS, self.METAMODEL_ID)
        self.assertEqual(response, {'test': 1})

        response = requester.get(METAMODELS, self.METAMODEL_ID, version=1)
        self.assertEqual(response, {'test': 1})

    @patch('evolvclient.request.requests.get', side_effect=mocked_request_bad_response)
    def test_get_method_bad_response(self, mock_get):
        """
        Tests a bad get request to the experiment api.
        """
        config = EvolvConfig(
            api_domain=self.API_DOMAIN,
            api_key=self.API_KEY,
            api_version=self.API_VERSION
        )
        requester = EvolvRequest(config)

        with self.assertRaises(EvolvRequest.BadResponse):
            requester.get(METAMODELS, self.METAMODEL_ID)

    @patch('evolvclient.request.requests.get', side_effect=mocked_request)
    def test_query_method(self, mock_get):
        """
        Tests a query request to the experiment api.
        """
        config = EvolvConfig(
            api_domain=self.API_DOMAIN,
            api_key=self.API_KEY,
            api_version=self.API_VERSION
        )
        requester = EvolvRequest(config)

        response = requester.query(METAMODELS)
        self.assertEqual(response, {'test': 1})

        response = requester.query(METAMODELS, 'test')
        self.assertEqual(response, {'test': 1})

    @patch('evolvclient.request.requests.get', side_effect=mocked_request_bad_response)
    def test_query_method_bad_response(self, mock_get):
        """
        Tests a bad query request to the experiment api.
        """
        config = EvolvConfig(
            api_domain=self.API_DOMAIN,
            api_key=self.API_KEY,
            api_version=self.API_VERSION
        )
        requester = EvolvRequest(config)

        with self.assertRaises(EvolvRequest.BadResponse):
            requester.query(METAMODELS)

    @patch('evolvclient.request.requests.post', side_effect=mocked_request)
    def test_post_method(self, mock_get):
        """
        Tests a post request to the experiment api.
        """
        config = EvolvConfig(
            api_domain=self.API_DOMAIN,
            api_key=self.API_KEY,
            api_version=self.API_VERSION
        )
        requester = EvolvRequest(config)

        response = requester.post(METAMODELS, {'test_request': 1})
        self.assertEqual(response, {'test': 1})

    @patch('evolvclient.request.requests.post', side_effect=mocked_request_bad_response)
    def test_post_method_bad_response(self, mock_get):
        """
        Tests a bad post request to the experiment api.
        """
        config = EvolvConfig(
            api_domain=self.API_DOMAIN,
            api_key=self.API_KEY,
            api_version=self.API_VERSION
        )
        requester = EvolvRequest(config)

        with self.assertRaises(EvolvRequest.BadResponse):
            requester.post(METAMODELS, {'test_request': 1})

    def test_json_response(self):
        """
        Tests the json response method.
        """
        class MockResponse:
            def __init__(self, data, headers={'Content-Type': 'application/json'}):
                self.data = data
                self.headers = headers

                if data and headers['Content-Type'] == 'application/json':
                    self.content = json.dumps(data).encode()
                elif data and headers['Content-Type'] == 'application/yaml':
                    self.content = yaml.dump(data).encode()
                else:
                    self.content = b''

            def json(self):
                return self.data

        response = MockResponse(None)
        self.assertEqual(EvolvRequest.json_response(response, many=True), [])

        response = MockResponse(None)
        self.assertEqual(EvolvRequest.json_response(response), {})

        response = MockResponse({'test': 1})
        self.assertEqual(EvolvRequest.json_response(response), {'test': 1})

        response = MockResponse([{'test': 1}, {'test': 2}])
        self.assertEqual(EvolvRequest.json_response(response), [{'test': 1}, {'test': 2}])

        response = MockResponse({'_name': 'Sample'}, headers={'Content-Type': 'application/yaml'})
        self.assertEqual(EvolvRequest.json_response(response), {'response_yaml': True, 'content': '_name: Sample\n'})


if __name__ == '__main__':
    unittest.main()
