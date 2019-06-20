import logging
import re

import boto3.session
import pkg_resources
import requests
from munch import munchify
from pkg_resources import iter_entry_points
from probator.constants import PLUGIN_NAMESPACES
from probator.exceptions import ProbatorError
from probator.utils import get_user_data_configuration, read_config, get_vault_configuration
from werkzeug.local import LocalProxy

__version__ = pkg_resources.get_distribution('probator').version

logger = logging.getLogger(__name__)
__regions = None
__plugins = None

# Setup app wide variables
config_path, app_config = LocalProxy(read_config)


def get_local_aws_session():
    """Returns a session for the local instance, not for a remote account

    Returns:
        :obj:`boto3:boto3.session.Session`
    """
    if not all((app_config.aws_api.access_key, app_config.aws_api.secret_key)):
        return boto3.session.Session()
    else:
        # If we are not running on an EC2 instance, assume the instance role
        # first, then assume the remote role
        session_args = [app_config.aws_api.access_key, app_config.aws_api.secret_key]
        if app_config.aws_api.session_token:
            session_args.append(app_config.aws_api.session_token)

        return boto3.session.Session(*session_args)


def get_aws_session(account):
    """Function to return a boto3 Session based on the account passed in the first argument.

    Args:
        account (:obj:`Account`): Account to create the session object for

    Returns:
        :obj:`boto3:boto3.session.Session`
    """
    from probator.config import dbconfig
    from probator.plugins.types.accounts import AWSAccount

    if not isinstance(account, AWSAccount):
        raise ProbatorError(f'Non AWSAccount passed to get_aws_session, got a {account.__class__.__name__} object')

    # If no keys are on supplied for the account, use sts.assume_role instead
    session = get_local_aws_session()
    if session.get_credentials().method == 'iam-role':
        sts = session.client('sts')
    else:
        # If we are not running on an EC2 instance, assume the instance role
        # first, then assume the remote role
        temp_sts = session.client('sts')

        audit_sts_role = temp_sts.assume_role(
            RoleArn=app_config.aws_api.instance_role_arn,
            RoleSessionName='probator'
        )
        sts = boto3.session.Session(
            audit_sts_role['Credentials']['AccessKeyId'],
            audit_sts_role['Credentials']['SecretAccessKey'],
            audit_sts_role['Credentials']['SessionToken']
        ).client('sts')

    role = sts.assume_role(
        RoleArn=f'arn:aws:iam::{account.account_number}:role/{dbconfig.get("role_name", default="probator_role")}',
        RoleSessionName='probator'
    )

    sess = boto3.session.Session(
        role['Credentials']['AccessKeyId'],
        role['Credentials']['SecretAccessKey'],
        role['Credentials']['SessionToken']
    )

    return sess


def get_aws_regions(*, force=False):
    """Load a list of AWS regions from the AWS static data.

    Args:
        force (`bool`): Force fetch list of regions even if we already have a cached version

    Returns:
        :obj:`list` of `str`
    """
    from probator.config import dbconfig
    global __regions

    if force or not __regions:
        logger.debug('Loading list of AWS regions from static data')
        data = requests.get('https://ip-ranges.amazonaws.com/ip-ranges.json').json()
        rgx = re.compile(dbconfig.get('ignored_aws_regions_regexp', default='(^cn-|GLOBAL|-gov)'), re.I)
        __regions = sorted(list({x['region'] for x in data['prefixes'] if not rgx.search(x['region'])}))

    return __regions


def get_plugin_by_name(ns, name):
    """Load a plugin by namespace.name

    Args:
        ns (`str`): Plugin namespace
        name (`str`): Plugin name

    Returns:
        `class`,`None` - Return the class object for the requested plugin, if found
    """
    for plugin in PROBATOR_PLUGINS[ns]['plugins']:
        if plugin.name == name:
            return plugin.load()


def load_plugins():
    """Load available plugins

    Returns:
        `dict`
    """
    global __plugins

    if not __plugins:
        __plugins = {}
        for plugin_type, namespace in PLUGIN_NAMESPACES.items():
            __plugins[namespace] = munchify({
                'name': plugin_type,
                'plugins': []
            })

            try:
                for entry_point in iter_entry_points(namespace):
                    __plugins[namespace]['plugins'].append(entry_point)

            except Exception as ex:
                print(f'Failed loading plugin: {ex}')

    return __plugins


# Check if the user has opted to use userdata based configuration for DB, and load it if needed
if app_config.config_method == 'userdata':
    get_user_data_configuration()

elif app_config.config_method == 'vault':
    get_vault_configuration()

AWS_REGIONS = LocalProxy(get_aws_regions)
PROBATOR_PLUGINS = LocalProxy(load_plugins)
