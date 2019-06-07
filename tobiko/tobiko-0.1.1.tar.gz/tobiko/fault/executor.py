# Copyright 2019 Red Hat
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

import sys

from oslo_log import log

import jsonschema
import os_faults

from tobiko.fault.config import FaultConfig

LOG = log.getLogger(__name__)


class FaultExecutor(object):
    """Responsible for executing faults."""

    def __init__(self, conf_file=None, cloud=None):
        self.config = FaultConfig(conf_file=conf_file)
        self.cloud = cloud

    def connect(self):
        """Connect to the cloud using os-faults."""
        try:
            self.cloud = os_faults.connect(
                config_filename=self.config.conf_file)
            self.cloud.verify()
        except os_faults.ansible.executor.AnsibleExecutionUnreachable:
            LOG.warning("Couldn't verify connectivity to the"
                        " cloud with os-faults configuration")
        except jsonschema.exceptions.ValidationError:
            LOG.error("Wrong os-fault configuration format. Exiting...")
            sys.exit(2)

    def execute(self, fault):
        """Executes given fault using os-faults human API."""
        LOG.info("Using %s" % self.config.conf_file)
        self.connect()
        os_faults.human_api(self.cloud, fault)
