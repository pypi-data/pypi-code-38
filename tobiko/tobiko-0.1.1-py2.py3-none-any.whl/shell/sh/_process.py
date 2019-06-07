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

import io
import time

from oslo_log import log

from tobiko.shell.sh import _exception
from tobiko.shell.sh import _io


LOG = log.getLogger(__name__)


class Timeout(object):

    timeout = float('inf')

    def __init__(self, timeout=None, start_time=None):
        if timeout is None:
            timeout = float('inf')
        else:
            timeout = float(timeout)
        self.timeout = timeout
        start_time = start_time and float(start_time) or time.time()
        self.start_time = start_time
        self.end_time = start_time + timeout

    def __float__(self):
        return self.timeout

    def time_left(self, now=None):
        now = now or time.time()
        return self.end_time - now

    def is_expired(self, now=None):
        raise self.time_left(now=now) <= 0.


class ShellProcess(object):

    buffer_size = io.DEFAULT_BUFFER_SIZE
    stdin = None
    stdout = None
    stderr = None
    poll_time = 0.1

    def __init__(self, command, timeout=None, stdin=None, stdout=None,
                 stderr=None, buffer_size=None, poll_time=None):
        self.command = command
        self.timeout = Timeout(timeout)
        if buffer_size is not None:
            self.buffer_size = max(64, int(buffer_size))
        if stdin:
            self.stdin = _io.ShellStdin(stdin, buffer_size=self.buffer_size)
        if stdout:
            self.stdout = _io.ShellStdout(stdout, buffer_size=self.buffer_size)
        if stderr:
            self.stderr = _io.ShellStderr(stderr, buffer_size=self.buffer_size)
        if poll_time is not None:
            self.poll_time = max(0., float(poll_time))

    def __enter__(self):
        return self

    def __exit__(self, _exception_type, _exception_value, _traceback):
        self.close()

    def close(self):
        if self.is_running:
            self.kill()
        for f in _io.select_opened_files([self.stdin,
                                          self.stdout,
                                          self.stderr]):
            f.close()

    def kill(self):
        pass

    def poll_exit_status(self):
        raise NotImplementedError

    @property
    def exit_status(self):
        return self.poll_exit_status()

    @property
    def is_running(self):
        return self.poll_exit_status() is None

    def check_is_running(self):
        exit_status = self.poll_exit_status()
        if exit_status is not None:
            raise _exception.ShellProcessTeriminated(
                command=self.command,
                exit_status=int(exit_status),
                stdin=self.stdin,
                stdout=self.stdout,
                stderr=self.stderr)

    def check_stdin_is_opened(self):
        if self.stdin.closed:
            raise _exception.ShellStdinClosed(
                command=self.command,
                stdin=self.stdin,
                stdout=self.stdout,
                stderr=self.stderr)

    def send(self, data, timeout=None):
        self.comunicate(stdin=data, timeout=timeout, wait=False)

    def wait(self, timeout=None):
        self.comunicate(stdin=None, timeout=timeout, wait=True)

    def comunicate(self, stdin=None, stdout=True, stderr=True, timeout=None,
                   wait=True):
        timeout = Timeout(timeout=timeout)
        # Avoid waiting for data in the first loop
        poll_time = 0.
        poll_files = _io.select_opened_files([stdin and self.stdin,
                                              stdout and self.stdout,
                                              stderr and self.stderr])

        while wait or stdin or poll_files:
            self.check_timeout(timeout=timeout)
            if stdin:
                self.check_is_running()
                self.check_stdin_is_opened()
            else:
                wait = wait and self.is_running

            read_ready, write_ready = _io.select_files(files=poll_files,
                                                       timeout=poll_time)
            if read_ready or write_ready:
                # Avoid waiting for data the next time
                poll_time = 0.
            else:
                # Wait for data in the following loops
                poll_time = min(self.poll_time,
                                self.check_timeout(timeout=timeout))

            if self.stdin in write_ready:
                # Write data to remote STDIN
                sent_bytes = self.stdin.write(stdin)
                if sent_bytes:
                    stdin = stdin[sent_bytes:]
                    if not stdin:
                        self.stdin.flush()
                else:
                    LOG.debug("STDIN channel closed by peer on %r", self)
                    self.stdin.close()

            if self.stdout in read_ready:
                # Read data from remote STDOUT
                chunk = self.stdout.read(self.buffer_size)
                if not chunk:
                    LOG.debug("STDOUT channel closed by peer on %r", self)
                    self.stdout.close()

            if self.stderr in read_ready:
                # Read data from remote STDERR
                chunk = self.stderr.read(self.buffer_size)
                if not chunk:
                    LOG.debug("STDERR channel closed by peer on %r", self)
                    self.stderr.close()

            poll_files = _io.select_opened_files(poll_files)

    def time_left(self, now=None, timeout=None):
        now = now or time.time()
        time_left = self.timeout.time_left(now=now)
        if timeout:
            time_left = min(time_left, timeout.time_left(now=now))
        return time_left

    def check_timeout(self, timeout=None, now=None):
        now = now or time.time()
        time_left = float('inf')
        for timeout in [self.timeout, timeout]:
            if timeout is not None:
                time_left = min(time_left, timeout.time_left(now=now))
                if time_left <= 0.:
                    ex = _exception.ShellTimeoutExpired(
                        command=self.command,
                        timeout=timeout.timeout,
                        stdin=self.stdin,
                        stdout=self.stdout,
                        stderr=self.stderr)
                    LOG.debug("%s", ex)
                    raise ex
        return time_left

    def check_exit_status(self, expected_status=0):
        exit_status = self.poll_exit_status()
        if exit_status is None:
            time_left = self.check_timeout()
            ex = _exception.ShellProcessNotTeriminated(
                command=self.command,
                time_left=time_left,
                stdin=self.stdin,
                stdout=self.stdout,
                stderr=self.stderr)
            LOG.debug("%s", ex)
            raise ex

        exit_status = int(exit_status)
        if expected_status != exit_status:
            ex = _exception.ShellCommandFailed(
                command=self.command,
                exit_status=exit_status,
                stdin=self.stdin,
                stdout=self.stdout,
                stderr=self.stderr)
            LOG.debug("%s", ex)
            raise ex

        LOG.debug("Command '%s' succeeded (exit_status=%d):\n"
                  "stdin:\n%s\n"
                  "stderr:\n%s\n"
                  "stdout:\n%s",
                  self.command, exit_status,
                  self.stdin, self.stdout, self.stderr)


def clamp(left, value, right):
    return max(left, min(value, right))
