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
import pytest

from mock import patch
from tests import TEST_DATA_DIR, MockMBSBuildsData, make_mmd, URSA_MAJOR_TEST_CONFIG
from ursa_major import ModuleConfig
from ursa_major.cli import main
from ursa_major.handlers.add_module import AddModuleHandler


def get_tag_side_effect(info):
    return {
        'f30-build': {'id': 99, 'name': 'f30-build'},
        'module-mariadb-10.4-3020190313091759-a5b0195c': {
            'id': 100,
            'name': 'module-mariadb-10.4-3020190313091759-a5b0195c',
        },
        'module-mariadb-10.4-3020190304180835-a5b0195c': {
            'id': 101,
            'name': 'module-mariadb-10.4-3020190304180835-a5b0195c',
        },
    }[info]


class TestAddModule:

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
        self.ClientSession_patcher.stop()

        os.unlink(self.tag_config_file)

    def write_tag_config_file(self, content):
        with open(self.tag_config_file, 'w') as f:
            json.dump(content, f)

    def read_tag_config_file(self):
        with open(self.tag_config_file, 'r') as f:
            return json.load(f)

    def add_module(self,
                   command_options=None,
                   tag_configs_content=None,
                   update_inheritance_only=None,
                   update_tag_config_only=None,
                   mock_inheritance_data=None,
                   mock_mbs_modules=None):
        """
        Run add-module command for test. Behavior could be changed by arguments
        for specific tests.
        """
        self.koji_session.getInheritanceData.return_value = mock_inheritance_data or [
            {'parent_id': 20,
             'name': 'module-ant-1.10-20181122140939-819b5873',
             'priority': 10},
        ]
        self.koji_session.getTag.side_effect = get_tag_side_effect

        mock_builds = mock_mbs_modules or [
            {
                'koji_tag': 'module-mariadb-10.4-3020190313091759-a5b0195c',
                'modulemd': make_mmd(name='mariadb', stream='10.4',
                                     version='3020190313091759', context='a5b0195c',
                                     requires={'platform': 'f30'},
                                     buildrequires={'platform': 'f30'}).dumps(),
            },
            {
                'koji_tag': 'module-mariadb-10.4-3020190304180835-a5b0195c',
                'modulemd': make_mmd(name='mariadb', stream='10.4',
                                     version='3020190304180835', context='a5b0195c',
                                     requires={'platform': 'f30'},
                                     buildrequires={'platform': 'f30'}).dumps(),
            },
        ]
        mock_builds_data = MockMBSBuildsData(mock_builds)

        self.mock_get.side_effect = mock_builds_data.get

        # For this test, we write an empty tag config file.
        self.write_tag_config_file(tag_configs_content or {})

        cli_cmd_options = command_options or [
            '--name', 'mariadb', '--stream', '10.4', '--priority', '50',
            '--require', 'platform:f30',
            '--buildrequire', 'platform:f30',
            '--tag', 'f30-build',
            '--tag-config-file', self.tag_config_file
        ]
        if update_inheritance_only:
            cli_cmd_options.append('--update-inheritance-only')
        if update_tag_config_only:
            cli_cmd_options.append('--update-config-only')

        config_file = os.path.join(TEST_DATA_DIR, 'ursa-major-test.conf')
        cli_cmd = ['ursa-major', 'add-module', '--config', config_file] + cli_cmd_options

        with patch('sys.argv', new=cli_cmd):
            main()

    def test_common_add_module(self):
        """Test add a module to tag config file and its koji_tag to tag inheritance"""
        self.add_module()

        self.koji_session.setInheritanceData.assert_called_once_with(99, [
            {
                'parent_id': 20,
                'name': 'module-ant-1.10-20181122140939-819b5873',
                'priority': 10
            },
            {
                'child_id': 99,
                'parent_id': 100,
                'name': "module-mariadb-10.4-3020190313091759-a5b0195c",
                'priority': 50,
                'maxdepth': None,
                'intransitive': False,
                'noconfig': False,
                'pkg_filter': ''
            },
        ])

        expected = [{
            'name': 'mariadb',
            'stream': '10.4',
            'requires': {'platform': 'f30'},
            'buildrequires': {'platform': 'f30'},
            'priority': 50
        }]
        tag_configs = self.read_tag_config_file()
        assert expected == tag_configs['f30-build']['modules']

    def test_add_module_koji_tag_only(self):
        self.add_module(tag_configs_content={},
                        update_inheritance_only=True)

        self.koji_session.setInheritanceData.assert_called_once_with(99, [
            {
                'parent_id': 20,
                'name': 'module-ant-1.10-20181122140939-819b5873',
                'priority': 10
            },
            {
                'child_id': 99,
                'name': 'module-mariadb-10.4-3020190313091759-a5b0195c',
                'parent_id': 100,
                'priority': 50,
                'maxdepth': None,
                'intransitive': False,
                'noconfig': False,
                'pkg_filter': ''
            },
        ])

        tag_configs = self.read_tag_config_file()
        assert {} == tag_configs, 'Tag config file should keep unchanged.'

    def test_add_module_but_only_update_tag_config_file(self):
        self.add_module(tag_configs_content={},
                        update_tag_config_only=True)

        self.koji_session.setInheritanceData.assert_not_called()

        expected = [{
            'name': 'mariadb',
            'stream': '10.4',
            'requires': {'platform': 'f30'},
            'buildrequires': {'platform': 'f30'},
            'priority': 50
        }]

        tag_configs = self.read_tag_config_file()
        assert expected == tag_configs['f30-build']['modules']

    @patch('ursa_major.handlers.add_module.AddModuleHandler.write_tag_config')
    def test_specified_same_module_config(
            self, write_tag_config):
        """
        Both tag inheritance and tag config file are not updated because same
        module metadata is specified from command line.
        """
        self.add_module(tag_configs_content={
            'f30-build': {
                'modules': [
                    # Compare with the metadata specified from command line,
                    # all of them are same.
                    {
                        'name': 'mariadb',
                        'stream': '10.4',
                        'requires': {'platform': 'f30'},
                        'buildrequires': {'platform': 'f30'},
                        'priority': 50,
                    }
                ],
                'owners': ['owner@example.com']
            }
        })

        self.koji_session.setInheritanceData.assert_not_called()
        write_tag_config.assert_not_called()

    def test_remove_old_koji_tag_and_add_latest_koji_tag_to_inheritance(self):
        self.add_module(mock_inheritance_data=[
            # Noisy koji_tag, which should not be changed.
            {
                'parent_id': 5,
                'name': 'module-ant-1.10-20181122140939-819b5873',
                'priority': 2,
            },
            # This tag will be removed because this old koji_tag exists in the modules
            # returned from MBS.
            {
                'parent_id': 101,
                'name': 'module-mariadb-10.4-3020190304180835-a5b0195c',
                'priority': 10,
            },
        ])

        self.koji_session.setInheritanceData.assert_called_once_with(99, [
            {
                'parent_id': 5,
                'name': 'module-ant-1.10-20181122140939-819b5873',
                'priority': 2,
            },
            {
                'parent_id': 101,
                'name': 'module-mariadb-10.4-3020190304180835-a5b0195c',
                'priority': 10,
                'delete link': True,
            },
            {
                'child_id': 99,
                'parent_id': 100,
                'name': 'module-mariadb-10.4-3020190313091759-a5b0195c',
                'priority': 50,
                'maxdepth': None,
                'intransitive': False,
                'noconfig': False,
                'pkg_filter': ''
            },
        ])

    def test_add_module_with_buildrequires(self):
        """
        Add a module with buildrequires specified from command line but no
        buildrequires was specified before and the corresponding module config
        does not have buildrequires in tag config file.

        The expected result is to remove the koij_tag of the exisitng module
        within tag config file, and find latest module with the specified
        buildrequires by CLI option --buildrequires, and add its koji_tag to
        tag inheritance eventually.
        """
        self.add_module(
            mock_inheritance_data=[
                # Noisy tag in inheritance which should not be changed.
                {
                    'parent_id': 20,
                    'name': 'module-ant-1.10-20181122140939-819b5873',
                    'priority': 10,
                },
                # The is is the koji_tag that was added when buildrequires is
                # not specified in tag config. So, it will be removed and
                # koji_tag of latest mariadb:10.4 will be added to tag
                # inheritance.
                {
                    'parent_id': 101,
                    'name': 'module-mariadb-10.4-3020190304180835-a5b0195c',
                    'priority': 20,
                },
            ],
            tag_configs_content={
                'f30-build': {
                    'modules': [
                        # Compare with the metadata specified from command line,
                        # all of them are same.
                        {
                            'name': 'mariadb',
                            'stream': '10.4',
                            'requires': {'platform': 'f30'},
                            'priority': 50,
                            # Note that, this module was added without
                            # specifying buildrequires, whereas it is given by
                            # option --buildrequire from command line. This is
                            # just the difference.
                        }
                    ],
                    'owners': ['owner@example.com']
                }
            },
        )

        self.koji_session.setInheritanceData.assert_called_once_with(99, [
            {
                'parent_id': 20,
                'name': 'module-ant-1.10-20181122140939-819b5873',
                'priority': 10,
            },
            {
                'parent_id': 101,
                'name': 'module-mariadb-10.4-3020190304180835-a5b0195c',
                'priority': 20,
                'delete link': True,
            },
            # This is the koji_tag of the latest module mariadb:10.4 to add
            {
                'child_id': 99,
                'parent_id': 100,
                'name': 'module-mariadb-10.4-3020190313091759-a5b0195c',
                'priority': 50,
                'maxdepth': None,
                'intransitive': False,
                'noconfig': False,
                'pkg_filter': ''
            },
        ])

        expected = {
            'f30-build': {
                'modules': [
                    {
                        'name': 'mariadb',
                        'stream': '10.4',
                        'requires': {'platform': 'f30'},
                        'buildrequires': {'platform': 'f30'},
                        'priority': 50,
                    }
                ],
                'owners': ['owner@example.com']
            }
        }
        assert expected == self.read_tag_config_file()


