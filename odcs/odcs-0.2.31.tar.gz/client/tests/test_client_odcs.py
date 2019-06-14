# -*- coding: utf-8 -*-
# Copyright (c) 2017  Red Hat, Inc.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
# Written by Chenxiong Qi <cqi@redhat.com>

import json
import unittest

import mock
from mock import patch, Mock

from odcs.client.odcs import AuthMech
from odcs.client.odcs import ODCS
from odcs.client.odcs import validate_int


class TestValidateIntValue(unittest.TestCase):
    """Test validate_int"""

    def test_failure_validate_int(self):
        self.assertRaises(TypeError, validate_int, 'a')
        self.assertRaises(TypeError, validate_int, '1')
        self.assertRaises(TypeError, validate_int, '')
        self.assertRaises(TypeError, validate_int, None)
        self.assertRaises(ValueError, validate_int, 0)
        self.assertRaises(ValueError, validate_int, -1)

    def test_succeed_validate_int(self):
        self.assertEqual(None, validate_int(100))
        self.assertEqual(None, validate_int(1))


class TestMakeEndPoint(unittest.TestCase):
    """Test ODCS._make_endpoint"""

    def setUp(self):
        self.server_url = 'http://localhost/'

    def test_make_endpoint(self):
        odcs = ODCS(self.server_url)

        endpoint_url = odcs._make_endpoint('composes/')
        self.assertEqual(
            '{0}api/{1}/composes/'.format(self.server_url,
                                          odcs.api_version),
            endpoint_url)

        endpoint_url = odcs._make_endpoint('/composes/')
        self.assertEqual(
            '{0}api/{1}/composes/'.format(self.server_url,
                                          odcs.api_version),
            endpoint_url)


class TestMakeRequest(unittest.TestCase):
    """Test ODCS._make_request"""

    def setUp(self):
        self.server_url = 'http://localhost/'
        self.resource_path = 'composes/'

    @patch('odcs.client.odcs.requests')
    def test_raise_error(self, requests):
        requests.get.return_value.status_code = 401

        self.odcs = ODCS(self.server_url)
        r = self.odcs._make_request('get', self.resource_path)

        self.assertEqual(requests.get.return_value, r)
        requests.get.return_value.raise_for_status.assert_called_once()

    @patch('odcs.client.odcs.requests')
    @patch('odcs.client.odcs.HTTPKerberosAuth')
    def test_with_kerberos_auth(self, HTTPKerberosAuth, requests):
        requests.get.return_value.status_code = 200
        expected_auth = HTTPKerberosAuth.return_value

        odcs = ODCS(self.server_url, auth_mech=AuthMech.Kerberos)
        r = odcs._make_request('get', self.resource_path)

        self.assertEqual(requests.get.return_value, r)
        requests.get.assert_called_once_with(
            odcs._make_endpoint(self.resource_path),
            auth=expected_auth)

    @patch('odcs.client.odcs.requests')
    def test_with_openidc_auth(self, requests):
        fake_openidc_token = '1234567890'
        requests.post.return_value.status_code = 200

        odcs = ODCS(self.server_url,
                    auth_mech=AuthMech.OpenIDC,
                    openidc_token=fake_openidc_token)
        r = odcs._make_request('post', self.resource_path, data={'id': 1})

        self.assertEqual(requests.post.return_value, r)
        requests.post.assert_called_once_with(
            odcs._make_endpoint(self.resource_path),
            data=json.dumps({'id': 1}),
            headers={
                'Authorization': 'Bearer {0}'.format(fake_openidc_token),
                'Content-Type': 'application/json'
            })

    @patch('odcs.client.odcs.requests')
    def test_with_ssl_auth(self, requests):
        requests.post.return_value.status_code = 200

        odcs = ODCS(self.server_url,
                    auth_mech=AuthMech.SSL,
                    ssl_cert="./ssl.crt", ssl_key="./ssl.key")
        r = odcs._make_request('post', self.resource_path, data={'id': 1})

        self.assertEqual(requests.post.return_value, r)
        requests.post.assert_called_once_with(
            odcs._make_endpoint(self.resource_path),
            data=json.dumps({'id': 1}),
            cert=("./ssl.crt", "./ssl.key"),
            headers={
                'Content-Type': 'application/json'
            })

    @patch('odcs.client.odcs.requests')
    def test_do_not_verify_ssl(self, requests):
        requests.post.return_value.status_code = 200

        odcs = ODCS(self.server_url, verify_ssl=False)
        r = odcs._make_request('post', self.resource_path)

        self.assertEqual(requests.post.return_value, r)
        requests.post.assert_called_once_with(
            odcs._make_endpoint(self.resource_path),
            verify=False)


