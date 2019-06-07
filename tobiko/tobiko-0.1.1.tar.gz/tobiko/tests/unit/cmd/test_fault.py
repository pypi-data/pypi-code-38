# Copyright (c) 2018 Red Hat
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

import argparse
import sys

from tobiko.cmd import fault as _fault
from tobiko.tests import unit


class FaultCMDTest(unit.TobikoUnitTest):

    command_name = 'tobiko-fault'
    command_class = _fault.FaultCMD
    default_fault = ["some_fault"]

    def setUp(self):
        super(FaultCMDTest, self).setUp()
        self.mock_error = self.patch(argparse.ArgumentParser, 'error',
                                     side_effect=self.fail)

    def patch_argv(self, arguments=None):
        """Patch argv"""
        arguments = list(arguments or [])
        if not arguments:
            arguments = self.default_fault
        return self.patch(sys, 'argv',
                          [self.command_name] + arguments)

    def test_init(self, arguments=None):
        self.patch_argv(arguments=arguments)
        command = self.command_class()
        self.mock_error.assert_not_called()
        args = command.args
        self.assertIsNotNone(args)
