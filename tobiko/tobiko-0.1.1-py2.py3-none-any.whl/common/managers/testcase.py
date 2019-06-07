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

import os
import sys

from oslo_log import log
from stestr import config_file

LOG = log.getLogger(__name__)

os.environ.setdefault('PYTHON', sys.executable)


def discover_testcases(manager=None, **kwargs):
    manager = manager or TESTCASES
    return manager.discover(**kwargs)


class TestCaseManager(object):

    def __init__(self, config=None, repo_type=None, repo_url=None,
                 test_path=None, top_dir=None, group_regex=None,
                 blacklist_file=None, whitelist_file=None, black_regex=None,
                 filters=None):
        """
        :param str config: The path to the stestr config file. Must be a
            string.
        :param str repo_type: This is the type of repository to use. Valid
            choices are 'file' and 'sql'.
        :param str repo_url: The url of the repository to use.
        :param str test_path: Set the test path to use for unittest discovery.
            If both this and the corresponding config file option are set, this
            value will be used.
        :param str top_dir: The top dir to use for unittest discovery. This
            takes precedence over the value in the config file. (if one is
            present in the config file)
        :param str group_regex: Set a group regex to use for grouping tests
            together in the stestr scheduler. If both this and the
            corresponding config file option are set this value will be used.
        :param str blacklist_file: Path to a blacklist file, this file contains
            a separate regex exclude on each newline.
        :param str whitelist_file: Path to a whitelist file, this file contains
            a separate regex on each newline.
        :param str black_regex: Test rejection regex. If a test cases name
            matches on re.search() operation, it will be removed from the final
            test list.
        :param list filters: A list of string regex filters to initially apply
            on the test list. Tests that match any of the regexes will be used.
            (assuming any other filtering specified also uses it)
        """

        self.config = config or '.stestr.conf'
        self.repo_type = repo_type or 'file'
        self.repo_url = repo_url
        self.test_path = test_path
        self.top_dir = top_dir
        self.group_regex = group_regex
        self.blacklist_file = blacklist_file
        self.whitelist_file = whitelist_file
        self.black_regex = black_regex
        self.filters = filters

    def discover(self, **kwargs):
        """Iterate over test_ids for a project
        This method will print the test_ids for tests in a project. You can
        filter the output just like with the run command to see exactly what
        will be run.
        """
        params = dict(config=self.config, repo_type=self.repo_type,
                      repo_url=self.repo_url, test_path=self.test_path,
                      top_dir=self.top_dir, group_regex=self.group_regex,
                      blacklist_file=self.blacklist_file,
                      whitelist_file=self.whitelist_file,
                      black_regex=self.black_regex, filters=self.filters)
        if kwargs:
            params.update(kwargs)
        ids = None
        config = params.pop('config')
        conf = config_file.TestrConf(config)
        filters = params.pop('filters')
        blacklist_file = params.pop('blacklist_file')
        whitelist_file = params.pop('whitelist_file')
        black_regex = params.pop('black_regex')
        cmd = conf.get_run_command(
            regexes=filters, repo_type=params['repo_type'],
            repo_url=params['repo_url'], group_regex=params['group_regex'],
            blacklist_file=blacklist_file, whitelist_file=whitelist_file,
            black_regex=black_regex, test_path=params['test_path'],
            top_dir=params['top_dir'])
        not_filtered = filters is None and blacklist_file is None\
            and whitelist_file is None and black_regex is None

        try:
            cmd.setUp()
            # List tests if the fixture has not already needed to to filter.
            if not_filtered:
                ids = cmd.list_tests()
            else:
                ids = cmd.test_ids
        except SystemExit:
            msg = ("Error discovering test cases IDs with parameters: "
                   "{!r}").format(params)
            raise RuntimeError(msg)
        finally:
            cmd.cleanUp()

        return sorted(ids)


TESTCASES = TestCaseManager()
