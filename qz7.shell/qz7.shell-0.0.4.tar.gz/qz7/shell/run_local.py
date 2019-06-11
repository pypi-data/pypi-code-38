"""
Execute shell commands locally.
"""

import subprocess

from qz7.shell.cmdlist import CmdList

def run_local(cmd, *args, **kwargs):
    """
    Run the command described by cmd locally.

    Accepts an instance of CmdList as command.

    For the rest of the arguments and behavior see subprocess.run
    """

    if isinstance(cmd, CmdList):
        shell = kwargs.pop("shell", None)
        if shell is not None:
            cmd.shell = shell
        cmd = cmd.to_popen_args()
        return subprocess.run(cmd, *args, **kwargs)

    return subprocess.run(cmd, *args, **kwargs)
