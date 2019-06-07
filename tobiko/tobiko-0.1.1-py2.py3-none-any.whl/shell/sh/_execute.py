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

import fcntl
import subprocess
import os

from oslo_log import log
import paramiko
import six

import tobiko
from tobiko.shell import ssh
from tobiko.shell.sh import _command
from tobiko.shell.sh import _process


LOG = log.getLogger(__name__)


DATA_TYPES = six.string_types + (six.binary_type, six.text_type)


def execute(command, environment=None, timeout=None, shell=None, check=True,
            wait=None, stdin=True, stdout=True, stderr=True, ssh_client=None,
            **kwargs):
    """Execute command inside a remote or local shell

    :param command: command argument list

    :param timeout: command execution timeout in seconds

    :param check: when False it doesn't raises ShellCommandError when
    exit status is not zero. True by default

    :param ssh_client: SSH client instance used for remote shell execution

    :raises ShellTimeoutExpired: when timeout expires before command execution
    terminates. In such case it kills the process, then it eventually would
    try to read STDOUT and STDERR buffers (not fully implemented) before
    raising the exception.

    :raises ShellCommandError: when command execution terminates with non-zero
    exit status.
    """

    fixture = ShellExecuteFixture(
        command, environment=environment, shell=shell, stdin=stdin,
        stdout=stdout, stderr=stderr, timeout=timeout, check=check, wait=wait,
        ssh_client=ssh_client, **kwargs)
    return tobiko.setup_fixture(fixture).process


def local_execute(command, environment=None, shell=None, stdin=True,
                  stdout=True, stderr=True, timeout=None, check=True,
                  wait=None, **kwargs):
    """Execute command on local host using local shell"""

    return execute(
        command=command, environment=environment, shell=shell, stdin=stdin,
        stdout=stdout, stderr=stderr, timeout=timeout, check=check, wait=wait,
        ssh_client=False, **kwargs)


def ssh_execute(ssh_client, command, environment=None, shell=None, stdin=True,
                stdout=True, stderr=True, timeout=None, check=True, wait=None,
                **kwargs):
    """Execute command on local host using local shell"""
    return execute(
        command=command, environment=environment, shell=shell, stdin=stdin,
        stdout=stdout, stderr=stderr, timeout=timeout, check=check, wait=wait,
        ssh_client=ssh_client, **kwargs)


