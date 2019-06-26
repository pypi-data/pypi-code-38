# -*- coding: utf-8 -*-
# Copyright (c) 2019  Red Hat, Inc.
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
import os
import pytest
import tempfile

from mock import call, patch
from tests import TEST_DATA_DIR, MockMBSBuildsData, make_mmd
from ursa_major.cli import main


class TestCheckConfig:

    def setup_method(self, method):
        fd, self.tag_config_file = tempfile.mkstemp()
        os.close(fd)

        self.ClientSession_patcher = patch('koji.ClientSession')
        self.mock_ClientSession = self.ClientSession_patcher.start()
        self.koji_session = self.mock_ClientSession.return_value

        self.get_patcher = patch('requests.get')
        self.mock_get = self.get_patcher.start()

    def teardown_method(self, method):
        self.get_patcher.stop()
        os.unlink(self.tag_config_file)

    def write_tag_config_file(self, content):
        with open(self.tag_config_file, 'w') as f:
            json.dump(content, f)

    def check_config(self):
        config_file = os.path.join(TEST_DATA_DIR, 'ursa-major-test.conf')
        cli_cmd = [
            'ursa-major', 'check-config',
            '--config', config_file,
            '--tag-config-file', self.tag_config_file
        ]

        with patch('sys.argv', new=cli_cmd):
            main()

    @pytest.mark.parametrize('modules,error_log', [
        ([
            [{'name': 'mariadb'}],
            'Missing stream in module config: {}'.format({u'name': u'mariadb'})
        ]),
        ([
            [{'stream': '10.4', 'priority': 10}],
            'Missing name in module config: {}'.format(
                {u'stream': u'10.4', u'priority': 10})
        ]),
        ([
            [{'name': 'mariadb', 'stream': '10.4'}],
            'Missing priority in module config: {}'.format(
                {u'name': u'mariadb', u'stream': u'10.4'})
        ]),
    ])
    def test_missing_mandatory_fields(self, modules, error_log):
        self.write_tag_config_file({
            'f30-build': {
                'modules': modules,
                'owners': ['owner@example.com']
            }
        })

        self.koji_session.getInheritanceData.return_value = [
            {
                'parent': 10,
                'name': 'module-ant-1.10-20181122140939-819b5873',
                'priority': 10
            }
        ]

        with patch('ursa_major.handlers.check_config.log') as log:
            # This is only for making the program terminate and raise SystemExit
            log.error.counter = 3

            with pytest.raises(SystemExit):
                self.check_config()

            log.error.assert_has_calls([call(error_log)])

    def test_show_error_if_cannot_get_tag_inheritance_data(self):
        self.write_tag_config_file({
            'f30-build': {
                'modules': [],
                'owners': ['owner@example.com']
            }
        })

        # This test requires an error raised from Koji API getInheritanceData
        # So, just raise any error
        self.koji_session.getInheritanceData.side_effect = ValueError

        with patch('ursa_major.handlers.check_config.log') as log:
            # This is only for making the program terminate and raise SystemExit
            log.error.counter = 3

            with pytest.raises(SystemExit):
                self.check_config()

            log.error.assert_has_calls([
                call('Unable to get inheritance data of tag %s: %s', u'f30-build', '')
            ], any_order=True)

    def test_verify_valid_module_config(self):
        self.write_tag_config_file({
            'f30-build': {
                'modules': [
                    {
                        'name': 'mariadb', 'stream': '10.4', 'priority': 30,
                        'requires': {'platform': 'f30'},
                        'buildrequires': {'platform': 'f30'}
                    },
                    {'name': 'ffsend', 'stream': 'latest', 'priority': 40},
                ],
                'owners': ['owner@example.com']
            }
        })

        mock_builds = [
            {
                'id': 3617,
                'name': 'mariadb',
                'koji_tag': 'module-mariadb-10.4-3020190313091759-a5b0195c',
                'modulemd': make_mmd(name='mariadb', stream='10.4',
                                     version='3020190313091759', context='a5b0195c',
                                     requires={'platform': 'f30'},
                                     buildrequires={'platform': 'f30'}).dumps(),
            },
            {
                'id': 3640,
                'name': 'ffsend',
                'koji_tag': 'module-ffsend-latest-3020190316024948-a5b0195c',
                'modulemd': make_mmd(name='mariadb', stream='10.4',
                                     version='3020190316024948', context='a5b0195c',
                                     requires={'platform': 'f30'},
                                     buildrequires={'platform': 'f30'}).dumps(),
            }
        ]

        mock_mbs_builds_data = MockMBSBuildsData(mock_builds)
        self.mock_get.side_effect = mock_mbs_builds_data.get

        self.koji_session.getInheritanceData.return_value = [
            {
                'parent': 10,
                'name': 'module-ant-1.10-20181122140939-819b5873',
                'priority': 10
            }
        ]

        with patch('ursa_major.handlers.check_config.log') as log:
            # This is only for making the program terminate normally
            log.error.counter = 0

            self.check_config()
            log.error.assert_not_called()
