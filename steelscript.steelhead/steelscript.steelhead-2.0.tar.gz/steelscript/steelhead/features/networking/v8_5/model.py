# Copyright (c) 2019 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the MIT License
# accompanying the software ("License").  This software is distributed "AS IS"
# as set forth in the License.

from __future__ import (absolute_import, unicode_literals, print_function,
                        division)

import datetime
import ipaddress
import netaddr
import re

from steelscript.common.interaction.model import model, Model
from steelscript.cmdline.parsers import cli_parse_basic


@model
class NetworkingModel(Model):
    """
    Kauai Networking model for the SteelHead product
    """

    def show_interfaces(self, interface=None, brief=False):
        """
        Return parsed output of 'show interfaces <interface> [brief]':

        .. code-block:: none

            Interface inpath0_0 state
            Up:                 yes
            Interface type:     ethernet
            IP address:         10.11.100.2
            Netmask:            255.255.255.0
            IPv6 link-local address: fe80::5054:ff:fe10:3fe9/64
            MTU:                1500
            HW address:         52:54:00:10:3F:E9
            Traffic status:     Normal
            HW blockable:       no
            Counters cleared date:  2014/01/31 14:28:28

        :param interface:  Optional.  Return just this interface.
        :type interface:  string
        :param brief:  Whether to run just brief output.
        :type brief:  boolean

        :return: List of dictionaries of values returned:

        .. code-block:: python

            {
                'name':         'inpath0_0',
                'ip address':   IPv4Interface('10.11.100.2/24'),
                'ipv6 address': IPv6Interface('fe80::5054:ff:fe10:3fe9/64'),
                'hw address':   EUI('52-54-00-10-3F-E9'),
                'up':           True,
                'rx bytes':     42,
            ...}

        """
        cmd = ["show interfaces"]
        if interface:
            cmd.append(interface)
        if brief:
            cmd.append("brief")

        output = self.cli.exec_command(" ".join(cmd), output_expected=True)
        return self._parse_show_interfaces_dict(output)

    def show_interfaces_configured(self, interface=None):
        """
        Return parsed output of 'show interfaces <interface> configured':

        .. code-block:: none

            Interface inpath0_0 state
            Enabled:            yes
            DHCP:               yes
            Dynamic DNS DHCP:   yes
            DHCPv6:             no
            Dynamic DNS DHCPv6: no
            IP address:         10.11.100.2
            Netmask:            255.255.255.0
            IPv6 address:
            Speed:              auto
            Duplex:             auto
            MTU:                1500

        :param interface:  Optional.  Return just this interface.
        :type interface:  string

        :return: List of dictionaries of values returned

        .. code-block:: python

            {'name':         'inpath0_0',
             'enabled':      True
             'dhcp':         True
             ip address':    IPv4Interface('10.11.100.2/24'),
             'ipv6 address': IPv6Interface('fe80::5054:ff:fe10:3fe9/64'),
             'mtu':          1500,
             ...}
        """
        cmd = ["show interfaces"]
        if interface:
            cmd.append(interface)
        cmd.append("configured")

        output = self.cli.exec_command(" ".join(cmd), output_expected=True)
        return self._parse_show_interfaces_dict(output)

    def _parse_show_interfaces_dict(self, output):
        # Trim the output
        output = output.strip()

        # Split the output for each interface.
        parts = re.split('\n\n(?=Interface)', output)

        return [self._parse_show_interfaces_interface(x) for x in parts]

    def _parse_show_interfaces_interface(self, output):
        # Parses show interface output for a single interface
        # Parse output into a dict, replace certain values with types
        parsed = cli_parse_basic(output)

        # Parse IP address fields
        if 'ip address' in parsed and parsed['ip address'] and \
                'netmask' in parsed and parsed['netmask']:
            parsed['ip address'] = ipaddress.ip_interface(
                "%s/%s" % (parsed['ip address'], parsed['netmask']))
            del parsed['netmask']
        for key in ['ipv6 address', 'ipv6 link-local address']:
            if key in parsed and parsed[key]:
                parsed[key] = ipaddress.ip_interface(parsed[key])

        # Parse MAC Addr fields.
        for key in ['hw address']:
            if key in parsed:
                parsed[key] = netaddr.EUI(parsed[key])

        # Parse Datetime fields.
        for key in ['counters cleared date']:
            if key in parsed:
                # Format:  2014/11/19 16:31:12
                parsed[key] = datetime.datetime.strptime(parsed[key],
                                                         '%Y/%m/%d %H:%M:%S')

        # Add in 'name'
        name = re.match('Interface (\S+) ', output).group(1)
        parsed['name'] = name

        return parsed
