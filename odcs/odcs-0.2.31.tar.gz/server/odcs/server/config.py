# -*- coding: utf-8 -*-

# Copyright (c) 2016  Red Hat, Inc.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
# Written by Jan Kaluza <jkaluza@redhat.com>

import imp
import os
import sys

from odcs.server import logger
from odcs.common.types import COMPOSE_RESULTS, COMPOSE_FLAGS


def init_config(app):
    """
    Configure ODCS
    """
    config_module = None
    config_file = '/etc/odcs/config.py'
    config_section = 'DevConfiguration'

    # automagically detect production environment:
    #   - existing and readable config_file presets ProdConfiguration
    try:
        with open(config_file):
            config_section = 'ProdConfiguration'
    except (OSError, IOError) as e:
        # Use stderr here, because logging is not initialized so far...
        sys.stderr.write("WARN: Cannot open %s: %s\n" % (
            config_file, e.strerror))
        sys.stderr.write("WARN: DevConfiguration will be used.\n")

    # try getting config_file from os.environ
    if 'ODCS_CONFIG_FILE' in os.environ:
        config_file = os.environ['ODCS_CONFIG_FILE']
    # try getting config_section from os.environ
    if 'ODCS_CONFIG_SECTION' in os.environ:
        config_section = os.environ['ODCS_CONFIG_SECTION']
    # TestConfiguration shall only be used for running tests, otherwise...
    if any(['nosetests' in arg or 'noserunner.py' in arg or 'py.test' in arg or 'pytest.py' in arg for arg in sys.argv]):
        config_section = 'TestConfiguration'
        from conf import config
        config_module = config
    # ...ODCS_DEVELOPER_ENV has always the last word
    # and overrides anything previously set before!
    # In any of the following cases, use configuration directly from ODCS
    # package -> /conf/config.py.

    elif ('ODCS_DEVELOPER_ENV' in os.environ and
          os.environ['ODCS_DEVELOPER_ENV'].lower() in (
            '1', 'on', 'true', 'y', 'yes')):
        config_section = 'DevConfiguration'
        from conf import config
        config_module = config
    # try loading configuration from file
    if not config_module:
        try:
            config_module = imp.load_source('odcs_runtime_config',
                                            config_file)
        except Exception:
            raise SystemError("Configuration file {} was not found."
                              .format(config_file))

    # finally configure ODCS
    config_section_obj = getattr(config_module, config_section)
    conf = Config(config_section_obj)
    app.config.from_object(config_section_obj)
    return conf


