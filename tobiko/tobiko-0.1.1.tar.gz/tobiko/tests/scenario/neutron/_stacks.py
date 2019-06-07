# Copyright (c) 2019 Red Hat
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

import os

from tobiko import config
from tobiko.openstack import heat
from tobiko.openstack import neutron


CONF = config.CONF


TEMPLATE_DIRS = [os.path.join(os.path.dirname(__file__), 'templates')]


def heat_template_file(template_file):
    """Fixture to load template files from templates directory

    Return fixtures to loads templates from
    'tobiko/tests/scenario/neutron/templates' directory
    """
    return heat.heat_template_file(template_file=template_file,
                                   template_dirs=TEMPLATE_DIRS)


class InternalNetworkFixture(heat.HeatStackFixture):
    """Heat stack for creating internal network with a router to external

    """

    #: Heat template file
    template = heat_template_file('internal_network.yaml')

    #: Floating IP network where the Neutron floating IP is created
    floating_network = CONF.tobiko.neutron.floating_network

    #: Disable port security by default for new network ports
    port_security_enabled = False

    #: whenever has net-mtu networking extension
    @property
    def has_net_mtu(self):
        return neutron.has_networking_extensions('net-mtu')

    #: Value for maximum transfer unit on the internal network
    mtu = None

    def setup_parameters(self):
        """Setup template parameters

        """
        super(InternalNetworkFixture, self).setup_parameters()
        if self.port_security_enabled or neutron.has_networking_extensions(
                'port-security'):
            self.setup_port_security()
        if self.mtu:
            self.setup_net_mtu_writable()

    @neutron.skip_if_missing_networking_extensions('port-security')
    def setup_port_security(self):
        """Setup default port security value for internal network ports

        """
        self.parameters.update(
            port_security_enabled=self.port_security_enabled)

    @neutron.skip_if_missing_networking_extensions('net-mtu-writable')
    def setup_net_mtu_writable(self):
        """Setup maximum transfer unit size for internal network

        """
        self.parameters.setdefault('value_specs', {}).update(mtu=self.mtu)


class InternalNetworkFixtureWithPortSecurity(InternalNetworkFixture):
    """Heat stack for creating internal network with port security

    """
    #: Enable port security by default for new network ports
    port_security_enabled = True


@neutron.skip_if_missing_networking_extensions('net-mtu-writable')
class InternalNetworkWithNetMtuWritableFixture(InternalNetworkFixture):
    """Heat stack for creating internal network with custom mtu parameter

    """
    #: Force value for internal network maximum transfer unit
    mtu = 1000


@neutron.skip_if_missing_networking_extensions('security-group')
class SecurityGroupsFixture(heat.HeatStackFixture):
    """Heat stack with some security groups

    """
    #: Heat template file
    template = heat_template_file('security_groups.yaml')
