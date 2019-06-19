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
import sys
import re
import os.path
import subprocess
import tempfile
import shutil

launch_path = os.environ.get('SY_LAUNCH')

if not launch_path:
    launch_path = 'launch.py'

launch_path = os.path.join(os.path.dirname(__file__), '..', '..', launch_path)
warnings_regex = re.compile(b'build succeeded(?:, )?([0-9]+ warnings?)?.')


def test_generate_documentation():
    tempdir = tempfile.mkdtemp()
    try:
        args = [sys.executable, launch_path, 'sy', '-L5',
                '--generate_documentation', tempdir]
        output = subprocess.check_output(
            args, stderr=subprocess.STDOUT)
        match = warnings_regex.search(output)
        if match is not None and match.group(1):
            print(output)
            raise AssertionError(
                'Documentation failed due to: {}.'.format(match.group(1)))
    finally:
        try:
            shutil.rmtree(tempdir)
        except (OSError, IOError):
            pass


test_generate_documentation.slow = 1
