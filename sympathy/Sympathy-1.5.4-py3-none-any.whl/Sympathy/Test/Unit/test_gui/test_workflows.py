# -*- coding:utf-8 -*-
# This file is part of Sympathy for Data.
# Copyright (c) 2013, 2017 Combine Control Systems AB
#
# Sympathy for Data is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Sympathy for Data is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Sympathy for Data.  If not, see <http://www.gnu.org/licenses/>.
import os
import unittest
import fnmatch
import sys
from sympathy.platform import workflow_converter
from Gui import interactive
from sympathy.platform import version_support as vs


_absdir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(
    os.path.join(_absdir, os.pardir))

import run_workflow

PLATFORM_TEST_DIR = os.path.join(_absdir, os.pardir, os.pardir)
fs_encoding = sys.getfilesystemencoding()


def flow_should_run(flow_path):
    with open(flow_path, 'rb') as f:
        flow_dict = workflow_converter.XMLToJson(f).dict()
        return 'NO_TEST' not in flow_dict.get('environment', {})


def test_workflows():
    """
    Test all workflows in library workflow test directories.
    Test workflows using command line tool sy.
    """
    workflow_test_paths = [
        os.path.join(vs.str_(library_path, fs_encoding), 'Test', 'Workflow')
        for library_path in interactive.available_libraries()]
    workflow_test_paths.append(
        os.path.join(PLATFORM_TEST_DIR, 'Workflow'))
    workflows = []

    for test_dir in workflow_test_paths:
        for dirpath, dirnames, filenames in os.walk(test_dir):
            for filename in fnmatch.filter(filenames, '*.syx'):
                flow = os.path.join(dirpath, filename)
                if flow_should_run(flow):
                    workflows.append(flow)

    run_workflow.run_workflow([], workflows)()


def test_example_workflows():
    """
    Test all workflows in library example directories.
    Test workflows using command line tool sy.
    """
    workflow_test_paths = [
        os.path.join(vs.str_(library_path, fs_encoding), 'Examples')
        for library_path in interactive.available_libraries()]
    workflows = []
    for test_dir in workflow_test_paths:
        for dirpath, dirnames, filenames in os.walk(test_dir):
            for filename in fnmatch.filter(filenames, '*.syx'):
                flow = os.path.join(dirpath, filename)
                if flow_should_run(flow):
                    workflows.append(flow)

    run_workflow.run_workflow([], workflows)()


test_example_workflows.slow = 1

if __name__ == '__main__':
    unittest.main()
