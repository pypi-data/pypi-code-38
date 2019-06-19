# -*- coding:utf-8 -*-
# Copyright (c) 2017, Combine Control Systems AB
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of the Combine Control Systems AB nor the
#       names of its contributors may be used to endorse or promote products
#       derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.
# IN NO EVENT SHALL COMBINE CONTROL SYSTEMS AB BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
import argparse


class SympathyArgumentParser(argparse.ArgumentParser):

    def __init__(self, using_gui):
        super(SympathyArgumentParser, self).__init__(
            'The Python script used to properly launch Sympathy for Data.')

        self.__using_gui = using_gui

        # Filename is a positional argument.
        self.add_argument(
            'filename', action='store', nargs='?', default=None,
            help='File containing workflow.')
        self.add_argument(
            '-e', '--extras-inifile', '--extras_inifile',
            action='store', default=None,
            help='Extras ini-file.')
        self.add_argument(
            '--exit-after-exception', '--exit_after_exception',
            action='store', type=int,
            default=int(not using_gui),
            choices=[0, 1],
            help='Exit after uncaught exception occurs in a signal handler.')
        self.add_argument(
            '-v', '--version', action='store_true', default=None,
            help='Show Sympathy for Data version.')
        self.add_argument(
            '-L', '--loglevel', action='store', type=int, default=2,
            choices=range(0, 6),
            help='(0) disable logging,\n'
                 '(5) enable all logging')
        self.add_argument(
            '-N', '--node-loglevel', '--node_loglevel',
            action='store', type=int, default=4,
            choices=range(0, 6),
            help='(0) disable logging,\n'
                 '(5) enable all logging')
        self.add_argument(
            '--num-worker-processes', '--num_worker_processes',
            action='store', type=int, default=0,
            help='Number of python worker processes\n'
                 '(0) use system number of CPUs')
        self.add_argument(
            '-C', '--configfile', nargs='+', default=None,
            help='Specify a workflow configuration file,'
                 ' used to change parameters and an optional outfile for the'
                 ' modified workflow.')
        self.add_argument(
            '-I', '--inifile', action='store', default=None,
            help='Specify preferences file.')

        self.add_argument(
            '--generate-documentation', '--generate_documentation',
            action='store_true', default=None,
            help='Generate documentation files for Sympathy.')

        self.add_argument(
            '--benchmark', action='store', type=str, default=None,
            help='Write benchmark HTML report to BENCHMARK (filename)'
                 ' Use --loglevel 5 and --node-loglevel 5 to get full output.')

        self.add_argument(
            '--nocapture', action='store_true', default=False,
            help=('Disable capturing of node output and send it directly '
                  'to stdout/stderr.'))

    def parse_args(self, args=None, namespace=None, known=False):
        if known:
            # Discarding unknown arguments.
            parsed = super(SympathyArgumentParser, self).parse_known_args(
                args, namespace)[0]
        else:
            parsed = super(SympathyArgumentParser, self).parse_args(
                args, namespace)
        return parsed


def create_parser(using_gui):
    return SympathyArgumentParser(using_gui)


gui_parser = create_parser(using_gui=True)
parser = create_parser(using_gui=False)


def instance(using_gui=False):
    if using_gui:
        return gui_parser
    else:
        return parser
