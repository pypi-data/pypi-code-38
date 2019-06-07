import os
import requests
from unittest import TestCase
from unittest.mock import Mock, patch
from egcg_core import integration_testing, config


class TestIntegrationTesting(TestCase):
    def setUp(self):
        self.original_baseurl = integration_testing.rest_communication.default.baseurl

    def tearDown(self):
        integration_testing.rest_communication.default._baseurl = self.original_baseurl

    def test_wrapped_func(self):
        if os.path.isfile('checks.log'):
            os.remove('checks.log')

        w = integration_testing.WrappedFunc(self, self.assertEqual)
        w('a check', 1, 1)
        with self.assertRaises(AssertionError):
            w('another check', 1, 2)

        with open('checks.log', 'r') as f:
            assert f.readline() == '%s.test_wrapped_func\ta check\tassertEqual\tsuccess\t(1, 1)\n' % self.__class__.__name__
            assert f.readline() == '%s.test_wrapped_func\tanother check\tassertEqual\tfailed\t(1, 2)\n' % self.__class__.__name__

    def test_integration_test(self):
        t = integration_testing.IntegrationTest()
        t.patches = (patch('os.path.isdir', return_value=1337),)
        for attr in ('assertEqual', 'assertTrue'):
            assert getattr(t, attr).assert_func == getattr(t.asserter, attr)

        wd = os.getcwd()
        assert os.path.isdir(wd) is True
        t.setUp()
        assert os.path.isdir(wd) == 1337
        t.tearDown()
        assert os.path.isdir(wd) is True

    @patch('requests.get', side_effect=[requests.exceptions.ConnectionError, Mock()])
    @patch('egcg_core.integration_testing.sleep')
    @patch('egcg_core.integration_testing.get_cfg')
    @patch('egcg_core.integration_testing.check_output')
    def test_reporting_app_integration_test(self, mocked_check_output, mocked_get_cfg, mocked_sleep, mocked_get):
        mocked_check_output.side_effect = [
            b'docker_id\n',
            (
                b'[\n'
                b'    {\n'
                b'        "NetworkSettings": {"Networks": {"bridge": {"IPAddress": "1.2.3.4"}}},\n'
                b'        "Config": {"ExposedPorts": {"80/tcp": {}}}\n'
                b'    }\n'
                b']\n'
            ),
            b'docker_id\n',
            b'docker_id\n'
        ]
        fake_cfg = config.Configuration()
        fake_cfg.content = {
            'reporting_app': {'image_name': 'an_image', 'username': 'a_user', 'password': 'a_password'}
        }
        mocked_get_cfg.return_value = fake_cfg

        t = integration_testing.ReportingAppIntegrationTest()
        t.setUp()
        mocked_get.assert_called_with('http://1.2.3.4:80/api/0.1', timeout=2)
        assert mocked_get.call_count == 2
        assert mocked_sleep.call_count == 1
        t.tearDown()
