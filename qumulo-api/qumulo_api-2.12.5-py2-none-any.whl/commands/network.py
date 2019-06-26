# Copyright (c) 2012 Qumulo, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License. You may obtain a copy of
# the License at http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations under
# the License.

import argparse

import qumulo.lib.auth
import qumulo.lib.opts
import qumulo.lib.util
import qumulo.rest.network as network

class ModifyClusterNetworkConfigCommand(qumulo.lib.opts.Subcommand):
    NAME = "network_conf_mod"
    DESCRIPTION = "Modify cluster-wide network config [DEPRECATED]"

    @staticmethod
    def options(parser):
        parser.add_argument("--assigned-by", choices=[ 'DHCP', 'STATIC' ],
            help="Specify mechanism for persistent IP configuration")
        parser.add_argument("--ip-ranges", action="append",
            help="(if STATIC) List of persistent IP ranges to replace the" \
                " current ranges. Can be single addresses or ranges," \
                " comma separated. eg. 10.1.1.20-21 or 10.1.1.20,10.1.1.21")
        group = parser.add_mutually_exclusive_group()
        group.add_argument("--floating-ip-ranges", action="append",
            help="List of floating IP ranges to replace the " \
                " current ranges. Can be single addresses or ranges," \
                " comma separated. eg. 10.1.1.20-21 or 10.1.1.20,10.1.1.21")
        group.add_argument("--clear-floating-ip-ranges",
            action="store_const", const=[], dest="floating_ip_ranges",
            help="Remove all floating ip ranges")
        parser.add_argument("--netmask",
            help="(if STATIC) Netmask in decimal format. eg. 255.255.255.0")
        parser.add_argument("--gateway",
            help="(if STATIC) IPv4 gateway address")
        parser.add_argument("--gateway-ipv6",
            help="(if STATIC) IPv6 gateway address")
        parser.add_argument("--dns-servers", action="append",
            help="(if STATIC) DNS server")
        parser.add_argument("--dns-search-domains", action="append",
            help="(if STATIC) DNS search domain")
        parser.add_argument("--mtu", type=int,
             help="(if STATIC) The maximum transfer unit (MTU) in bytes")
        parser.add_argument("--bonding-mode",
             choices=[ 'ACTIVE_BACKUP', 'IEEE_8023AD' ],
             help="Ethernet bonding mode")

    @staticmethod
    def main(conninfo, credentials, args):
        if (args.assigned_by == 'DHCP'
            and any([args.dns_servers, args.dns_search_domains,
                     args.ip_ranges, args.gateway, args.netmask, args.mtu])):
            raise ValueError(
                "DHCP configuration conflicts with static configuration")

        attributes = {
            key: getattr(args, key) for key in network.V1_SETTINGS_FIELDS
                if getattr(args, key) is not None }

        if not attributes:
            raise ValueError("One or more options must be specified")

        print network.modify_cluster_network_config(conninfo, credentials,
                **attributes)

class MonitorNetworkCommand(qumulo.lib.opts.Subcommand):
    NAME = "network_poll"
    DESCRIPTION = "Poll network status"

    @staticmethod
    def options(parser):
        parser.add_argument("--interface-id", type=int, default=1,
            help=argparse.SUPPRESS)
        parser.add_argument("--node-id", help="Node ID")
        parser.add_argument("--version", type=int, default=2,
            choices=list(range(1, 3)), help="API version to use (default 2)")

    @staticmethod
    def main(conninfo, credentials, args):
        if args.node_id is not None:
            if args.version == 1:
                print network.get_network_status(
                    conninfo, credentials, args.node_id)
            elif args.version == 2:
                print network.get_network_status_v2(
                    conninfo, credentials, args.interface_id, args.node_id)

        else:
            if args.version == 1:
                print network.list_network_status(conninfo, credentials)
            elif args.version == 2:
                print network.list_network_status_v2(conninfo, credentials,
                    args.interface_id)

class GetClusterNetworkConfigCommand(qumulo.lib.opts.Subcommand):
    NAME = "network_conf_get"
    DESCRIPTION = "Get cluster-wide network config [DEPRECATED]"

    @staticmethod
    def main(conninfo, credentials, _args):
        print network.get_cluster_network_config(conninfo, credentials)

class GetInterfaces(qumulo.lib.opts.Subcommand):
    NAME = "network_list_interfaces"
    DESCRIPTION = "List configurations for interfaces on the cluster"

    @staticmethod
    def main(conninfo, credentials, _args):
        print network.list_interfaces(conninfo, credentials)

