# Copyright (c) 2018 Red Hat
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
from __future__ import absolute_import

import argparse
import io
import os
import subprocess
import sys

import tobiko
from tobiko.cmd import fixture as _fixture
from tobiko.tests.unit import test_fixture
from tobiko.tests import unit


MyFixture = test_fixture.MyFixture
MyFixture2 = test_fixture.MyFixture2
MyRequiredFixture = test_fixture.MyRequiredFixture
canonical_name = test_fixture.canonical_name


class ExitCalled(Exception):
    pass


class FixtureUtilTest(unit.TobikoUnitTest):

    command_name = 'tobiko-fixture'
    command_class = _fixture.FixtureUtil

    test_path = os.path.dirname(__file__)
    top_dir = os.path.dirname(os.path.dirname(tobiko.__file__))

    required_fixture = tobiko.required_fixture(MyRequiredFixture)

    def setUp(self):
        super(FixtureUtilTest, self).setUp()
        self.mock_error = self.patch(argparse.ArgumentParser, 'error',
                                     side_effect=self.fail)

    def patch_argv(self, subcommand=None, arguments=None,
                   config_file=None, repo_type=None, repo_url=None,
                   test_path=None, top_dir=None, group_regex=None,
                   blacklist_file=None, whitelist_file=None,
                   black_regex=None, filters=None):
        subcommand = subcommand or 'list'
        arguments = list(arguments or [])
        if config_file:
            arguments += ['--config', config_file]
        if repo_type:
            arguments += ['--repo-type', repo_type]
        if repo_url:
            arguments += ['--repo-url', repo_url]
        if test_path:
            arguments += ['--test-path', test_path]
        if top_dir:
            arguments += ['--top-dir', top_dir]
        if group_regex:
            arguments += ['--group-regex', group_regex]
        if blacklist_file:
            arguments += ['--blacklist-file', blacklist_file]
        if whitelist_file:
            arguments += ['--whitelist-file', whitelist_file]
        if black_regex:
            arguments += ['--black-regex', black_regex]
        if filters:
            arguments += list(filters)
        return self.patch(sys, 'argv',
                          [self.command_name, subcommand] + arguments)

    def test_init(self, subcommand=None, arguments=None, filters=None,
                  config_file=None, repo_type=None,
                  repo_url=None, test_path=None, top_dir=None,
                  group_regex=None, blacklist_file=None,
                  whitelist_file=None, black_regex=None):
        self.patch_argv(subcommand=subcommand, arguments=arguments)
        command = self.command_class()
        self.mock_error.assert_not_called()
        args = command.args
        self.assertIsNotNone(args)
        self.assertEqual(filters or [], args.filters)
        self.assertEqual(config_file or '.stestr.conf', args.config)
        self.assertEqual(subcommand or 'list', args.subcommand)
        self.assertEqual(repo_type or 'file', args.repo_type)
        self.assertEqual(repo_url, args.repo_url)
        self.assertEqual(test_path, args.test_path)
        self.assertEqual(top_dir, args.top_dir)
        self.assertEqual(group_regex, args.group_regex)
        self.assertEqual(blacklist_file, args.blacklist_file)
        self.assertEqual(whitelist_file, whitelist_file)
        self.assertEqual(black_regex, args.black_regex)

    def test_init_with_list(self):
        self.test_init(subcommand='list')

    def test_init_with_seutp(self):
        self.test_init(subcommand='setup')

    def test_init_with_cleanup(self):
        self.test_init(subcommand='cleanup')

    def test_init_with_c(self):
        self.test_init(arguments=['-c', 'some-config-file'],
                       config_file='some-config-file')

    def test_init_with_config(self):
        self.test_init(arguments=['--config', 'some-config-file'],
                       config_file='some-config-file')

    def test_init_with_r(self):
        self.test_init(arguments=['-r', 'file'], repo_type='file')

    def test_init_with_repo_type_file(self):
        self.test_init(arguments=['--repo-type', 'file'], repo_type='file')

    def test_init_with_repo_type_sql(self):
        self.assertRaises(self.failureException, self.test_init,
                          arguments=['--repo-type', 'sql'])

    def test_init_with_u(self):
        self.test_init(arguments=['-u', 'some-url'], repo_url='some-url')

    def test_init_with_repo_url(self):
        self.test_init(arguments=['--repo-url', 'some-url'],
                       repo_url='some-url')

    def test_init_with_filters(self):
        self.test_init(arguments=['a', 'b', 'c'], filters=['a', 'b', 'c'])

    def test_init_with_t(self):
        self.test_init(arguments=['-t', 'some/test/path'],
                       test_path='some/test/path')

    def test_init_with_test_path(self):
        self.test_init(arguments=['--test-path', 'some/test/path'],
                       test_path='some/test/path')

    def test_init_with_top_dir(self):
        self.test_init(arguments=['--top-dir', 'some/top/dir'],
                       top_dir='some/top/dir')

    def test_init_with_g(self):
        self.test_init(arguments=['-g', 'some-regex'],
                       group_regex='some-regex')

    def test_init_with_group_regex(self):
        self.test_init(arguments=['--group-regex', 'some-regex'],
                       group_regex='some-regex')

    def test_init_with_group_regex2(self):
        self.test_init(arguments=['--group_regex', 'some-regex'],
                       group_regex='some-regex')

    def test_init_with_b(self):
        self.test_init(arguments=['-b', 'some/blacklist-file'],
                       blacklist_file='some/blacklist-file')

    def test_init_with_blacklist_file(self):
        self.test_init(arguments=['--blacklist-file', 'some/blacklist-file'],
                       blacklist_file='some/blacklist-file')

    def test_init_with_w(self):
        self.test_init(arguments=['-w', 'some/whitelist-file'],
                       whitelist_file='some/whitelist-file')

    def test_init_with_whitelist_file(self):
        self.test_init(arguments=['--whitelist-file', 'some/whitelist-file'],
                       whitelist_file='some/whitelist-file')

    def test_init_with_B(self):
        self.test_init(arguments=['-B', 'some-black-regex'],
                       black_regex='some-black-regex')

    def test_init_with_blacklist_regex(self):
        self.test_init(arguments=['--black-regex', 'some-black-regex'],
                       black_regex='some-black-regex')

    def test_main(self, subcommand=None, config_file=None, repo_type=None,
                  repo_url=None, test_path=None, top_dir=None,
                  group_regex=None, blacklist_file=None, whitelist_file=None,
                  black_regex=None, filters=None):
        test_path = test_path or self.test_path
        top_dir = top_dir or self.top_dir
        self.setup_file_repo(top_dir=top_dir)
        self.patch_argv(subcommand=subcommand, config_file=config_file,
                        repo_type=repo_type, repo_url=repo_url,
                        test_path=test_path, top_dir=top_dir,
                        group_regex=group_regex,
                        blacklist_file=blacklist_file,
                        whitelist_file=whitelist_file,
                        black_regex=black_regex, filters=filters)
        stdout = self.patch(sys, 'stdout', io.StringIO())
        _fixture.main()
        self.mock_error.assert_not_called()
        return stdout

    def test_list(self, fixture1=MyFixture, fixture2=MyFixture2):
        stdout = self.test_main(subcommand='list')
        written_lines = stdout.getvalue().splitlines()
        self.assertIn(canonical_name(fixture1), written_lines)
        self.assertIn(canonical_name(fixture2), written_lines)
        self.assertIn(canonical_name(MyRequiredFixture),
                      written_lines)

    def test_list_with_filters(self, fixture=MyFixture):
        stdout = self.test_main(subcommand='list', filters=[self.id()])
        written_lines = stdout.getvalue().splitlines()
        self.assertEqual([canonical_name(fixture),
                          canonical_name(MyRequiredFixture)],
                         written_lines)
        self.assertIn(canonical_name(MyRequiredFixture),
                      written_lines)

    def test_setup(self, fixture=MyFixture, fixture2=MyFixture2):
        stdout = self.test_main(subcommand='setup')
        written_lines = stdout.getvalue().splitlines()
        for obj in [fixture, fixture2, MyRequiredFixture]:
            self.assertIn(canonical_name(obj), written_lines)
            tobiko.get_fixture(obj).setup_fixture.assert_called_once_with()
            tobiko.get_fixture(obj).cleanup_fixture.assert_not_called()

    def test_setup_with_filters(self, fixture=MyFixture):
        stdout = self.test_main(subcommand='setup', filters=[self.id()])
        written_lines = stdout.getvalue().splitlines()
        self.assertEqual([canonical_name(fixture),
                          canonical_name(MyRequiredFixture)],
                         written_lines)
        for obj in [fixture, MyRequiredFixture]:
            tobiko.get_fixture(obj).setup_fixture.assert_called_once_with()
            tobiko.get_fixture(obj).cleanup_fixture.assert_not_called()

    def test_cleanup(self, fixture=MyFixture, fixture2=MyFixture2):
        stdout = self.test_main(subcommand='cleanup')
        written_lines = stdout.getvalue().splitlines()
        for obj in [fixture, fixture2, MyRequiredFixture]:
            self.assertIn(canonical_name(obj), written_lines)
            tobiko.get_fixture(obj).setup_fixture.assert_not_called()
            tobiko.get_fixture(obj).cleanup_fixture.assert_called_once_with()

    def test_cleanup_with_filters(self, fixture=MyFixture):
        stdout = self.test_main(subcommand='cleanup', filters=[self.id()])
        written_lines = stdout.getvalue().splitlines()
        self.assertEqual([canonical_name(fixture),
                          canonical_name(MyRequiredFixture)],
                         written_lines)
        for obj in [fixture, MyRequiredFixture]:
            tobiko.get_fixture(obj).setup_fixture.assert_not_called()
            tobiko.get_fixture(obj).cleanup_fixture.assert_called_once_with()

    def setup_file_repo(self, top_dir):
        if not os.path.isdir(os.path.join(top_dir, '.stestr')):
            command = ['stestr', '--top-dir', top_dir, 'init']
            subprocess.check_call(command)
