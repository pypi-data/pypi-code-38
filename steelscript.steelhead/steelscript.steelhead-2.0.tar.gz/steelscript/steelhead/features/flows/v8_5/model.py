# Copyright (c) 2019 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the MIT License
# accompanying the software ("License").  This software is distributed "AS IS"
# as set forth in the License.

from __future__ import (unicode_literals, print_function, division,
                        absolute_import)

from steelscript.common.interaction.model import model, Model

import re
import ipaddress
from collections import namedtuple


@model
class FlowsModel(Model):
    """
    Kauai Flows model for the SteelHead product
    """

    def _parse_ip_addr(self, ip):
        ParsedIP = namedtuple('ParsedIP', ['address', 'port'])

        # IPv4 looks like 123.124.125.126:1234
        # IPv6 looks like [2001:0db8:85a3:0000:0000:8a2e:0370:7334]:1234
        ip_pattern = "\[*([\w\.:]+)\]*:(\d+)"
        ip_regex = re.compile(ip_pattern)
        ip_match = ip_regex.search(ip)
        if ip_match:
            return ParsedIP(address=ipaddress.ip_address(ip_match.group(1)),
                            port=int(ip_match.group(2)))

    def _parse_flow_summary(self, output):
        # group 1
        type_pattern = "([a-zA-Z]+)"
        # group 2-5 (src/dst) in IPv4 or IPv6 format
        ip_pattern = "([\w\.\[\]:]+)"
        # group 6
        app_pattern = "(.+?)"
        # group 7 - this only shows up for optimized connections
        reduction_pattern = "(\d*)%*"
        # group 8-13
        # The Rdn Since value can be a date+time or the string pre_existing
        since_pattern = "(pre_existing|\d+\/\d+\/\d+\s+\d+:\d+:\d+)"

        flow_pattern = "%s\s+%s\s+%s\s+%s\s+%s\s+%s\s*$" \
                       % (type_pattern, ip_pattern, ip_pattern,
                          app_pattern, reduction_pattern, since_pattern)

        flow_info_dict = None
        regex = re.compile(flow_pattern)
        match = regex.search(output)
        if match:
            src = self._parse_ip_addr(match.group(2))
            dst = self._parse_ip_addr(match.group(3))
            flow_info_dict = dict()
            flow_info_dict = {
                'type': match.group(1),
                'source ip': src.address,
                'source port': src.port,
                'destination ip': dst.address,
                'destination port': dst.port,
                'app': match.group(4)}
            if match.group(5):
                flow_info_dict['reduction'] = int(match.group(5))
            if match.group(6) == 'pre_existing':
                flow_info_dict['since'] = {'pre_existing': True}
            else:
                date_time = match.group(6).split(' ')
                datestring = date_time[0].split('/')
                timestring = date_time[1].split(':')
                flow_info_dict['since'] = {'year': datestring[0],
                                           'month': datestring[1],
                                           'day': datestring[2],
                                           'hour': timestring[0],
                                           'min': timestring[1],
                                           'secs': timestring[2]}
        return flow_info_dict

    def show_flows(self, type='all'):
        """
        Method to show Flows on a SteelHead.  Currently, some flow types are
        not supported and will not be included in the output.  These types are
        IPv6 and pre_existing connections.

        :param type: Optional parameter to select the type of Flows.  Valid
                     choices include all, optimized, passthrough, packet-mode,
                     and tcp-term.
        :type type: string

        :return: dictionary

        .. code-block:: python

            {
                'flows_list': [
                    {'app': 'UDPv4',
                    'destination ip': IPv4Address(u'10.190.5.2'),
                    'destination port': 1003,
                    'reduction': 99,
                    'since': {'day': '10',
                              'hour': '23',
                              'min': '58',
                              'month': '02',
                              'secs': '01',
                              'year': '2014'},
                    'source ip': IPv4Address(u'10.190.0.1'),
                    'source port': 406,
                    'type': 'N'},...],
                'flows_summary': {
                    'denied': {'all': 1},
                    'discarded': {'all': 1},
                    'establishing': {'all': 1, 'v4': 2, 'v6': 3},
                    'forwarded': {'all': 1, 'v4': 2, 'v6': 3},
                    'half_closed optimized': {'all': 11, 'v4': 22, 'v6': 33},
                    'half_opened optimized': {'all': 1, 'v4': 2, 'v6': 3},
                    'optimized': {'all': '1', 'v4': 2, 'v6': 3},
                    'packet_mode optimized': {'all': 11, 'v4': 22, 'v6': 33},
                    'passthrough': {'all': 11, 'v4': 22, 'v6': 33},
                    'passthrough intentional': {'all': 1, 'v4': 2, 'v6': 3},
                    'passthrough unintentional':
                        {'all': 11, 'v4': 22, 'v6': 33},
                    'passthrough unintentional packet_mode':
                        {'all': 11, 'v4': 22, 'v6': 33},
                    'passthrough unintentional terminated':
                        {'all': 1, 'v4': 2, 'v6': 3},
                    'rios only': {'all': 1, 'v4': 3, 'v6': 3},
                    'rios scps': {'all': 1, 'v4': 2, 'v6': 3},
                    'scps only': {'all': 11, 'v4': 22, 'v6': 33},
                    'tcp proxy': {'all': 1, 'v4': 2, 'v6': 3},
                    'total': {'all': 1, 'v4': 2, 'v6': 3}
            }

        """

        cmd = "show flows %s" % type
        result = self.cli.exec_command(cmd, output_expected=True)

        # Parse show flows all cmd output
        lines = result.splitlines()

        title_parsed = False
        title_pattern = "T\s+Source\s+Destination\s+App\s+Rdn\s+Since"
        title_regex = re.compile(title_pattern)

        flows_list = []
        flows_summary_dict = dict()

        summary_list = {'Established Optimized': 'established optimized',
                        'RiOS Only (O)': 'rios only',
                        'SCPS Only (SO)': 'scps only',
                        'RiOS+SCPS (RS)': 'rios scps',
                        'TCP Proxy (TP)': 'tcp proxy',
                        'Packet-mode optimized (N)': 'packet_mode optimized',
                        'Half-opened optimized (H)': 'half_opened optimized',
                        'Half-closed optimized (C)': 'half_closed optimized',
                        'Establishing (E)': 'establishing',
                        'Passthrough': 'passthrough',
                        'Passthrough intentional (PI)':
                            'passthrough intentional',
                        'Passthrough unintentional (PU)':
                            'passthrough unintentional',
                        'Terminated': 'passthrough unintentional terminated',
                        'Packet-mode': 'passthrough unintentional packet_mode',
                        'Forwarded (F)': 'forwarded',
                        'Discarded (terminated)': 'discarded',
                        'Denied (terminated)': 'denied',
                        'Total': 'total'}

        for line in lines:
            # Skip empty line
            if not len(line):
                continue

            # Parse Title
            if title_parsed is not True:
                match = title_regex.search(line)
                if match:
                    title_parsed = True
                    # Done parsing Title
                    continue

            # Skip "-----------..." lines
            match = re.match(r'^-+$', line)
            if match:
                continue

            # Parse connections/flows
            flow_info_dict = self._parse_flow_summary(line)
            if flow_info_dict:
                flows_list.append(flow_info_dict)
                continue

            # Parse Summary report
            items = line.split(':')
            for category in summary_list:
                output = items[0].strip()
                exp_output = category.strip()
                if output == exp_output:
                    match = re.match('\s+(\d+)\s+(\d+)\s+(\d+)\s*$', items[1])
                    if match:
                        flows_summary_dict[summary_list[category]] = \
                            {'all': int(match.group(1)),
                             'v4':  int(match.group(2)),
                             'v6':  int(match.group(3))}
                        break
                    match = re.match('\s+(\d+)$', items[1])
                    if match:
                        flows_summary_dict[summary_list[category]] = \
                            {'all': int(match.group(1))}
                        break

        output = {'flows_list': flows_list,
                  'flows_summary': flows_summary_dict}
        return output
