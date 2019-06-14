import sys
import os
import subprocess

CREATE_NO_WINDOW = 0x08000000
CREATE_NEW_PROCESS_GROUP = 0x00000200


def run_in_background(cmd_list):
    """Run a process in the background, cmd_list is the list of commands to execute"""
    close_fds = False

    if sys.platform != 'win32':
        cmd_list.insert(0, 'nice')
        cmd_list.insert(0, 'nohup')
        close_fds = True
    else:
        # /i so that windows doesn't create "%SYSTEM_DRIVE%" folder
        cmd_list.insert(0, 'start /b /i')

    cmd = ' '.join(cmd_list)
    if sys.platform != 'win32':
        stdout = open(os.path.devnull, 'a')
        stderr = open(os.path.devnull, 'a')
        subprocess.Popen(args=cmd, stdin=subprocess.PIPE, stdout=stdout,
                         stderr=stderr, shell=True, close_fds=close_fds, preexec_fn=os.setpgrp)
    else:
        # Windows specific instructions
        # https://docs.microsoft.com/en-us/windows/desktop/ProcThread/process-creation-flags
        subprocess.Popen(args=cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE, shell=True, close_fds=close_fds,
                         creationflags=CREATE_NO_WINDOW | CREATE_NEW_PROCESS_GROUP)
