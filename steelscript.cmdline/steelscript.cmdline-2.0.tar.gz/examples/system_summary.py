# Copyright (c) 2019 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the MIT License
# accompanying the software ("License").  This software is distributed "AS IS"
# as set forth in the License.


"""
This script presents a python example of logging into a Linux/Unix-based
machine to print a simple system status.
"""

from __future__ import (absolute_import, unicode_literals, print_function,
                        division)

from steelscript.common.app import Application
from steelscript.cmdline import cli


def filter_input(input_string, match=None, unmatch=None):
    """Filter input_string on a per-line basis

    :param input_string: the input string to be filtered
    :param match: a string required in one line
    :param unmatch: a string should not exist in one line
    """
    ret = []
    for line in input_string.split('\n'):
        if ((match is None or match in line) and
                (unmatch is None or unmatch not in line)):
            ret.append(line)
    return '\n'.join(ret)


def disk_usage(cli):
    """Parse the output of 'df -h' and return a list of 3-element lists
    each list consist of mount point, use percentage and total size

    :param input_string: the output of df -h
    """
    output = filter_input(cli.exec_command('df -h\n'), match='%',
                          unmatch='Filesystem')
    ret = []
    for line in output.split('\n'):
        fs = line.split()
        # fs follows pattern as "/dev/sda3 862G  183G  637G  23% /"
        # as "filesystem total used available percentage mount-point"
        try:
            ret.append(' '.join([fs[-1], fs[-5], fs[-2]]))
        except IndexError:
            return 'Error, `df -h` returned invalid data!'

    return '\n'.join(ret)


def time_info(cli):
    """Return time/timezone info by running 'date' command"""
    return cli.exec_command('date\n')


def cpu_load(cli):
    """Return the cpu load for the last minute, 5 minutes and 15 minutes"""
    # uptime returns as
    # 16:45  up 11 days,  6:49, 8 users, load averages: 2.00 1.75 1.67
    uptime = cli.exec_command('uptime\n')

    if uptime:
        return ' '.join(uptime.split()[-5:])
    else:
        return 'Error, `uptime` returned empty results!'


class BasicInfoApp(Application):

    def add_options(self, parser):
        super(BasicInfoApp, self).add_options(parser)

        parser.add_option('-H', '--host',
                          help='hostname or IP address')
        parser.add_option('-u', '--username', help="Username to connect with")
        parser.add_option('-p', '--password', help="Password to connect with")

    def validate_args(self):
        super(BasicInfoApp, self).validate_args()

        if not self.options.host:
            self.parser.error("Host name needs to be specified")

        if not self.options.username:
            self.parser.error("User Name needs to be specified")

        if not self.options.password:
            self.parser.error("Password needs to be specified")

    def main(self):
        cli_obj = cli.CLI(hostname=self.options.host,
                          username=self.options.username,
                          password=self.options.password)
        cli_obj.start()
        print(time_info(cli_obj))
        print(cpu_load(cli_obj))
        print(disk_usage(cli_obj))


if __name__ == '__main__':
    BasicInfoApp().run()
