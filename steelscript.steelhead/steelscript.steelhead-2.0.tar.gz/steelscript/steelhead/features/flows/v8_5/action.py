# Copyright (c) 2019 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the MIT License
# accompanying the software ("License").  This software is distributed "AS IS"
# as set forth in the License.

from __future__ import (unicode_literals, print_function, division,
                        absolute_import)

from steelscript.common.interaction import action, uidelegation


@action.action
class FlowsAction(action.Action):
    """
    Kauai Flows Actions for SteelHead product
    """


class CLI(uidelegation.CLIDelegatee):
    """
    Kauai Flows CLI Delegatee
    """

    def show_flows_optimized(self):
        """
        Method to show optimized flows on a Steelhead

        :return: dictionary

        .. code-block:: python

             {
                 'flows_list': [
                     {'app': 'UDPv4',
                      'destination ip': IPv4Address('10.190.5.2'),
                      'destination port': 1003,
                      'percent': 99,
                      'since': {'day': '10',
                                'hour': '23',
                                'min': '58',
                                'month': '02',
                                'secs': '01',
                                'year': '2014'},
                      'source ip': IPv4Address('10.190.0.1'),
                      'source port': 406,
                      'type': 'N'},...],
                 'flows_summary': {
                     'established optimized': {'all': 1, 'v4': 2, 'v6': 3},
                     'packet_mode optimized': {'all': 11, 'v4': 22, 'v6': 33},
                     'rios only': {'all': 1, 'v4': 3, 'v6': 3},
                     'rios scps': {'all': 1, 'v4': 2, 'v6': 3},
                     'scps only': {'all': 11, 'v4': 22, 'v6': 33},
                     'tcp proxy': {'all': 1, 'v4': 2, 'v6': 3},
                     'total': {'all': 11', v4: 40, 'v6': 70}}
             }

        """

        return self.model.show_flows(type="optimized")

    def show_flows_passthrough(self):
        """
        Method to show passthrough flows on a Steelhead

        :return: dictionary

        .. code-block:: python

            {
             'flows_list': [
                {'app': 'TCP',
                 'destination ip': IPv4Address('10.190.174.120'),
                 'destination port': 443,
                 'since': {'day': '02',
                           'hour': '06',
                           'min': '00',
                           'month': '01',
                           'secs': '50',
                           'year': '2014'},
                 'source ip': IPv4Address('10.3.2.54'),
                 'source port': 40097,
                 'type': 'PI'}...],
             'flows_summary': {
                 'forwarded': {'all': 1, 'v4': 2, 'v6': 3},
                 'passthrough': {'all': 11, 'v4': 22, 'v6': 33},
                 'passthrough intentional': {'all': 1, 'v4': 2, 'v6': 3},
                 'passthrough unintentional': {'all': 11, 'v4': 22, 'v6': 33},
                 'passthrough unintentional packet_mode': {'all': 11,
                                                           'v4': 22,
                                                           'v6': 33},
                 'passthrough unintentional terminated': {'all': 1,
                                                          'v4': 2,
                                                          'v6': 3},
                 'total': {'all': 11, 'v4': 40, 'v6': 70}}
            }
        """

        return self.model.show_flows(type="passthrough")
