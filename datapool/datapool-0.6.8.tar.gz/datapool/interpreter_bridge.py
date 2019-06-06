# encoding: utf-8
from __future__ import absolute_import, division, print_function

import os
import subprocess
import sys

import psutil

from .logger import logger as get_logger
from .utils import run_timed

ENCODING = sys.getdefaultencoding()
"""
Concept: We start an (matlab|julia|...) interpreter in a sub process and communicate using pipes to
stdin / from stdout.

To execute given code we first wrap this specific code in a template. For example see
`julia_runner.py` and `matlab_runner.py`. Then we write this code to STDIN of our server which
starts to execute this as manually typed commands.  The framing code writes special markers to
STDOUT which the client reads from the implemented pipe.

The markers start with "!!!" followed by a pair MESSAGE:[PAYLOAD]. We use the following markers:

    - "ERROR:START" and "ERROR:END" to indicate start and end of exception related output

    - "FINISHED:0" is the last output, so the client stops to request output from the server
"""


def used_memory(process):
    """returns memory consumed by process, unit is MB. This method is not 100% exact and
    usually overestimated the "memory freed if we terminate the process" number. But to
    get the exact numbers with psutil we (might) need root priviledges."""
    return psutil.Process(process.pid).memory_info()[0] / float(2 ** 20)


class InterpreterBridge(object):

    NAME = "NOT SET"
    EXTRA_ARGS = []
    TEMPLATE = ""
    NAME = "NOT SET"
    ENV = {}
    ENV = dict(LC_ALL="en_US.UTF-8", LANG="en_US.UTF-8")

    def __init__(
        self,
        executable,
        mem_limit=500,
        call_limit=1000,
        noop="0",
        used_memory=used_memory,
    ):
        """executable:  path to executable as matlab or julia
           mem_limit:   if the interpreter consumes more that mem_limit MB it will be restarted,
                        to disable this use mem_limit=None.
           call_limit:  if more than call_limits commands are sent to interpreter, the subprocess
                        will be restarted. To disable this use call_limit=None.
           noop:        a "no operation" command for health check of subprocess.
        """
        self.args = [executable] + self.EXTRA_ARGS
        self.logger = get_logger()
        self.p = None
        self.mem_limit = mem_limit
        self.call_limit = call_limit
        self.noop = noop
        self.used_memory = used_memory

    def start_interpreter(self, verbose=False):

        self.call_count = 0
        self.p = self._start_interpreter(verbose)
        self.wait_until_available(verbose=verbose)
        return self

    def _start_interpreter(self, verbose=False):

        try:
            env = os.environ.copy()
            env.update(self.ENV)
            return subprocess.Popen(
                self.args,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                env=env,
            )
        except OSError as e:
            msg = "failed to start '{}'. reason: {}".format(" ".join(self.args), e)
            raise OSError(msg) from None

    def kill(self):
        self.p.communicate()
        self.p = None

    def wait_until_available(self, verbose=False):
        return self.run_command(
            self.noop, skip_limits_check=True, timeout_in_seconds=None, verbose=verbose
        )

    def is_alive(self, timeout_in_seconds=1):
        try:
            exit_code = run_timed(
                self.wait_until_available, timeout_in_seconds=timeout_in_seconds
            )
        except TimeoutError:
            return False
        return exit_code == 0

    def _check_and_restart_if_needed(self):
        call_limit_exceeded = (
            self.call_limit is not None and self.call_count > self.call_limit
        )
        if call_limit_exceeded:
            self.logger.info(
                "call limit {} exceeded, will restart the process".format(
                    self.call_limit
                )
            )

        mem_used = self.used_memory(self.p)
        mem_limit_exceeded = self.mem_limit is not None and mem_used > self.mem_limit
        if mem_limit_exceeded:
            self.logger.info(
                "memory limit of {} MB exceeded (actual consumption is {} MB), "
                "will restart the process".format(self.mem_limit, mem_used)
            )

        if call_limit_exceeded or mem_limit_exceeded:
            """we first start a new one, so we can assume that old and new process will have
            different process ids. some tests rely on this"""
            p = self._start_interpreter()
            self.kill()
            self.p = p
            self.wait_until_available()
            self.call_count = 0

    def run_command(
        self, command, timeout_in_seconds=None, skip_limits_check=False, verbose=False
    ):
        assert self.p is not None, "you have to start the interpreter first"

        if not skip_limits_check:
            self._check_and_restart_if_needed()

        try:
            exit_code = run_timed(
                self._run_command,
                (command,),
                {"verbose": verbose},
                timeout_in_seconds=timeout_in_seconds,
            )
        except TimeoutError as e:
            raise TimeoutError(
                "command '{}' did not finish with {} seconds".format(
                    command, timeout_in_seconds
                )
            ) from None
        self.call_count += 1
        return exit_code

    @property
    def pid(self):
        """process id of running interpreter"""
        assert self.p is not None, "you have to start the interpreter first"
        return self.p.pid

    def _wrap_command(self, command):
        return self.TEMPLATE.format(command=command, MSG_MARKER=self.MSG_MARKER)

    def _run_command(self, command, verbose):

        code = self._wrap_command(command)
        if verbose:
            print(code)

        self.p.stdin.write(code.encode(ENCODING))
        self.p.stdin.write(b"\n")
        self.p.stdin.flush()

        log_error = False

        exit_code = 1
        lines = []
        for line in iter(self.p.stdout.readline, b""):

            line = str(line, ENCODING).rstrip()
            lines.append(line)

            # we might have multiple ">> " before the actual output:
            while line.startswith(">>"):
                line = line[2:]
                line = line.lstrip()  # maybe one space or none

            if line.startswith(self.MSG_MARKER):
                message, __, payload = line[len(self.MSG_MARKER) :].partition(":")

                if message == "ERROR":
                    log_error = payload == "START"
                    continue
                if message == "EXITCODE":
                    exit_code = int(payload)
                    continue

                if message == "FINISHED":
                    return exit_code

            if log_error:
                self.logger.error("{}: {}".format(self.NAME, line))
            elif verbose:
                print(">>", line)
        # this happens if stoud dies before the FINSHED marker was written, eg if
        # the interpreter startup fails before 'code' was executed
        self.logger.error(
            "{}: interpreter startup or code execution failed".format(self.NAME)
        )
        self.logger.error("{}: this is the recorded output:".format(self.NAME))
        for line in lines:
            self.logger.error("{}:    {}".format(self.NAME, line))
        return 1