class ShellExecuteFixture(tobiko.SharedFixture):

    command = None
    shell = None
    environment = {}
    stdin = None
    stderr = None
    stdout = None
    timeout = 120.
    check = None
    wait = None
    process = None
    process_parameters = None

    def __init__(self, command=None, shell=None, environment=None, stdin=None,
                 stdout=None, stderr=None, timeout=None, check=None, wait=None,
                 ssh_client=None, **kwargs):
        super(ShellExecuteFixture, self).__init__()

        if ssh_client is not None:
            self.ssh_client = ssh_client
        else:
            self.ssh_client = ssh_client = self.default_ssh_client

        if shell is not None:
            self.shell = shell = bool(shell) and _command.shell_command(shell)
        elif not ssh_client:
            self.shell = shell = self.default_shell_command

        if command is None:
            command = self.command
        command = _command.shell_command(command)
        if shell:
            command = shell + [str(command)]
        self.command = command

        environment = environment or self.environment
        if environment:
            self.environment = dict(environment).update(environment)

        if stdin is not None:
            self.stdin = stdin
        if stdout is not None:
            self.stdout = stdout
        if stderr is not None:
            self.stderr = stderr
        if timeout is not None:
            self.timeout = timeout
        if check is not None:
            self.check = check
        if wait is not None:
            self.wait = wait

        self.process_parameters = (self.process_parameters and
                                   dict(self.process_parameters) or
                                   {})
        if kwargs:
            self.process_parameters.update(kwargs)

    @property
    def default_shell_command(self):
        from tobiko import config
        CONF = config.CONF
        return _command.shell_command(CONF.tobiko.shell.command)

    @property
    def default_ssh_client(self):
        return ssh.ssh_proxy_client()

    def setup_fixture(self):
        self.setup_process()

    def setup_process(self):
        self.process = self.execute()

    def execute(self, timeout=None, stdin=None, stdout=None, stderr=None,
                check=None, ssh_client=None, wait=None, **kwargs):
        command = self.command
        environment = self.environment
        if timeout is None:
            timeout = self.timeout
        LOG.debug("Execute command '%s' on local host (timeout=%r, "
                  "environment=%r)...",
                  command, timeout, environment)

        if stdin is None:
            stdin = self.stdin
        if stdout is None:
            stdout = self.stdout
        if stderr is None:
            stderr = self.stderr
        if check is None:
            check = self.check
        if wait is None:
            wait = self.wait
        if ssh_client is None:
            ssh_client = self.ssh_client

        process_parameters = self.process_parameters
        if kwargs:
            process_parameters = dict(process_parameters, **kwargs)

        process = self.create_process(command=command,
                                      environment=environment,
                                      timeout=timeout, stdin=stdin,
                                      stdout=stdout, stderr=stderr,
                                      ssh_client=ssh_client,
                                      **process_parameters)
        self.addCleanup(process.close)

        if stdin and isinstance(stdin, DATA_TYPES):
            process.send(data=stdin)

        if wait or check:
            if process.stdin:
                process.stdin.close()
            process.wait()
            if check:
                process.check_exit_status()

        return process

    def create_process(self, ssh_client, **kwargs):
        if ssh_client:
            return self.create_ssh_process(ssh_client=ssh_client, **kwargs)
        else:
            return self.create_local_process(**kwargs)

    def create_local_process(self, command, environment, timeout, stdin,
                             stdout, stderr, **kwargs):
        popen_params = {}
        if stdin:
            popen_params.update(stdin=subprocess.PIPE)
        if stdout:
            popen_params.update(stdout=subprocess.PIPE)
        if stderr:
            popen_params.update(stderr=subprocess.PIPE)
        process = subprocess.Popen(command,
                                   universal_newlines=True,
                                   env=environment,
                                   **popen_params)
        if stdin:
            set_non_blocking(process.stdin.fileno())
            kwargs.update(stdin=process.stdin)
        if stdout:
            set_non_blocking(process.stdout.fileno())
            kwargs.update(stdout=process.stdout)
        if stderr:
            set_non_blocking(process.stderr.fileno())
            kwargs.update(stderr=process.stderr)
        return LocalShellProcess(process=process, command=command,
                                 timeout=timeout, **kwargs)

    def create_ssh_process(self, command, environment, timeout, stdin, stdout,
                           stderr, ssh_client, **kwargs):
        """Execute command on a remote host using SSH client"""
        if isinstance(ssh_client, ssh.SSHClientFixture):
            # Connect to SSH server
            ssh_client = ssh_client.connect()
        if not isinstance(ssh_client, paramiko.SSHClient):
            message = "Object {!r} is not an SSHClient".format(ssh_client)
            raise TypeError(message)

        LOG.debug("Execute command %r on remote host (timeout=%r)...",
                  str(command), timeout)
        channel = ssh_client.get_transport().open_session()
        if environment:
            channel.update_environment(environment)
        channel.exec_command(str(command))
        if stdin:
            kwargs.update(stdin=StdinSSHChannelFile(channel, 'wb'))
        if stdout:
            kwargs.update(stdout=StdoutSSHChannelFile(channel, 'rb'))
        if stderr:
            kwargs.update(stderr=StderrSSHChannelFile(channel, 'rb'))
        return SSHShellProcess(channel=channel, command=command,
                               timeout=timeout, **kwargs)


def set_non_blocking(fd):
    flag = fcntl.fcntl(fd, fcntl.F_GETFL)
    fcntl.fcntl(fd, fcntl.F_SETFL, flag | os.O_NONBLOCK)


class LocalShellProcess(_process.ShellProcess):

    def __init__(self, process=None, **kwargs):
        super(LocalShellProcess, self).__init__(**kwargs)
        self.process = process

    def poll_exit_status(self):
        return self.process.poll()

    def kill(self):
        self.process.kill()


class SSHChannelFile(paramiko.ChannelFile):

    def fileno(self):
        return self.channel.fileno()


class StdinSSHChannelFile(SSHChannelFile):

    def close(self):
        super(StdinSSHChannelFile, self).close()
        self.channel.shutdown_write()

    @property
    def write_ready(self):
        return self.channel.send_ready()

    def write(self, data):
        super(StdinSSHChannelFile, self).write(data)
        return len(data)


class StdoutSSHChannelFile(SSHChannelFile):

    def fileno(self):
        return self.channel.fileno()

    def close(self):
        super(StdoutSSHChannelFile, self).close()
        self.channel.shutdown_read()

    @property
    def read_ready(self):
        return self.channel.recv_ready()


class StderrSSHChannelFile(SSHChannelFile, paramiko.channel.ChannelStderrFile):

    def fileno(self):
        return self.channel.fileno()

    @property
    def read_ready(self):
        return self.channel.recv_stderr_ready()


class SSHShellProcess(_process.ShellProcess):

    def __init__(self, channel=None, **kwargs):
        super(SSHShellProcess, self).__init__(**kwargs)
        self.channel = channel

    def poll_exit_status(self):
        if self.channel.exit_status_ready():
            return self.channel.recv_exit_status()

    def close(self):
        super(SSHShellProcess, self).close()
        self.channel.close()
