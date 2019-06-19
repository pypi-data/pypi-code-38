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
from __future__ import (print_function, division, unicode_literals,
                        absolute_import)
import os
import shutil
import glob
import coverage
import fnmatch

APP_DIR = os.environ['SY_APPLICATION_DIR']
COVERAGE_DIR = os.path.join(APP_DIR, 'Test/Coverage')
COVERAGE = {
    'data_dir': os.path.join(COVERAGE_DIR, 'data'),
    'html_dir': os.path.join(COVERAGE_DIR, 'html'),
    'config': os.path.join(COVERAGE_DIR, 'config'),
    'summary': os.path.join(COVERAGE_DIR, 'summary.txt'),
    'data_file': os.path.join(COVERAGE_DIR, 'data/coverage.dat'),
    'ref_file': os.path.join(COVERAGE_DIR, 'reference.txt')}


def prepare_coverage(dirs):
    """Clear coverage folders and set necessary environment variables"""
    dirs = (
        [os.path.abspath(os.path.join(APP_DIR, '..'))] if not len(dirs) else
        [os.path.abspath(os.path.join(APP_DIR, dir_)) for dir_ in dirs])

    if os.path.isdir(COVERAGE['data_dir']):
        shutil.rmtree(COVERAGE['data_dir'])
    os.mkdir(COVERAGE['data_dir'])
    if os.path.isfile(COVERAGE['summary']):
        os.remove(COVERAGE['summary'])
    if os.path.isdir(COVERAGE['html_dir']):
        shutil.rmtree(COVERAGE['html_dir'])
    os.environ['COVERAGE_PROCESS_START'] = COVERAGE['config']
    os.environ['COVERAGE_DATA'] = COVERAGE['data_file']
    os.environ['COVERAGE_DIRS'] = ', '.join(dirs)


class CoverageTester(object):
    def __init__(self):
        self.coverage = coverage.Coverage(
            config_file=COVERAGE['config'],
            data_file=COVERAGE['data_file'],
            source=os.environ['COVERAGE_DIRS'].split(', '))

    def start_coverage(self):
        self.coverage.start()

    def stop_coverage(self):
        self.coverage.stop()
        self.coverage.save()

    def report_coverage(self):
        """Combine coverage data from all tasks and create the reports"""
        self.coverage.combine([COVERAGE['data_dir']])
        self.coverage.save()
        combined = glob.glob(COVERAGE['data_file'] + '*')[0]
        os.rename(combined, os.path.join(
            COVERAGE_DIR, os.path.basename(COVERAGE['data_file'])))
        os.rmdir(COVERAGE['data_dir'])
        os.mkdir(COVERAGE['html_dir'])
        try:
            with open(COVERAGE['summary'], 'w') as file:
                self.coverage.report(file=file, show_missing=False)
                self.coverage.html_report(directory=COVERAGE['html_dir'])
        except coverage.misc.CoverageException:
            print('The selected folder(s) does not contain any files which '
                  'were touched by the coverage test.')
        _coverage_reference()


def _coverage_reference():
    """Gather all relevant python files and create a reference. Diff it
    to the summary report to detect files thar are not tested at all.
    """
    src_dirs = [
        os.path.join(APP_DIR, '../Library/Common'),
        os.path.join(APP_DIR, '../Library/Library'),
        os.path.join(APP_DIR, 'Gui'),
        os.path.join(APP_DIR, 'Internal'),
        os.path.join(APP_DIR, 'Python')]
    excluded_files = [
        '__init__.py',
        'launch.py',
        'types_lexer.py',
        'types_parser.py',
        'coverage.py',
        '__main__.py',
        'p_sympathy.py',
        'sympathygui.py',
        'python_startup.py',
        'unit.py',
        'validate.py']

    py_files = []
    for directory in src_dirs:
        for root, dirnames, filenames in os.walk(directory):
            for filename in fnmatch.filter(filenames, '*.py'):
                if filename in excluded_files:
                    continue
                root = root.split('/../Library')
                if len(root) > 1:
                    root = 'Library' + root[1]
                else:
                    root = root[0].split('/Sympathy')
                    if len(root) > 1:
                        root = 'Sympathy' + root[1]
                    else:
                        root = root[0]
                py_files.append(os.path.join(root, filename))

    line_end = '0      0      0%\n'
    nbr_of_spaces = len(max(py_files, key=len)) + 6
    start = 'Name{}Stmts   Miss   Cover\n'.format(
        ''.join([' '] * (nbr_of_spaces - 8)))
    end = '{}\nTOTAL{}{}'.format(
        ''.join(['-'] * (len(start) - 1)),
        ''.join([' '] * (nbr_of_spaces - 5)),
        line_end)
    start += ''.join(['-'] * (len(start) - 1)) + '\n'
    with open(COVERAGE['ref_file'], 'w') as file:
        file.write(start)
        for py_file in sorted(py_files):
            file.write(
                '{}{}{}'.format(
                    py_file,
                    ''.join([' '] * (nbr_of_spaces - len(py_file))),
                    line_end))
        file.write(end)
