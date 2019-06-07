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

import sys

from oslo_log import log

import tobiko
from tobiko.cmd import base

LOG = log.getLogger(__name__)


class CreateUtil(base.TobikoCMD):

    def get_parser(self):
        parser = super(CreateUtil, self).get_parser()
        parser.add_argument(
            '--playbook', '-p',
            help="The name of the playbook to execute.\n"
                 "This is based on the playbook name in playbooks dir")
        return parser

    def run_playbook(self, playbook):
        """Executes given playbook."""
        self.ansibleManager.run_playbook(playbook, mode='create')


class NoSuchTemplateError(tobiko.TobikoException):
    message = "no such template; existing templates are: {templates}"


def main():
    """Create CLI main entry."""
    create_cmd = CreateUtil()
    create_cmd.set_stream_handler_logging_level()
    if create_cmd.args.playbook:
        create_cmd.run_playbook(create_cmd.args.playbook)


if __name__ == '__main__':
    sys.exit(main())
