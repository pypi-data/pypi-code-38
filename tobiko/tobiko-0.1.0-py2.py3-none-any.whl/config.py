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

import importlib
import logging
import os

from oslo_config import cfg
from oslo_log import log

import tobiko

LOG = log.getLogger(__name__)

CONFIG_MODULES = ['tobiko.openstack.keystone.config',
                  'tobiko.openstack.neutron.config',
                  'tobiko.openstack.nova.config',
                  'tobiko.shell.ssh.config',
                  'tobiko.shell.ping.config',
                  'tobiko.shell.sh.config']

CONFIG_DIRS = [os.getcwd(),
               os.path.expanduser("~/.tobiko"),
               '/etc/tobiko']


class GlobalConfig(object):

    # this is a singletone
    _instance = None
    _sources = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = object.__new__(cls)
        return cls._instance

    def set_source(self, name, source_conf):
        if source_conf is None:
            raise TypeError("Config source cannot be None")
        actual = self._sources.setdefault(name, source_conf)
        if actual is not source_conf:
            msg = "Config source already registered: {!r}".format(name)
            raise RuntimeError(msg)

    def __getattr__(self, name):
        sources = self._sources.get(name)
        if sources is None:
            msg = "Config source not registered: {!r}".format(name)
            raise NoSuchConfigSource(msg)
        return sources


CONF = GlobalConfig()


def init_config():
    init_tobiko_config()
    init_environ_config()


def init_tobiko_config(default_config_dirs=None, product_name='tobiko',
                       version='unknown'):
    default_config_dirs = default_config_dirs or CONFIG_DIRS

    # Register configuration options
    conf = cfg.ConfigOpts()
    log.register_options(conf)
    register_tobiko_options(conf=conf)

    # Initialize tobiko configuration object
    conf(args=[], default_config_dirs=default_config_dirs)
    CONF.set_source('tobiko', conf)

    # setup final configuration
    log.setup(conf=conf, product_name=product_name, version=version)
    setup_tobiko_config(conf=conf)


def register_tobiko_options(conf):

    conf.register_opts(
        group=cfg.OptGroup('http'),
        opts=[cfg.StrOpt('http_proxy',
                         help="HTTP proxy URL for Rest APIs"),
              cfg.StrOpt('https_proxy',
                         help="HTTPS proxy URL for Rest APIs"),
              cfg.StrOpt('no_proxy',
                         help="Don't use proxy server to connect to listed "
                         "hosts")])

    for module_name in CONFIG_MODULES:
        module = importlib.import_module(module_name)
        if hasattr(module, 'register_tobiko_options'):
            module.register_tobiko_options(conf=conf)


def setup_tobiko_config(conf):
    # Redirect all warnings to logging library
    logging.captureWarnings(True)
    warnings_logger = log.getLogger('py.warnings')
    if conf.debug:
        if not warnings_logger.isEnabledFor(log.WARNING):
            # Print Python warnings
            warnings_logger.logger.setLevel(log.WARNING)
    elif warnings_logger.isEnabledFor(log.WARNING):
        # Silence Python warnings
        warnings_logger.logger.setLevel(log.ERROR)

    tobiko.setup_fixture(HttpProxyFixture)

    for module_name in CONFIG_MODULES:
        module = importlib.import_module(module_name)
        if hasattr(module, 'setup_tobiko_config'):
            module.setup_tobiko_config(conf=conf)


class HttpProxyFixture(tobiko.SharedFixture):
    """Make sure we have http proxy environment variables defined when required
    """

    http_proxy = None
    https_proxy = None
    no_proxy = None
    source = None

    def setup_fixture(self):
        source = None
        http_proxy = os.environ.get('http_proxy')
        https_proxy = os.environ.get('https_proxy')
        no_proxy = os.environ.get('no_proxy')
        if http_proxy or https_proxy:
            source = 'environment'
        else:
            http_conf = CONF.tobiko.http
            http_proxy = http_conf.http_proxy
            https_proxy = http_conf.https_proxy
            no_proxy = http_conf.no_proxy
            if http_proxy:
                os.environ['http_proxy'] = http_proxy
            if https_proxy:
                os.environ['https_proxy'] = https_proxy
            if http_proxy or https_proxy:
                source = 'tobiko.conf'
                if no_proxy:
                    os.environ['no_proxy'] = no_proxy

        if source:
            LOG.info("Using HTTP proxy configuration defined in %s:\n"
                     "  http_proxy: %r\n"
                     "  https_proxy: %r\n"
                     "  no_proxy: %r",
                     source, os.environ.get('http_proxy'),
                     os.environ.get('https_proxy'), os.environ.get('no_proxy'))
        else:
            LOG.debug("Connecting to REST API services without a proxy "
                      "server")

        self.source = source
        self.http_proxy = os.environ.get('http_proxy')
        self.https_proxy = os.environ.get('https_proxy')
        self.no_proxy = os.environ.get('no_proxy')


def init_environ_config():
    CONF.set_source('environ', EnvironConfig())


class EnvironConfig(object):

    def __getattr__(self, name):
        value = get_env(name)
        if value is None:
            msg = "Environment variable not defined: {!r}".format(name)
            raise cfg.NoSuchOptError(msg)
        return value


class NoSuchConfigSource(AttributeError):
    pass


def get_any_option(*sources, **kwargs):
    default = kwargs.get('default', None)
    for source in sources:
        value = CONF
        for name in source.split('.'):
            try:
                value = getattr(value, name)
            except (NoSuchConfigSource,
                    cfg.NoSuchOptError,
                    cfg.NoSuchGroupError) as ex:
                LOG.debug("No such option value for %r: %s", source, ex)
                break
        else:
            if value != default:
                return value
    return default


def get_env(name):
    value = os.environ.get(name)
    if value:
        return value
    else:
        LOG.debug("Environment variable %r is not defined")
        return None


def get_int_env(name):
    value = get_env(name)
    if value:
        try:
            return int(value)
        except TypeError:
            LOG.exception("Environment variable %r is not an integer: %r",
                          name, value)
    return None


init_config()
