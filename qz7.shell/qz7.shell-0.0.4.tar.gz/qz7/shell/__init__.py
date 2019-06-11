"""
Execute shell commands locally and remotely via ssh.
"""

from qz7.shell.cmdlist import command_format
from qz7.shell.run_local import run_local
from qz7.shell.run_remote import run_remote, set_term

from qz7.shell.run_remote import (
    RemoteCompletedProcess,
    RemoteCalledProcessError,
    RemoteExecError
)


# NOTE: Deprecated method names
command = command_format
remote = run_remote
local = run_local
