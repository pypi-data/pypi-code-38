# -*- coding: utf-8 -*-
# Copyright (c) 2018  Red Hat, Inc.
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
#            Qixiang Wan <qwan@redhat.com>

import mock

from tests import UrsaMajorTestCase, MockResponse, MockMBSBuildsData
from ursa_major.mbs import MBS


class TestMBS(UrsaMajorTestCase):
    @mock.patch('ursa_major.mbs.requests.get')
    def test_get_modules_with_no_page_releated_params(self, get):
        mock_builds = [
            {'id': 1, 'name': 'mariadb', 'stream': '10.4', 'koji_tag': '123', 'state': 5},
            {'id': 2, 'name': 'mariadb', 'stream': '10.4', 'koji_tag': '234', 'state': 5},
            {'id': 3, 'name': 'mariadb', 'stream': '10.4', 'koji_tag': '456', 'state': 5},
            {'id': 4, 'name': 'mariadb', 'stream': '10.4', 'koji_tag': '789', 'state': 5},
            {'id': 5, 'name': 'mariadb', 'stream': '10.4', 'koji_tag': '012', 'state': 5},
        ]

        mock_data = MockMBSBuildsData(mock_builds)

        get.side_effect = mock_data.get

        mbs = MBS('http://mbs.example.com')
        modules = mbs.get_modules(name='mariadb')

        self.assertEqual(modules, mock_builds)

    @mock.patch('ursa_major.mbs.requests.get')
    def test_get_modules_with_page_related_params(self, get):
        mock_builds = [
            {'id': 1, 'name': 'mariadb', 'stream': '10.4', 'koji_tag': '123', 'state': 5},
            {'id': 2, 'name': 'mariadb', 'stream': '10.4', 'koji_tag': '234', 'state': 5},
            {'id': 3, 'name': 'mariadb', 'stream': '10.4', 'koji_tag': '456', 'state': 5},
            {'id': 4, 'name': 'mariadb', 'stream': '10.4', 'koji_tag': '789', 'state': 5},
            {'id': 5, 'name': 'mariadb', 'stream': '10.4', 'koji_tag': '012', 'state': 5},
        ]

        mock_data = MockMBSBuildsData(mock_builds)

        get.side_effect = mock_data.get

        mbs = MBS('http://mbs.example.com')
        modules = mbs.get_modules(name='mariadb', page=1, per_page=2)

        expected = [
            {'id': 1, 'name': 'mariadb', 'stream': '10.4', 'koji_tag': '123', 'state': 5},
            {'id': 2, 'name': 'mariadb', 'stream': '10.4', 'koji_tag': '234', 'state': 5},
        ]

        self.assertEqual(modules, expected)

    @mock.patch('ursa_major.mbs.requests.get')
    def test_get_module_mmd(self, get):

        testmodule_file = 'mbs_testmodule_604_verbose.json'
        resp_data = self.load_json_from_file(testmodule_file)
        get.return_value = MockResponse(resp_data, 200)

        mbs = MBS('http://mbs.example.com')
        mmd = mbs.get_module_mmd(604)
        self.assertEqual(mmd.peek_name(), 'testmodule')
        self.assertEqual(mmd.peek_stream(), 'rhel-8.0')
        self.assertEqual(str(mmd.peek_version()), '20180507102412')
        self.assertEqual(mmd.peek_context(), 'c2c572ec')

    @mock.patch('ursa_major.mbs.requests.get')
    def test_module_has_requires(self, get):

        testmodule_file = 'mbs_testmodule_604_verbose.json'
        resp_data = self.load_json_from_file(testmodule_file)
        get.return_value = MockResponse(resp_data, 200)

        mbs = MBS('http://mbs.example.com')
        self.assertTrue(mbs.module_has_requires(604, {'platform': 'el8'}))

    @mock.patch('ursa_major.mbs.requests.get')
    def test_module_not_has_requires(self, get):

        testmodule_file = 'mbs_testmodule_604_verbose.json'
        resp_data = self.load_json_from_file(testmodule_file)
        get.return_value = MockResponse(resp_data, 200)

        mbs = MBS('http://mbs.example.com')
        self.assertFalse(mbs.module_has_requires(604, {'platform': 'f28'}))

    def test_get_modules(self):
        mbs_resp_data = self.load_json_from_file('test_get_modules_with_requires.json')
        mbs = MBS('http://mbs.example.com')

        # name, stream, requires, buildrequires, expected module build ids
        test_matrix = (
            ('testmodule', 'rhel-8.0', None, None, [604, 605]),
            ('testmodule', 'rhel-8.0', {'platform': 'el8'}, None, [604, 605]),
            ('testmodule', 'rhel-8.0', None, {'platform': 'el8'}, [604]),
            ('testmodule', 'rhel-8.0', {'platform': 'el8'}, {'platform': 'el8'}, [604]),
            ('testmodule', 'rhel-8.0', {'platform': 'f30'}, None, []),
            ('testmodule', 'rhel-8.0', {'platform': 'f30'}, {'platform': 'f30'}, []),
            ('testmodule', 'rhel-8.0', None, {'platform': 'f30'}, []),
        )

        for name, stream, requires, buildrequires, expected_build_ids in test_matrix:
            with mock.patch('ursa_major.mbs.requests.get') as get:
                get.return_value = MockResponse(mbs_resp_data, 200)

                module_builds = mbs.get_modules(
                    name=name,
                    stream=stream,
                    requires=requires,
                    buildrequires=buildrequires)

                params = {'name': name, 'stream': stream}
                if requires or buildrequires:
                    params['verbose'] = 'true'
                get.assert_called_once_with(mbs.module_builds_api_url, params=params)

                build_ids = sorted(build_info['id'] for build_info in module_builds)
                assert expected_build_ids == build_ids
