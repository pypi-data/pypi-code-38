# Copyright (c) 2019 Red Hat, Inc.
#
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

import testtools

import tobiko
from tobiko import config
from tobiko.openstack import stacks
from tobiko.shell import sh


CONF = config.CONF


class ExecuteTest(testtools.TestCase):

    ssh_client = None
    shell = '/bin/sh -c'

    def test_succeed(self, command='true', stdout='', stderr='', **kwargs):
        result = self.execute(command, **kwargs)
        expected_result = sh.ShellExecuteResult(
            command=self.expected_command(command),
            timeout=kwargs.get('timeout'),
            exit_status=0,
            stdout=stdout,
            stderr=stderr)
        self.assertEqual(expected_result, result)

    def test_succeed_with_command_list(self):
        self.test_succeed(['echo', 'something'],
                          stdout='something\n')

    def test_succeed_reading_from_stdout(self):
        self.test_succeed('echo something',
                          stdout='something\n')

    def test_succeed_reading_from_stderr(self):
        self.test_succeed('echo something >&2',
                          stderr='something\n')

    def test_succeed_writing_to_stdin(self):
        self.test_succeed('cat',
                          stdin='some input\n',
                          stdout='some input\n')

    def test_succeed_with_timeout(self):
        self.test_succeed(timeout=30.)

    def test_fails(self, command='false', exit_status=None, stdout='',
                   stderr='', **kwargs):
        ex = self.assertRaises(sh.ShellCommandFailed, self.execute, command,
                               **kwargs)
        self.assertEqual(self.expected_ex_command(command), ex.command)
        self.assertEqual(stdout, ex.stdout)
        self.assertEqual(stderr, ex.stderr)
        if exit_status:
            self.assertEqual(exit_status, ex.exit_status)
        else:
            self.assertTrue(ex.exit_status)

    def test_fails_getting_exit_status(self):
        self.test_fails('exit 15', exit_status=15)

    def test_fails_reading_from_stdout(self):
        self.test_fails(command='echo something && false',
                        stdout='something\n')

    def test_fails_reading_from_stderr(self):
        self.test_fails(command='echo something >&2 && false',
                        stderr='something\n')

    def test_fails_writing_to_stdin(self):
        self.test_fails('cat && false',
                        stdin='some input\n',
                        stdout='some input\n')

    def test_timeout_expires(self, command='sleep 5', timeout=0.1, stdout='',
                             stderr='', **kwargs):
        ex = self.assertRaises(sh.ShellTimeoutExpired, self.execute, command,
                               timeout=timeout, **kwargs)
        self.assertEqual(self.expected_ex_command(command), ex.command)
        self.assertTrue(stdout.startswith(ex.stdout))
        self.assertTrue(stderr.startswith(ex.stderr))
        self.assertEqual(timeout, ex.timeout)

    def execute(self, command, **kwargs):
        kwargs.setdefault('shell', self.shell)
        kwargs.setdefault('ssh_client', self.ssh_client)
        return sh.execute(command, **kwargs)

    def expected_command(self, command):
        return sh.split_command(self.shell) + [sh.join_command(command)]

    def expected_ex_command(self, command):
        return sh.join_command(self.expected_command(command))


class ExecuteWithSSHClientTest(ExecuteTest):

    server_stack = tobiko.required_setup_fixture(
        stacks.NeutronServerStackFixture)

    @property
    def ssh_client(self):
        return self.server_stack.ssh_client


class ExecuteWithSSHCommandTest(ExecuteTest):

    server_stack = tobiko.required_setup_fixture(
        stacks.NeutronServerStackFixture)

    @property
    def shell(self):
        return self.server_stack.ssh_command
