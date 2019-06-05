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

import collections
import select
import subprocess
import sys
import time

from oslo_log import log
import six

import tobiko
from tobiko.shell import ssh
from tobiko.shell.sh import _exception


LOG = log.getLogger(__name__)


def execute(command, stdin=None, environment=None, timeout=None, shell=None,
            check=True, ssh_client=None):
    """Execute command inside a remote or local shell

    :param command: command argument list

    :param timeout: command execution timeout in seconds

    :param check: when False it doesn't raises ShellCommandError when
    exit status is not zero. True by default

    :param ssh_client: SSH client instance used for remote shell execution

    :returns: STDOUT text when command execution terminates with zero exit
    status.

    :raises ShellTimeoutExpired: when timeout expires before command execution
    terminates. In such case it kills the process, then it eventually would
    try to read STDOUT and STDERR buffers (not fully implemented) before
    raising the exception.

    :raises ShellCommandError: when command execution terminates with non-zero
    exit status.
    """

    if timeout:
        timeout = float(timeout)

    ssh_client = ssh_client or ssh.ssh_proxy_client()
    if not ssh_client and not shell:
        from tobiko import config
        CONF = config.CONF
        shell = CONF.tobiko.shell.command

    if shell:
        command = split_command(shell) + [join_command(command)]
    else:
        command = split_command(command)

    if ssh_client:
        result = execute_remote_command(command=command, stdin=stdin,
                                        environment=environment,
                                        timeout=timeout,
                                        ssh_client=ssh_client)
    else:
        result = execute_local_command(command=command, stdin=stdin,
                                       environment=environment,
                                       timeout=timeout)

    if result.exit_status == 0:
        LOG.debug("Command %r succeeded:\n"
                  "stderr:\n%s\n"
                  "stdout:\n%s\n",
                  command, result.stderr, result.stdout)
    elif result.exit_status is None:
        LOG.debug("Command %r timeout expired (timeout=%s):\n"
                  "stderr:\n%s\n"
                  "stdout:\n%s\n",
                  command, timeout, result.stderr, result.stdout)
    else:
        LOG.debug("Command %r failed (exit_status=%s):\n"
                  "stderr:\n%s\n"
                  "stdout:\n%s\n",
                  command, result.exit_status, result.stderr, result.stdout)
    if check:
        result.check()

    return result


def execute_remote_command(command, ssh_client, stdin=None, timeout=None,
                           environment=None):
    """Execute command on a remote host using SSH client"""

    if isinstance(ssh_client, ssh.SSHClientFixture):
        # Connect to fixture
        ssh_client = tobiko.setup_fixture(ssh_client).client

    transport = ssh_client.get_transport()
    with transport.open_session() as channel:
        if environment:
            channel.update_environment(environment)
        channel.exec_command(join_command(command))
        stdout, stderr = comunicate_ssh_channel(channel, stdin=stdin,
                                                timeout=timeout)
        if channel.exit_status_ready():
            exit_status = channel.recv_exit_status()
        else:
            exit_status = None
    return ShellExecuteResult(command=command, timeout=timeout,
                              stdout=stdout, stderr=stderr,
                              exit_status=exit_status)


