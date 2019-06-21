# Copyright (c) 2015 Qumulo, Inc.
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
import json
import sys

import qumulo.lib.opts
import qumulo.rest.dns as dns

import qumulo.lib.util

class ResolveIpAddresses(qumulo.lib.opts.Subcommand):
    NAME = "dns_resolve_ips"
    DESCRIPTION = "Resolve IP addresses to hostnames"

    @staticmethod
    def options(parser):
        parser.add_argument(
            "--ips",
            required=True,
            nargs="+",
            help="IP addresses to resolve")

    @staticmethod
    def main(conninfo, credentials, args):
        print dns.resolve(conninfo, credentials, args.ips)

class ResolveHostnames(qumulo.lib.opts.Subcommand):
    NAME = "dns_resolve_hostnames"
    DESCRIPTION = "Resolve hostnames to IP addresses"

    @staticmethod
    def options(parser):
        parser.add_argument(
            "--hosts",
            required=True,
            nargs="+",
            help="Hostnames to resolve")

    @staticmethod
    def main(conninfo, credentials, args):
        print dns.resolve_names_to_ips(conninfo, credentials, args.hosts)

#  _             _
# | | ___   ___ | | ___   _ _ __
# | |/ _ \ / _ \| |/ / | | | '_ \
# | | (_) | (_) |   <| |_| | |_) |
# |_|\___/ \___/|_|\_\\__,_| .__/____
#                          |_| |_____|
#                           _     _
#   _____   _____ _ __ _ __(_) __| | ___  ___
#  / _ \ \ / / _ \ '__| '__| |/ _` |/ _ \/ __|
# | (_) \ V /  __/ |  | |  | | (_| |  __/\__ \
#  \___/ \_/ \___|_|  |_|  |_|\__,_|\___||___/
#  FIGLET: lookup_overrides
#

class DNSLookupOverridesGetCommand(qumulo.lib.opts.Subcommand):
    NAME = 'dns_get_lookup_overrides'
    DESCRIPTION = \
        ('List the configured set of DNS lookup overrides. '
        'These rules override any lookup results from the configured DNS '
        'servers and serve as static mappings between IP address and hostname')

    @staticmethod
    def main(conninfo, credentials, _args):
        print dns.lookup_overrides_get(conninfo, credentials)

class DNSLookupOverridesSetCommand(qumulo.lib.opts.Subcommand):
    NAME = 'dns_set_lookup_overrides'
    DESCRIPTION = \
        ('Replace the configured set of DNS lookup overrides. '
        'These rules override any lookup results from the configured DNS '
        'servers and serve as static mappings between IP address and hostname. '
        'The provided overrides document should have the following '
        'structure:\n\n'
        '{\n'
        '  "lookup_overrides": [\n'
        '    {"ip_address": "1.2.3.4", "aliases": ["foo.com", "www.foo.com"]}\n'
        '    {"ip_address": "2.3.4.5", "aliases": ["bar.com", "www.bar.com"]}\n'
        '  ]\n'
        '}\n\n'
        'The first hostname in the "aliases" list is what will be resolved '
        'when doing reverse lookups from IP address to hostname.')

    @staticmethod
    def options(parser):
        parser.formatter_class=argparse.RawDescriptionHelpFormatter
        group = parser.add_mutually_exclusive_group(required=True)
        group.add_argument(
            "--file", help="JSON-encoded file containing overrides.", type=str)
        group.add_argument(
            "--stdin",
            action="store_true",
            help="Read JSON-encoded overrides from stdin")

    @staticmethod
    def main(conninfo, credentials, args):
        infile = open(args.file, "rb") if args.file else sys.stdin
        overrides = json.load(infile)
        dns.lookup_overrides_set(conninfo, credentials, overrides)
