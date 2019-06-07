# Copyright 2019 Red Hat
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
from __future__ import absolute_import

import argparse
import logging
import sys

from tobiko.fault import executor


LOG = logging.getLogger(__name__)


class FaultCMD(object):

    def __init__(self):
        self.parser = self.get_parser()
        self.args = self.parser.parse_args()

    def get_parser(self):
        parser = argparse.ArgumentParser(add_help=True)
        parser.add_argument(
            'fault',
            help="The fault to execute (e.g. restart neutron service).\n")
        return parser

    def run(self):
        """Run faults."""
        fault_exec = executor.FaultExecutor()
        fault_exec.execute(self.args.fault)


def setup_logging(debug=None):
    """Sets the logging."""
    # pylint: disable=W0622
    format = '%(message)s'
    level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(level=level, format=format)


def main():
    """Run CLI main entry."""
    setup_logging()
    fault_cli = FaultCMD()
    fault_cli.run()


if __name__ == '__main__':
    sys.exit(main())
