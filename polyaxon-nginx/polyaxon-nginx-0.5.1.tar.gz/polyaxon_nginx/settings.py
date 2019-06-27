# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function

import os

import rhea

NGINX_CONFIG_PATH = '/polyaxon/web/nginx.json'

config = rhea.Rhea.read_configs([
    rhea.ConfigSpec(NGINX_CONFIG_PATH, check_if_exists=False),
    os.environ,
])

NGINX_PLUGINS = config.get_dict_of_dicts('POLYAXON_PLUGINS',
                                         is_optional=True,
                                         default={})
WS_PORT = config.get_int('POLYAXON_WS_PORT',
                         is_optional=True,
                         default=1337)
DNS_USE_RESOLVER = config.get_boolean('POLYAXON_DNS_USE_RESOLVER',
                                      is_optional=True,
                                      default=False)

DNS_CUSTOM_CLUSTER = config.get_string('POLYAXON_DNS_CUSTOM_CLUSTER',
                                       is_optional=True,
                                       default='cluster.local')
DNS_BACKEND = config.get_string('POLYAXON_DNS_BACKEND',
                                is_optional=True,
                                default='kube-dns')
DNS_PREFIX = config.get_string('POLYAXON_DNS_PREFIX',
                               is_optional=True)

NAMESPACE = config.get_string('POLYAXON_K8S_NAMESPACE',
                              is_optional=True)

LOGGING_LEVEL = config.get_string('POLYAXON_NGINX_LOGGING_LEVEL',
                                  is_optional=True,
                                  default='warn')

TIMEOUT = config.get_int('POLYAXON_NGINX_TIMEOUT',
                         is_optional=True,
                         default=600)

SSL_PATH = config.get_string('POLYAXON_SSL_PATH',
                             is_optional=True,
                             default='/etc/ssl/polyaxon')

INDENT_CHAR = config.get_string('POLYAXON_NGINX_INDENT_CHAR',
                                is_optional=True,
                                default=' ')

INDENT_WIDTH = config.get_int('POLYAXON_NGINX_INDENT_WIDTH',
                              is_optional=True,
                              default=4)

SSL_ENABLED = config.get_boolean('POLYAXON_SSL_ENABLED',
                                 is_optional=True,
                                 default=False)

REPOS_PATH = config.get_string('POLYAXON_NGINX_REPOS_PATH',
                               is_optional=True,
                               default='/repos')

DATA_PATH = config.get_string('POLYAXON_NGINX_DATA_PATH',
                              is_optional=True,
                              default='/data')

OUTPUTS_PATH = config.get_string('POLYAXON_NGINX_OUTPUTS_PATH',
                                 is_optional=True,
                                 default='/outputs')