class TestGetCompose(unittest.TestCase):
    """Test ODCS.get_compose"""

    def setUp(self):
        self.server_url = 'http://localhost/'
        self.odcs = ODCS(self.server_url)

    @patch('odcs.client.odcs.requests')
    def test_get_compose(self, requests):
        fake_compose = {
            'flags': [],
            'id': 1,
            'owner': 'Unknown',
            'result_repo': 'http://odcs.host.qe.eng.pek2.redhat.com/composes/latest-odcs-1-1/compose/Temporary',
            'source': 'cf-1.0-rhel-5',
            'source_type': 1,
            'state': 4,
            'state_name': 'failed',
            'time_done': '2017-07-11T13:05:40Z',
            'time_removed': None,
            'time_submitted': '2017-07-11T13:05:40Z',
            'time_to_expire': '2017-07-12T13:05:40Z'
        }
        requests.get = Mock()
        requests.get.return_value.status_code = 200
        requests.get.return_value.json.return_value = fake_compose

        compose = self.odcs.get_compose(1)

        self.assertEqual(fake_compose, compose)
        requests.get.assert_called_once_with(
            '{0}api/{1}/composes/1'.format(
                self.server_url, self.odcs.api_version))


class TestDeleteCompose(unittest.TestCase):
    """Test ODCS.delete_compose"""

    def setUp(self):
        self.server_url = 'http://localhost/'
        self.odcs = ODCS(self.server_url)

    @patch('odcs.client.odcs.requests')
    def test_compose_id_not_found(self, requests):
        fake_response = {
            'status': 404,
            'error': 'Not Found',
            'message': 'No such compose found.',
        }
        requests.delete.return_value.status_code = 404
        requests.delete.return_value.json.return_value = fake_response

        self.odcs.delete_compose(1)

        requests.delete.return_value.raise_for_status.assert_called_once()

    @patch('odcs.client.odcs.requests')
    def test_delete_compose(self, requests):
        fake_response = {
            'status': 202,
            'message': 'The delete request for compose (id=1) has been accepted'
        }
        requests.delete.return_value.status_code = 202
        requests.delete.return_value.json.return_value = fake_response

        r = self.odcs.delete_compose(1)

        self.assertEqual(fake_response, r)
        requests.delete.assert_called_once_with(
            self.odcs._make_endpoint('composes/1'))


class TestNewCompose(unittest.TestCase):
    """Test ODCS.new_compose"""

    def setUp(self):
        self.server_url = 'http://localhost/'
        self.odcs = ODCS(self.server_url)

    @patch('odcs.client.odcs.requests')
    def test_create_a_new_compose(self, requests):
        fake_new_compose = {
            'flags': [],
            'id': 7,
            'owner': 'Unknown',
            'result_repo': 'http://odcs.host.qe.eng.pek2.redhat.com/composes/latest-odcs-7-1/compose/Temporary',
            'source': 'cf-1.0-rhel-5',
            'source_type': 1,
            'state': 0,
            'state_name': 'wait',
            'time_done': None,
            'time_removed': None,
            'time_submitted': '2017-07-21T03:33:43Z',
            'time_to_expire': '2017-07-22T03:33:43Z'
        }
        requests.post.return_value.status_code = 200
        requests.post.return_value.json.return_value = fake_new_compose

        new_compose = self.odcs.new_compose('cf-1.0-rhel-5',
                                            'tag',
                                            packages=['libdnet'],
                                            sigkeys=['123', '456'],
                                            results=["boot.iso"])

        self.assertEqual(fake_new_compose, new_compose)
        requests.post.assert_called_once_with(
            self.odcs._make_endpoint('composes/'),
            data=json.dumps({
                'source': {'source': 'cf-1.0-rhel-5',
                           'type': 'tag',
                           'packages': ['libdnet'],
                           'sigkeys': ['123', '456']},
                'results': ['boot.iso'],
            }),
            headers={'Content-Type': 'application/json'}
        )


