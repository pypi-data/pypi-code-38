# encoding: utf-8

import unittest
import apiutil
from apiutil import _metadata
from apiutil.endpoints import Endpoints, Hosts

from configurationutil import configuration
configuration.DEV_FORCE_REWRITE_CONFIG = True


class TestEndpoints(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_version(self):
        self.assertEqual(apiutil.__version__, _metadata.__version__, u'Version is incorrect')

    # Instantiation
    def test_instantiation(self):
        Endpoints()

    def test_match_path(self):
        eps = Endpoints()
        endpoint = eps.ep_2

        test_path = u'/some/endpoint/path/2/dummy_data'
        test_path_2 = u'/endpoint/path/2/dummy_data'

        self.assertEqual(21, endpoint.match_path(test_path), u'Endpoint Match Path length mismatch')
        self.assertEqual(0, endpoint.match_path(test_path_2), u'Endpoint Match Path no match failed')

    def test_match_url_with_host(self):
        hosts = Hosts()
        eps = Endpoints(host=hosts.prod_1)
        endpoint = eps.ep_2

        test_path = u'https://p1.example.com:80/some/endpoint/path/2/dummy_data'
        test_path_2 = u'http://l1.example.com:8080/endpoint/path/2/dummy_data'

        self.assertEqual(21, endpoint.match_url(test_path), u'Endpoint Match URL failed')
        self.assertEqual(-1, endpoint.match_url(test_path_2), u'Endpoint Match URL no match failed')

    def test_match_url_without_host(self):
        eps = Endpoints()
        endpoint = eps.ep_2

        test_path = u'https://p1.example.com:80/some/endpoint/path/2/dummy_data'
        test_path_2 = u'http://l1.example.com:8080/endpoint/path/2/dummy_data'

        self.assertEqual(21, endpoint.match_url(test_path), u'Endpoint Match URL failed')
        self.assertEqual(-1, endpoint.match_url(test_path_2), u'Endpoint Match URL no match failed')

    def test_url_with_host(self):
        hosts = Hosts()
        eps = Endpoints(host=hosts.prod_1)

        expected_urls = {
            u'default_root': u'{url}/'.format(url=hosts.prod_1.url),
            u'ep_1': u'{url}/some/endpoint/path/1'.format(url=hosts.prod_1.url),
            u'ep_2': u'{url}/some/endpoint/path/2'.format(url=hosts.prod_1.url),
            u'ep_3': u'{url}/some/endpoint/path/3'.format(url=hosts.prod_1.url),
            u'ep_4': u'{url}/some/endpoint/path/4'.format(url=hosts.prod_1.url)
        }

        for ep in eps:
            self.assertEqual(expected_urls[ep], eps[ep].url, u'Endpoint URL does not match')

    def test_url_without_host(self):
        eps = Endpoints()

        for ep in eps:
            with self.assertRaises(AttributeError):
                _ = eps[ep].url


if __name__ == u'__main__':
    unittest.main()
