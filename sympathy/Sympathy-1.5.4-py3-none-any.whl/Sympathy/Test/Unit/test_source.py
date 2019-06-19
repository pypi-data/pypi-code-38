# -*- coding:utf-8 -*-
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
from __future__ import (
    print_function, division, unicode_literals, absolute_import)

import os
import io
import fnmatch
import unittest
import itertools
import sys
import six


FORBIDDEN_DIRS = ['.hg', 'sphinx_rtd_theme']
_fs_encoding = sys.getfilesystemencoding()


class TestSource(unittest.TestCase):
    """
    Run some sanity checks on the source code.

    These tests recursively finds all files ending with .py and not starting
    with a period. They don't descend into subfolders whose names are in
    FORBIDDEN_DIRS or whose names start with a period.
    """
    def _syroot_path(self):
        """Return the path to sympathy root directory."""
        sympathy_root_dir = os.path.join(
            os.path.dirname(__file__), os.pardir, os.pardir, os.pardir)
        if six.PY2:
            sympathy_root_dir = sympathy_root_dir.decode(_fs_encoding)
        return sympathy_root_dir

    def _source_files(self, ending_extensions):
        """
        Returns a generator yielding absolute paths to all relevant python
        source files found in sympathy root folder or any of its subfolders.
        """
        for root, dirs, files in os.walk(self._syroot_path()):
            for ending_extension in ending_extensions:
                for python_file in fnmatch.filter(
                        files, "[!.]*." + ending_extension):
                    absolute_path = os.path.normpath(
                        os.path.join(root, python_file))
                    yield absolute_path

            # Don't descend into any folder whose name is in FORBIDDEN_DIRS
            for forbidden_dir in FORBIDDEN_DIRS:
                if forbidden_dir in dirs:
                    dirs.remove(forbidden_dir)

    def test_lineendings(self):
        """All source files should use unix line endings."""
        files_with_bad_line_endings = []

        for python_file in self._source_files(['py', 'rst']):
            try:
                with io.open(python_file, 'r', encoding='latin1') as source:
                    full_content = source.read()
                    if '\r' in full_content:
                        files_with_bad_line_endings.append(python_file)
            except (IOError, OSError):
                pass

        assert not files_with_bad_line_endings, (
            "Bad line endings in files:\n{}".format(
                "\n".join(files_with_bad_line_endings)))

    def test_preambles(self):
        """All source files should have correct license preambles."""
        root_path = self._syroot_path()
        excluded_files = ['types_lexer.py', 'types_parser.py', 'colormaps.py']
        bsd_excerpt = 'permitted provided that the following conditions'
        gpl_excerpt = 'GNU General Public License'
        gpl_paths = [
            '__main__.py',
            'Sympathy/launch.py',
            'Sympathy/Gui/*',
            'Sympathy/Internal/*',
            'Sympathy/Test/Unit/test_gui/*',
        ]

        files_without_preamble = []
        for python_file in self._source_files(['py']):
            exclude = False
            for file in excluded_files:
                if file in python_file:
                    exclude = True
                    break
            if exclude:
                continue

            rel_python_file = os.path.relpath(python_file, root_path)
            correct_license = 'bsd'
            for gpl_path in gpl_paths:
                if fnmatch.fnmatch(
                        rel_python_file, os.path.normpath(gpl_path)):
                    correct_license = 'gpl'
            found_preamble = None
            checked_any_lines = False
            try:
                with io.open(python_file, 'r', encoding='latin1') as source:
                    for line in itertools.islice(source, 10):
                        checked_any_lines = True
                        if bsd_excerpt in line:
                            found_preamble = 'bsd'
                        elif gpl_excerpt in line:
                            found_preamble = 'gpl'
                    if checked_any_lines and found_preamble != correct_license:
                        files_without_preamble.append(rel_python_file)
            except (IOError, OSError):
                pass

        assert not files_without_preamble, (
            "Missing or incorrect license preamble in files:\n{}".format(
                "\n".join(files_without_preamble)))


if __name__ == '__main__':
    unittest.main()
