import binascii
import hashlib
import json
import logging
import os
import random
import re
import string
import time
import zlib
from base64 import b64decode
from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime
from difflib import unified_diff
from functools import wraps

import boto3.session
import hvac
import jwt
import munch
import requests
from argon2 import PasswordHasher
from dateutil import parser
from hvac.exceptions import Forbidden
from jinja2 import Environment, BaseLoader
from probator.constants import RGX_EMAIL_VALIDATION_PATTERN, RGX_BUCKET, ROLE_ADMIN, DEFAULT_CONFIG, CONFIG_FILE_PATHS
from probator.exceptions import ProbatorError

__jwt_data = None

log = logging.getLogger(__name__)


@dataclass
class NotificationContact(object):
    """Notification Contact object

    This object describes a single notification contact. This is used by the notification systems to decide which notification
    plugins is responsible for sending the notification.

    >>> NotificationContact(type='slack', value='#noc')
    NotificationContact(type='slack', value='#noc')

    or

    >>> NotificationContact(type='email', value='me@domain.tld')
    NotificationContact(type='email', value='me@domain.tld')

    Args:
        type (str): Type of contact
        value (str): Value of the contact informations, for example ``#noc`` or ``user@domain.tld``
    """
    type: str
    value: str

    def __hash__(self):
        return hash(f'type={self.type}|value={self.value}')

    @classmethod
    def get(cls, data):
        return cls(type=data['type'], value=data['value'])


