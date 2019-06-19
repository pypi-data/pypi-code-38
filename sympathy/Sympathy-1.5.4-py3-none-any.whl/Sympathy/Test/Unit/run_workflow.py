# Copyright (c) 2013, Combine Control Systems AB
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of the Combine Control Systems AB nor the
#       names of its contributors may be used to endorse or promote products
#       derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.
# IN NO EVENT SHALL COMBINE CONTROL SYSTEMS AB BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
import os
import sys
import signal
import subprocess

import six


TIMEOUT = 60 * 4
fs_encoding = sys.getfilesystemencoding()


def collect_call(args, timeout, pipe_workflows=None, **kwargs):
    """Calls args, returning the exit code and stdout as a string."""
    if six.PY2:
        args = [arg.encode(fs_encoding)
                if isinstance(arg, six.text_type) else arg
                for arg in args]

    process = None
    exitcode = None

    try:
        close_fds = os.name == 'posix'
        if pipe_workflows:
            pipe_workflows = list(pipe_workflows)
            pipe_workflows.extend(['', ''])

            process = subprocess.Popen(
                args, stdin=subprocess.PIPE, bufsize=1,
                universal_newlines=True, close_fds=close_fds,
                **kwargs)
            process.communicate(input='\n'.join(pipe_workflows))
        else:
            process = subprocess.Popen(
                args, stdin=subprocess.PIPE, bufsize=1,
                universal_newlines=True, close_fds=close_fds,
                **kwargs)
            process.communicate()
        exitcode = process.poll()
    except Exception:
        import traceback
        traceback.print_exc()
        if process is not None:
            if sys.platform == 'win32':
                process.kill()
            else:
                os.kill(-process.pid, signal.SIGKILL)
        raise

    if exitcode != 0:
        raise subprocess.CalledProcessError(
            exitcode, 'Sympathy exited with a non-zero exitcode.')


def run_workflow(args, pipe_workflows=None, **kwargs):
    """
    Returns a function which runs the workflow as required by nosetest's
    generator interface.
    The function will have its description attribute set to the name of the
    workflow. This will be presented as the test name by nosetest.
    """
    launch_path = os.environ.get('SY_LAUNCH')
    if not launch_path:
        launch_path = 'launch.py'

    def inner():
        if pipe_workflows:
            workflows = pipe_workflows
            collect_call(
                [sys.executable, launch_path, 'sy', '-L', '4',
                 '--num_worker_processes', '1', '-'], TIMEOUT, workflows,
                **kwargs)
        else:
            collect_call(
                [sys.executable, launch_path, 'sy', '-L', '4',
                 '--num_worker_processes', '1'] + args, TIMEOUT,
                **kwargs)

    try:
        filename = args[0]
    except IndexError:
        filename = ''

    desc = 'Test WF {}'.format(os.path.basename(filename))
    if six.PY2:
        desc = desc.decode('ascii', errors='ignore')

    inner.description = desc
    return inner
