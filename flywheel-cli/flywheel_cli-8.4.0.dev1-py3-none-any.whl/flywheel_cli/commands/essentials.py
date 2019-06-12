import logging
import os
import sys

from urllib.parse import urlparse

import crayons
import flywheel
from .. import sdk_impl, console, util


log = logging.getLogger(__name__)
perror = util.perror


def add_commands(subparsers, parsers):
    # Login
    login_parser = subparsers.add_parser('login', help='Login to a Flywheel instance')
    login_parser.add_argument('api_key', help='Your Flywheel API Key')
    login_parser.set_defaults(func=login)
    login_parser.set_defaults(parser=login_parser)
    parsers['login'] = login_parser

    # Logout
    logout_parser = subparsers.add_parser('logout', help='Delete your saved API key')
    logout_parser.set_defaults(func=logout)
    logout_parser.set_defaults(parser=logout_parser)
    parsers['logout'] = logout_parser

    # Status
    status_parser = subparsers.add_parser('status', help='See your current login status')
    status_parser.set_defaults(func=status)
    status_parser.set_defaults(parser=status_parser)
    parsers['status'] = status_parser

    # Version
    version_parser = subparsers.add_parser('version', help='Print the CLI version and exit')
    version_parser.set_defaults(func=version)
    version_parser.set_defaults(parser=version_parser)
    parsers['version'] = version_parser

    # Copy
    cp_parser = subparsers.add_parser('cp', help='Copy a local file to a remote location, or vice-a-versa')
    cp_parser.add_argument('src', help='The source path, either a local file or a flywheel file (e.g. fw://)')
    cp_parser.add_argument('dst', help='The destination path, either a local file or a flywheel file (e.g. fw://)')
    cp_parser.set_defaults(func=copy_file)
    cp_parser.set_defaults(parser=cp_parser)
    parsers['cp'] = cp_parser

    # List
    ls_parser = subparsers.add_parser('ls', help='Show remote files')
    ls_parser.add_argument('path', nargs='?', default=None, help='The path to list subfolders and files')
    ls_parser.add_argument('--ids', action='store_true', help='Display database identifiers')
    ls_parser.set_defaults(func=ls)
    ls_parser.set_defaults(parser=ls_parser)
    parsers['ls'] = ls_parser


def login(args):
    fw = flywheel.Client(args.api_key)

    try:
        # Get current user
        user = fw.get_current_user()

        # Save credentials
        sdk_impl.save_api_key(args.api_key)

        print('You are now logged in as {} {}!'.format(user.firstname, user.lastname))
    except Exception as e:
        log.debug('Login error', exc_info=True)
        perror('Error logging in: {}'.format(str(e)))
        sys.exit(1)


def logout(args):
    sdk_impl.save_api_key(None)
    print('You are now logged out.')


def status(args):
    fw = sdk_impl.create_flywheel_client(require=False)
    if not fw:
        perror('You are not currently logged in.')
        perror('Try `fw login` to login to Flywheel.')
        sys.exit(1)

    try:
        user = fw.get_current_user()

        # Print out status and site
        host_url = fw.api_client.configuration.host
        hostname = urlparse(host_url).hostname

        print('You are currently logged in as {} {} to {}'.format(
            user.firstname, user.lastname, hostname))
    except Exception as e:
        perror('{}\n'.format(e))
        perror('Could not authenticate - are you sure your API key is up to date?')
        perror('Try `fw login` to login to Flywheel.')
        sys.exit(1)


def version(args):
    version = util.get_cli_version()

    print('flywheel-cli')
    print('  version: {}\n'.format(version))


def copy_file(args):
    src_is_fw = args.src.startswith('fw://')
    dst_is_fw = args.dst.startswith('fw://')
    if src_is_fw == dst_is_fw:
        perror('Must specify exactly one Flywheel location (fw://<path>)!')
        sys.exit(1)

    if src_is_fw:
        # Download, must reference a file
        download_file(args.src, args.dst)
    else:
        # Upload, must reference a valid destination container
        upload_file(args.src, args.dst)


