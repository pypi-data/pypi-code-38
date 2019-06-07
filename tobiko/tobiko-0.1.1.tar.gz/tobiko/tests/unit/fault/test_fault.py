# Copyright (c) 2019 Red Hat, Inc.
#
# All Rights Reserved.
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

from tobiko.tests import unit
from tobiko.fault import executor


class FaultTest(unit.TobikoUnitTest):

    conf_file = "/some/conf/file"
    fault = "some_fault"

    def setUp(self):
        super(FaultTest, self).setUp()
        self.fault_exec = executor.FaultExecutor(conf_file=self.conf_file)

    def test_init(self):
        self.assertEqual(self.fault_exec.config.conf_file, self.conf_file)
        self.assertEqual(self.fault_exec.cloud, None)
