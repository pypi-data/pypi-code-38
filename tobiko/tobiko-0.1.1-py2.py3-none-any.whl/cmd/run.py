# Copyright 2018 Red Hat
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
import sys

import paramiko

from oslo_log import log

LOG = log.getLogger(__name__)


class Tobiko():

    def __init__(self):
        self.parser = self.get_parser()
        self.args = (self.parser).parse_args()
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    def get_parser(self):
        parser = argparse.ArgumentParser(add_help=True)
        parser.add_argument(
            '--host',
            help="The name of the host where your cloud is deployed.\n")
        parser.add_argument(
            '--key', '-k',
            help="They SSH key to use to connect the host.")
        return parser

    def verify_connection(self):
        """Verifies it's able to connect the host provided by the user."""
        try:
            self.ssh.connect(self.args.host)
        except paramiko.ssh_exception.AuthenticationException:
            LOG.error("Unable to connect %r", self.args.host)


def main():
    """Run CLI main entry."""
    tobiko = Tobiko()
    tobiko.verify_connection()
    # run.discover_environment()


if __name__ == '__main__':
    sys.exit(main())
