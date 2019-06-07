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

from collections import namedtuple
import os

from ansible.executor import playbook_executor
from ansible.inventory.manager import InventoryManager
from ansible.parsing.dataloader import DataLoader
from ansible.vars.manager import VariableManager
from oslo_log import log

from tobiko import config
from tobiko.openstack import keystone


LOG = log.getLogger(__name__)
CONF = config.CONF


TEMPLATE_SUFFIX = ".yaml"


class AnsibleManager(object):
    """Manages Ansible entities."""

    def __init__(self, playbooks_dir):
        self.playbooks_dir = playbooks_dir
        self.loader = DataLoader()
        self.inventory = InventoryManager(loader=self.loader,
                                          sources='localhost,')
        self.variable_manager = VariableManager(loader=self.loader,
                                                inventory=self.inventory)
        self.options = self.get_options()
        self.passwords = dict(vault_pass='secret')

    def get_playbooks_names(self, strip_suffix=False):
        """Returns a list of all the files in playbooks dir."""
        playbooks = []
        for (_, _, files) in os.walk(self.playbooks_dir):
            playbooks.extend(files)
        if strip_suffix:
            playbooks = [
                f[:-len(TEMPLATE_SUFFIX)] for f in playbooks]
        return playbooks

    def get_options(self):
        """Returns namedtuple of Ansible options."""
        Options = namedtuple('Options', ['connection', 'module_path',
                                         'forks', 'become', 'become_method',
                                         'become_user', 'check', 'diff',
                                         'listhosts', 'listtasks',
                                         'listtags', 'syntax'])

        options = Options(connection='local', module_path=['/to/mymodules'],
                          forks=10, become=None, become_method=None,
                          become_user=None, check=False, diff=False,
                          listhosts=False,
                          listtasks=False, listtags=False, syntax=False)

        return options

    def run_playbook(self, playbook, mode='create'):
        """Executes given playbook."""
        playbook_path = self.playbooks_dir + '/' + playbook

        credentials = keystone.default_keystone_credentials()
        extra_vars = {'mode': mode,
                      'auth_url': credentials.auth_url,
                      'username': credentials.username,
                      'project_name': credentials.project_name,
                      'password': credentials.project_name.password,
                      'image': CONF.tobiko.nova.image,
                      'flavor': CONF.tobiko.nova.flavor}

        self.variable_manager.extra_vars = extra_vars

        pb_executor = playbook_executor.PlaybookExecutor(
            playbooks=[playbook_path],
            inventory=self.inventory,
            variable_manager=self.variable_manager,
            loader=self.loader,
            options=self.options,
            passwords=self.passwords)

        pb_executor.run()
