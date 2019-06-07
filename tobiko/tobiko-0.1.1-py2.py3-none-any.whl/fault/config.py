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

import os

import jinja2

from oslo_log import log

from tobiko.fault import constants as fault_const
from tobiko.common.utils import file as file_utils
from tobiko.openstack import nova


LOG = log.getLogger(__name__)


class FaultConfig(object):
    """Responsible for managing faults configuration."""

    DEFAULT_CONF_PATH = os.path.expanduser('~/.config/openstack')
    DEFAULT_CONF_NAME = "os-faults.yml"
    DEFAULT_CONF_FILE = os.path.join(DEFAULT_CONF_PATH, DEFAULT_CONF_NAME)

    def __init__(self, conf_file):
        self.templates_dir = os.path.join(os.path.dirname(__file__),
                                          'templates')
        if conf_file:
            self.conf_file = conf_file
        else:
            conf_file = self.DEFAULT_CONF_FILE
            if os.path.isfile(conf_file):
                self.conf_file = conf_file
            else:
                self.conf_file = self.generate_config_file()

    def generate_config_file(self):
        """Generates os-faults configuration file."""
        LOG.info("Generating os-fault configuration file.")
        file_utils.makedirs(self.DEFAULT_CONF_PATH)
        rendered_conf = self.get_rendered_configuration()
        with open(self.DEFAULT_CONF_FILE, "w") as f:
            f.write(rendered_conf)
        return self.DEFAULT_CONF_FILE

    def get_rendered_configuration(self):
        """Returns rendered os-fault configuration file."""
        j2_env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(self.templates_dir),
            trim_blocks=True)
        template = j2_env.get_template('os-faults.yml.j2')
        nodes = self.get_nodes()
        return template.render(nodes=nodes,
                               services=fault_const.SERVICES,
                               containers=fault_const.CONTAINERS)

    def get_nodes(self):
        """Returns a list of dictionaries with nodes name and address."""
        client = nova.get_nova_client()
        return [{'name': server.name,
                 'address': server.addresses['ctlplane'][0]['addr']}
                for server in client.servers.list()]
