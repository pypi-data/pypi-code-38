"""Module containing constants for use througout the application
"""
import os
import re
from dataclasses import dataclass, field
from typing import Any

from munch import munchify


@dataclass
class ConfigOption(object):
    name: str
    default_value: Any
    type: str
    description: str = None


@dataclass
class NewResource(object):
    resource_id: str
    properties: dict
    tags: dict = field(default_factory=dict)
    parent: object = None


# region Plugin namespaces
PLUGIN_NAMESPACES = munchify({
    'auditor': 'probator.plugins.auditors',
    'auth': 'probator.plugins.auth',
    'collector': 'probator.plugins.collectors',
    'commands': 'probator.plugins.commands',
    'notifier': 'probator.plugins.notifiers',
    'schedulers': 'probator.plugins.schedulers',
    'types': 'probator.plugins.types',
    'accounts': 'probator.plugins.types.accounts',
    'view': 'probator.plugins.views',
    'issues': 'probator.plugins.types.issues',
})
# endregion

# region Regular Expressions
RGX_BUCKET = re.compile(r'(?P<bucket>.*?)\.s3(-website-(?P<region>.*?))?\.amazonaws.com')
RGX_BUCKET_WEBSITE = re.compile(r'^s3-website-(?P<region>.*?)?\.amazonaws.com')
RGX_DOMAIN_NAME = re.compile(r'(?=^.{4,253}$)(^((?!-)[a-zA-Z0-9-]{0,62}[a-zA-Z0-9]\.)+[a-zA-Z]{2,63}$)')
RGX_EMAIL_VALIDATION_PATTERN = r'([a-zA-Z0-9._%+-]+[^+]@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})'
RGX_INSTANCE = re.compile(r'^i-(?:[0-9a-fA-F]{8}|[0-9a-fA-F]{17})$', re.IGNORECASE)
RGX_INSTANCE_DNS = re.compile(r'ec2-(\d+)-(\d+)-(\d+)-(\d+)\.(?:.*\.compute|compute-\d)\.amazonaws.com')
RGX_IP = re.compile(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', re.IGNORECASE)
RGX_TAG = re.compile(r'^(?P<type>tag):(?P<value>.*)$', re.IGNORECASE)
RGX_PROPERTY = re.compile(r'^(?P<type>property):(?P<value>.*)$', re.IGNORECASE)
# endregion

# region Built-in roles
ROLE_ADMIN = 'Admin'
ROLE_NOC = 'NOC'
ROLE_USER = 'User'
# endregion

# region General variables
UNAUTH_MESSAGE = 'Unauthorized, please log in'
MSG_INVALID_USER_OR_PASSWORD = 'Invalid user or password provided'
# endregion

# region Default app settings
CONFIG_FILE_PATHS = (
    os.path.expanduser('~/.probator/config.json'),
    os.path.join(os.getcwd(), 'config.json'),
    '/usr/local/etc/probator/config.json',
)

DEFAULT_CONFIG = {
    'log_level': 'INFO',
    'config_method': 'local',
    'kms_region': 'us-west-2',
    'user_data_url': 'http://169.254.269.254/latest/user-data',

    'aws_api': {
        'access_key': None,
        'secret_key': None,
        'instance_role_arn': None,
        'session_token': None
    },

    'database_uri': 'mysql://probator:secretpass@localhost:3306/probator',

    'flask': {
        'secret_key': 'verysecretkey',
        'json_sort_keys': False,
    },

    'vault': {
        'address': None,
        'path': None,
        'role_id': None,
        'secret_id': None,
    }
}

DEFAULT_CONFIG_OPTIONS = [
    {
        'prefix': 'default',
        'name': 'Default',
        'sort_order': 0,
        'options': [
            ConfigOption('debug', False, 'bool', 'Enable debug mode for flask'),
            ConfigOption('session_expire_time', 43200, 'int', 'Time in seconds before sessions expire'),
            ConfigOption(
                'role_name',
                'probator_role',
                'string',
                'Role name Probator will use in each account'
            ),
            ConfigOption(
                'ignored_aws_regions_regexp',
                '(^cn-|GLOBAL|-gov)',
                'string',
                'A regular expression used to filter out regions from the AWS static data'
            ),
            ConfigOption(
                name='auth_system',
                default_value={
                    'enabled': ['Local Authentication'],
                    'available': ['Local Authentication'],
                    'max_items': 1,
                    'min_items': 1
                },
                type='choice',
                description='Enabled authentication module'
            ),
            ConfigOption('scheduler', 'StandaloneScheduler', 'string', 'Default scheduler module'),
            ConfigOption(
                'jwt_key_file_path',
                'ssl/private.key',
                'string',
                'Path to the private key used to encrypt JWT session tokens. Can be relative to the '
                'folder containing the configuration file, or absolute path'
            )
        ],
    },
    {
        'prefix': 'log',
        'name': 'Logging',
        'sort_order': 1,
        'options': [
            ConfigOption('log_level', 'INFO', 'string', 'Log level'),
            ConfigOption(
                'enable_syslog_forwarding',
                False,
                'bool',
                'Enable forwarding logs to remote log collector'
            ),
            ConfigOption(
                'remote_syslog_server_addr',
                '127.0.0.1',
                'string',
                'Address of the remote log collector'
            ),
            ConfigOption('remote_syslog_server_port', 514, 'string', 'Port of the remote log collector'),
            ConfigOption('log_keep_days', 31, 'int', 'Delete log entries older than n days'),
        ],
    },
    {
        'prefix': 'api',
        'name': 'API',
        'sort_order': 2,
        'options': [
            ConfigOption('host', '127.0.0.1', 'string', 'Host of the API server'),
            ConfigOption('port', 5000, 'int', 'Port of the API server'),
            ConfigOption('workers', 6, 'int', 'Number of worker processes spawned for the API')
        ]
    },
    {
        'prefix': 'collector_aws',
        'name': 'AWS Collector',
        'sort_order': 2,
        'options': [
            ConfigOption('enabled', True, 'bool', 'Enable the AWS Region-based Collector'),
            ConfigOption('interval', 15, 'int', 'Run frequency, in minutes'),
            ConfigOption('max_instances', 1000, 'int', 'Maximum number of instances per API call'),
        ]
    }
]
# endregion


# HTTP Response codes
class HTTP(object):
    OK = 200
    CREATED = 201
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    CONFLICT = 409
    SERVER_ERROR = 500
    UNAVAILABLE = 503


class SchedulerStatus(object):
    PENDING = 0
    STARTED = 1
    COMPLETED = 2
    ABORTED = 8
    FAILED = 9


class AccountTypes(object):
    AWS = 'AWS'
    DNS_AXFR = 'DNS_AXFR'
    DNS_CLOUDFLARE = 'DNS_CLOUDFLARE'