class GetInterface(qumulo.lib.opts.Subcommand):
    NAME = "network_get_interface"
    DESCRIPTION = "Get configuration for the specified interface"

    @staticmethod
    def options(parser):
        parser.add_argument("--interface-id", type=int, default=1,
            help="The unique ID of the interface")

    @staticmethod
    def main(conninfo, credentials, args):
        print network.get_interface(conninfo, credentials, args.interface_id)

class GetNetworks(qumulo.lib.opts.Subcommand):
    NAME = "network_list_networks"
    DESCRIPTION = "List network configurations"

    @staticmethod
    def options(parser):
        parser.add_argument("--interface-id", type=int, default=1,
            help=argparse.SUPPRESS)

    @staticmethod
    def main(conninfo, credentials, args):
        print network.list_networks(conninfo, credentials, args.interface_id)

class GetNetwork(qumulo.lib.opts.Subcommand):
    NAME = "network_get_network"
    DESCRIPTION = "Get configuration for the specified network"

    @staticmethod
    def options(parser):
        parser.add_argument("--interface-id", type=int, default=1,
            help=argparse.SUPPRESS)
        parser.add_argument("--network-id", type=int, required=True,
            help="The unique ID of the network on the interface")

    @staticmethod
    def main(conninfo, credentials, args):
        print network.get_network(conninfo, credentials,
            args.interface_id, args.network_id)

class ModInterface(qumulo.lib.opts.Subcommand):
    NAME = "network_mod_interface"
    DESCRIPTION = "Modify interface configuration"

    @staticmethod
    def options(parser):
        parser.add_argument("--interface-id", type=int, default=1,
            help=argparse.SUPPRESS)

        parser.add_argument("--default-gateway",
            help="The default IPv4 gateway address")
        parser.add_argument("--default-gateway-ipv6",
            help="The default IPv6 gateway address")
        parser.add_argument("--bonding-mode",
            choices=["ACTIVE_BACKUP", "IEEE_8023AD"],
             help="Ethernet bonding mode")
        parser.add_argument("--mtu", type=int,
            help="The maximum transfer unit (MTU) in bytes of the interface " \
                "and any untagged STATIC network.")

    @staticmethod
    def main(conninfo, credentials, args):
        attributes = {
            key: getattr(args, key) for key in network.V2_INTERFACE_FIELDS
                if getattr(args, key) is not None }

        if not attributes:
            raise ValueError("One or more options must be specified")

        print network.modify_interface(conninfo, credentials, args.interface_id,
            **attributes)

def join_nargs_arg(arg_value):
    """
    Joins nargs argument values and returns a single array containing all the
    individual values.

    If the arg_value is not a list or a list of lists, the arg_value is
    returned.

    This function exists to handle the legacy syntax where arguments used
    "append" over "nargs".
    """
    if type(arg_value) != list:
        return arg_value

    joined = []
    for value_n in arg_value:
        if type(value_n) != list:
            joined.append(value_n)
        else:
            joined.extend(value_n)
    return joined

def parse_comma_deliminated_ip_ranges(ip_ranges):
    nested = [ ranges.split(',') for ranges in ip_ranges ]
    return [ r.strip() for ranges in nested for r in ranges \
                 if r.strip() != '']

