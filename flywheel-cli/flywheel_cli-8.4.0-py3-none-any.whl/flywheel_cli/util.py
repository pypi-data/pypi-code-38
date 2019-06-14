import argparse
import datetime
import dateutil.parser
import logging
import re
import os
import string
import subprocess
import sys

import fs
import tzlocal

log = logging.getLogger(__name__)

METADATA_ALIASES = {
    'group': 'group._id',
    'project': 'project.label',
    'session': 'session.label',
    'subject': 'subject.label',
    'acquisition': 'acquisition.label'
}

METADATA_TYPES = {
    'group': 'string-id',
    'group._id': 'string-id'
}

METADATA_EXPR = {
    'string-id': r'[0-9a-z][0-9a-z.@_-]{0,30}[0-9a-z]',
    'default': r'.+'
}


NO_FILE_CONTAINERS = [ 'group', 'subject' ]

try:
    DEFAULT_TZ = tzlocal.get_localzone()
except:
    import pytz
    print('Could not determine timezone, defaulting to UTC')
    DEFAULT_TZ = pytz.utc

def set_nested_attr(obj, key, value):
    """Set a nested attribute in dictionary, creating sub dictionaries as necessary.

    Arguments:
        obj (dict): The top-level dictionary
        key (str): The dot-separated key
        value: The value to set
    """
    parts = key.split('.')
    for part in parts[:-1]:
        obj.setdefault(part, {})
        obj = obj[part]
    obj[parts[-1]] = value

def sorted_container_nodes(containers):
    """Returns a sorted iterable of containers sorted by label or id (whatever is available)

    Arguments:
        containers (iterable): The the list of containers to sort

    Returns:
        iterable: The sorted set of containers
    """
    return sorted(containers, key=lambda x: (x.label or x.id or '').lower(), reverse=True)

class UnsupportedFilesystemError(Exception):
    """Error for unsupported filesystem type"""
    pass

def to_fs_url(path, support_archive=True):
    """Convert path to an fs url (such as osfs://~/data)

    Arguments:
        path (str): The path to convert
        support_archive (bool): Whether or not to support archives

    Returns:
        str: A filesystem url
    """
    if path.find(':') > 1:
        # Likely a filesystem URL
        return path

    # Check if the path actually exists
    if not os.path.exists(path):
        raise UnsupportedFilesystemError('File {} does not exist!'.format(path))

    if not os.path.isdir(path):
        if support_archive:
            # Specialized path options for tar/zip files
            if is_tar_file(path):
                return 'tar://{}'.format(path)

            if is_zip_file(path):
                return 'zip://{}'.format(path)

        log.debug('Unknown filesystem type for {}: stat={}'.format(path, os.stat(path)))
        raise UnsupportedFilesystemError('Unknown or unsupported filesystem for: {}'.format(path))

    # Default is OSFS pointing at directory
    return 'osfs://{}'.format(path)

def open_fs(path):
    """Wrapper for fs.open_fs"""
    return fs.open_fs(path)

def is_tar_file(path):
    """Check if path appears to be a tar archive"""
    return bool(re.match('^.*(\.tar|\.tgz|\.tar\.gz|\.tar\.bz2)$', path, re.I))

def is_zip_file(path):
    """Check if path appears to be a zip archive"""
    _, ext = fs.path.splitext(path.lower())
    return (ext == '.zip')

def is_archive(path):
    """Check if path appears to be a zip or tar archive"""
    return is_zip_file(path) or is_tar_file(path)

def confirmation_prompt(message):
    """Continue prompting at the terminal for a yes/no repsonse

    Arguments:
        message (str): The prompt message

    Returns:
        bool: True if the user responded yes, otherwise False
    """
    responses = { 'yes': True, 'y': True, 'no': False, 'n': False }
    while True:
        print('{} (yes/no): '.format(message), end='')
        choice = input().lower()
        if choice in responses:
            return responses[choice]
        print('Please respond with "yes" or "no".')

def perror(*args, **kwargs):
    """Print to stderr"""
    kwargs['file'] = sys.stderr
    kwargs['flush'] = True
    print(*args, **kwargs)

def contains_dicoms(walker):
    """Check if the given walker contains dicoms"""
    # If we encounter a single dicom, assume true
    for root, _, files in walker.walk():
        for file_info in files:
            if is_dicom_file(file_info.name):
                return True
    return False


DICOM_EXTENSIONS = ('.dcm', '.dcm.gz', '.dicom', '.dicom.gz')


def is_dicom_file(path):
    """Check if the given path appears to be a dicom file.

    Only looks at the extension, not the contents.

    Args:
        path (str): The path to the dicom file

    Returns:
        bool: True if the file appears to be a dicom file
    """
    path = path.lower()
    for ext in DICOM_EXTENSIONS:
        if path.endswith(ext):
            return True
    return False