class TestAddModuleFunctions:

    # NOTE: once MBS supports filtering modules builds by requires or
    # buildrequires, the test data should be updated because it is unnecessary
    # to filter module builds locally by Ursa-Major itself.

    @pytest.mark.parametrize(
        'module_config,module_builds,expected_koji_tags', [
            # None of these koji_tags exist in tag inheritance.
            (ModuleConfig({'name': 'mariadb', 'stream': '10.3',
                           'version': '3120190304180825', 'context': 'f636be4b'}),
             [{'id': 1,
               'name': 'mariadb',
               'koji_tag': 'module-mariadb-10.3-3020190301191548-a5b0195c'},
              {'id': 2,
               'name': 'mariadb',
               'koji_tag': 'module-mariadb-10.3-3120190304180825-f636be4b'}],
             []),

            # koji_tag exists in tag inheritance
            (ModuleConfig({'name': 'mariadb', 'stream': '10.4',
                           'version': '3120190304180825', 'context': 'f636be4b'}),
             [{'id': 1,
               'name': 'mariadb',
               'koji_tag': 'module-mariadb-10.4-3020190313091759-a5b0195c'},
              {'id': 2,
               'name': 'mariadb',
               # This older koji_tag was added previously
               'koji_tag': 'module-mariadb-10.4-3020190304180835-a5b0195c'}],
             ['module-mariadb-10.4-3020190304180835-a5b0195c']),

            # Modules are filtered by requires.
            # None of these koji_tags exist in tag inheritance.
            (ModuleConfig({'name': 'mariadb', 'stream': '10.3',
                           'version': '3120190304180825', 'context': 'f636be4b',
                           'requires': {'platform': 'f30'}}),
             [{'id': 1,
               'name': 'mariadb',
               'koji_tag': 'module-mariadb-10.3-3020190301191548-a5b0195c',
               'modulemd': make_mmd(name='mariadb', stream='10.3',
                                    version='3020190301191548', context='a5b0195c',
                                    requires={'platform': 'f30'},
                                    buildrequires={'platform': 'f30'}).dumps(),
               },
              {'id': 2,
               'name': 'mariadb',
               'koji_tag': 'module-mariadb-10.3-3120190304180825-f636be4b',
               'modulemd': make_mmd(name='mariadb', stream='10.3',
                                    version='3120190304180825', context='f636be4b',
                                    requires={'platform': 'f29'},
                                    buildrequires={'platform': 'f29'}).dumps(),
               }],
             []),

            # koji_tag exists in tag inheritance and module builds
            (ModuleConfig({'name': 'mariadb', 'stream': '10.4',
                           'version': '3120190304180825', 'context': 'f636be4b',
                           'requires': {'platform': 'f30'},
                           'buildrequires': {'platform': 'f30'}}),
             [{'id': 1,
               'name': 'mariadb',
               'koji_tag': 'module-mariadb-10.4-3020190313091759-a5b0195c',
               'modulemd': make_mmd(name='mariadb', stream='10.4',
                                    version='3020190313091759', context='a5b0195c',
                                    requires={'platform': 'f29'},
                                    buildrequires={'platform': 'f29'}).dumps(),
               },
              {'id': 2,
               'name': 'mariadb',
               # This is the koji_tag for platform:f30
               'koji_tag': 'module-mariadb-10.4-3020190304180835-a5b0195c',
               'modulemd': make_mmd(name='mariadb', stream='10.4',
                                    version='3020190304180835', context='a5b0195c',
                                    requires={'platform': 'f30'},
                                    buildrequires={'platform': 'f30'}).dumps(),
               }],
             ['module-mariadb-10.4-3020190304180835-a5b0195c']),

            # filter with requires/buildrequires, it won't filter out mariadb:10.4 modules
            (ModuleConfig({'name': 'mariadb', 'stream': '10.4',
                           'version': '3120190304180825', 'context': 'f636be4b',
                           'requires': {'platform': 'f30'},
                           'buildrequires': {'platform': 'f30'}}),
             [{'id': 1,
               'name': 'mariadb',
               'koji_tag': 'module-mariadb-10.4-3020190313091759-a5b0195c',
               'modulemd': make_mmd(name='mariadb', stream='10.4',
                                    version='3020190313091759', context='a5b0195c',
                                    requires={'platform': 'f29'},
                                    buildrequires={'platform': 'f29'}).dumps(),
               },
              # Although this koji_tag was added to tag inheritance, but no
              # koji_tag is found that matches platform:f30.
              {'id': 2,
               'name': 'mariadb',
               'koji_tag': 'module-mariadb-10.4-3020190304180835-a5b0195c',
               'modulemd': make_mmd(name='mariadb', stream='10.4',
                                    version='3020190304180835', context='a5b0195c',
                                    requires={'platform': 'f28'},
                                    buildrequires={'platform': 'f28'}).dumps(),
               }],
             ['module-mariadb-10.4-3020190304180835-a5b0195c']),
        ])
    @patch('ursa_major.koji_service.koji')
    @patch('requests.get')
    def test_find_module_tags_from_koji_inheritance(
            self, get, koji, module_config, module_builds, expected_koji_tags):
        koji_session = koji.ClientSession.return_value
        koji_session.getInheritanceData.return_value = [
            {'parent_id': 100,
             'name': 'module-ant-1.10-20181122140939-819b5873'},
            {'parent_id': 101,
             'name': 'module-hyperfine-latest-3120190318171218-f636be4b'},
            {'parent_id': 102,
             'name': 'module-exa-latest-2820190316115637-8de94f32'},
            {'parent_id': 103,
             'name': 'module-mariadb-10.4-3020190304180835-a5b0195c'},
        ]

        mock_mbs_builds_data = MockMBSBuildsData(module_builds)
        get.side_effect = mock_mbs_builds_data.get

        handler = AddModuleHandler(config=URSA_MAJOR_TEST_CONFIG)
        handler.connect_koji()
        handler.connect_mbs()
        found_koji_tags = handler.find_module_tags_from_koji_inheritance(
            'f30-build', module_config)
        assert expected_koji_tags == found_koji_tags
