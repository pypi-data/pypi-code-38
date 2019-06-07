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

import tobiko
from tobiko import config
from tobiko.shell import ping
from tobiko.shell import ssh
from tobiko.shell import sh
from tobiko.openstack import heat
from tobiko.openstack import neutron
from tobiko.openstack import stacks
from tobiko.tests import base
from tobiko.tests.scenario.neutron import _stacks


CONF = config.CONF


class FloatingIPFixture(heat.HeatStackFixture):
    """Heat stack for testing a floating IP instance
    """

    #: Heat template file
    template = _stacks.heat_template_file('floating_ip.yaml')

    #: Floating IP network where the Neutron floating IP is created
    floating_network = CONF.tobiko.neutron.floating_network

    #: Glance image used to create a Nova server instance
    image = CONF.tobiko.nova.image

    #: Nova flavor used to create a Nova server instance
    flavor = CONF.tobiko.nova.flavor

    #: Username used to login to Nova server instance
    username = CONF.tobiko.nova.username

    @property
    def internal_network(self):
        """Internal network where the Nova server instance is connected

        """
        return self.internal_network_stack.outputs.network_id

    # --- required fixtures ---

    #: Heat stack for creating internal network with a router to floating
    #:  network
    internal_network_stack = tobiko.required_setup_fixture(
        _stacks.InternalNetworkFixture)

    # --- class parameters ---
    #: Whenever port security on internal network is enable
    key_pair_stack = tobiko.required_setup_fixture(
        stacks.NovaKeyPairStackFixture)
    port_security_enabled = False

    #: Security groups to be associated to network ports
    security_groups = []

    def setup_parameters(self):
        """Setup template parameters

        """
        super(FloatingIPFixture, self).setup_parameters()
        if self.port_security_enabled:
            self.setup_port_security()

    @neutron.skip_if_missing_networking_extensions('port-security')
    def setup_port_security(self):
        """Setup port security template parameters

        """
        self.parameters.update(
            port_security_enabled=self.port_security_enabled,
            security_groups=self.security_groups or [])

    @property
    def key_name(self):
        return self.key_pair_stack.outputs.key_name

    @property
    def server_name(self):
        return self.outputs.server_name

    @property
    def floating_ip_address(self):
        return self.outputs.floating_ip_address

    @property
    def ssh_client(self):
        return ssh.ssh_client(host=self.floating_ip_address,
                              username=self.username)

    @property
    def ssh_command(self):
        return ssh.ssh_command(host=self.floating_ip_address,
                               username=self.username)


class FloatingIPTest(base.TobikoTest):
    """Tests connectivity to Nova instances via floating IPs"""

    #: Resources stack with floating IP and Nova server
    floating_ip_stack = tobiko.required_setup_fixture(FloatingIPFixture)

    @property
    def floating_ip_address(self):
        """Floating IP address"""
        return self.floating_ip_stack.floating_ip_address

    @property
    def server_name(self):
        """Floating IP address"""
        return self.floating_ip_stack.server_name

    @property
    def ssh_client(self):
        """Floating IP address"""
        return self.floating_ip_stack.ssh_client

    def test_ssh(self):
        """Test SSH connectivity to floating IP address"""
        result = sh.execute("hostname", ssh_client=self.ssh_client)
        self.assertEqual([self.server_name.lower()],
                         str(result.stdout).splitlines())

    def test_ssh_from_cli(self):
        """Test SSH connectivity to floating IP address from CLI"""
        result = sh.execute(self.floating_ip_stack.ssh_command + ['hostname'])
        self.assertEqual([self.server_name.lower()],
                         str(result.stdout).splitlines())

    def test_ping(self):
        """Test ICMP connectivity to floating IP address"""
        ping.ping_until_received(self.floating_ip_address).assert_replied()

    # --- test port-security extension ---------------------------------------

    @neutron.skip_if_missing_networking_extensions('port-security')
    def test_port_security_enabled_port_attribute(self):
        """Test port security enabled port attribute"""
        self.assertEqual(self.expected_port_security_enabled,
                         self.observed_port_security_enabled)

    @property
    def expected_port_security_enabled(self):
        """Expected port security enabled value"""
        return self.floating_ip_stack.port_security_enabled

    @property
    def observed_port_security_enabled(self):
        """Actual MTU value for internal network"""
        return self.floating_ip_stack.outputs.port_security_enabled

    # --- test security_group extension --------------------------------------

    @neutron.skip_if_missing_networking_extensions('security-group')
    def test_security_groups_port_attribute(self):
        """Test security groups port attribute"""
        self.assertEqual(self.expected_security_groups,
                         self.observed_security_groups)

    @property
    def expected_security_groups(self):
        """Expected port security groups"""
        return set(self.floating_ip_stack.security_groups)

    @property
    def observed_security_groups(self):
        """Actual port security group"""
        return set(self.floating_ip_stack.outputs.security_groups)

    # --- test net-mtu and net-mtu-writable extensions -----------------------

    @neutron.skip_if_missing_networking_extensions('net-mtu')
    def test_ping_with_net_mtu(self):
        """Test connectivity to floating IP address with MTU sized packets"""
        # Wait until it can reach remote port with maximum-sized packets
        ping.ping(self.floating_ip_address,
                  until=ping.RECEIVED,
                  packet_size=self.observed_net_mtu,
                  fragmentation=False).assert_replied()

        # Verify it can't reach remote port with over-sized packets
        ping.ping(self.floating_ip_address,
                  packet_size=self.observed_net_mtu + 1,
                  fragmentation=False,
                  count=5,
                  check=False).assert_not_replied()

    @neutron.skip_if_missing_networking_extensions('net-mtu-writable')
    def test_mtu_net_attribute(self):
        """Test 'mtu' network attribute"""
        if self.expected_net_mtu:
            self.assertEqual(self.expected_net_mtu,
                             self.observed_net_mtu)

    @property
    def expected_net_mtu(self):
        """Expected MTU value for internal network"""
        return self.floating_ip_stack.internal_network_stack.mtu

    @property
    def observed_net_mtu(self):
        """Actual MTU value for internal network"""
        return self.floating_ip_stack.internal_network_stack.outputs.mtu