def comunicate_ssh_channel(ssh_channel, stdin=None, chunk_size=None,
                           timeout=None, sleep_time=None, read_stdout=True,
                           read_stderr=True):
    if read_stdout:
        rlist = [ssh_channel]
    else:
        rlist = []

    if not stdin:
        ssh_channel.shutdown_write()
        stdin = None
        wlist = []
    else:
        wlist = [ssh_channel]
        if not isinstance(stdin, six.binary_type):
            stdin = stdin.encode()

    chunk_size = chunk_size or 1024
    sleep_time = sleep_time or 1.
    timeout = timeout or float("inf")
    start = time.time()
    stdout = None
    stderr = None

    while True:
        chunk_timeout = min(sleep_time, timeout - (time.time() - start))
        if chunk_timeout < 0.:
            LOG.debug('Timed out reading from SSH channel: %r', ssh_channel)
            break
        ssh_channel.settimeout(chunk_timeout)
        if read_stdout and ssh_channel.recv_ready():
            chunk = ssh_channel.recv(chunk_size)
            if stdout:
                stdout += chunk
            else:
                stdout = chunk
            if not chunk:
                LOG.debug("STDOUT channel closed by peer on SSH channel %r",
                          ssh_channel)
                read_stdout = False
        elif read_stderr and ssh_channel.recv_stderr_ready():
            chunk = ssh_channel.recv_stderr(chunk_size)
            if stderr:
                stderr += chunk
            else:
                stderr = chunk
            if not chunk:
                LOG.debug("STDERR channel closed by peer on SSH channel %r",
                          ssh_channel)
                read_stderr = False
        elif ssh_channel.exit_status_ready():
            break
        elif stdin and ssh_channel.send_ready():
            sent_bytes = ssh_channel.send(stdin[:chunk_size])
            stdin = stdin[sent_bytes:] or None
            if not stdin:
                LOG.debug('shutdown_write() on SSH channel: %r', ssh_channel)
                ssh_channel.shutdown_write()
        else:
            select.select(rlist, wlist, rlist or wlist, chunk_timeout)

    if stdout:
        if not isinstance(stdout, six.string_types):
            stdout = stdout.decode()
    else:
        stdout = ''
    if stderr:
        if not isinstance(stderr, six.string_types):
            stderr = stderr.decode()
    else:
        stderr = ''
    return stdout, stderr


def execute_local_command(command, stdin=None, environment=None, timeout=None):
    """Execute command on local host using local shell"""

    LOG.debug("Executing command %r on local host (timeout=%r)...",
              command, timeout)

    stdin = stdin or None
    process = subprocess.Popen(command,
                               universal_newlines=True,
                               env=environment,
                               stdin=subprocess.PIPE,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)

    if timeout and sys.version_info < (3, 3):
        LOG.warning("Popen.communicate method doens't support for timeout "
                    "on Python %r", sys.version)
        timeout = None

    # Wait for process execution while reading STDERR and STDOUT streams
    if timeout:
        try:
            # pylint: disable=unexpected-keyword-arg,no-member
            stdout, stderr = process.communicate(input=stdin,
                                                 timeout=timeout)
        except subprocess.TimeoutExpired:
            # At this state I expect the process to be still running
            # therefore it has to be kill later after calling poll()
            LOG.exception("Command %r timeout expired.", command)
            stdout = stderr = ''
    else:
        stdout, stderr = process.communicate(input=stdin)

    # Check process termination status
    exit_status = process.poll()
    if exit_status is None:
        # The process is still running after calling communicate():
        # let kill it
        process.kill()

    return ShellExecuteResult(command=command, timeout=timeout,
                              stdout=stdout, stderr=stderr,
                              exit_status=exit_status)


class ShellExecuteResult(collections.namedtuple(
        'ShellExecuteResult', ['command', 'timeout', 'exit_status', 'stdout',
                               'stderr'])):

    def check(self):
        command = join_command(self.command)
        if self.exit_status is None:
            raise _exception.ShellTimeoutExpired(command=command,
                                                 timeout=self.timeout,
                                                 stderr=self.stderr,
                                                 stdout=self.stdout)

        elif self.exit_status != 0:
            raise _exception.ShellCommandFailed(command=command,
                                                exit_status=self.exit_status,
                                                stderr=self.stderr,
                                                stdout=self.stdout)


def split_command(command):
    if isinstance(command, six.string_types):
        return command.split()
    elif command:
        return [str(a) for a in command]
    else:
        return []


def join_command(command):
    if isinstance(command, six.string_types):
        return command
    elif command:
        return subprocess.list2cmdline([str(a) for a in command])
    else:
        return ""