class AddNetwork(qumulo.lib.opts.Subcommand):
    NAME = "network_add_network"
    DESCRIPTION = "Add network configuration"

    @staticmethod
    def options(parser):
        parser.add_argument("--interface-id", type=int, default=1,
            help=argparse.SUPPRESS)

        parser.add_argument("--name", required=True, help="Network name")

        parser.add_argument("--assigned-by", default="STATIC",
            help=argparse.SUPPRESS)

        parser.add_argument("--netmask", required=True,
            metavar=("<netmask-or-subnet>"),
            help="(if STATIC) IPv4 or IPv6 Netmask or Subnet CIDR" \
                " eg. 255.255.255.0 or 10.1.1.0/24")

        parser.add_argument("--ip-ranges", nargs="+", action="append",
            metavar=("<address-or-range>"), required=True,
            help="(if STATIC) List of persistent IP ranges to replace the" \
                " current ranges. Can be single addresses or ranges," \
                " comma separated. eg. 10.1.1.20-21 or 10.1.1.20,10.1.1.21")

        parser.add_argument("--floating-ip-ranges", nargs="+", default=[],
            action="append", metavar=("<address-or-range>"),
            help="(if STATIC) List of floating IP ranges to replace the" \
                " current ranges. Can be single addresses or ranges," \
                " comma separated. eg. 10.1.1.20-21 or 10.1.1.20,10.1.1.21")

        parser.add_argument("--dns-servers", nargs="+", default=[],
            action="append", metavar=("<address-or-range>"),
            help="(if STATIC) List of DNS Server IP addresses. Can be a" \
                 " single address or multiple comma separated addresses." \
                 " eg. 10.1.1.10 or 10.1.1.10,10.1.1.15")

        parser.add_argument("--dns-search-domains", nargs="+", default=[],
            action="append", metavar=("<search-domain>"),
            help="(if STATIC) List of DNS Search Domains")

        parser.add_argument("--mtu", type=int,
            help="(if STATIC) The Maximum Transfer Unit (MTU) in bytes" \
                " of a tagged STATIC network. The MTU of an untagged STATIC" \
                " network needs to be specified through interface MTU.")

        parser.add_argument("--vlan-id", type=int,
            help="(if STATIC) User assigned VLAN tag for network configuration."
            " 1-4094 are valid VLAN IDs and 0 is used for untagged networks.")

    @staticmethod
    def main(conninfo, credentials, args):
        attributes = {
            key: join_nargs_arg(getattr(args, key))
                for key in network.V2_NETWORK_FIELDS
                if getattr(args, key) is not None
        }

        attributes['ip_ranges'] = \
                parse_comma_deliminated_ip_ranges(attributes.get('ip_ranges'))
        floating_input = attributes.get('floating_ip_ranges', None)
        if floating_input:
            attributes['floating_ip_ranges'] = \
                parse_comma_deliminated_ip_ranges(floating_input)
        dnsservers_input = attributes.get('dns_servers', None)
        if dnsservers_input:
            attributes['dns_servers'] = \
                parse_comma_deliminated_ip_ranges(dnsservers_input)

        if not attributes:
            raise ValueError("One or more options must be specified")

        print network.add_network(conninfo, credentials, args.interface_id,
            **attributes)

class DeleteNetwork(qumulo.lib.opts.Subcommand):
    NAME = "network_delete_network"
    DESCRIPTION = "Delete network configuration"

    @staticmethod
    def options(parser):
        parser.add_argument("--interface-id", type=int, default=1,
            help=argparse.SUPPRESS)
        parser.add_argument("--network-id", type=int, required=True,
            help="The unique ID of the network on the interface")

    @staticmethod
    def main(conninfo, credentials, args):
        print network.delete_network(conninfo, credentials, args.interface_id,
            args.network_id)

class ModNetwork(qumulo.lib.opts.Subcommand):
    NAME = "network_mod_network"
    DESCRIPTION = "Modify network configuration"

    @staticmethod
    def options(parser):
        parser.add_argument("--interface-id", type=int, default=1,
            help=argparse.SUPPRESS)

        parser.add_argument("--network-id", type=int, required=True,
            help="The unique ID of the network on the interface")

        parser.add_argument("--name", help="Network name")

        parser.add_argument("--assigned-by", choices=["DHCP", "STATIC"],
            help="How to assign IP address, either DHCP or STATIC")

        parser.add_argument("--netmask", metavar=("<netmask-or-subnet>"),
            help="(if STATIC) IPv4 or IPv6 Netmask or Subnet CIDR" \
                " eg. 255.255.255.0 or 10.1.1.0/24")

        parser.add_argument("--ip-ranges", nargs="+", action="append",
            metavar=("<address-or-range>"),
            help="(if STATIC) List of persistent IP ranges to replace the" \
                " current ranges. Can be single addresses or ranges," \
                " comma separated. eg. 10.1.1.20-21 or 10.1.1.20,10.1.1.21")

        parser.add_argument("--floating-ip-ranges", nargs="+",
            action="append", metavar=("<address-or-range>"),
            help="(if STATIC) List of floating IP ranges to replace the" \
                " current ranges. Can be single addresses or ranges," \
                " comma separated. eg. 10.1.1.20-21 or 10.1.1.20,10.1.1.21")

        parser.add_argument("--clear-floating-ip-ranges", action="store_true",
            help="(if STATIC) Clear the floating IP address ranges")

        parser.add_argument("--dns-servers", nargs="+",
            action="append", metavar=("<address-or-range>"),
            help="(if STATIC) List of DNS Server IP addresses to replace the" \
                 " current ranges. Can be a single address or multiple comma" \
                 " separated addresses. eg. 10.1.1.10 or 10.1.1.10,10.1.1.15")

        parser.add_argument("--clear-dns-servers", action="store_true",
            help="(if STATIC) Clear the DNS servers")

        parser.add_argument("--dns-search-domains", nargs="+",
            action="append", metavar=("<search-domain>"),
            help="(if STATIC) List of DNS Search Domains")

        parser.add_argument("--clear-dns-search-domains", action="store_true",
            help="(if STATIC) Clear the DNS search domains")

        parser.add_argument("--mtu", type=int,
            help="(if STATIC) The Maximum Transfer Unit (MTU) in bytes" \
                " of a tagged STATIC network. The MTU of an untagged STATIC" \
                " network needs to be specified through interface MTU.")

        parser.add_argument("--vlan-id", type=int,
            help="(if STATIC) User assigned VLAN tag for network configuration."
            " 1-4094 are valid VLAN IDs and 0 is used for untagged networks.")

    @staticmethod
    def main(conninfo, credentials, args):
        attributes = {
            key: join_nargs_arg(getattr(args, key))
                for key in network.V2_NETWORK_FIELDS
                if getattr(args, key) is not None
        }

        if args.clear_floating_ip_ranges:
            attributes["floating_ip_ranges"] = []

        if args.clear_dns_servers:
            attributes["dns_servers"] = []

        if args.clear_dns_search_domains:
            attributes["dns_search_domains"] = []

        if not attributes:
            raise ValueError("One or more options must be specified")

        persistent_input = attributes.get('ip_ranges', None)
        if persistent_input:
            attributes['ip_ranges'] = \
                parse_comma_deliminated_ip_ranges(persistent_input)
        floating_input = attributes.get('floating_ip_ranges', None)
        if floating_input:
            attributes['floating_ip_ranges'] = \
                parse_comma_deliminated_ip_ranges(floating_input)
        dnsservers_input = attributes.get('dns_servers', None)
        if dnsservers_input:
            attributes['dns_servers'] = \
                parse_comma_deliminated_ip_ranges(dnsservers_input)

        print network.modify_network(conninfo, credentials, args.interface_id,
            args.network_id, **attributes)