class TestRenewCompose(unittest.TestCase):
    """Test ODCS.renew_compose"""

    def setUp(self):
        self.server_url = 'http://localhost/'
        self.odcs = ODCS(self.server_url)

    @patch('odcs.client.odcs.requests')
    def test_renew_a_compose(self, requests):
        fake_renew_compose = {
            'flags': [],
            'id': 7,
            'owner': 'Unknown',
            'result_repo': 'http://odcs.host.qe.eng.pek2.redhat.com/composes/latest-odcs-7-1/compose/Temporary',
            'source': 'cf-1.0-rhel-5',
            'source_type': 1,
            'state': 0,
            'state_name': 'wait',
            'time_done': None,
            'time_removed': None,
            'time_submitted': '2017-07-21T03:33:43Z',
            'time_to_expire': '2017-07-22T03:33:43Z'
        }
        requests.patch.return_value.status_code = 200
        requests.patch.return_value.json.return_value = fake_renew_compose

        r = self.odcs.renew_compose(6, seconds_to_live=60)

        self.assertEqual(fake_renew_compose, r)
        requests.patch.assert_called_once_with(
            self.odcs._make_endpoint('composes/6'),
            data=json.dumps({'seconds-to-live': 60}),
            headers={'Content-Type': 'application/json'})


class TestFindComposes(unittest.TestCase):
    """Test ODCS.find_composes"""

    def setUp(self):
        self.server_url = 'http://localhost/'
        self.odcs = ODCS(self.server_url)

    @patch('odcs.client.odcs.requests')
    def test_find_composes_without_pagination(self, requests):
        fake_found_composes = {
            'items': [
                {
                    'flags': [],
                    'id': 1,
                    'owner': 'Unknown',
                    'result_repo': 'http://localhost/composes/latest-odcs-1-1/compose/Temporary',
                    'source': 'cf-1.0-rhel-5',
                    'source_type': 1,
                    'state': 4,
                    'state_name': 'failed',
                    'time_done': '2017-07-11T13:05:40Z',
                    'time_removed': None,
                    'time_submitted': '2017-07-11T13:05:40Z',
                    'time_to_expire': '2017-07-12T13:05:40Z'
                },
                {
                    'flags': [],
                    'id': 2,
                    'owner': 'Unknown',
                    'result_repo': 'http://localhost/composes/latest-odcs-2-1/compose/Temporary',
                    'source': 'cf-1.0-rhel-5',
                    'source_type': 1,
                    'state': 4,
                    'state_name': 'failed',
                    'time_done': '2017-07-11T13:07:42Z',
                    'time_removed': None,
                    'time_submitted': '2017-07-11T13:07:41Z',
                    'time_to_expire': '2017-07-12T13:07:41Z'
                },
            ],
            'meta': {
                'page': 1,
                'pages': 1,
            }
        }
        requests.get.return_value.status_code = 200
        requests.get.return_value.json.return_value = fake_found_composes

        r = self.odcs.find_composes(owner='unknown',
                                    source_type='tag')

        self.assertEqual(fake_found_composes, r)
        requests.get.assert_called_once_with(
            self.odcs._make_endpoint('composes/'),
            params={'owner': 'unknown', 'source_type': 'tag'})

    @patch('odcs.client.odcs.requests')
    def test_find_composes_the_second_page(self, requests):
        fake_found_composes = {
            'items': [
                {
                    'flags': [],
                    'id': 1,
                    'owner': 'Unknown',
                    'result_repo': 'http://localhost/composes/latest-odcs-1-1/compose/Temporary',
                    'source': 'cf-1.0-rhel-5',
                    'source_type': 1,
                    'state': 4,
                    'state_name': 'failed',
                    'time_done': '2017-07-11T13:05:40Z',
                    'time_removed': None,
                    'time_submitted': '2017-07-11T13:05:40Z',
                    'time_to_expire': '2017-07-12T13:05:40Z'
                },
                {
                    'flags': [],
                    'id': 2,
                    'owner': 'Unknown',
                    'result_repo': 'http://localhost/composes/latest-odcs-2-1/compose/Temporary',
                    'source': 'cf-1.0-rhel-5',
                    'source_type': 1,
                    'state': 4,
                    'state_name': 'failed',
                    'time_done': '2017-07-11T13:07:42Z',
                    'time_removed': None,
                    'time_submitted': '2017-07-11T13:07:41Z',
                    'time_to_expire': '2017-07-12T13:07:41Z'
                },
            ],
            'meta': {
                'page': 1,
                'pages': 1,
            }
        }
        requests.get.return_value.status_code = 200
        requests.get.return_value.json.return_value = fake_found_composes

        r = self.odcs.find_composes(owner='unknown',
                                    source_type='tag',
                                    page=2)

        self.assertEqual(fake_found_composes, r)
        requests.get.assert_called_once_with(
            self.odcs._make_endpoint('composes/'),
            params={'owner': 'unknown', 'source_type': 'tag', 'page': 2})