@neutron.skip_if_missing_networking_extensions('port-security')
class FloatingIPWithPortSecurityFixture(FloatingIPFixture):
    """Heat stack for testing a floating IP instance with port security enabled

    """

    #: Resources stack with security group to allow ping Nova servers
    security_groups_stack = tobiko.required_setup_fixture(
        _stacks.SecurityGroupsFixture)

    #: Enable port security on internal network
    port_security_enabled = True

    @property
    def security_groups(self):
        """List with ICMP security group"""
        return [self.security_groups_stack.outputs.ssh_security_group_id]


@neutron.skip_if_missing_networking_extensions('port-security',
                                               'security-group')
class FloatingIPWithPortSecurityTest(FloatingIPTest):
    """Tests connectivity to Nova instances via floating IPs with port security

    """

    #: Resources stack with floating IP and Nova server with port security
    floating_ip_stack = tobiko.required_setup_fixture(
        FloatingIPWithPortSecurityFixture)

    def test_ping(self):
        """Test connectivity to floating IP address"""
        # Wait for server instance to get ready by logging in
        tobiko.setup_fixture(self.ssh_client)

        # Check can't reach secured port via floating IP
        ping.ping(self.floating_ip_address,
                  count=5,
                  check=False).assert_not_replied()

    @neutron.skip_if_missing_networking_extensions('net-mtu')
    def test_ping_with_net_mtu(self):
        """Test connectivity to floating IP address"""
        # Wait for server instance to get ready by logging in
        tobiko.setup_fixture(self.ssh_client)

        # Verify it can't reach secured port with maximum-sized packets
        ping.ping(self.floating_ip_address,
                  packet_size=self.observed_net_mtu,
                  fragmentation=False,
                  count=5,
                  check=False).assert_not_replied()

        # Verify it can't reach secured port with over-sized packets
        ping.ping(self.floating_ip_address,
                  packet_size=self.observed_net_mtu + 1,
                  fragmentation=False,
                  count=5,
                  check=False).assert_not_replied()


class FloatingIPWithICMPSecurityGroupFixture(
        FloatingIPWithPortSecurityFixture):
    """Heat stack for testing a floating IP instance with security groups

    """

    @property
    def security_groups(self):
        """List with ICMP security group"""
        return [self.security_groups_stack.outputs.ssh_security_group_id,
                self.security_groups_stack.outputs.icmp_security_group_id]


@neutron.skip_if_missing_networking_extensions('port-security',
                                               'security-group')
class FloatingIPWithICMPSecurityGroupTest(FloatingIPTest):
    """Tests connectivity via floating IP with security ICMP security group

    """
    #: Resources stack with floating IP and Nova server to ping
    floating_ip_stack = tobiko.required_setup_fixture(
        FloatingIPWithICMPSecurityGroupFixture)


class FloatingIPWithNetMtuWritableFixture(FloatingIPFixture):
    """Heat stack for testing setting MTU value to internal network

    """

    #: Heat stack for creating internal network with custom MTU value
    internal_network_stack = tobiko.required_setup_fixture(
        _stacks.InternalNetworkWithNetMtuWritableFixture)


@neutron.skip_if_missing_networking_extensions('net-mtu-writable')
class FlatingIpWithMtuWritableTest(FloatingIPTest):
    """Tests connectivity via floating IP with modified MTU value

    """

    #: Resources stack with floating IP and Nova server
    floating_ip_stack = tobiko.required_setup_fixture(
        FloatingIPWithNetMtuWritableFixture)