def deprecated(msg):
    """Marks a function / method as deprecated.

    Takes one argument, a message to be logged with information on future usage of the function or alternative methods
    to call.

    >>> @deprecated('This method is deprecated')
    ... def test():
    ...     print('Hello there')
    ...     print('General Kenobi!')
    ...
    >>> test()
    This method is deprecated
    Hello there
    General Kenobi!

    Args:
        msg (str): Deprecation message to be logged

    Returns:
        `callable`
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            logging.getLogger(__name__).warning(msg)
            return func(*args, **kwargs)

        return wrapper

    return decorator


def get_hash(data):
    """Return the SHA256 hash of an object

    >>> get_hash('my-test-string')
    '56426297313df008f6ac9d4554b0724a2b3d39a7134bf2d9aede21ec680dd9c4'

    Args:
        data: Object to hash

    Returns:
        SHA256 hash of the object
    """
    return hashlib.sha256(str(data).encode('utf-8')).hexdigest()


def is_truthy(value, default=False):
    """Evaluate a value for truthiness

    >>> is_truthy('Yes')
    True
    >>> is_truthy('False')
    False
    >>> is_truthy(1)
    True

    Args:
        value (Any): Value to evaluate
        default (bool): Optional default value, if the input does not match the true or false values

    Returns:
        True if a truthy value is passed, else False
    """

    if value is None:
        return False

    if isinstance(value, bool):
        return value

    if isinstance(value, int):
        return value > 0

    trues = ('1', 'true', 'y', 'yes', 'ok')
    falses = ('', '0', 'false', 'n', 'none', 'no')

    if value.lower().strip() in falses:
        return False

    elif value.lower().strip() in trues:
        return True

    else:
        if default:
            return default
        else:
            raise ValueError(f'Invalid argument given to truthy: {value}')


def validate_email(email, partial_match=False):
    """Perform email address validation

    >>> validate_email('user@domain.tld')
    True
    >>> validate_email('John Doe <user@domain.tld')
    False
    >>> validate_email('John Doe <user@domain.tld', partial_match=True)
    True

    Args:
        email (str): Email address to match
        partial_match (bool): If False (default), the entire string must be a valid email address. If true, any valid
         email address in the string will trigger a valid response

    Returns:
        True if the value contains an email address, else False
    """
    rgx = re.compile(RGX_EMAIL_VALIDATION_PATTERN, re.I)
    if partial_match:
        return rgx.search(email) is not None
    else:
        return rgx.match(email) is not None


def get_template(template):
    """Return a Jinja2 template by filename

    Args:
        template (str): Name of the template to return

    Returns:
        A Jinja2 Template object
    """
    from probator.database import db
    from probator.plugins.types.accounts import BaseAccount

    tmpl = db.Template.find_one(template_name=template)
    if not tmpl:
        raise ProbatorError(f'No such template found: {template}')

    tmplenv = Environment(loader=BaseLoader, autoescape=True)
    tmplenv.filters['json_loads'] = json.loads
    tmplenv.filters['slack_quote_join'] = lambda data: ', '.join(f'`{x}`' for x in data)
    tmplenv.filters['account_name_from_id'] = lambda aid: BaseAccount.get(aid).account_name

    return tmplenv.from_string(tmpl.template)


def parse_bucket_info(domain):
    """Parse a domain name to gather the bucket name and region for an S3 bucket. Returns a tuple
    (bucket_name, bucket_region) if a valid domain name, else `None`

    >>> parse_bucket_info('www.domain.tld.s3-website-us-west-2.amazonaws.com')
    ('www.domain.tld', 'us-west-2')

    Args:
        domain (`str`): Domain name to parse

    Returns:
        :obj:`list` of `str`: `str`,`None`
    """
    match = RGX_BUCKET.match(domain)
    if match:
        data = match.groupdict()
        return data['bucket'], data['region'] or 'us-east-1'


def to_utc_date(date):
    """Convert a datetime object from local to UTC format

    >>> from datetime import datetime
    >>> d = datetime(2017, 8, 15, 18, 24, 31)
    >>> to_utc_date(d)
    datetime.datetime(2017, 8, 16, 1, 24, 31)

    Args:
        date (`datetime`): Input datetime object

    Returns:
        `datetime`
    """
    return datetime.utcfromtimestamp(float(date.strftime('%s'))).replace(tzinfo=None) if date else None


def isoformat(date):
    """Convert a datetime object to a ISO 8601 formatted string, with added None type handling

    >>> from datetime import datetime
    >>> d = datetime(2017, 8, 15, 18, 24, 31)
    >>> isoformat(d)
    '2017-08-15T18:24:31'

    Args:
        date (`datetime`): Input datetime object

    Returns:
        `str`
    """
    return date.isoformat() if date else None


def generate_password(length=32):
    """Generate a cryptographically secure random string to use for passwords

    Args:
        length (int): Length of password, defaults to 32 characters

    Returns:
        Randomly generated string
    """
    return ''.join(random.SystemRandom().choice(string.ascii_letters + '!@#$+.,') for _ in range(length))


def generate_csrf_token():
    """Return a randomly generated string for use as CSRF Tokens

    Returns:
        `str`
    """
    return binascii.hexlify(os.urandom(32)).decode()


def hash_password(password):
    """Return an argon2 hashed version of the password provided

        password: Password to hash

    Returns:
        String representing the hashed password
    """
    return PasswordHasher().hash(password)


def generate_jwt_token(user, authsys, **kwargs):
    """Generate a new JWT token, with optional extra information. Any data provided in `**kwargs`
    will be added into the token object for auth specific usage

    Args:
        user (:obj:`User`): User object to generate token for
        authsys (str): The auth system for which the token was generated
        **kwargs (dict): Any optional items to add to the token

    Returns:
        Encoded JWT token
    """
    # Local import to prevent app startup failures
    from probator.config import dbconfig

    token = {
        'auth_system': authsys,
        'exp': time.time() + dbconfig.get('session_expire_time'),
        'user': user.to_json(),
        'roles': [role.name for role in user.roles]
    }

    if kwargs:
        token.update(**kwargs)

    enc = jwt.encode(token, get_jwt_key_data(), algorithm='HS512')
    return enc.decode()


def get_jwt_key_data():
    """Returns the data for the JWT private key used for encrypting the user login token as a string object

    Returns:
        `str`
    """
    global __jwt_data

    if __jwt_data:
        return __jwt_data

    from probator import config_path
    from probator.config import dbconfig

    jwt_key_file = dbconfig.get('jwt_key_file_path', default='ssl/private.key')
    if not os.path.isabs(jwt_key_file):
        jwt_key_file = os.path.join(config_path, jwt_key_file)

    with open(os.path.join(jwt_key_file), 'r') as f:
        __jwt_data = f.read()

    return __jwt_data


def has_access(user, required_roles, match_all=True):
    """Check if the user meets the role requirements. If mode is set to AND, all the provided roles must apply

    Args:
        user (:obj:`User`): User object
        required_roles (`list` of `str`): List of roles that the user must have applied
        match_all (`bool`): If true, all the required_roles must be applied to the user, else any one match will
         return `True`

    Returns:
        `bool`
    """
    # Admins have access to everything
    if ROLE_ADMIN in user.roles:
        return True

    if isinstance(required_roles, str):
        if required_roles in user.roles:
            return True

        return False

    # If we received a list of roles to match against
    if match_all:
        for role in required_roles:
            if role not in user.roles:
                return False

        return True

    else:
        for role in required_roles:
            if role in user.roles:
                return True

        return False


def merge_lists(*args):
    """Merge an arbitrary number of lists into a single list and dedupe it



    Args:
        *args: Two or more lists

    Returns:
        A deduped merged list of all the provided lists as a single list
    """

    out = {}
    for contacts in filter(None, args):
        for contact in contacts:
            out[contact.value] = contact

    return list(out.values())


def to_camelcase(in_str):
    """Converts a string from snake_case to camelCase

    >>> to_camelcase('convert_to_camel_case')
    'convertToCamelCase'

    Args:
        in_str (str): String to convert

    Returns:
        String formatted as camelCase
    """
    return re.sub('_([a-z])', lambda x: x.group(1).upper(), in_str)


def from_camelcase(in_str):
    """Converts a string from camelCase to snake_case

    >>> from_camelcase('convertToPythonicCase')
    'convert_to_pythonic_case'

    Args:
        in_str (str): String to convert

    Returns:
        String formatted as snake_case
    """
    return re.sub('[A-Z]', lambda x: '_' + x.group(0).lower(), in_str)


def get_resource_id(prefix, *data):
    """Returns a unique ID based on the SHA256 hash of the provided data. The input data is flattened and sorted to
    ensure identical hashes are generated regardless of the order of the input. Values must be of types `str`, `int` or
    `float`, any other input type will raise a `ValueError`

    >>> get_resource_id('ec2', 'lots', 'of', 'data')
    'ec2-1d21940125214123'
    >>> get_resource_id('ecs', 'foo', ['more', 'data', 'here', 2, 3])
    'ecs-e536b036ea6fd463'
    >>> get_resource_id('ecs', ['more'], 'data', 'here', [[2], 3], 'foo')
    'ecs-e536b036ea6fd463'

    Args:
        prefix (`str`): Key prefix
        *data (`str`, `int`, `float`, `list`, `tuple`): Data used to generate a unique ID

    Returns:
        `str`
    """
    parts = flatten(data)
    for part in parts:
        if type(part) not in (str, int, float):
            raise ValueError(f'Supported data types: int, float, list, tuple, str. Got: {type(part)}')

    hash = get_hash('-'.join(sorted(map(str, parts))))[-16:]
    return f'{prefix}-{hash}'


def parse_date(date_string, ignoretz=True):
    """Parse a string as a date. If the string fails to parse, `None` will be returned instead

    >>> parse_date('2017-08-15T18:24:31')
    datetime.datetime(2017, 8, 15, 18, 24, 31)

    Args:
        date_string (`str`): Date in string format to parse
        ignoretz (`bool`): If set ``True``, ignore time zones and return a naive :class:`datetime` object.

    Returns:
        `datetime`, `None`
    """
    try:
        return parser.parse(date_string, ignoretz=ignoretz)
    except TypeError:
        return None


def get_user_data_configuration():
    """Retrieve and update the application configuration with information from the user-data

    Returns:
        `None`
    """
    from probator import get_local_aws_session, app_config

    kms_region = app_config.kms_region
    session = get_local_aws_session()

    if session.get_credentials().method == 'iam-role':
        kms = session.client('kms', region_name=kms_region)
    else:
        sts = session.client('sts')
        audit_role = sts.assume_role(RoleArn=app_config.aws_api.instance_role_arn, RoleSessionName='probator')
        kms = boto3.session.Session(
            audit_role['Credentials']['AccessKeyId'],
            audit_role['Credentials']['SecretAccessKey'],
            audit_role['Credentials']['SessionToken'],
        ).client('kms', region_name=kms_region)

    user_data_url = app_config.user_data_url
    res = requests.get(user_data_url)

    if res.status_code == 200:
        data = kms.decrypt(CiphertextBlob=b64decode(res.content))
        kms_config = json.loads(zlib.decompress(data['Plaintext'], wbits=zlib.MAX_WBITS | 32).decode('utf-8'))

        app_config.database_uri = kms_config['db_uri']
    else:
        raise RuntimeError(f'Failed loading user-data, cannot continue: {res.status_code}: {res.content}')


def get_vault_configuration():
    """Retrieve and update the application configuration with information from Vault

    Returns:
        `None`
    """
    from probator import app_config, get_local_aws_session

    try:
        session = get_local_aws_session()
        kms = session.client('kms', region_name=app_config.kms_region)
        role_id = kms.decrypt(CiphertextBlob=b64decode(app_config.vault.role_id)).get('Plaintext').decode('utf-8')
        secret_id = kms.decrypt(CiphertextBlob=b64decode(app_config.vault.secret_id)).get('Plaintext').decode('utf-8')

        client = hvac.Client(url=app_config.vault.address)
        client.auth_approle(role_id=role_id, secret_id=secret_id)

        result = munch.munchify(client.read(path=app_config.vault.path))
        if result:
            data = result.get('data', {}).get('data', {})
            if not data:
                raise ProbatorError('No configuration data returned from Vault')

            for key in ('username', 'password', 'hostname', 'dbname'):
                if key not in data:
                    raise ProbatorError(f'Vault configuration is incomplete, missing {key}')

            app_config.database_uri = f'mysql://{data.username}:{data.password}@{data.hostname}:3306/{data.dbname}'

    except Forbidden:
        log.exception('Failed reading data from Vault, unable to authenticate')


def read_config():
    """Attempts to read the application configuration file and will raise a `FileNotFoundError` if the
    configuration file is not found. Returns the folder where the configuration file was loaded from, and
    a `Munch` (dict-like object) containing the configuration

    Configuration file paths searched, in order:
        * ~/.probator/config.json'
        * ./config.json
        * /usr/local/etc/probator/config.json

    Returns:
        `str`, `dict`
    """
    def __recursive_update(old, new):
        out = deepcopy(old)
        for k, v in new.items():
            if issubclass(type(v), dict):
                if k in old:
                    out[k] = __recursive_update(old[k], v)
                else:
                    out[k] = v
            else:
                out[k] = v

        return out

    for fpath in CONFIG_FILE_PATHS:
        if os.path.exists(fpath):
            data = munch.munchify(json.load(open(fpath, 'r')))

            # Our code expects a munch, so ensure that any regular dicts are converted
            return os.path.dirname(fpath), munch.munchify(__recursive_update(DEFAULT_CONFIG, data))

    raise FileNotFoundError('Configuration file not found')


def flatten(data):
    """Returns a flattened version of a list.

    Courtesy of https://stackoverflow.com/a/12472564

    Args:
        data (`tuple` or `list`): Input data

    Returns:
        `list`
    """
    if not data:
        return data

    if type(data[0]) in (list, tuple):
        return list(flatten(data[0])) + list(flatten(data[1:]))

    return list(data[:1]) + list(flatten(data[1:]))


def send_notification(*, subsystem, recipients, subject, body_html, body_text):
    """Method to send a notification. A plugin may use only part of the information, but all fields are required.

    Args:
        subsystem (`str`): Name of the subsystem originating the notification
        recipients (`list` of :obj:`NotificationContact`): List of recipients
        subject (`str`): Subject / title of the notification
        body_html (`str`): HTML formatted version of the message
        body_text (`str`): Text formatted version of the message

    Returns:
        `None`
    """
    from probator import PROBATOR_PLUGINS

    if not body_html and not body_text:
        raise ValueError('body_html or body_text must be provided')

    # Make sure that we don't have any duplicate recipients
    recipients = list(set(recipients))

    notifiers = map(lambda plugin: plugin.load(), PROBATOR_PLUGINS['probator.plugins.notifiers']['plugins'])

    for cls in filter(lambda x: x.enabled(), notifiers):
        for recipient in recipients:
            if isinstance(recipient, NotificationContact):
                if recipient.type == cls.notifier_type:
                    try:
                        notifier = cls()
                        notifier.notify(subsystem, recipient.value, subject, body_html, body_text)

                    except ProbatorError:
                        log.exception(f'Failed sending notification for {recipient.type}/{recipient.value}')
            else:
                log.warning(f'Unexpected recipient {recipient}')


def diff(a, b, filename='file'):
    """Return the difference between two strings

    Will return a human-readable difference between two strings. See
    https://docs.python.org/3/library/difflib.html#difflib.unified_diff for more information about the output format

    Args:
        a (str): Original string
        b (str): New string
        filename (str): Optional filename argument for diff output. Default: `file`

    Returns:
        `str`
    """
    return ''.join(
        unified_diff(
            a.splitlines(keepends=True),
            b.splitlines(keepends=True),
            fromfile=f'a/{filename}',
            tofile=f'b/{filename}'
        )
    )


def limit_value(*, value, min_value, max_value):
    """Limit a value to be between min_value and max_value

    >>> limit_value(value=17, min_value=0, max_value=100)
    17
    >>> limit_value(value=231, min_value=0, max_value=100)
    100
    >>> limit_value(value=-16, min_value=0, max_value=100)
    0

    Args:
        value (`int` or `float`): The value to limit
        min_value (`int` or `float`): The minimum allowed value
        max_value (`int` or `float`): The maximum allowed value

    Returns:
        `int` or `float`
    """
    if type(value) not in (int, float):
        raise TypeError(type(value))

    if value > max_value:
        return max_value

    if value < min_value:
        return min_value

    return value