class GetStaticIpAllocationCommand(qumulo.lib.opts.Subcommand):
    NAME = "static_ip_allocation"
    DESCRIPTION = "Get cluster-wide static IP allocation"

    @staticmethod
    def options(parser):
        parser.add_argument("--try-ranges",
            help="Specify ip range list to try "
                 "(e.g. '1.1.1.10-12,10.20.5.0/24'")
        parser.add_argument("--try-netmask",
            help="Specify netmask to apply when using --try-range option")
        parser.add_argument("--try-floating-ranges",
            help="Specify floating ip range list to try "
                 "(e.g. '1.1.1.10-12,10.20.5.0/24'")

    @staticmethod
    def main(conninfo, credentials, args):
        print network.get_static_ip_allocation(
            conninfo, credentials,
            args.try_ranges, args.try_netmask, args.try_floating_ranges)

class GetFloatingIpAllocationCommand(qumulo.lib.opts.Subcommand):
    NAME = "floating_ip_allocation"
    DESCRIPTION = "Get cluster-wide floating IP allocation"

    @staticmethod
    def main(conninfo, credentials, _args):
        print network.get_floating_ip_allocation(conninfo, credentials)

def print_connection_counts(connlist):
    def initial_counts():
        return {
            'CONNECTION_TYPE_NFS': 0,
            'CONNECTION_TYPE_SMB': 0,
            'CONNECTION_TYPE_FTP': 0,
        }

    # Initialize counts to zero
    totals = initial_counts()
    per_node = {}
    for node_data in connlist.data:
        per_node[node_data['id']] = initial_counts()

    # Sum up connection counts
    for node_data in connlist.data:
        for conn in node_data['connections']:
            totals[conn['type']] += 1
            per_node[node_data['id']][conn['type']] += 1

    # Output pretty-printed connection counts
    print 'Total: SMB {} NFS {} FTP {}'.format(
        totals['CONNECTION_TYPE_SMB'],
        totals['CONNECTION_TYPE_NFS'],
        totals['CONNECTION_TYPE_FTP'])
    for node in sorted(per_node.keys()):
        print 'Node{}: SMB {} NFS {} FTP {}'.format(node,
            per_node[node]['CONNECTION_TYPE_SMB'],
            per_node[node]['CONNECTION_TYPE_NFS'],
            per_node[node]['CONNECTION_TYPE_FTP'])

class GetClientConnectionsCommand(qumulo.lib.opts.Subcommand):
    NAME = 'network_list_connections'
    DESCRIPTION = 'Get the list of SMB and NFS protocol connections per node.'

    @staticmethod
    def options(parser):
        parser.add_argument("-c", "--counts",
            help="Pretty-print connection counts for the cluster and each node",
            action="store_true")

    @staticmethod
    def main(conninfo, credentials, args):
        if args.counts:
            print_connection_counts(network.connections(conninfo, credentials))
        else:
            print network.connections(conninfo, credentials)