class Config(object):
    """Class representing the odcs configuration."""
    _defaults = {
        'debug': {
            'type': bool,
            'default': False,
            'desc': 'Debug mode'},
        'log_backend': {
            'type': str,
            'default': None,
            'desc': 'Log backend'},
        'log_file': {
            'type': str,
            'default': '',
            'desc': 'Path to log file'},
        'log_level': {
            'type': str,
            'default': 0,
            'desc': 'Log level'},
        'net_timeout': {
            'type': int,
            'default': 120,
            'desc': 'Global network timeout for read/write operations, in seconds.'},
        'net_retry_interval': {
            'type': int,
            'default': 30,
            'desc': 'Global network retry interval for read/write operations, in seconds.'},
        'arches': {
            'type': list,
            'default': ["x86_64"],
            'desc': 'Compose architectures.'},
        'pungi_koji': {
            'type': str,
            'default': "pungi-koji",
            'desc': 'Name or full-path to pungi-koji binary.'},
        'pungi_timeout': {
            'type': int,
            'default': 3600,
            'desc': 'Time in seconds after which the local pungi-koji is '
                    'killed and compose is marked as failed'},
        'pungi_runroot_enabled': {
            'type': bool,
            'default': False,
            'desc': 'When True, ODCS will run Pungi in Koji runroot'},
        'pungi_parent_runroot_channel': {
            'type': str,
            'default': "",
            'desc': 'Name of Koji channel to run pungi runroot task with.'},
        'pungi_parent_runroot_packages': {
            'type': list,
            'default': "",
            'desc': 'List of packages to install to pungi Koji runroot task.'},
        'pungi_parent_runroot_mounts': {
            'type': list,
            'default': "",
            'desc': 'List of mounts to mount in pungi Koji runroot task.'},
        'pungi_parent_runroot_weight': {
            'type': float,
            'default': 3,
            'desc': 'Weight of pungi Koji runroot task.'},
        'pungi_parent_runroot_tag': {
            'type': str,
            'default': "",
            'desc': 'Name of tag to run pungi Koji runroot task for.'},
        'pungi_parent_runroot_arch': {
            'type': str,
            'default': "x86_64",
            'desc': 'Architecture to run pungi Koji runroot task for.'},
        'pungi_runroot_target_dir': {
            'type': str,
            'default': "",
            'desc': 'Path to target dir to which store composes done by pungi in runroot'},
        'pungi_runroot_target_dir_url': {
            'type': str,
            'default': "",
            'desc': 'Public facing URL to target_dir.'},
        'pungi_conf_path': {
            'type': str,
            'default': "/etc/odcs/pungi.conf",
            'desc': 'Full path to the pungi.conf jinja2 template.'},
        'pungi_runroot_koji_conf_path': {
            'type': str,
            'default': "/etc/odcs/runroot_koji.conf",
            'desc': 'Full path to the runroot_koji.conf configuration file. '
                    'This file holds Koji configuration used in a Pungi parent '
                    'runroot task if pungi_runroot_enabled is True.'},
        'target_dir': {
            'type': str,
            'default': "/tmp",
            'desc': 'Path to target dir to which store composes'},
        'target_dir_url': {
            'type': str,
            'default': "http://localhost/odcs",
            'desc': 'Public facing URL to target_dir.'},
        'seconds_to_live': {
            'type': int,
            'default': 24 * 60 * 60,
            'desc': 'Default number of seconds for which the compose is available.'},
        'max_seconds_to_live': {
            'type': int,
            'default': 72 * 60 * 60,
            'desc': 'Max number of seconds for which the compose is available.'},
        'mbs_url': {
            'type': str,
            'default': "http://localhost/module-build-service",
            'desc': 'URL to MSB API.'},
        'num_concurrent_pungi': {
            'type': int,
            'default': 2,
            'desc': 'Number of concurrent Pungi processes.'},
        'allowed_source_types': {
            'type': list,
            'default': ["tag", "module", "build"],
            'desc': 'Allowed source types.'},
        'allowed_flags': {
            'type': list,
            'default': COMPOSE_FLAGS.keys(),
            'desc': 'Allowed compose flags.'},
        'allowed_arches': {
            'type': list,
            'default': ["x86_64"],
            'desc': 'Allowed compose arches.'},
        'allowed_results': {
            'type': list,
            'default': COMPOSE_RESULTS,
            'desc': 'Allowed compose results.'},
        'allowed_sources': {
            'type': list,
            'default': [""],
            'desc': 'Allowed sources.'},
        'auth_ldap_server': {
            'type': str,
            'default': '',
            'desc': "Server URL to query user's groups."},
        'auth_ldap_group_base': {
            'type': str,
            'default': '',
            'desc': "Group base to query user's groups from LDAP server."},
        'allowed_clients': {
            'type': dict,
            'default': {'groups': {}, 'users': {}},
            'desc': "Groups and users that are allowed to generate composes."},
        'admins': {
            'type': dict,
            'default': {'groups': [], 'users': []},
            'desc': "Admin groups and users."},
        'auth_backend': {
            'type': str,
            'default': '',
            'desc': "Select which authentication backend is enabled and work "
                    "with frond-end authentication together."},
        'auth_openidc_userinfo_uri': {
            'type': str,
            'default': '',
            'desc': 'UserInfo endpoint to get user information from FAS.'},
        'auth_openidc_required_scopes': {
            'type': list,
            'default': [],
            'desc': 'Required scopes for submitting request to run new compose.'},
        'base_module_names': {
            'type': set,
            'default': set(['platform', 'bootstrap']),
            'desc': ("Set of module names which defines the product version "
                     "(by their stream) of modules depending on them.")},
        'messaging_backend': {
            'type': str,
            'default': '',
            'desc': 'Messaging backend, fedmsg or umb.'},
        'messaging_broker_urls': {
            'type': list,
            'default': [],
            'desc': 'List of messaging broker URLs.'},
        'messaging_cert_file': {
            'type': str,
            'default': '',
            'desc': 'Path to certificate file used to authenticate ODCS by broker.'},
        'messaging_key_file': {
            'type': str,
            'default': '',
            'desc': 'Path to private key file used to authenticate ODCS by broker.'},
        'messaging_ca_cert': {
            'type': str,
            'default': '',
            'desc': 'Path to trusted CA certificate bundle.'},
        'messaging_topic_prefix': {
            'type': str,
            'default': '',
            'desc': 'Prefix for MESSAGING_TOPIC and INTERNAL_MESSAGING_TOPIC.'
        },
        'messaging_topic': {
            'type': str,
            'default': '',
            'desc': 'Messaging topic to which messages are sent.'},
        'internal_messaging_topic': {
            'type': str,
            'default': '',
            'desc': 'Messaging topic to which internal ODCS-only messages are sent.'},
        'oidc_base_namespace': {
            'type': str,
            'default': 'https://pagure.io/odcs/',
            'desc': 'Base namespace of OIDC scopes.'},
        'sigkeys': {
            'type': list,
            'default': [],
            'desc': 'Default list of sigkeys. Any package in a compose must '
                    'be signed by one of those keys. Can be overriden in a '
                    'compose request.'},
        'pulp_server_url': {
            'type': str,
            'default': '',
            'desc': 'Server URL of Pulp.'},
        'pulp_username': {
            'type': str,
            'default': '',
            'desc': 'Username to login Pulp.'},
        'pulp_password': {
            'type': str,
            'default': '',
            'desc': 'Password to login Pulp.'},
        'koji_config': {
            'type': str,
            'default': None,
            'desc': 'Koji config file.'},
        'koji_profile': {
            'type': str,
            'default': None,
            'desc': 'Koji config profile.'},
        'koji_krb_ccache': {
            'type': str,
            'default': None,
            'desc': 'Kerberos ccache file to use for Koji auth.'},
        'koji_krb_keytab': {
            'type': str,
            'default': None,
            'desc': 'Kerberos keytab to use for Koji auth.'},
        'koji_krb_principal': {
            'type': str,
            'default': None,
            'desc': 'Kerberos principal to use for Koji auth.'},
        'koji_tag_cache_cleanup_timeout': {
            'type': int,
            'default': 30,
            'desc': 'Number of days after which the cached Koji tag data '
                    'stored in the "koji_tag_cache" directory will be '
                    'removed.'},
        'raw_config_urls': {
            'type': dict,
            'default': {},
            'desc': 'URLs to get the raw Pungi config from for "raw_config" '
                    'source_type. Key is the name of the raw_config "source", '
                    'value is the URL in which the %s string is replaced with, '
                    '"commit_hash" value.'},
        'raw_config_wrapper_conf_path': {
            'type': str,
            'default': "/etc/odcs/raw_config_wrapper.conf",
            'desc': 'Full path to the raw_config_wrapper.conf configuration '
                    'file. This file holds Pungi configuration which should '
                    'import real pungi configuration from raw_config.conf '
                    'in order to override some variables.'},
        'pungi_koji_args': {
            'type': list,
            'default': [],
            'desc': 'Command line arguments used to construct pungi-koji '
                    'command.'
        },
        'raw_config_pungi_koji_args': {
            'type': dict,
            'default': {},
            'desc': 'Command line argument for raw_config source type, which '
                    'overwrite arguments listed PUNGI_KOJI_ARGS.'
        },
        'celery_config': {
            'type': dict,
            'default': {},
            'desc': 'Configuration dict to pass to Celery.'
        },
        'celery_broker_url': {
            'type': str,
            'default': "",
            'desc': 'Celery broker URL'
        },
        'celery_pulp_composes_queue': {
            'type': str,
            'default': "pulp_composes",
            'desc': 'Name of the Celery queue for Pulp composes.'
        },
        'celery_pungi_composes_queue': {
            'type': str,
            'default': "pungi_composes",
            'desc': 'Name of the Celery queue for Pungi composes.'
        },
        'celery_cleanup_queue': {
            'type': str,
            'default': "cleanup",
            'desc': 'Name of the Celery queue for cleanup task.'
        },
        'celery_router_config': {
            'type': dict,
            'default': {
                "routing_rules": {
                    "odcs.server.celery_tasks.generate_pungi_compose": {
                        "pungi_composes": {
                            "source_type": 3,
                        },
                    },
                    "odcs.server.celery_tasks.generate_pulp_compose": {
                        "pulp_composes": {
                            "source_type": 4,
                        },
                    },
                },
                "cleanup_task": "odcs.server.celery_tasks.run_cleanup",
                "default_queue": "pungi_composes",
            },
            'desc': 'Configuration for custom celery router.'
        },
        'runroot_extra_mounts': {
            'type': list,
            'default': [],
            'desc': 'Extra mountpoint directories for odcs-mock-runroot.'
        },
    }

    def __init__(self, conf_section_obj):
        """
        Initialize the Config object with defaults and then override them
        with runtime values.
        """

        # read items from conf and set
        for key in dir(conf_section_obj):
            # skip keys starting with underscore
            if key.startswith('_'):
                continue
            # set item (lower key)
            self.set_item(key.lower(), getattr(conf_section_obj, key))

        # set item from defaults if the item is not set
        for name, values in self._defaults.items():
            if hasattr(self, name):
                continue
            self.set_item(name, values['default'])

        # Used by Flask-Login to disable the @login_required decorator
        self.login_disabled = self.auth_backend == 'noauth'

    def set_item(self, key, value):
        """
        Set value for configuration item. Creates the self._key = value
        attribute and self.key property to set/get/del the attribute.
        """
        if key == 'set_item' or key.startswith('_'):
            raise Exception("Configuration item's name is not allowed: %s" % key)

        # Create the empty self._key attribute, so we can assign to it.
        setattr(self, "_" + key, None)

        # Create self.key property to access the self._key attribute.
        # Use the setifok_func if available for the attribute.
        setifok_func = '_setifok_{}'.format(key)
        if hasattr(self, setifok_func):
            setx = lambda self, val: getattr(self, setifok_func)(val)
        else:
            setx = lambda self, val: setattr(self, "_" + key, val)
        getx = lambda self: getattr(self, "_" + key)
        delx = lambda self: delattr(self, "_" + key)
        setattr(Config, key, property(getx, setx, delx))

        # managed/registered configuration items
        if key in self._defaults:
            # type conversion for configuration item
            convert = self._defaults[key]['type']
            if convert in [bool, int, list, str, set, dict, float]:
                try:
                    # Do no try to convert None...
                    if value is not None:
                        value = convert(value)
                except Exception:
                    raise TypeError("Configuration value conversion failed for name: %s" % key)
            # unknown type/unsupported conversion
            elif convert is not None:
                raise TypeError("Unsupported type %s for configuration item name: %s" % (convert, key))

        # Set the attribute to the correct value
        setattr(self, key, value)

    #
    # Register your _setifok_* handlers here
    #

    def _setifok_allowed_clients(self, clients):
        if type(clients) != dict:
            raise TypeError("allowed_clients must be a dict.")
        for role, role_dict in clients.items():
            if role not in ["users", "groups"]:
                raise ValueError("Unknown role %s in allowed_clients." % role)
            if type(role_dict) != dict:
                raise TypeError("allowed_clients['%s'] is not a dict" % role)
            for user, user_dict in role_dict.items():
                if type(user_dict) != dict:
                    raise TypeError(
                        "allowed_clients['%s']['%s'] is not a dict" % (role, user))
                for key, value in user_dict.items():
                    if type(value) not in [set, list]:
                        raise ValueError(
                            "allowed_clients['%s']['%s']['%s'] is not a "
                            "list" % (role, user, key))
        self._allowed_clients = clients

    def _setifok_raw_config_urls(self, raw_config_urls):
        if type(raw_config_urls) != dict:
            raise TypeError("raw_config_urls must be a dict.")
        for name, url_data in raw_config_urls.items():
            if type(url_data) != dict:
                raise TypeError("raw_config_urls['%s'] is not a dict." % name)
            for key in ["url", "config_filename"]:
                if key not in url_data:
                    raise ValueError(
                        "raw_config_urls['%s']['%s'] is not defined."
                        % (name, key))
        self._raw_config_urls = raw_config_urls

    def _setifok_log_backend(self, s):
        if s is None:
            self._log_backend = "console"
        elif s not in logger.supported_log_backends():
            raise ValueError("Unsupported log backend")
        self._log_backend = str(s)

    def _setifok_log_file(self, s):
        if s is None:
            self._log_file = ""
        else:
            self._log_file = str(s)

    def _setifok_log_level(self, s):
        level = str(s).lower()
        self._log_level = logger.str_to_log_level(level)

    def _setifok_target_dir(self, s):
        if not os.path.isabs(s):
            raise ValueError("Compose target dir is not an absolute path: %s" % s)
        if not (os.path.exists(s) and os.path.isdir(s)):
            raise ValueError("Compose target dir doesn't exist or not a directory: %s" % s)
        self._target_dir = s

    def _setifok_pungi_conf_path(self, s):
        if not os.path.isfile(s):
            raise ValueError("Pungi config template doesn't exist: %s" % s)
        self._pungi_conf_path = s

    def _setifok_celery_router_config(self, celery_router_config):
        if type(celery_router_config) != dict:
            raise TypeError("celery_router_config must be a dict.")

        required_config_keys = ["routing_rules", "cleanup_task", "default_queue"]

        for conf_key in required_config_keys:
            if not celery_router_config.get(conf_key):
                raise KeyError("celery_router_config is missing %s" % conf_key)

        if type(celery_router_config["routing_rules"]) != dict:
            raise TypeError("routing_rules must be a dict.")

        self._celery_router_config = celery_router_config
