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
import tempfile

from mock import patch, Mock
from ursa_major.cli import main
from tests import TEST_DATA_DIR, MockMBSBuildsData, make_mmd


class TestRemoveModule:
    """Test CLI command remove-module"""

    def setup_method(self, method):
        fd, self.tag_config_file = tempfile.mkstemp()
        os.close(fd)

    def teardown_method(self, method):
        os.unlink(self.tag_config_file)

    def write_tag_config_file(self, content):
        with open(self.tag_config_file, 'w') as f:
            json.dump(content, f)

    def run_cli(self, options):
        config_file = os.path.join(TEST_DATA_DIR, 'ursa-major-test.conf')
        cli_cmd = ['ursa-major', 'remove-module', '--config', config_file] + options

        with patch('sys.argv', new=cli_cmd):
            main()

    @patch('koji.ClientSession')
    @patch('ursa_major.mbs.requests.get')
    def test_module_koji_tag_isnt_present_in_tag_inheritance(self, get, ClientSession):
        session = ClientSession.return_value
        session.getInheritanceData.return_value = [
            {'name': 'module-ant-123'},
            {'name': 'module-java-456'},
        ]

        get.return_value = Mock(status_code=200)
        get.return_value.json.return_value = {
            'items': [
                {
                    # This koji_tag is not present in the tag inheritance, so
                    # no tag is going to be removed.
                    'koji_tag': 'module-python-3.6',
                    'modulemd': make_mmd(name='mariadb', stream='10.4',
                                         version='3020190313091759', context='a5b0195c',
                                         requires={'platform': 'f30'},
                                         buildrequires={'platform': 'f30'}).dumps(),
                },
            ],
            'meta': {
                'prev': None,
                'last': None,
                'next': None,
                'total': 1,
                'per_page': 10,
                'first': 'https://mbs.example.com/module-build-service/1/module-builds/'
                         '?per_page=10&page=1&name=testmodule',
                'pages': 1,
                'page': 1
            }
        }

        # Write empty tag config file because we do not want to test if the tag
        # config file is written.
        self.write_tag_config_file({})

        self.run_cli([
            '--name', 'python', '--stream', '3.6', '--tag', 'f30-build',
            '--tag-config-file', self.tag_config_file
        ])

        session.setInheritanceData.assert_not_called()

    @patch('koji.ClientSession')
    @patch('ursa_major.mbs.requests.get')
    def remove_module(self, not_update_file, get, ClientSession):
        session = ClientSession.return_value
        session.getInheritanceData.return_value = [
            {'parent_id': 20,
             'name': 'module-ant-1.10-20181122140939-819b5873'},
            {'parent_id': 100,
             'name': 'module-mariadb-10.4-3020190304180835-a5b0195c'},
        ]
        session.getTag.return_value = {
            'id': 100,
            'name': 'module-mariadb-10.4-3020190304180835-a5b0195c',
        }

        mock_builds = [
            {
                'koji_tag': 'module-mariadb-10.4-3020190313091759-a5b0195c',
                'modulemd': make_mmd(name='mariadb', stream='10.4',
                                     version='3020190313091759', context='a5b0195c',
                                     requires={'platform': 'f30'},
                                     buildrequires={'platform': 'f30'}).dumps(),
            },
            {
                # This koji_tag is present in the inheritance, so it should be removed.
                'koji_tag': 'module-mariadb-10.4-3020190304180835-a5b0195c',
                'modulemd': make_mmd(name='mariadb', stream='10.4',
                                     version='3020190304180835', context='a5b0195c',
                                     requires={'platform': 'f30'},
                                     buildrequires={'platform': 'f30'}).dumps(),
            }
        ]
        mock_mbs_builds_data = MockMBSBuildsData(mock_builds)
        get.side_effect = mock_mbs_builds_data.get

        cmd = [
            '--name', 'mariadb', '--stream', '10.4',
            '--require', 'platform:f30', '--buildrequire', 'platform:f30',
            '--tag', 'f30-build',
            '--tag-config-file', self.tag_config_file
        ]
        if not_update_file:
            cmd.append('--not-update-config')

        self.run_cli(cmd)

        data = session.getInheritanceData.return_value[:]
        data[-1]['delete link'] = True
        session.setInheritanceData.assert_called_once_with('f30-build', data)

    def test_remove_module_and_remove_module_config_from_tag_configs(self):
        fake_tag_configs = {
            'f30-build': {
                'modules': [
                    {
                        'name': 'mariadb',
                        'stream': '10.4',
                        'requires': {'platform': 'f30'},
                        'buildrequires': {'platform': 'f30'},
                    }
                ],
                'owners': ['someone@example.com']
            }
        }
        self.write_tag_config_file(fake_tag_configs)

        self.remove_module(False)

        with open(self.tag_config_file, 'r') as f:
            tag_configs = json.load(f)

        mariadb_module_config = fake_tag_configs['f30-build']['modules'][0]
        assert mariadb_module_config not in tag_configs['f30-build']['modules']

    def test_remove_module_and_not_remove_module_config_from_tag_configs(self):
        fake_tag_configs = {
            'f30-build': {
                'modules': [
                    {
                        'name': 'mariadb',
                        'stream': '10.4',
                        'requires': {'platform': 'f30'},
                        'buildrequires': {'platform': 'f30'},
                    }
                ],
                'owners': ['someone@example.com']
            }
        }
        self.write_tag_config_file(fake_tag_configs)

        self.remove_module(True)

        with open(self.tag_config_file, 'r') as f:
            tag_configs = json.load(f)

        mariadb_module_config = fake_tag_configs['f30-build']['modules'][0]
        assert mariadb_module_config in tag_configs['f30-build']['modules']

    def test_specified_module_isnt_present_in_module_config_file(self):
        # remove_module removes mariadb, but tag config file only contains ant-1.10
        fake_tag_configs = {
            'f30-build': {
                'modules': [
                    {
                        'name': 'ant',
                        'stream': '1.10',
                        'requires': {'platform': 'f30'},
                        'buildrequires': {'platform': 'f30'},
                    }
                ],
                'owners': ['someone@example.com']
            }
        }
        self.write_tag_config_file(fake_tag_configs)

        self.remove_module(False)

        with open(self.tag_config_file, 'r') as f:
            tag_configs = json.load(f)

        expected = fake_tag_configs['f30-build']['modules']
        assert expected == tag_configs['f30-build']['modules']