def localize_timestamp(timestamp, timezone=None):
    # pylint: disable=missing-docstring
    timezone = DEFAULT_TZ if timezone is None else timezone
    return timezone.localize(timestamp)

def split_key_value_argument(val):
    """Split value into a key, value tuple.

    Raises ArgumentTypeError if val is not in key=value form

    Arguments:
        val (str): The key value pair

    Returns:
        tuple: The split key-value pair
    """
    key, delim, value = val.partition('=')

    if not delim:
        raise argparse.ArgumentTypeError('Expected key value pair in the form of: key=value')

    return (key.strip(), value.strip())

def parse_datetime_argument(val):
    """Convert an argument into a datetime value using dateutil.parser.

    Raises ArgumentTypeError if the value is inscrutable

    Arguments:
        val (str): The date-time value string

    Returns:
        datetime: The parsed datetime instance
    """
    try:
        return dateutil.parser.parse(val)
    except ValueError as e:
        raise argparse.ArgumentTypeError(' '.join(e.args))

def args_to_list(items):
    """Convert an argument into a list of arguments (by splitting each element on comma)"""
    result = []
    if items is not None:
        for item in items:
            if item:
                for val in item.split(','):
                    val = val.strip()
                    if val:
                        result.append(val)
    return result

def files_equal(walker, path1, path2):
    chunk_size = 8192

    with walker.open(path1, 'rb') as f1, walker.open(path2, 'rb') as f2:
        while True:
            chunk1 = f1.read(chunk_size)
            chunk2 = f2.read(chunk_size)

            if chunk1 != chunk2:
                return False

            if not chunk1:
                return True


def regex_for_property(name):
    """Get the regular expression match template for property name

    Arguments:
        name (str): The property name

    Returns:
        str: The regular expression for that property name
    """
    property_type = METADATA_TYPES.get(name, 'default')
    if property_type in METADATA_EXPR:
        return METADATA_EXPR[property_type]
    return METADATA_EXPR['default']

def str_to_python_id(val):
    """Convert a string to a valid python id in a reversible way

    Arguments:
        val (str): The value to convert

    Returns:
        str: The valid python id
    """
    result = ''
    for c in val:
        if c in string.ascii_letters or c == '_':
            result = result + c
        else:
            result = result + '__{0:02x}__'.format(ord(c))
    return result

def python_id_to_str(val):
    """Convert a python id string to a normal string

    Arguments:
        val (str): The value to convert

    Returns:
        str: The converted value
    """
    return re.sub('__([a-f0-9]{2})__', _repl_hex, val)

def str_to_filename(val):
    """Convert a string to a valid filename string

    Arguments:
        val (str): The value to convert
    Returns:
        str: The converted value
    """
    keepcharacters = (' ', '.', '_', '-')
    result = ''.join([c if (c.isalnum() or c in keepcharacters) else '_' for c in val])
    return re.sub('_{2,}', '_', result).strip('_ ')

def _repl_hex(m):
    return chr(int(m.group(1), 16))

def sanitize_string_to_filename(value):
    """
    Best-effort attempt to remove blatantly poor characters from a string before turning into a filename.

    Happily stolen from the internet, then modified.
    http://stackoverflow.com/a/7406369
    """
    keepcharacters = (' ', '.', '_', '-')
    return "".join([c for c in value if c.isalnum() or c in keepcharacters]).rstrip()

def hrsize(size):
    """Return human-readable size from size value"""
    if size < 1000:
        return '%d%s' % (size, 'B')
    for suffix in 'KMGTPEZY':
        size /= 1024.
        if size < 10.:
            return '%.1f%sB' % (size, suffix)
        if size < 1000.:
            return '%.0f%sB' % (size, suffix)
    return '%.0f%sB' % (size, 'Y')

def edit_file(path):
    """
    Open the given path in a file editor, wait for the editor to exit.

    Arguments:
        path (str): The path to the file to edit
    """
    if sys.platform == 'darwin':
        default_editor = 'pico'
    elif sys.platform == 'windows':
        default_editor = 'notepad'
    else:
        default_editor = 'nano'

    editor = os.environ.get('EDITOR', default_editor)
    subprocess.call([editor, path])

def package_root():
    """Get a path to the package root folder"""
    pkg_dir = os.path.dirname(__file__)
    return os.path.abspath(pkg_dir)

def get_cli_version():
    """Get the installed CLI version"""
    version_path = os.path.join(package_root(), 'VERSION')
    try:
        with open(version_path, 'r') as f:
            version = f.read().strip()
    except:
        version = 'undetermined'
    return version
