# encoding: utf-8

import unittest
import apiutil
from apiutil import _metadata
from apiutil.endpoints import APIS, Host, Endpoints

from configurationutil import configuration
configuration.DEV_FORCE_REWRITE_CONFIG = True


class TestAPIs(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_version(self):
        self.assertEqual(apiutil.__version__, _metadata.__version__, u'Version is incorrect')

    # Instantiation
    def test_instantiation(self):
        APIS()

    def test_match_url(self):
        apis = APIS()
        api = apis.api_1

        test_path = u'https://p1.example.com:80/some/endpoint/path/2/dummy_data'
        test_path_2 = u'http://l1.example.com:8080/endpoint/path/2/dummy_data'
        test_path_3 = u'https://p1.example.com:80/some/endpoint/path/dummy_data'

        test_path_expected = ([(u'family_a', u'api_1', u'ep_2')], 21)
        test_path_2_expected = ([], -1)
        test_path_3_expected = ([(u'family_a', u'api_1', u'ep_1'), (u'family_a', u'api_1', u'ep_2')], 20)

        self.assertEqual(test_path_expected, api.match_url(test_path), u'API Match URL failed')
        self.assertEqual(test_path_2_expected, api.match_url(test_path_2), u'API Match URL no match failed')

        matches_3 = api.match_url(test_path_3)
        matches_3[0].sort()  # Sort as Py2 iteration is un-ordered!
        self.assertEqual(test_path_3_expected, matches_3, u'API Match URL multi match failed')

    def test_get_endpoint_for_request(self):
        apis = APIS()

        test_path = u'https://p1.example.com:80/some/endpoint/path/2/dummy_data'
        test_path_2 = u'http://l1.example.com:8080/endpoint/path/dummy_data'

        test_path_expected = (u'family_a', u'api_1', u'ep_2')

        self.assertEqual(test_path_expected,
                         apis.get_endpoint_for_request(test_path),
                         u'APIs get endpoint for request failed')

        with self.assertRaises(LookupError):
            apis.get_endpoint_for_request(test_path_2)

    def test_get_api_family(self):
        apis = APIS()

        expected_family_apis = [u'api_2', u'api_3']

        self.assertEqual(expected_family_apis,
                         sorted(apis.get_api_family(u'family_b')),
                         u'APIS get api family failed')

    def test_getitem(self):
        apis = APIS()
        api = apis.api_1

        self.assertTrue(isinstance(api.family, str), u'API family type incorrect')
        self.assertTrue(isinstance(api.host, Host), u'API host type incorrect')
        self.assertTrue(isinstance(api.endpoints, Endpoints), u'API endpoints type incorrect')
        self.assertTrue(isinstance(api.parameters, dict), u'API parameters type incorrect')


if __name__ == u'__main__':
    unittest.main()
