# -*- coding: utf-8 -*-
# Copyright (c) 2017, Combine Control Systems AB
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
from __future__ import print_function

import argparse
import contextlib
import os
import six
import sys


if sys.stdout is None or sys.stdout.fileno() < 0:
    devnull = open(os.devnull, 'w')
    sys.stdout = devnull

if sys.stderr is None or sys.stderr.fileno() < 0:
    devnull = open(os.devnull, 'w')
    sys.stderr = devnull


@contextlib.contextmanager
def quiet():
    old_stderr = sys.stderr
    devnull = open(os.devnull, 'w')
    sys.stderr = devnull
    old_stdout = sys.stdout
    devnull = open(os.devnull, 'w')
    sys.stdout = devnull
    try:
        yield
    finally:
        sys.stdout = old_stdout
        sys.stderr = old_stderr


root = os.path.abspath(os.path.join(
    os.path.dirname(__file__), os.pardir, os.pardir))

sys.path.append(os.path.join(root, 'Python'))

cd = six.moves.getcwd()


def generate_ply():
    """Import ply-modules to trigger generation of lexer and parser files."""
    print('Generating type parser and lexer modules...')
    try:
        # Build type parser and lexer.
        os.chdir(os.path.join(root, 'Python', 'sympathy', 'types'))
        import sympathy.types.types  # NOQA
        import sympathy.types.types_lexer  # NOQA
        import sympathy.types.types_parser  # NOQA
    finally:
        os.chdir(cd)


def compile_all():
    import compileall
    dir = os.path.abspath(os.path.join(root, os.pardir))
    print('Compiling *.py files under {}... (this could take a few minutes.)'
          ''.format(dir))
    with quiet():
        compileall.compile_dir(dir, quiet=True, force=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('mode', choices=['all', 'compile-all', 'generate-all'],
                        default='all', nargs='?')
    parsed = parser.parse_args()

    if parsed.mode == 'all':
        generate_ply()
        compile_all()
    elif parsed.mode == 'compile-all':
        compile_all()
    elif parsed.mode == 'generate-all':
        generate_ply()
