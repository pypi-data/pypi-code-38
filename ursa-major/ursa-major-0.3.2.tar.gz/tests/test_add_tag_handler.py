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

import json
import mock
import os
import shutil
import tempfile
from argparse import Namespace

from tests import UrsaMajorTestCase, MockResponse, make_mmd
from ursa_major import ModuleConfig, MBS_BUILD_STATES
from ursa_major.handlers.add_tag import ModuleInfo, AddTagHandler
from ursa_major.mbs import MBS


class AddTagHandlerTestCase(UrsaMajorTestCase):
    def setUp(self):

        config = mock.MagicMock()
        self.handler = AddTagHandler(config)

        self.tmpdir = tempfile.mkdtemp(suffix='_ursa_major_test')
        self.tag_config_file = os.path.join(self.tmpdir, 'default.json')
        with open(self.tag_config_file, 'w') as f:
            json.dump({}, f)

        self.set_args()

    def tearDown(self):
        try:
            shutil.rmtree(self.tmpdir)
        except:  # noqa
            pass

    def write_tag_config(self, content):
        """ Write content to tag config file.

        :param content: content in dict format
        """
        with open(self.tag_config_file, 'w') as f:
            json.dump(content, f, indent=2, sort_keys=True)

    def set_args(self, **kwargs):
        kwargs.setdefault('tag_config_file', self.tag_config_file)
        kwargs.setdefault('module_from_env', 'CI_MESSAGE')
        kwargs.setdefault('wait_regen_repo', False)
        kwargs.setdefault('send_mail', False)
        kwargs.setdefault('dry_run', False)
        args = Namespace()
        for k, v in kwargs.items():
            setattr(args, k, v)
        self.handler.set_args(args)


