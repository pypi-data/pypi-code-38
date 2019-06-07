# Copyright (c) 2018 Red Hat
# All Rights Reserved.
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

import os
import logging
import argparse

from oslo_log import log

from tobiko.common.managers import ansible
from tobiko import config


LOG = log.getLogger(__name__)


class TobikoCMD(object):
    """Manages different command line utilities."""

    def __init__(self):
        config.CONF.tobiko.use_stderr = True
        log.setup(config.CONF.tobiko, 'tobiko')
        self.parser = self.get_parser()
        self.args = (self.parser).parse_args()

        curr_dir = os.path.dirname(__file__)
        self.playbooks_dir = os.path.join(curr_dir,
                                          "../tests/scenario/playbooks")
        self.ansibleManager = ansible.AnsibleManager(self.playbooks_dir)

    def get_parser(self):
        parser = argparse.ArgumentParser(add_help=True)
        parser.add_argument('--verbose', '-v', action='count',
                            help='Make the output more verbose, incremental.')
        parser.add_argument('--quiet', '-q', action='count',
                            help='Make the output less verbose, incremental.')
        return parser

    def set_stream_handler_logging_level(self):
        num_quiet = self.args.quiet or 0
        num_verb = self.args.verbose or 0
        level = logging.WARNING - (num_verb * 10) + (num_quiet * 10)
        root_logger = logging.getLogger()
        for handler in root_logger.handlers:
            if isinstance(handler, logging.StreamHandler):
                handler.setLevel(level)
