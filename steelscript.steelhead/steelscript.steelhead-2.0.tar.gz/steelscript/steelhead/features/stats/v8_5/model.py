# Copyright (c) 2019 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the MIT License
# accompanying the software ("License").  This software is distributed "AS IS"
# as set forth in the License.

from __future__ import (unicode_literals, print_function, division,
                        absolute_import)

import re

from steelscript.common.interaction.model import model, Model
from steelscript.cmdline.parsers import cli_parse_basic


@model
class StatsModel(Model):
    """
    Kauai Stats model for the SteelHead product
    """

    def show_stats_bandwidth(self, port='all', type=None, frequency=None):
        """
        Method to show Bandwidth Stats on a SteelHead

        :param port: Optional parameter to filter the bandwidth summary to
                     traffic on a specific port.  The value is simply the port
                     number (e.g., "80") and defaults to "all."
        :type port: string

        :param type: The type of traffic to summarize.  Options include
                     bi-directional, lan-to-wan, and wan-to-lan.
        :type type: string

        :param frequency: Last period of time to lookback during stats
                          collection.  Options include 1min, 5min, hour, day,
                          week, or month.

        :return: dictionary

        .. code-block:: python

             {
                 'wan data': '5.4 GB',
                 'lan data': '6 GB',
                 'data reduction': 10,
                 'data reduction peak': 95,
                 'data reduction peak time': '2014/12/05 14:50:00',
                 'capacity increase': '1.1'
             }

        """

        cmd = "show stats bandwidth %s" % port
        if type is not None:
            cmd = cmd + " " + type
        if frequency is not None:
            cmd = cmd + " " + frequency

        result = self.cli.exec_command(cmd, output_expected=True)
        result.strip()
        parsed = cli_parse_basic(result)

        pct_pattern = "(\d+\.*\d*) [%X]"
        regex = re.compile(pct_pattern)

        for stat in parsed:
            if not parsed[stat]:
                parsed[stat] = 'None'
                continue
            match = regex.search(parsed[stat])
            if match:
                parsed[stat] = float(match.group(1))

        return parsed
