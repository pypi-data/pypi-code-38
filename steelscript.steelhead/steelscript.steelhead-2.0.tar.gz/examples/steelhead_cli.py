#!/usr/bin/env python

# Copyright (c) 2019 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the MIT License
# accompanying the software ("License").  This software is distributed "AS IS"
# as set forth in the License.


"""
This script presents a python example of using Command Line Interface (CLI)
to show version, networking state, current connections (flows) and bandwidth
statistics of a SteelHead appliance.

First of all, the steelhead module needs to be imported, from which the
SteelHead class is used. An authentication object is created by
instantiating the UserAuth class with user name and password to access the
SteelHead appliance. Afterwards, a SteelHead object is created by
instantiating the SteelHead class with the host name or IP address of the
SteelHead appliance and the existing authentication object. Then, we can use
the SteelHead object to execute command on the SteelHead appliance as follows:
steelhead_object.cli.exec_command("command_to_be_executed").

This example script should be executed as follows:
steelhead_cli.py <HOST> [-u USERNAME] [-p PASSWORD]
"""

from __future__ import (absolute_import, unicode_literals, print_function,
                        division)

import steelscript.steelhead.core.steelhead as steelhead

from steelscript.common.app import Application
from steelscript.common.service import UserAuth


class SteelHeadCLIApp(Application):
    def add_positional_args(self):
        self.add_positional_arg('host', 'SteelHead hostname or IP address')

    def add_options(self, parser):
        super(SteelHeadCLIApp, self).add_options(parser)

        parser.add_option('-u', '--username', help="Username to connect with")
        parser.add_option('-p', '--password', help="Password to use")

    def validate_args(self):
        super(SteelHeadCLIApp, self).validate_args()

        if not self.options.username:
            self.parser.error("User Name needs to be specified")

        if not self.options.password:
            self.parser.error("Password needs to be specified")

    def main(self):
        auth = UserAuth(username=self.options.username,
                        password=self.options.password)
        sh = steelhead.SteelHead(host=self.options.host, auth=auth)

        print("\n********** Version **********\n")
        print(sh.cli.exec_command("show version"))

        print("\n********** Networking State **********\n")
        print(sh.cli.exec_command("show interfaces aux"))

        print("\n********** All Current Flows **********\n")
        print(sh.cli.exec_command("show flows all"))
        print("\n********** All Optimized Flows **********\n")
        print(sh.cli.exec_command("show flows optimized"))
        print("\n********** All Passthrough Flows **********\n")
        print(sh.cli.exec_command("show flows passthrough"))

        print ("\n********** Bandwidth Statistics **********\n")
        print (sh.cli.exec_command("show stats bandwidth all "
                                   "bi-directional 5min"))

if __name__ == '__main__':
    SteelHeadCLIApp().run()
