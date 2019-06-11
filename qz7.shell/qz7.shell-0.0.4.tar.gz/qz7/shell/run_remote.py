"""
Execute shell commands remotely via ssh.
"""
#pylint: disable=too-many-arguments
#pylint: disable=too-many-branches

import sys
import logging
import subprocess

from blessings import Terminal

from qz7.shell.cmdlist import CmdList
from qz7.shell.ssh import get_ssh_client

DEFAULT_ENCODING = "UTF-8"
DEFAULT_TERM_WIDTH = 1024
TERM = None

log = logging.getLogger(__name__)

def set_term(term):
    """
    Set the global terminal object.

    Args:
        term: Blessings terminal object
    """

    global TERM

    TERM = term

def get_term():
    """
    Return the global terminal object.
    """

    global TERM

    if TERM is None:
        TERM = Terminal()

    return TERM

class RemoteCompletedProcess(subprocess.CompletedProcess):
    """
    Return value of remote(), representing a remote process that finished.

    Attributes:
        hostname: Hostname of the remote host
        args: Command that was executed
        returncode: Exit code of the command
        stdout: Captured standard output of the command
    """

    def __init__(self, hostname, args, returncode, stdout):
        super().__init__(args, returncode, stdout)

        self.hostname = hostname

    def __repr__(self):
        d = dict(self.__dict__)
        del d["stdout"]
        del d["stderr"]
        return f"{self.__class__.__name__}({d!r})"

class RemoteCalledProcessError(subprocess.CalledProcessError):
    """
    Raised when the remote process exits with a non zero exit status.

    Attributes:
        hostname: Hostname of the remote host
        args: Command that was executed
        returncode: Exit code of the command
        output: Captured standard output of the command
    """

    def __init__(self, hostname, cmd, returncode, stdout):
        super().__init__(returncode, cmd, output=stdout)

        self.hostname = hostname

    def __repr__(self):
        d = dict(self.__dict__)
        del d["output"]
        del d["stderr"]
        return f"{self.__class__.__name__}({d!r})"

class RemoteExecError(subprocess.SubprocessError):
    """
    Raised when an exception occurs when running remote command.

    Attributes:
        hostname: Hostname of the remote host
    """

    def __init__(self, e, hostname):
        super().__init__(str(e))

        self.hostname = hostname

    def __repr__(self):
        return f"{self.__class__.__name__}({self.__dict__!r})"

def _do_remote(hostname, cmd, pty, echo_output, capture, check, text):
    """
    Do the remote execution.
    """

    try:
        term = get_term()

        with get_ssh_client(hostname) as ssh_client:
            chan = ssh_client.get_transport().open_session()
            if pty:
                if hasattr(term, "width") and term.width is not None:
                    term_width = term.width
                else:
                    term_width = DEFAULT_TERM_WIDTH
                chan.get_pty(width=term_width)
            chan.exec_command(cmd)
            sout = chan.makefile("rb", -1)

            output = []
            for line in sout:
                if echo_output:
                    sys.stdout.write(line.decode(DEFAULT_ENCODING))
                    sys.stdout.flush()
                if capture:
                    output.append(line)
                output = b"".join(output)

            if not capture:
                output = None

            if output is not None and text is True:
                output = output.decode(DEFAULT_ENCODING)

            returncode = chan.recv_exit_status()
    except Exception as e:
        raise RemoteExecError(e, hostname)

    if check and returncode != 0:
        raise RemoteCalledProcessError(hostname, cmd, returncode, output)

    return RemoteCompletedProcess(hostname, cmd, returncode, output)

def run_remote(hostname, cmd, shell="/bin/bash -l -c",
               pty=True, echo_output=True,
               capture_output=False, check=False, text=False):
    """
    Run the command described by cmd on a remote host.

    If shell is not None, and cmd is a CmdList instance,
    then the explicit shell argument has priority.

    Args:
        hostname: Ssh remote host specification; e.g host or user@host
        cmd: Command to execute on the remote host
        shell: Shell to execute the command in the remote host
        pty: If true, run the remote command in the context of a pty
        echo_output: If true, echo the output of the command locally
        capture_output: If true, capture the output of the remote command
        check: If true, raise RemoteCalledProcessError if remote command exits
               with non zero exit code
        text: If true, read the output as a string mode

    Returns:
        An instance of RemoteCompletedProcess

    Raises:
        RemoteCalledProcessError in case check==True and the remote process
            exited with a non-zero exit code.

        RemoteExecError in case any unexpected exception occurs
            when executing the remote process.
    """

    if isinstance(cmd, CmdList):
        if shell is not None:
            cmd.shell = shell
        cmd = str(cmd)

    return _do_remote(hostname, cmd, pty, echo_output, capture_output, check, text)
