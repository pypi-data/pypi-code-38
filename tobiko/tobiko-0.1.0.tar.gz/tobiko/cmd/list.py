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
import logging
import sys

from tobiko.cmd import base

LOG = logging.getLogger(__name__)


class ListUtil(base.TobikoCMD):

    def __init__(self):
        super(ListUtil, self).__init__()
        self.parser = self.get_parser()
        self.args = (self.parser).parse_args()

    def get_parser(self):
        parser = argparse.ArgumentParser(add_help=True)
        parser.add_argument('--playbooks', '-p',
                            help="List playbooks provided by Tobiko",
                            const='list_playbooks',
                            action='store_const', dest='action')
        return parser

    def list_playbooks(self):
        """Lists playbooks included in Tobiko."""
        for playbook in self.ansibleManager.get_playbooks_names():
            sys.stdout.write(playbook + '\n')


def main():
    """List CLI main entry."""
    list_cmd = ListUtil()
    if list_cmd.args.action:
        action_func = getattr(list_cmd, list_cmd.args.action)
        action_func()
    else:
        list_cmd.list_playbooks()


if __name__ == '__main__':
    sys.exit(main())