@patch('time.sleep')
@patch('odcs.client.odcs.ODCS.get_compose')
class TestWaitForCompose(unittest.TestCase):
    """Test ODCS.wait_for_compose"""

    _TIME_TMP_VAR = 0

    def setUp(self):
        self.server_url = 'http://localhost/'
        self.odcs = ODCS(self.server_url)

    def test_wait_for_compose(self, get_compose, sleep):
        for state in ["done", "removed", "failed"]:
            get_compose.reset_mock()
            sleep.reset_mock()
            get_compose.side_effect = [{"state_name": "wait"},
                                       {"state_name": "generating"},
                                       {"state_name": state}]
            self.odcs.wait_for_compose(1)

            self.assertEqual(sleep.mock_calls,
                             [mock.call(1), mock.call(2)])
            self.assertEqual(get_compose.mock_calls,
                             [mock.call(1)] * 3)

    @patch('time.time')
    def test_wait_for_compose_timeout(self, time_travel, get_compose, sleep):
        get_compose.side_effect = [{"state_name": "wait"}] * 2
        time_travel.side_effect = [1, 301]
        self.assertRaises(RuntimeError, self.odcs.wait_for_compose, 1)

    @patch('time.time')
    def test_wait_for_compose_elapsed_close_to_timeout(
            self, _time, get_compose, sleep):
        TestWaitForCompose._TIME_TMP_VAR = 0

        # Replace time.sleep() method which does not sleep, but updates the
        # _TIME_TMP_VAR with number of seconds it would sleep.
        def mocked_sleep(seconds):
            TestWaitForCompose._TIME_TMP_VAR += seconds
        sleep.side_effect = mocked_sleep

        # Replace time.time() method to return _TIME_TMP_VAR.
        def mocked_time():
            return TestWaitForCompose._TIME_TMP_VAR
        _time.side_effect = mocked_time

        get_compose.side_effect = [{"state_name": "wait"}] * 10
        self.assertRaises(RuntimeError, self.odcs.wait_for_compose, 1, 10)

        self.assertEqual(sleep.mock_calls,
                         [mock.call(1), mock.call(2), mock.call(3), mock.call(4)])
