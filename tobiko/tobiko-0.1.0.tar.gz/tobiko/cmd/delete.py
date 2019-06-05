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

import logging
import sys

from tobiko.cmd import base

LOG = logging.getLogger(__name__)


class DeleteUtil(base.TobikoCMD):

    def get_parser(self):
        parser = super(DeleteUtil, self).get_parser()
        parser.add_argument(
            '--playbook', '-p',
            help="The name of the playbook to execute in delete mode.")
        return parser

    def run_playbook(self, playbook):
        """Executes given playbook."""
        self.ansibleManager.run_playbook(playbook, mode='delete')


def main():
    """Delete CLI main entry."""
    delete_cmd = DeleteUtil()
    delete_cmd.set_stream_handler_logging_level()
    delete_cmd.run_playbook(delete_cmd.args.playbook)


if __name__ == '__main__':
    sys.exit(main())
