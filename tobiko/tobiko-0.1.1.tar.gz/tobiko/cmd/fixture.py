# Copyright 2018 Red Hat
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

import sys

from oslo_log import log
import six

import tobiko
from tobiko.cmd import base

LOG = log.getLogger(__name__)


class FixtureUtil(base.TobikoCMD):

    def get_parser(self):
        parser = super(FixtureUtil, self).get_parser()

        subparsers = parser.add_subparsers(
            title='subcommands', description='fixture operation')

        subcommand_parser = subparsers.add_parser(
            'help', help=('show this help message'))
        subcommand_parser.set_defaults(subcommand='help')

        for subcommand_name in ['cleanup', 'list', 'setup']:
            subcommand_parser = subparsers.add_parser(
                subcommand_name, help=(subcommand_name + ' fixtures'))
            subcommand_parser.set_defaults(subcommand=subcommand_name)
            subcommand_parser.add_argument(
                '--config', '-c',
                default='.stestr.conf',
                help=("Set a stestr config file to use with this command. "
                      "If one isn't specified then .stestr.conf in the "
                      "directory that a command is running from is used"))
            subcommand_parser.add_argument(
                '--repo-type', '-r',
                choices=['file'],
                default='file',
                help=("Select the repo backend to use"))
            subcommand_parser.add_argument(
                '--repo-url', '-u',
                help=("Set the repo url to use. An acceptable value for "
                      "this depends on the repository type used."))
            subcommand_parser.add_argument(
                '--test-path', '-t',
                help=("Set the test path to use for unittest discovery. If "
                      "both this and the corresponding config file option "
                      "are set, this value will be used."))
            subcommand_parser.add_argument(
                '--top-dir',
                help=("Set the top dir to use for unittest discovery. If "
                      "both this and the corresponding config file option "
                      "are set, this value will be used."))
            subcommand_parser.add_argument(
                '--group-regex', '--group_regex', '-g',
                help=("Set a group regex to use for grouping tests together "
                      "in the stestr scheduler. If both this and the "
                      "corresponding config file option are set this value "
                      "will be used."))
            subcommand_parser.add_argument(
                '--blacklist-file', '-b',
                help=("Path to a blacklist file, this file contains a "
                      "separate regex exclude on each newline."))
            subcommand_parser.add_argument(
                '--whitelist-file', '-w',
                help=("Path to a whitelist file, this file contains a "
                      "separate regex on each newline."))
            subcommand_parser.add_argument(
                '--black-regex', '-B',
                help=("Test rejection regex. If a test cases name matches "
                      "on re.search() operation , it will be removed from "
                      "the final test list. Effectively the black-regexp is "
                      "added to black regexp list, but you do need to edit "
                      "a file. The black filtering happens after the "
                      "initial white selection, which by default is "
                      "everything."))
            subcommand_parser.add_argument(
                'filters',
                nargs='*',
                help=("A list of string regex filters to initially apply "
                      "on the test list. Tests that match any of the "
                      "regexes will be used. (assuming any other filtering "
                      "specified also uses it)."))
        return parser

    def execute(self):
        action = self.args.subcommand or 'list'
        if action == 'help':
            return self.show_help()
        if action == 'list':
            return self.list_fixtures()
        elif action == 'setup':
            return self.setup_fixtures()
        elif action == 'cleanup':
            return self.cleanup_fixtures()

    def show_help(self, stream=None):
        stream = stream or sys.stdout
        self.parser.print_help(stream)

    def discover_testcases(self):
        args = self.args
        return tobiko.discover_testcases(
            config=args.config,
            repo_type=args.repo_type,
            repo_url=args.repo_url,
            test_path=args.test_path,
            top_dir=args.top_dir,
            group_regex=args.group_regex,
            blacklist_file=args.blacklist_file,
            whitelist_file=args.whitelist_file,
            black_regex=args.black_regex,
            filters=args.filters)

    def list_fixtures(self, stream=None):
        stream = stream or sys.stdout
        test_cases = self.discover_testcases()
        fixtures_names = tobiko.list_required_fixtures(test_cases)
        if fixtures_names:
            output = '\n'.join(fixtures_names) + '\n'
            if six.PY2:
                output = output.decode()
            stream.write(output)

    def setup_fixtures(self, stream=None):
        stream = stream or sys.stdout
        test_cases = self.discover_testcases()
        success = True
        for fixture_name in tobiko.list_required_fixtures(test_cases):
            output = fixture_name + '\n'
            if six.PY2:
                output = output.decode()
            stream.write(output)
            try:
                tobiko.setup_fixture(fixture_name)
            except Exception:
                LOG.exception('Fixture %r setup failed', fixture_name)
                success = False
        if not success:
            sys.exit(1)

    def cleanup_fixtures(self, stream=None):
        stream = stream or sys.stdout
        test_cases = self.discover_testcases()
        success = True
        for fixture_name in tobiko.list_required_fixtures(test_cases):
            output = fixture_name + '\n'
            if six.PY2:
                output = output.decode()
            stream.write(output)
            try:
                tobiko.cleanup_fixture(fixture_name)
            except Exception:
                LOG.exception('Fixture %r cleanup failed', fixture_name)
                success = False
        if not success:
            sys.exit(1)


def main():
    """Create CLI main entry."""
    fixture_util = FixtureUtil()
    fixture_util.set_stream_handler_logging_level()
    fixture_util.execute()


if __name__ == '__main__':
    sys.exit(main())
