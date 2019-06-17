# Copyright (c) 2019 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the MIT License
# accompanying the software ("License").  This software is distributed "AS IS"
# as set forth in the License.

from __future__ import (absolute_import, unicode_literals, print_function,
                        division)

from steelscript.common.interaction.model import model, Model
from steelscript.cmdline.parsers import cli_parse_basic


@model
class CommonModel(Model):
    """
    Kauai model for the 'common' REST Service on the SteelHead product.
    """

    def show_version(self):
        """
        Returns parsed output of 'show version'.

        .. code-block:: none

            Product name:      rbt_sh
            Product release:   9.0.1
            Build ID:          #19
            Build date:        2014-11-19 01:59:36
            Build arch:        x86_64
            Built by:          mockbuild@bannow-worker4

            Uptime:            15d 23h 22m 33s

            Product model:     CX1555
            System memory:     6378 MB used / 1552 MB free / 7931 MB total
            Number of CPUs:    4
            CPU load averages: 0.08 / 0.17 / 0.10

        :return: Dictionaries of values returned

        .. code-block:: python

            {'product name': 'rbt_sh',
             'product release': '9.0.1',
             'build id': '#19',
             'build arch': 'x86_64',
             ...

        """
        output = self.cli.exec_command("show version", output_expected=True)
        parsed = cli_parse_basic(output)

        # Force 'product model' to be a string.
        for key in ['product model']:
            if key in parsed:
                parsed[key] = str(parsed[key])

        # Remove 'uptime' because we don't know what object to parse it into,
        # along with some others we don't want to format right now.
        for key in ['uptime', 'cpu load averages', 'system memory',
                    'build date']:
            if key in parsed:
                del parsed[key]

        return parsed
