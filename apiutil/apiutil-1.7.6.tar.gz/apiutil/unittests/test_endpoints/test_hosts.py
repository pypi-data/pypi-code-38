# encoding: utf-8

import unittest
import apiutil
from apiutil import _metadata
from apiutil.endpoints import Hosts, Host

from configurationutil import configuration
configuration.DEV_FORCE_REWRITE_CONFIG = True


class TestHosts(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_version(self):
        self.assertEqual(apiutil.__version__, _metadata.__version__, u'Version is incorrect')

    # Instantiation
    def test_instantiation(self):
        Hosts()

    def test_host_url(self):
        hosts = Hosts()

        expected_urls = {
            u'prod_1': u'https://p1.example.com:80',
            u'prod_2': u'http://p2.example.com:8080',
            u'lab_1': u'http://l1.example.com:8080'
        }

        for host in hosts:
            self.assertEqual(expected_urls[host], hosts[host].url, u'Host URL does not match')

    def test_convert_domain_to_friendly_name(self):
        hosts = Hosts()

        self.assertEqual(u'prod_2',
                         hosts.convert_domain_to_friendly_name(u'p2.example.com'),
                         u'Convert domain to friendly name failed')

    def test_convert_friendly_name_to_host(self):
        hosts = Hosts()

        host = hosts.convert_friendly_name_to_host(u'lab_1')

        self.assertTrue(isinstance(host, Host), u'Host is not a Host object')
        self.assertEqual(u'l1.example.com',
                         host.domain,
                         u'Convert friendly name to Host failed')


if __name__ == u'__main__':
    unittest.main()
