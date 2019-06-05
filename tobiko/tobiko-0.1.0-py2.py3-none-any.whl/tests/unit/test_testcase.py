# Copyright 2018 Red Hat
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
from __future__ import absolute_import

import os

import tobiko
from tobiko.tests import unit


class TestCasesManagerTest(unit.TobikoUnitTest):

    test_path = os.path.dirname(__file__)

    def setUp(self):
        super(TestCasesManagerTest, self).setUp()

        top_dir = os.path.abspath(self.test_path)
        while os.path.isdir(top_dir) and top_dir != os.path.sep:
            if os.path.isdir(os.path.join(top_dir, '.stestr')):
                break
            top_dir = os.path.dirname(top_dir)
        else:
            raise self.fail("Unable to find '.stestr' directory")
        self.top_dir = top_dir
        self.repo_url = top_dir

        # Move to top directory
        original_work_dir = os.getcwd()
        os.chdir(self.top_dir)
        self.addCleanup(os.chdir, original_work_dir)

    def test_discover_testcases(self):
        testcases = tobiko.discover_testcases(test_path=self.test_path,
                                              top_dir=self.top_dir,
                                              repo_url=self.repo_url,
                                              filters=[self.id()])
        self.assertIn(self.id(), testcases)
