# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""
Functionality to execute a function in a child process created using "spawn".

This file contains the client portion.
"""
import datetime
import dill
import os
import re
import shutil
import signal
import subprocess
import sys
import tempfile

from automl.client.core.common import killable_subprocess
from automl.client.core.common import limit_function_call_exceptions as lfce


def run_in_proc(timeout, f, args, **kwargs):
    """Invoke f with the given arguments in a new process."""
    process = None
    try:
        # Create a folder for temporary files, used to communicate across
        # processes and to persist stdout/stderr.
        tempdir = tempfile.mkdtemp()
        timestamp = datetime.datetime.now().strftime('%H%M%S')
        file_name_prefix = "automl_" + timestamp + "_"

        def create_file(name):
            """Create a file used for inter-process communication."""
            f = os.path.join(tempdir, file_name_prefix + name)
            open(f, 'a').close()
            return f

        # Create all files used for data exchange across client and server.
        config_file_name = create_file("config")
        input_file_name = create_file("input")
        output_file_name = create_file("output")
        stdout_file_name = create_file("stdout")
        stderr_file_name = create_file("stderr")

        # Create a configuration object to pass to the target process. This
        # configuration is applied prior to deserialization of the input,
        # thus it can influence the environment code gets loaded in.
        config = {
            'path': sys.path,
        }

        # Use dill to store configuration information needed to set up
        # the target process.
        with open(config_file_name, 'wb') as file:
            dill.dump(config, file, protocol=dill.HIGHEST_PROTOCOL)

        # Use dill to store the function and arguments to run in the target
        # process.
        with open(input_file_name, 'wb') as file:
            dill.dump((f, args, kwargs), file, protocol=dill.HIGHEST_PROTOCOL)

        # Locate the Python executable, working directory, our sibling
        # spawn_server, and the environment variables.
        python_executable = sys.executable
        cwd = os.getcwd()
        curdir = os.path.dirname(__file__)
        srv_script_file = os.path.join(curdir, "spawn_server.py")
        env = os.environ.copy()

        # Open files to redirect stdout and stderr to.
        with open(stdout_file_name, 'w') as stdout:
            with open(stderr_file_name, 'w') as stderr:
                # Spawn child process and wait for completion.
                cmd = [
                    python_executable,
                    srv_script_file,
                    config_file_name,
                    input_file_name,
                    output_file_name]

                process = subprocess.Popen(cmd, cwd=cwd, env=env, stdout=stdout, stderr=stderr)
                try:
                    returncode = process.wait(timeout)
                except subprocess.TimeoutExpired:
                    # Attempt to kill the process and its children, and report
                    # the exception.
                    killable_subprocess.kill_process_tree_in_linux(process.pid)
                    raise

        if returncode < 0:
            errorcode = -returncode
            errorname = signal.Signals(errorcode).name

            if sys.platform == 'linux' and errorcode == signal.SIGKILL:
                # On Linux, the kernel memory allocator overcommits memory by default. If we attempt to
                # actually use all that memory, then the OOM killer will kick in and send SIGKILL. We
                # have to check the kernel logs to see if this is the case.
                check_linux_oom_killed(process.pid)

            raise lfce.SubprocessException(
                'Subprocess (pid {}) killed by unhandled signal {} ({})'.format(
                    process.pid, errorcode, errorname))
        elif returncode > 0:
            # Ideally we would like to capture stderr here since it will have the real exception
            # when the returncode is 1, but it might have PII.
            with open(stderr_file_name, 'r') as stderr:
                sys.stderr.write('Subprocess stderr: \n{}'.format('\n'.join(stderr.readlines())))
            raise lfce.SubprocessException(
                'Subprocess (pid {}) exited with non-zero exit status {}'.format(
                    process.pid, returncode))

        # Read the output and use dill to deserialize the result into a
        # (value, error) pair.
        with open(output_file_name, 'rb') as output_file:
            return dill.load(output_file)

    finally:
        if process is not None:
            for i in range(5):
                try:
                    # poll() returns None if the process is still running (no returncode)
                    if process.poll() is None:
                        killable_subprocess.kill_process_tree_in_linux(process.pid)
                    break
                except Exception:
                    pass
        # Clean up the temporary files.
        if tempdir is not None:
            shutil.rmtree(tempdir)


def check_linux_oom_killed(pid: int) -> None:
    """
    Check to see if the Linux out of memory killer sent SIGKILL to this process. Raise an exception if killed by OOM.

    :param pid: process pid
    :return: None
    """
    oom_killed = False
    mem_usage = 0
    try:
        out = subprocess.run(['dmesg', '-l', 'err'],
                             stdout=subprocess.PIPE, universal_newlines=True)
        log_lines = out.stdout.strip().lower().split('\n')
        for line in log_lines:
            if 'out of memory: kill process {}'.format(pid) in line:
                oom_killed = True
            else:
                match = re.search(r'killed process {} .+? anon-rss:(\d+)kb'.format(pid), line)
                if match is not None:
                    mem_usage = int(match.group(1)) * 1024
    except Exception:
        pass

    if oom_killed:
        raise lfce.MemorylimitException(mem_usage)
