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

from oslo_config import cfg


def register_tobiko_options(conf):

    conf.register_opts(
        group=cfg.OptGroup('keystone'),
        opts=[cfg.IntOpt('api_version',
                         default=None,
                         help="Identity API version"),
              cfg.StrOpt('auth_url',
                         default=None,
                         help="Identity service URL"),
              cfg.StrOpt('username',
                         default=None,
                         help="Username"),
              cfg.StrOpt('project_name',
                         default=None,
                         help="Project name"),
              cfg.StrOpt('password',
                         default=None,
                         help="Password"),
              cfg.StrOpt('domain_name',
                         default=None,
                         help="Domain name"),
              cfg.StrOpt('user_domain_name',
                         default=None,
                         help="User domain name"),
              cfg.StrOpt('project_domain_name',
                         default=None,
                         help="Project domain name"),
              cfg.StrOpt('project_domain_id',
                         default=None,
                         help="Project domain ID"),
              cfg.StrOpt('trust_id',
                         default=None,
                         help="Trust ID for trust scoping.")])
