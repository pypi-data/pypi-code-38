# encoding: utf-8

import os
import shutil
import unittest
from fdutil.path_tools import pop_path
from configurationutil import Configuration, cfg_params
from pydnserver import dns_lookup, __version__, __authorshort__


class TestConfiguration(unittest.TestCase):

    def setUp(self):
        cfg_params.APP_NAME = u'TestPyDNServer'
        cfg_params.APP_VERSION = __version__
        cfg_params.APP_AUTHOR = __authorshort__
        dns_lookup.TEMPLATE = os.path.join(pop_path(__file__), u'resources', u'dns_lookup.json')
        Configuration().__init__()  # Calling this here to ensure config re-inited following deletion in cleanup!

        self.addCleanup(self.clean)

    def tearDown(self):
        pass

    @staticmethod
    def clean():
        try:
            shutil.rmtree(pop_path(pop_path(Configuration().config_path)) + os.sep)

        except OSError:
            pass

    def test_get_redirection_config(self):
        expected_output = {
            u'example.com': {u'active': True, u'redirect_host': u'alt.example.com'},
            u'example2.com': {u'active': False, u'redirect_host': u'default'},
            u'example3.com': {u'active': True, u'redirect_host': u'alt.example3.com'}
        }

        self.assertEqual(expected_output,
                         dns_lookup.get_redirection_config(),
                         u'Get Redirection Config failed')

    def test_get_active_redirection_config(self):
        expected_output = {
            u'example.com': {u'active': True, u'redirect_host': u'alt.example.com'},
            u'example3.com': {u'active': True, u'redirect_host': u'alt.example3.com'}
        }

        self.assertEqual(expected_output,
                         dns_lookup.get_active_redirection_config(),
                         u'Get Redirection Config failed')

    def test_get_active_redirect_record_for_host(self):
        expected_output = {u'active': True, u'redirect_host': u'alt.example3.com'}

        self.assertEqual(expected_output,
                         dns_lookup.get_active_redirect_record_for_host(u'example3.com'),
                         u'Get Redirection Config for host failed')

    def test_get_active_redirect_record_for_bad_host(self):
        with self.assertRaises(dns_lookup.NoActiveRecordForHost):
            _ = dns_lookup.get_active_redirect_record_for_host(u'DoesNotExist.com')

    def test_get_redirect_hostname_for_host(self):
        self.assertEqual(dns_lookup.get_redirect_hostname_for_host(u'example3.com'), u'alt.example3.com',
                         u'Get Redirection Config for host failed')

    def test_get_redirect_hostname_for_bad_host(self):
        with self.assertRaises(dns_lookup.NoActiveRecordForHost):
            _ = dns_lookup.get_redirect_hostname_for_host(u'DoesNotExist.com')


if __name__ == u'__main__':
    unittest.main()
