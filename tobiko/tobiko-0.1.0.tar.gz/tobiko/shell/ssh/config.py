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

import getpass

from oslo_config import cfg
from oslo_log import log


def register_tobiko_options(conf):
    conf.register_opts(
        group=cfg.OptGroup('ssh'),
        opts=[cfg.BoolOpt('debug',
                          default=False,
                          help=('Logout debugging messages of paramiko '
                                'library')),
              cfg.StrOpt('command',
                         default='/usr/bin/ssh',
                         help=('Default SSH client command')),
              cfg.StrOpt('port',
                         default=22,
                         help=('Default SSH port')),
              cfg.StrOpt('username',
                         default=getpass.getuser(),
                         help=('Default SSH username')),
              cfg.ListOpt('config_files',
                          default=['/etc/ssh/ssh_config', '~/.ssh/config'],
                          help="Default user SSH configuration files"),
              cfg.StrOpt('key_file',
                         default='~/.ssh/id_rsa',
                         help="Default SSH private key file"),
              cfg.BoolOpt('allow_agent',
                          default=False,
                          help=("Set to False to disable connecting to the "
                                "SSH agent")),
              cfg.BoolOpt('compress',
                          default=False,
                          help="Set to True to turn on compression"),
              cfg.FloatOpt('timeout',
                           default=5.,
                           help="SSH connect timeout in seconds"),
              cfg.IntOpt('connection_attempts',
                         default=24,
                         help=("Incremental seconds to wait after every "
                               "failed SSH connection attempt")),
              cfg.FloatOpt('connection_interval',
                           default=5.,
                           help=("Minimal seconds to wait between every "
                                 "failed SSH connection attempt")),
              cfg.StrOpt('proxy_jump',
                         default=None,
                         help="Default SSH proxy server"),
              cfg.StrOpt('proxy_command',
                         default=None,
                         help="Default proxy command"),
              ])


def setup_tobiko_config(conf):
    paramiko_logger = log.getLogger('paramiko')
    if conf.ssh.debug:
        if not paramiko_logger.isEnabledFor(log.DEBUG):
            # Print paramiko debugging messages
            paramiko_logger.logger.setLevel(log.DEBUG)
    elif paramiko_logger.isEnabledFor(log.DEBUG):
        # Silence paramiko debugging messages
        paramiko_logger.logger.setLevel(log.WARNING)