class TestAddTagHandler(AddTagHandlerTestCase):
    def setUp(self):
        super(TestAddTagHandler, self).setUp()
        fake_tag_config = {
            'rhel-8.0-build': {
                'owners': ['foo@example.com'],
                'modules': [
                    {'name': 'autotools', 'stream': 'rhel-8.0', 'priority': 10,
                     'requires': {'platform': 'rhel-8.0'}},
                    {'name': 'ant', 'stream': '1.10', 'priority': 20,
                     'requires': {'platform': 'rhel-8.0'}},
                ]
            },
            'other-8.0-tag': {
                'owners': ['bar@example.com'],
                'modules': [
                    {'name': 'autotools', 'stream': 'rhel-8.0', 'priority': 30,
                     'requires': {'platform': 'rhel-8.0'}}
                ]
            }
        }
        self.write_tag_config(fake_tag_config)

    @mock.patch('ursa_major.handlers.add_tag.log')
    @mock.patch('ursa_major.handlers.base.KojiService')
    def test_terminate_if_module_build_is_not_ready(self, KojiService, log):
        ci_message = json.dumps(dict(
            id=1,
            state=4,
            state_name='done',
        ))

        with mock.patch.dict(os.environ, {'CI_MESSAGE': ci_message}):
            self.handler.run()
        log.info.assert_any_call("MBS build state is not 'ready', skipping")

    def fake_get_inheritance_data(self, tag):
        mock_inheritance = {
            'rhel-8.0-build': [
                {'name': 'tag1'},
                {'name': 'module-908765'},  # Remove inheritance from this one.
            ],
            'other-8.0-tag': [
                {'name': 'tag7'}
            ],
        }
        return mock_inheritance[tag]

    @mock.patch('ursa_major.handlers.add_tag.MailAPI')
    @mock.patch('ursa_major.koji_service.koji')
    @mock.patch('ursa_major.koji_service.KojiService.update_tag_inheritance')
    def test_update_module_koji_tag(self, update_tag_inheritance, koji, mail_api):
        self.handler.connect_mbs = mock.MagicMock()
        self.handler._mbs = mock.MagicMock()
        self.handler.mbs.get_modules.return_value = [
            {'koji_tag': 'module-123456'},
            {'koji_tag': 'module-908765'},
        ]

        build_url = 'http://www.example.com/job/test/1'

        # Not going to test kerberos auth. Just make sure login successfully.
        koji.get_profile_module.return_value.config.authtype = 'kerberos'
        session = koji.ClientSession.return_value
        session.getInheritanceData.side_effect = self.fake_get_inheritance_data

        def fake_update_tag_inheritance(tag, add_tags=None, remove_tags=None):
            if tag == "rhel-8.0-build":
                return (['module-123456'], ['module-908765'])
            elif tag == "other-8.0-tag":
                return (['module-123456'], [])

        update_tag_inheritance.side_effect = fake_update_tag_inheritance

        self.handler._mbs.get_module_mmd.return_value = make_mmd(
            'autotools', 'rhel-8.0', '20180101', '123456',
            {'platform': ['rhel-8.0']})

        ci_message = json.dumps(dict(
            id=123,
            state=MBS_BUILD_STATES['ready'],
            state_name='ready',
            koji_tag='module-123456'
        ))

        mock_env = {'CI_MESSAGE': ci_message,
                    'BUILD_URL': 'http://www.example.com/job/test/1'}

        self.set_args(send_mail=True)

        with mock.patch.dict(os.environ, mock_env):
            self.handler.run()

        update_tag_inheritance.assert_has_calls([
            mock.call('rhel-8.0-build',
                      add_tags=[{'name': 'module-123456', 'priority': 10}],
                      remove_tags=[{'name': 'module-908765'}]),
            mock.call('other-8.0-tag',
                      add_tags=[{'name': 'module-123456', 'priority': 30}],
                      remove_tags=[]),
        ], any_order=True)

        rhel_80_build_data = {
            'removed_tags': ['module-908765'],
            'tag': 'rhel-8.0-build',
            'added_tags': ['module-123456'],
            'module': {
                'build_id': 123,
                'nsvc': 'autotools:rhel-8.0:20180101:123456',
                'koji_tag': 'module-123456',
                'requires': {'platform': ['rhel-8.0']},
            },
            'build_url': build_url,
        }

        other_80_tag_data = {
            'removed_tags': [],
            'tag': 'other-8.0-tag',
            'added_tags': ['module-123456'],
            'module': {
                'build_id': 123,
                'nsvc': 'autotools:rhel-8.0:20180101:123456',
                'koji_tag': 'module-123456',
                'requires': {'platform': ['rhel-8.0']},
            },
            'build_url': build_url,
        }

        self.handler.mail_api.send_mail.assert_called()
        self.assertEqual(u'test', 'test')
        self.handler.mail_api.send_mail.assert_has_calls(
            [mock.call('add-tag.txt',
                       ['foo@example.com'],
                       data=rhel_80_build_data,
                       subject='Tag rhel-8.0-build is updated'),
             mock.call('add-tag.txt',
                       ['bar@example.com'],
                       data=other_80_tag_data,
                       subject='Tag other-8.0-tag is updated')],
            any_order=True)

    @mock.patch('ursa_major.handlers.add_tag.log')
    def test_skip_module(self, log):
        ci_message = json.dumps(dict(
            id=123,
            state=MBS_BUILD_STATES['ready'],
            state_name='ready',
            koji_tag='module-d243299e85d7e9aa'
        ))
        mock_mbs = mock.MagicMock()
        fake_mmd = make_mmd("testmodule", "master", "20180101", "1234567")
        mock_mbs.get_module_mmd.return_value = fake_mmd
        self.handler.connect_koji = mock.MagicMock()
        self.handler.connect_mbs = mock.MagicMock()
        self.handler._mbs = mock_mbs
        self.handler.manage_tag_inheritance = mock.MagicMock()

        with mock.patch.dict(os.environ, {'CI_MESSAGE': ci_message}):
            self.handler.run()

        self.handler.manage_tag_inheritance.assert_not_called()

        # If module represented by the CI_MESSAGE does not match any
        # criteria, just logging to skip this module. There are at
        # least two logging.info calls in addition to log other
        # messages.
        self.assertGreaterEqual(log.info.call_count, 2)

    def assert_get_module_config(self, fake_configs, expected_result):
        message_file = "testmodule_with_requires_ready_message.json"
        message = self.load_json_from_file(message_file)
        mock_mbs = mock.MagicMock()
        fake_requires = {"platform": ["el8"]}
        fake_mmd = make_mmd("testmodule", "rhel-8.0",
                            "20180409051516", "9e5fe74b",
                            requires=fake_requires,
                            buildrequires=fake_requires)
        mock_mbs.get_module_mmd.return_value = fake_mmd
        modinfo = ModuleInfo.from_mbs_message(mock_mbs, message)
        matched_config = AddTagHandler.get_module_config(fake_configs, modinfo)
        self.assertEqual(matched_config, expected_result)

    def test_get_module_config_match_requires(self):
        # ((fake_module_configs, expected result), ...)
        test_matrix = (
            (
                [
                    {
                        'name': 'testmodule', 'stream': 'rhel-8.0', 'priority': 10,
                        'requires': {'platform': 'el8'}
                    },
                    # This noisy config should not impact to choose the correct one.
                    {
                        'name': 'testmodule2', 'stream': 'rhel-8.0', 'priority': 20,
                    }
                ],
                {
                    'name': 'testmodule', 'stream': 'rhel-8.0', 'priority': 10,
                    'requires': {'platform': 'el8'}
                },
            ),
            (
                [
                    # buildrequires could be specified in config as well.
                    {
                        'name': 'testmodule', 'stream': 'rhel-8.0', 'priority': 10,
                        'buildrequires': {'platform': 'el8'}
                    },
                ],
                {
                    'name': 'testmodule', 'stream': 'rhel-8.0', 'priority': 10,
                    'buildrequires': {'platform': 'el8'}
                },
            ),
            (
                [
                    # Both requires and buildrequires are specified to match the
                    # module metadata.
                    {
                        'name': 'testmodule', 'stream': 'rhel-8.0', 'priority': 10,
                        'requires': {'platform': 'el8'},
                        'buildrequires': {'platform': 'el8'},
                    },
                ],
                {
                    'name': 'testmodule', 'stream': 'rhel-8.0', 'priority': 10,
                    'requires': {'platform': 'el8'},
                    'buildrequires': {'platform': 'el8'},
                },
            ),
            # Either requires or buildrequires is not included in module metadata.
            (
                [
                    {
                        'name': 'testmodule', 'stream': 'rhel-8.0', 'priority': 10,
                        'requires': {'platform': 'f30'},
                    },
                ],
                None,
            ),
            (
                [
                    # Both requires and buildrequires are specified to match the
                    # module metadata.
                    {
                        'name': 'testmodule', 'stream': 'rhel-8.0', 'priority': 10,
                        'buildrequires': {'platform': 'f30'},
                    },
                ],
                None,
            ),
            (
                [
                    {
                        'name': 'testmodule', 'stream': 'rhel-8.0', 'priority': 10,
                        'requires': {'platform': 'f30'},
                        'buildrequires': {'platform': 'f30'},
                    },
                ],
                None,
            ),
            # Either name or stream is not matched module metadata.
            (
                # Module name is not matched in this config
                [{'name': 'module-xxxx', 'stream': 'rhel-8.0', 'priority': 20}],
                None,
            ),
            (
                # Module stream is not matched in this config
                [{'name': 'testmodule', 'stream': '100', 'priority': 20}],
                None,
            ),
            # Module name and stream are matched
            (
                [
                    {'name': 'testmodule', 'stream': 'rhel-8.0', 'priority': 20},
                    {'name': 'testmodule2', 'stream': 'rhel-8.0', 'priority': 20},
                ],
                {'name': 'testmodule', 'stream': 'rhel-8.0', 'priority': 20},
            ),
        )
        for config, expected_result in test_matrix:
            self.assert_get_module_config(config, expected_result)

    @mock.patch('ursa_major.mbs.requests.get')
    def test_add_module_to_tag(self, requests_get):
        self.handler._mbs = MBS('http://mbs.example.com')
        self.handler._koji = mock.MagicMock()

        modules_file = 'mbs_modules_testmodule_all_in_one_page.json'
        json_data = self.load_json_from_file(modules_file)
        resp = MockResponse(json_data, 200)
        requests_get.return_value = resp

        message = self.load_json_from_file("testmodule_ready_message.json")
        mock_mbs = mock.MagicMock()
        fake_requires = {"platform": ["el8"]}
        fake_mmd = make_mmd("testmodule", "rhel-8.0",
                            "20180409051516", "9e5fe74b",
                            requires=fake_requires)
        mock_mbs.get_module_mmd.return_value = fake_mmd
        modinfo = ModuleInfo.from_mbs_message(mock_mbs, message)

        inheritance_tags = [
            {'name': 'tmp-build'},
            {'name': 'tmp-build-override'},
            {'name': 'testmodule-234'},
            {'name': 'module-358b0c179d25310c'}
        ]

        self.handler._koji.get_inheritance_data.return_value = \
            inheritance_tags

        self.handler._koji.update_tag_inheritance.return_value = (
            ['module-0c8d21d5c89ec363'], ['module-358b0c179d25310c'])

        module_config = ModuleConfig({
            'name': 'testmodule', 'stream': 'rhel-8.0',
            'priority': 10
        })
        added_tags, removed_tags = self.handler.add_module_to_tag(
            'test-tag', modinfo, module_config)

        self.handler.koji.update_tag_inheritance.assert_called_with(
            'test-tag',
            add_tags=[{'priority': 10, 'name': u'module-0c8d21d5c89ec363'}],
            remove_tags=[{'name': 'module-358b0c179d25310c'}]
        )
        expected_added_tags = ['module-0c8d21d5c89ec363']
        expected_removed_tags = ['module-358b0c179d25310c']

        self.assertEqual(set(added_tags), set(expected_added_tags))
        self.assertEqual(set(removed_tags), set(expected_removed_tags))
        self.handler.koji.regen_repos.assert_called()
