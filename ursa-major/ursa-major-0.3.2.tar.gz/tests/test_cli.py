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

import io
import os
import tempfile
import ursa_major.cli
import pytest

from mock import patch


class TestTagConfigFileCLIOption:
    """Test --tag-config-file"""

    @classmethod
    def setup_class(cls):
        # Create a real file to make json.load work
        fd, cls.tag_config_file = tempfile.mkstemp()
        with io.open(fd, 'w', encoding='utf-8', closefd=True) as f:
            f.write(u'{}')

    @classmethod
    def teardown_class(cls):
        os.unlink(cls.tag_config_file)

    @patch.object(ursa_major.cli, 'AddModuleHandler')
    @patch('ursa_major.cli.ConfigParser')
    @patch('os.path.exists', return_value=True)
    def test_use_default_file(self, exists, ConfigParser, AddModuleHandler):
        cli_cmd = [
            'ursa-major', 'add-module', '--name', 'nodejs', '--stream', '10',
            '--priority', '10', '--tag', 'f30-candidate'
        ]

        with patch('sys.argv', new=cli_cmd):
            with patch.object(ursa_major.cli, 'DEFAULT_TAG_CONFIG_FILE',
                              new=self.tag_config_file):
                ursa_major.cli.main()

        handler = AddModuleHandler.return_value
        pos_args, _ = handler.set_args.call_args
        args = pos_args[0]
        assert args.tag_config_file == self.tag_config_file

    @patch.object(ursa_major.cli, 'AddModuleHandler')
    @patch('ursa_major.cli.ConfigParser')
    @patch('os.path.exists', return_value=True)
    def test_default_file_does_not_exist(self, exists, ConfigParser, AddModuleHandler):
        cli_cmd = [
            'ursa-major', 'add-module', '--name', 'nodejs', '--stream', '10',
            '--priority', '10', '--tag', 'f30-candidate'
        ]

        with patch('sys.argv', new=cli_cmd):
            with patch.object(ursa_major.cli, 'DEFAULT_TAG_CONFIG_FILE', new='/tmp/xxxx'):
                with pytest.raises(SystemExit):
                    ursa_major.cli.main()

    @patch.object(ursa_major.cli, 'AddModuleHandler')
    @patch('ursa_major.cli.ConfigParser')
    @patch('os.path.exists', return_value=True)
    def test_specify_a_file(self, exists, ConfigParser, AddModuleHandler):
        cli_cmd = [
            'ursa-major', 'add-module', '--name', 'nodejs', '--stream', '10',
            '--priority', '10', '--tag', 'f30-candidate',
            '--tag-config-file', self.tag_config_file
        ]

        with patch('sys.argv', new=cli_cmd):
            ursa_major.cli.main()

        handler = AddModuleHandler.return_value
        pos_args, _ = handler.set_args.call_args
        args = pos_args[0]
        assert args.tag_config_file == self.tag_config_file

    @patch.object(ursa_major.cli, 'AddModuleHandler')
    @patch('ursa_major.cli.ConfigParser')
    @patch('os.path.exists', return_value=True)
    def test_specified_file_does_not_exist(self, exists, ConfigParser, AddModuleHandler):
        cli_cmd = [
            'ursa-major', 'add-module', '--name', 'nodejs', '--stream', '10',
            '--priority', '10', '--tag', 'f30-candidate',
            '--tag-config-file', '/tmp/xxxxx'
        ]

        with patch('sys.argv', new=cli_cmd):
            with pytest.raises(SystemExit):
                ursa_major.cli.main()