def upload_file(src, dst):
    valid_containers = ('project', 'subject', 'session', 'acquisition')

    # Determine destination
    fw = sdk_impl.create_flywheel_client()

    # Verify src exists
    src_path = os.path.abspath(src)
    if not os.path.isfile(src_path):
        perror('File {} does not exist!'.format(src_path))
        sys.exit(1)

    try:
        dst_path = sdk_impl.parse_resolver_path(dst)
        dst_cont = fw.lookup(dst_path)
    except Exception as e:
        perror('{}\n'.format(e))
        perror('Could not resolve dst_contination container')
        sys.exit(1)

    if dst_cont.container_type not in valid_containers:
        perror('Cannot upload to {}'.format(dst_cont.container_type))
        sys.exit(1)

    print('Uploading to {}... '.format(dst_cont.container_type), end='', flush=True)
    try:
        dst_cont.upload_file(src_path)
        print('Done')
    except Exception as e:
        print('ERROR')
        perror('\n{}'.format(e))


def download_file(src, dst):
    # Determine source
    fw = sdk_impl.create_flywheel_client()

    try:
        src_path = sdk_impl.parse_resolver_path(src)
        result = fw.resolve(src_path)
        src_cont = result.path[-1]
    except Exception as e:
        perror('{}\n'.format(e))
        perror('Could not resolve source container')
        sys.exit(1)

    if src_cont.container_type != 'file':
        perror('Can only copy files, not a {}'.format(src_cont.container_type))
        sys.exit(1)

    dst_path = os.path.abspath(dst)
    dst_dir = os.path.dirname(dst_path)
    if not os.path.exists(dst_dir):
        os.makedirs(dst_dir)

    print('Downloading {}... '.format(src_cont.name), end='', flush=True)
    try:
        parent_cont = result.path[-2]
        parent_cont.download_file(src_cont.name, dst_path)
        print('Done')
    except Exception as e:
        print('ERROR')
        perror('\n{}'.format(e))
        sys.exit(1)


TIME_FORMAT = '%b %d %H:%M'


def ls(args):
    fw = sdk_impl.create_flywheel_client()

    user = fw.get_current_user()

    path = sdk_impl.parse_resolver_path(args.path)
    result = fw.resolve(path)

    if result.path and not result.children:
        result.children = [result.path.pop()]

    if result.path:
        parent = result.path[-1]
    else:
        parent = None

    table = []
    for child in result.children:
        table.append(_get_row_for_container(child, parent, user, args.ids))

    console.print_table(sys.stdout, table)


def _get_row_for_container(cont, parent, user, show_ids):
    if 'permissions' in cont:
        level = _get_level(cont, user.id)
    else:
        level = _get_level(parent, user.id)

    size = ''
    modified = None
    if cont.container_type in ('session', 'acquisition'):
        modified = cont.timestamp
    if cont.container_type == 'file':
        modified = cont.modified
        size = util.hrsize(cont.size).rjust(6)

    if modified:
        modified = modified.strftime(TIME_FORMAT)
    else:
        modified = ''

    if cont.container_type == 'group':
        name = crayons.blue(cont.id, bold=True)
    elif cont.container_type == 'analysis':
        name = crayons.green('analyses/{}'.format(cont.label), bold=True)
    elif cont.container_type == 'file':
        name = 'files/{}'.format(cont.name)
    else:
        name = cont.get('label') or cont.get('code')
        if name:
            name = crayons.blue(name, bold=True)
        else:
            name = crayons.red('UNLABELED')

    if show_ids:
        cid = '' if cont.container_type == 'file' else '<id:{}>'.format(cont.id)
        return (cid, level, size, modified, name)
    else:
        return (level, size, modified, name)

def _get_level(cont, uid):
    if cont is not None:
        for perm in cont.get('permissions', []):
            if perm.id == uid:
                return perm.access
    return 'UNKNOWN'
