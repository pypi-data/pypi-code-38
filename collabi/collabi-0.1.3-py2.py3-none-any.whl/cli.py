"""This module provides the command line interface functionality of collabi.
"""
import os
import sys
import logging
import signal
import requests
import json
import humanize

from os import getenv
from getpass import getpass
from ast import literal_eval
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter, Action

from collabi import __version__ as collabi_version
from collabi.all_help_action import AllHelpAction
from collabi.formatter import Formatter
from collabi.cloud_config import CloudConfig
from collabi.rest import Rest
from collabi.core import Core
from collabi.auth import Auth
from collabi.accelerator import Accelerator
from collabi.collab import Collab

# TODO: add create project: POST /api/orgs/bradandy/projects "{\"name\":\"sst-1213\"}"

class StoreNameValuePair(Action):
    def __call__(self, parser, namespace, values, option_string=None):
        opts = {}
        for v in values:
            k, v = v.split('=')
            try:  # attempt converting simple types
                opts[k] = literal_eval(v)
            except:
                opts[k] = v
        setattr(namespace, self.dest, opts)

class StoreRegion(Action):
    def __call__(self, parser, namespace, value, option_string=None):
        setattr(namespace, self.dest, 'GCP_' + value.replace('-', '_').upper())

def main(main_args=sys.argv[1:], cloud_env=getenv('CLOUD_ENV', 'production')):
    parser = ArgumentParser(formatter_class=ArgumentDefaultsHelpFormatter)

    parser.add_argument('--all-help', action=AllHelpAction,
                        help='show help for all commands')
    parser.add_argument('--version', action='version', version=collabi_version)
    parser.add_argument('--log-level', choices=['debug','info','warning','error','critical'],
                        action=MarkedAction,
                        help='set logging level (saved for future calls)', default='warn')
    parser.add_argument('--log-file', metavar='FILENAME', action=MarkedAction,
                        help='write logs to FILENAME (saved for future calls)', default='STDOUT')
    parser.add_argument('-e', '--env', choices=['local','dev','staging','production'],
                        help='hosting environment for the Collab service',
                        default=cloud_env)
    parser.add_argument('-u', '--user-auth', metavar='EMAIL[:PASSWORD]',
                        help='credentials to use for authenticating with the service (if a password'
                             ' is not provided, it will be queried for on the terminal)')
    parser.add_argument('-f', '--format', choices=Formatter.choices,
                        help='format to use when printing data', default='simple')
    parser.add_argument('-o', '--output', metavar='FILENAME',
                        help='print data into OUTPUT', default='STDOUT')
    parser.add_argument('--insecure', action='store_true',
                        help='disable SSL/TLS certificate verification')
    parser.add_argument('--access-token',
                        help='access token to use for authenticating with the service')
    parser.add_argument('--accelerator', default='discover',
                        help='provide an accelerator health check URL; '\
                        'empty string indicates no accelerator should be used')
    parser.add_argument('--region', action=StoreRegion,
                        choices=['us-central-1', 'europe-west-1', 'asia-east-1'],
                        help='direct requests to a specific regional collab service')

    resource_sub = parser.add_subparsers(dest='resource')

    user_parser = resource_sub.add_parser(
        'user', help='work with a user',
        formatter_class=ArgumentDefaultsHelpFormatter
    )

    attr_sub = user_parser.add_subparsers(dest='attribute')

    me_parser = attr_sub.add_parser(
        'me', help='list user details for the current credentials',
        formatter_class=ArgumentDefaultsHelpFormatter
    )

    orgs_parser = attr_sub.add_parser(
        'orgs', help='list orgs accessible by the credentials',
        formatter_class=ArgumentDefaultsHelpFormatter
    )

    projects_parser = attr_sub.add_parser(
        'projects', help='list projects accessible by the credentials',
        formatter_class=ArgumentDefaultsHelpFormatter
    )

    projects_parser.add_argument('-o', '--org-foreign-key', default='ANY',
                                 help='list projects accessible by the ORG_FOREIGN_KEY')

    project_parser = resource_sub.add_parser(
        'project', help='work with a project',
        formatter_class=ArgumentDefaultsHelpFormatter
    )

    project_parser.add_argument('project_id',
                                help='identifier for the project hosted in the Collab service or '
                                     'path to project root')
    project_parser.add_argument('-b', '--branch-id', help=' the branch to use', default='master')
    project_parser.add_argument('-r', '--revision-id',
                                help='revision to work against',
                                default='HEAD')

    project_commands_sub = project_parser.add_subparsers(title='commands', dest='command')

    info_parser = project_commands_sub.add_parser(
        'info', help='information about project',
        formatter_class=ArgumentDefaultsHelpFormatter
    )

    ls_parser = project_commands_sub.add_parser(
        'list', help='list files',
        formatter_class=ArgumentDefaultsHelpFormatter
    )
    ls_parser.add_argument('-r', '--recursive', action='store_true',
                           help='recurse into subdirectories')
    ls_parser.add_argument('-H', '--human', action='store_true',
                           help='show size information using 1024-based computation (aka "binary")')
    ls_parser.add_argument('-s', '--summarize', action='store_true',
                           help='show final summary of all files listed')
    ls_parser.add_argument('paths', nargs='*',
                           help='one or more paths to list contents', default=['/'])

    branch_parser = project_commands_sub.add_parser(
        'branch', help='interact with branches in project',
        formatter_class=ArgumentDefaultsHelpFormatter
    )
    branch_commands_sub = branch_parser.add_subparsers(title='commands', dest='branch_command')
    branch_commands_sub.add_parser(
        'list', help='list branches',
        formatter_class=ArgumentDefaultsHelpFormatter
    )
    branch_create_parser = branch_commands_sub.add_parser(
        'create', help='create a new branch',
        formatter_class=ArgumentDefaultsHelpFormatter
    )
    branch_create_parser.add_argument('key_value', nargs='*', action=StoreNameValuePair)
    branch_update_parser = branch_commands_sub.add_parser(
        'update', help='update a branch',
        formatter_class=ArgumentDefaultsHelpFormatter
    )
    branch_update_parser.add_argument('key_value', nargs='*', action=StoreNameValuePair)

    history_parser = project_commands_sub.add_parser(
        'history', help='list change history',
        formatter_class=ArgumentDefaultsHelpFormatter
    )
    history_parser.add_argument('-l', '--limit', type=int, metavar='COUNT',
                                help='list only COUNT number of changes in history')
    history_parser.add_argument('paths', nargs='*',
                                help='one or more files to list changes '
                                     '(nothing shown for directories other than the root)',
                                default=['/'])

    dl_parser = project_commands_sub.add_parser(
        'download', help='download files',
        formatter_class=ArgumentDefaultsHelpFormatter
    )
    dl_parser.add_argument('-r', '--recursive', action='store_true',
                           help='recurse into subdirectories')
    dl_parser.add_argument('-c', '--concurrency', type=int, default=4,
                           help='number of files to download simultaneously')
    dl_parser.add_argument('--overwrite', action='store_true',
                           help='overwrite files instead of sending to trash')
    dl_parser.add_argument('paths', nargs='+',
                           help='list of paths')
    dl_parser.add_argument('destination_path',
                           help='local path for storing downloaded files (will OVERWRITE); you may also use "/dev/null" to discard all downloaded data')

    ul_parser = project_commands_sub.add_parser(
        'upload', help='upload files',
        formatter_class=ArgumentDefaultsHelpFormatter
    )
    ul_parser.add_argument('-r', '--recursive', action='store_true',
                           help='recurse into subdirectories')
    ul_parser.add_argument('-s', '--strip-components', type=int, metavar='COUNT',
                           help='strip the count of parents from each absolute path to be uploaded',
                           default=0)
    ul_parser.add_argument('-c', '--concurrency', type=int, default=4,
                           help='number of files to upload simultaneously')
    ul_parser.add_argument('paths', nargs='+',
                           help='list of local paths to upload')
    ul_parser.add_argument('message', help='commit message')

    ulsync_parser = project_commands_sub.add_parser(
        'upload_sync', help='synchronize files on the local system to the cloud (upload MINE)',
        formatter_class=ArgumentDefaultsHelpFormatter
    )
    ulsync_parser.add_argument('-s', '--strip-components', type=int, metavar='COUNT',
                               help='strip the count of parents from '
                                    'the local path before querying the cloud',
                               default=0)
    ulsync_parser.add_argument('-c', '--concurrency', type=int, default=4,
                               help='number of files to upload simultaneously')
    ulsync_parser.add_argument('local_path', help='local path to use as basis for changes')
    ulsync_parser.add_argument('message', help='commit message')

    dlsync_parser = project_commands_sub.add_parser(
        'download_sync', help='synchronize files in the cloud to the local system '
                              '(download THEIRS)',
        formatter_class=ArgumentDefaultsHelpFormatter
    )
    dlsync_parser.add_argument('-s', '--strip-components', type=int, metavar='COUNT',
                               help='strip the count of parents from '
                                    'the local path before querying the cloud',
                               default=0)
    dlsync_parser.add_argument('-c', '--concurrency', type=int, default=4,
                               help='number of files to download simultaneously')
    dlsync_parser.add_argument('--overwrite', action='store_true',
                               help='overwrite files instead of sending to trash')
    dlsync_parser.add_argument('local_path', help='local path to use as basis for changes')

    args = parser.parse_args(main_args)

    ######################################################################

    config = CloudConfig(args.env)

    if not hasattr(args, 'log_level_marked') and config.log_level:
        args.log_level = config.log_level
    if not hasattr(args, 'log_file_marked') and config.log_file:
        args.log_file = config.log_file

    log_kwargs = {
        'level': getattr(logging, args.log_level.upper())
    }
    if args.log_file != 'STDOUT':
        log_kwargs['filename'] = args.log_file
    logging.basicConfig(**log_kwargs)
    logger = logging.getLogger('unity.'+parser.prog)

    if args.output == 'STDOUT':
        output = sys.stdout
    else:
        output = open(args.output, 'w')
    formatter = Formatter(args.format, output)

    def signal_handler(signal, frame):
        sys.stderr.write('Interrupted--exiting\n')
        sys.exit(signal)
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    if not config.core:
        config.update()

    def save_auth_callback(access_token, refresh_token, expiry):
        config.access_token = access_token
        config.refresh_token = refresh_token
        config.expiry = expiry
        config.save()

    if args.env == 'local':
        args.insecure = True

    if args.insecure and args.log_level != 'debug':
        # suppress the verification warnings since it's expected to be insecure
        requests.packages.urllib3.disable_warnings(
            requests.packages.urllib3.exceptions.InsecureRequestWarning)

    user_agent = parser.prog + '/' + collabi_version

    # cache the log settings in the environment config to preserve for later calls
    config_changes = {}
    if hasattr(args, 'log_level_marked') and config.log_level != args.log_level:
        config_changes['log_level'] = args.log_level
    if hasattr(args, 'log_file_marked') and config.log_file != args.log_file:
        config_changes['log_file'] = args.log_file
    if len(config_changes) > 0:
        config.save(**config_changes)

    try:
        session = requests.Session()
        if hasattr(args, 'region') and args.region:
            session.headers.update({'X-Collab-Region': args.region})
        if hasattr(args, 'concurrency') and args.concurrency > 10:
            # the default pools are limited to 10
            adapter = requests.adapters.HTTPAdapter(pool_connections=args.concurrency,
                                                    pool_maxsize=args.concurrency)
            session.mount('https://', adapter)

        core_rest = Rest(session, config.core,
                         verify=(not args.insecure), user_agent=user_agent)
        core = Core(core_rest,
                    access_token=(args.access_token or config.access_token),
                    refresh_token=config.refresh_token,
                    expiry=config.expiry,
                    save_auth_callback=save_auth_callback)
        if args.user_auth:
            creds = args.user_auth.split(':', 2)
            if len(creds) == 1:
                creds.append(getpass('PASSWORD: '))
            core.login(creds[0], creds[1])

        if not core.get_authorization_header():
            sys.stderr.write('Authentication required. EMAIL: ')
            email = sys.stdin.readline().strip()
            passwd = getpass('PASSWORD: ')
            core.login(email, passwd)

        auth = Auth(core)

        ########################################
        # User resource

        if args.resource == 'user':
            if args.attribute == 'me':
                formatter.display(core.current_user(auth).as_json)
            elif args.attribute == 'orgs':
                formatter.display(core.current_user(auth).orgs())
            elif args.attribute == 'projects':
                org_fk = None if args.org_foreign_key == 'ANY' else args.org_foreign_key
                formatter.display(core.current_user(auth).projects(org_fk))
            else:
                raise NotImplementedError('Unknown attribute: '+args.attribute)
            return 0

        ########################################
        # Project resource

        settings = os.path.join(args.project_id, 'ProjectSettings', 'ProjectSettings.asset')
        if os.path.isfile(settings):
            args.project_id = _get_project_id_from(settings)

        project = core.current_user(auth).project(args.project_id)

        accelerator_rest = Rest(session, config['collab-accelerator'], auth=auth,
                                verify=(not args.insecure), user_agent=user_agent)
        accelerator = Accelerator(config, accelerator_rest, project)
        accelerator.discover(args.accelerator)

        collab_rest = Rest(session, accelerator.url, auth=accelerator.get_auth(auth),
                           verify=(not args.insecure), user_agent=user_agent)
        collab = Collab(config, collab_rest, args.project_id, args.branch_id, args.revision_id)

        def Mbps(bytes, seconds):
            # megabits = (bytes * 8) / (1000 * 1000)
            if (seconds == 0.0): return 0
            return (bytes * 0.000008) / seconds

        def transfer_report(bytes, seconds, name):
            details = '(%d/%.2f)' % (bytes, seconds)
            return '%10.2f Mbps %-15s %s' % (Mbps(bytes, seconds), details, name)

        def print_report_for(files):
            total_transfer_bytes = 0
            total_transfer_seconds = 0
            for fl in files:
                total_transfer_bytes += fl.transfer_bytes
                total_transfer_seconds += fl.transfer_seconds
                print transfer_report(fl.transfer_bytes, fl.transfer_seconds, fl.path)
            if len(files) > 1:
                print '-'*80
                print transfer_report(total_transfer_bytes, total_transfer_seconds,
                                      '%d files'%len(files))

        if args.command == 'info':
            formatter.display(core.current_user(auth).project(args.project_id))

        elif args.command == 'list':
            entries = collab.list(args.paths, recursive=args.recursive)
            total_files = 0
            total_bytes = 0
            for entry in entries:
                if isinstance(entry, Collab.DirectoryEntry):
                    print '%10s  %32s  %s/' % ('-', '-', entry.name)
                else:
                    total_files += 1
                    total_bytes += entry.size
                    if args.human:
                        print '%10s  %32s  %s' % (humanize.naturalsize(entry.size, binary=True),
                                                  entry.hash, entry.name)
                    else:
                        print '%10d  %32s  %s' % (entry.size, entry.hash, entry.name)
            if args.summarize:
                print
                print 'Total files: %d' % (total_files)
                print ' Total size: %s' % (
                    humanize.naturalsize(total_bytes, binary=True) if args.human else str(bytes))

        elif args.command == 'branch':
            if args.branch_command == 'list':
                branches = collab.branches()
                formatter.display(branches)
            elif args.branch_command == 'create':
                branch = collab.create_branch(args.key_value)
                formatter.display(branch)
            elif args.branch_command == 'update':
                branch = collab.update_branch(args.key_value)
                formatter.display(branch)
            else:
                raise NotImplementedError('Unknown branch command: '+args.branch_command)

        elif args.command == 'history':
            history = collab.history(args.paths, limit=args.limit)
            for path, revs in history.iteritems():
                print '*** Change history: '+path
                formatter.display(revs)

        elif args.command == 'download':
            download = collab.download(args.paths, args.destination_path,
                                       recursive=args.recursive, overwrite=args.overwrite,
                                       concurrency=args.concurrency)
            print_report_for(download.filemap.values())

        elif args.command == 'upload':
            upload = collab.upload(args.paths, upload_transaction_id=config.upload_transaction_id,
                                   recursive=args.recursive, concurrency=args.concurrency)
            print_report_for(upload.filemap.values())
            commit = collab.commit(args.message, upload, strip_components=args.strip_components)
            formatter.display(commit)

        elif args.command == 'upload_sync':
            commit = collab.upload_sync(args.local_path, args.message,
                                        strip_components=args.strip_components,
                                        concurrency=args.concurrency)
            if commit: formatter.display(commit)

        elif args.command == 'download_sync':
            download = collab.download_sync(args.local_path, strip_components=args.strip_components,
                                            overwrite=args.overwrite)
            if download: print_report_for(download.filemap.values())

        else:
            raise NotImplementedError('Unknown command: '+args.command)

    except requests.exceptions.HTTPError as exc:
        resp = exc.response
        sc = resp.status_code
        if sc == 401:
            logger.error('Authentication failed. Try establishing credentials (see --user option).')
        else:
            if args.log_level == 'debug':
                logger.exception('HTTPError') # shows traceback
            else:
                logger.error(exc)
            if len(resp.content) > 0 and 'application/json' in resp.headers['content-type']:
                js = resp.json()
                if js:
                    logger.error(json.dumps(js, indent=2))
        sc = str(sc)
        rc = int(sc[0]+sc[2])
        return rc # reduce status code to <255 for return code (ignore middle digit)
    return 0

def _get_project_id_from(pathname):
    with open(pathname, 'r') as stream:
        for line in stream:
            item = line.split(':', 1)
            if len(item) != 2: continue
            if item[0].strip() == 'cloudProjectId':
                return item[1].strip()
    raise LookupError('Unable to find cloudProjectId in '+pathname)

class MarkedAction(Action):
    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest+'_marked', True)
        setattr(namespace, self.dest, values)
