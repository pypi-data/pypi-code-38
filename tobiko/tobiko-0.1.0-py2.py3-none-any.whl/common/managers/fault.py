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

import os_faults
import yaml

from oslo_log import log

LOG = log.getLogger(__name__)

try:
    FileNotFoundError
except NameError:
    FileNotFoundError = IOError  # pylint: disable=redefined-builtin

CONF_DIR = os.path.expanduser('~')
CONF_FILE = 'os-faults.yaml'


class FaultManager():
    """Manages faults."""

    def __init__(self, test_file):
        self.faults_dir = os.path.join(os.path.dirname(test_file), 'faults')
        faults_f_name = os.path.splitext(os.path.basename(test_file))[0]
        self.faults_file = os.path.join(self.faults_dir, faults_f_name)
        fault_config_f = os.path.join(CONF_DIR, CONF_FILE)
        try:
            self.cloud = os_faults.connect(config_filename=fault_config_f)
            self.cloud.verify()
            self.scenarios = self.get_scenarios()
        except os_faults.ansible.executor.AnsibleExecutionUnreachable:
            LOG.warning("Couldn't verify connectivity to the"
                        " cloud with os-faults configuration")
            self.scenarios = None
        except FileNotFoundError:
            LOG.warning("Couldn't find os-faults configuration file")
            self.scenarios = None

    def get_scenarios(self):
        """Returns list of scenarios based on defined faults.

        A scenario composed out of scenario name and the fault to execute.
        """
        scenarios = []
        with open(self.faults_file, 'r') as stream:
            faults_yaml = yaml.load(stream)
            for fault in faults_yaml:
                scenarios.append((fault['name'], dict(fault=fault['action'])))
            return scenarios

    def run_fault(self, fault):
        """Executes given fault."""
        if self.scenarios:
            os_faults.human_api(self.cloud, fault)
        else:
            LOG.debug("Skipped fault: '{}' since".format(fault),
                      " scenarios are not defined.")
