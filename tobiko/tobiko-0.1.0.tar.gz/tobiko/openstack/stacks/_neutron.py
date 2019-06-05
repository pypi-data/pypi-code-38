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


import tobiko
from tobiko import config
from tobiko.openstack import heat
from tobiko.openstack.stacks import _hot
from tobiko.openstack.stacks import _nova
from tobiko.shell import ssh


CONF = config.CONF


class NeutronNetworkStackFixture(heat.HeatStackFixture):
    """Heat stack for creating internal network with a router to external

    """

    #: Heat template file
    template = _hot.heat_template_file('neutron/network.yaml')

    #: IPv4 sub-net CIDR
    ipv4_cidr = '190.40.2.0/24'

    @property
    def has_ipv4(self):
        return bool(self.ipv4_cidr)

    #: IPv6 sub-net CIDR
    ipv6_cidr = '2001:db8:1:2::/64'

    @property
    def has_ipv6(self):
        return bool(self.ipv6_cidr)

    #: Floating IP network where the Neutron floating IPs are created
    gateway_network = CONF.tobiko.neutron.floating_network

    @property
    def has_gateway(self):
        return bool(self.gateway_network)


class NeutronServerStackFixture(heat.HeatStackFixture):

    #: Heat template file
    template = _hot.heat_template_file('neutron/server.yaml')

    key_pair_stack = tobiko.required_setup_fixture(
        _nova.NovaKeyPairStackFixture)
    network_stack = tobiko.required_setup_fixture(NeutronNetworkStackFixture)

    #: Glance image used to create a Nova server instance
    image = CONF.tobiko.nova.image

    #: Nova flavor used to create a Nova server instance
    flavor = CONF.tobiko.nova.flavor

    #: username used to login to a Nova server instance
    username = CONF.tobiko.nova.username

    #: password used to login to a Nova server instance
    password = CONF.tobiko.nova.password

    @property
    def key_name(self):
        return self.key_pair_stack.outputs.key_name

    @property
    def network(self):
        return self.network_stack.outputs.network_id

    #: Floating IP network where the Neutron floating IP is created
    floating_network = CONF.tobiko.neutron.floating_network

    @property
    def has_floating_ip(self):
        return bool(self.floating_network)

    @property
    def ssh_client(self):
        return ssh.ssh_client(
            host=self.outputs.floating_ip_address,
            username=self.username,
            password=self.password)

    @property
    def ssh_command(self):
        return ssh.ssh_command(
            host=self.outputs.floating_ip_address,
            username=self.username)
