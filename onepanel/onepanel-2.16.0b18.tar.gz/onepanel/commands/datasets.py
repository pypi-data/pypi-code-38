""" Command line interface for the OnePanel Machine Learning platform

'Datasets' commands group.
"""
import os
import subprocess
import sys
import re
import threading
import time
import shutil
import logging
import platform

import click
import configobj
import humanize
from watchdog.observers import Observer

from onepanel.commands.base import APIViewController
from onepanel.commands.login import login_required
from onepanel.utilities.aws_utility import AWSUtility
from onepanel.utilities.cloud_storage_utility import CloudStorageUtility
from onepanel.utilities.creds_utility import CredsUtility
from onepanel.utilities.dataset_strings import sanitize_dataset_uid
from onepanel.utilities.s3_authenticator import S3Authenticator
from onepanel.utilities.dataset_downloader import DatasetDownloadListener
from onepanel.utilities.dataset_api import DatasetAPI
from onepanel.utilities.gcp_utility import GCPUtility
from onepanel.utilities.gcs_authenticator import GCSAuthenticator

from onepanel.utilities.s3.file_sync import FileSynchronizer, ThreadedFileSynchronizer, FileDifference, FileEvent
from onepanel.utilities.gcp_cs.file_sync import FileSynchronizer as FileSynchronizerGCP, \
    ThreadedFileSynchronizer as ThreadedFileSynchronizerGCP, FileDifference as FileDifferenceGCP,\
    FileEvent as FileEventGCP
from onepanel.utilities.s3.file_watch_sync import FileWatchSynchronizerEventHandler
from onepanel.utilities.gcp_cs.file_watch_sync import FileWatchSynchronizerEventHandler \
    as FileWatchSynchronizerEventHandlerGCP
from onepanel.utilities.s3.authentication import APIProvider as APIProviderAWS
from onepanel.utilities.gcp_cs.authentication import APIProvider as APIProviderGCP
from onepanel.utilities.process import run_in_background

import onepanel.utilities.s3.wrapper as S3
import onepanel.utilities.gcp_cs.wrapper as GCP_CS
import onepanel.services as services


class UploadUpdateThread(threading.Thread):
    def __init__(self, threadID, threadName, vc, provider_util, storage_push_to_dir):
        threading.Thread.__init__(self)
        self.exitFlag = False
        self.threadID = threadID
        self.threadName = threadName
        self.sleepTime = 5  # seconds
        self.vc = vc
        self.providerUtil = provider_util
        self.storagePushToDir = storage_push_to_dir

    def run(self):
        response_data = {}
        while True:
            cloud_provider = os.getenv('CLOUD_PROVIDER', 'AWS')
            if cloud_provider == "GCP":
                file_info_cloud_provider = self.providerUtil.get_cs_path_details(self.storagePushToDir)
            elif cloud_provider == "AWS":
                file_info_cloud_provider = self.providerUtil.get_s3_path_details(self.storagePushToDir)
            update_upload_url = '/update_upload'
            upload_data = {
                'bytesCurrent': int(file_info_cloud_provider['data']['total_bytes']),
                'filesCurrent': int(file_info_cloud_provider['data']['total_files']),
            }
            response_data['status_code'] = 500
            try:
                response_data = self.vc.post(upload_data, params=update_upload_url)
            except ValueError:
                click.echo("Error with POST, No JSON Object could be decoded.")

            if response_data['status_code'] != 200:
                click.echo(response_data['data'])
                return
            time.sleep(self.sleepTime)
            if self.exitFlag:
                exit(0)


class DatasetViewController(APIViewController):
    """ DatasetViewController data model
    """

    DATASET_FILE = os.path.join('.onepanel', 'dataset')
    EXCLUSIONS = [os.path.join('.onepanel', 'dataset')]

    account_uid = None
    dataset_uid = None

    def __init__(self, conn):
        APIViewController.__init__(self, conn)
        self.endpoint = '{}'.format(
            self.conn.URL,
        )

    def init_credentials_retrieval(self):
        # Figure out the account uid and dataset uid
        home = os.getcwd()
        onepanel_dir = os.path.join(home, '.onepanel')
        if not os.path.exists(onepanel_dir):
            print("ERROR.Directory does not exist, cannot carry out all datasets operations.")
            print("DETAILS." + onepanel_dir)
            exit(-1)
        dataset_file = os.path.join(home, DatasetViewController.DATASET_FILE)
        if not os.path.isfile(dataset_file):
            print("ERROR.Dataset file does not exist, cannot carry out all datasets operations.")
            print("DETAILS." + dataset_file)
            exit(-1)

        cfg = configobj.ConfigObj(dataset_file)

        dataset_uid = cfg['uid']
        dataset_account_uid = cfg['account_uid']

        if len(dataset_uid) < 1 or len(dataset_account_uid) < 1:
            print("ERROR.Dataset file has invalid credentials. Verify credentials or re-pull project.")
            exit(-1)
        self.account_uid = dataset_account_uid
        self.dataset_uid = dataset_uid

    def save(self, home):
        if not os.path.exists(home):
            os.makedirs(home)
        onepanel_dir = os.path.join(home, '.onepanel')
        if not os.path.exists(onepanel_dir):
            os.makedirs(onepanel_dir)
        dataset_file = os.path.join(home, DatasetViewController.DATASET_FILE)

        cfg = configobj.ConfigObj(dataset_file)
        cfg['uid'] = self.dataset_uid
        cfg['account_uid'] = self.account_uid
        cfg.write()

    def init_endpoint(self):
        self.endpoint = '{root}/accounts/{account_uid}/datasets/{dataset_uid}'.format(
            root=self.conn.URL,
            account_uid=self.account_uid,
            dataset_uid=self.dataset_uid
        )

    def mark_version_dirty(self, version, account_uid=None, dataset_uid=None):
        if account_uid is None:
            account_uid = self.account_uid

        if dataset_uid is None:
            dataset_uid = self.dataset_uid

        endpoint = '{root}/accounts/{account_uid}/datasets/{dataset_uid}/version/{version_uid}/mark_dirty'.format(
            root=self.conn.URL,
            account_uid=account_uid,
            dataset_uid=dataset_uid,
            version_uid=version
        )

        return self.put(endpoint=endpoint)

    @classmethod
    def from_json(cls, data):
        cls.account_uid = data['account']['uid']
        cls.dataset_uid = data['uid']

    @classmethod
    def is_uid_valid(cls, uid):
        pattern = re.compile('^[a-z0-9][-a-z0-9]{1,23}[a-z0-9]$')
        if pattern.match(uid):
            return True
        else:
            return False

    @classmethod
    def exists_local(cls, home):
        dataset_file = os.path.join(home, DatasetViewController.DATASET_FILE)
        if os.path.isfile(dataset_file):
            return True
        else:
            return False

    @classmethod
    def exists_remote(cls, dataset_uid, data):
        exists = False
        if data['uid'] == dataset_uid:
            exists = True
        return exists


def check_dataset_exists_remotely(ctx, account_uid, dataset_uid):
    vc = ctx.obj['vc']

    # Check if the dataset already exists remotely
    url_dataset_check = '/accounts/{}/datasets/{}'.format(account_uid, dataset_uid)
    response_data = vc.get(params=url_dataset_check)
    remote_dataset = response_data['data']
    if remote_dataset is not None and vc.exists_remote(dataset_uid, remote_dataset):
        click.echo("Dataset already exists. Please download the dataset if you want to use it.")
        return True
    return False


def init_dataset(ctx, account_uid, dataset_uid, target_dir):
    if not account_uid:
        account_uid = ctx.obj['connection'].account_uid

    if not check_dataset_exists_remotely(ctx, account_uid, dataset_uid):
        create_dataset(ctx, account_uid, dataset_uid, target_dir)
        click.echo('Dataset is initialized in current directory.')


def create_dataset(ctx, account_uid, dataset_uid, target_dir):
    """ Dataset creation method for 'datasets_create' commands
    """
    vc = ctx.obj['vc']

    if not account_uid:
        account_uid = ctx.obj['connection'].account_uid

    can_create = True
    if vc.exists_local(target_dir):
        can_create = click.confirm(
            'Dataset exists locally but does not exist in {}, create the dataset and remap local folder?'
                .format(account_uid))

    if can_create:
        data = {
            'uid': dataset_uid
        }
        url_dataset_create = '/accounts/{}/datasets'.format(account_uid)
        response = vc.post(data, params=url_dataset_create)
        if response['status_code'] == 200:
            vc.from_json(response['data'])
            vc.save(target_dir)
        else:
            click.echo("Encountered error.")
            click.echo(response['status_code'])
            click.echo(response['data'])
            return None
    return target_dir


@click.group(help='Dataset commands')
@click.pass_context
def datasets(ctx):
    ctx.obj['vc'] = DatasetViewController(ctx.obj['connection'])


@datasets.command('mount-downloader',
                  help='Starts a process in the background that watches for dataset mounts \
                and downloads them as they are created. Resource type is job|instance', hidden=True)
@click.option('-a', '--account_uid', type=str, help='The account uid that the resource is in')
@click.option('-p', '--project_uid', type=str, help='The project uid that the resource is in')
@click.option('-r', '--resource_type', type=str, help='The resource type, e.g. instance|job')
@click.option('-u', '--resource_uid', type=str, help='The resource uid, e.g. instance image-tester')
@click.option('-d', '--download_path', type=str, help='The path where dataset downloads will go to')
@click.option('-r', '--continue_listening', type=bool, help='If true, thread will continue listening for \
                    new dataset mounts. If false, it will stop as soon as there are no more to download.')
@click.option('-v', '--verbose', type=bool, help='If command should log what it is doing')
@click.pass_context
@login_required
def start_dataset_mount_downloader(ctx, account_uid, project_uid, resource_type, resource_uid, download_path, continue_listening, verbose):
    downloader = DatasetDownloadListener(ctx.obj['connection'], download_path, account_uid, project_uid, resource_type, resource_uid, continue_listening, verbose)
    downloader.start()
    downloader.join()


@datasets.command('delete-mount',
                  help='Deletes a dataset mount via API and local files', hidden=True)
@click.option('-a', '--account_uid', type=str, help='The account uid that the resource is in')
@click.option('-p', '--project_uid', type=str, help='The project uid that the resource is in')
@click.option('-d', '--dataset_mount_uuid', type=str, help='The dataset mount uuid')
@click.option('-d', '--download_path', type=str, help='The path where dataset downloads will go to')
@click.option('-v', '--verbose', type=bool, help='If command should log what it is doing')
@click.pass_context
@login_required
def remove_mount(ctx, account_uid, project_uid, dataset_mount_uuid, download_path, verbose):
    if download_path is None:
        download_path = '/onepanel/input/datasets'

    api = DatasetAPI(ctx.obj['connection'])

    logger = logging.getLogger('delete-mount')

    if verbose:
        logger.setLevel(logging.DEBUG)
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        ch.setFormatter(formatter)
        logger.addHandler(ch)

    try:
        response = api.get_dataset_mount(
            account_uid=account_uid,
            project_uid=project_uid,
            dataset_mount_uuid=dataset_mount_uuid)
    except:
        logger.warning('could not get dataset mount to delete')
        return

    response_code = response['status_code']
    if response_code != 200:
        logger.warning('could not get datasetmount to delete')
        return

    dataset_mount = response['data']
    
    try:
        response = api.delete_dataset_mount(account_uid, project_uid, dataset_mount['uuid'])
    except:
        logger.warning('could not delete dataset mount')
        return

    if not response:
        logger.warning('could not delete dataset mount')
        return

    path = os.path.join(download_path,
                        dataset_mount['dataset']['account']['uid'],
                        dataset_mount['dataset']['uid'],
                        str(dataset_mount['dataset_versioning']['version']))

    # Delete files locally and delete the symlink if any

    if dataset_mount['alias'] is not None:
        path = os.path.join(download_path,
                        '.onepanel',
                        dataset_mount['dataset']['account']['uid'],
                        dataset_mount['dataset']['uid'],
                        str(dataset_mount['dataset_versioning']['version']))

        symlink_path = os.path.join(download_path, dataset_mount['alias'])
    
        if os.path.lexists(symlink_path):
            os.unlink(symlink_path)
            logger.info('deleted symlink')
    else:
        logger.info('No alias to delete')

    logger.info('deleting files under path {}'.format(path))
    shutil.rmtree(path, True)

    logger.info('deleted files')

    logger.info('deleted Dataset Mount - {}'.format(dataset_mount['uuid']))

@datasets.command('list', help='Display a list of all datasets.')
@click.pass_context
@login_required
def datasets_list(ctx):
    vc = ctx.obj['vc']
    data = vc.list(params='/datasets')
    if data is None or len(data['data']) < 1:
        print("No datasets found.")
    else:
        data_print = []
        for datum in data['data']:
            uid = datum['uid']
            if datum['version'] is None:
                version_count = 'No version information provided'
                size = None
            else:
                version_count = datum['version']['version']
                size = datum['version']['size']
            # Some datasets may not have been uploaded to yet
            if size is None:
                size = 0
            size_formatted = humanize.naturalsize(size, binary=True)
            data_print.append({'uid': uid,
                               'version_count': version_count,
                               'size': size_formatted
                               })

        empty_message = "No datasets found."
        fields = ['uid', 'version_count', 'size']
        field_names = ['NAME', 'VERSIONS', 'SIZE']
        DatasetViewController.print_items(data_print, fields, field_names, empty_message)


@datasets.command('init', help='Initialize dataset in current directory.')
@click.option(
    '-n', '--name',
    type=str,
    required=False,
    help='Dataset name.'
)
@click.pass_context
@login_required
def datasets_init(ctx, name):
    vc = ctx.obj['vc']
    # Get the parent dir as the default dataset name
    # To support symbolic links as a parent dir name
    dataset_uid = name

    if dataset_uid==None:
        if platform.system() is 'Windows':
            wd = os.popen('cd').readline().strip('\n')
        else:
            wd = os.popen('pwd').readline().strip('\n')
        dataset_uid = os.path.basename(wd)

        # Always prompt user for a dataset name
        suggested = sanitize_dataset_uid(dataset_uid)

        click.echo('Please enter a valid name [{suggested}].'.format(suggested=suggested))
        prompt_msg = click.style('To use suggested name "{suggested}", just press enter'
                                .format(suggested=suggested), fg='blue')
        try:
            dataset_uid = click.prompt(prompt_msg, default="", type=str, show_default=False)
        except click.Abort:
            return None
        if len(dataset_uid) == 0:
            dataset_uid = suggested

    if not vc.is_uid_valid(dataset_uid):
        suggested = sanitize_dataset_uid(dataset_uid)
        prompt_msg = click.style('The name you entered is invalid.',fg='red')
        prompt_msg += click.style('\nName should be 3 to 25 chracters long, lower case alphanumeric or \'-\' '
                      'and must start and end with an alphanumeric character.',fg='red')
        prompt_msg += '\nPlease enter a valid name [{suggested}].'.format(suggested=suggested)
        prompt_msg += click.style('\nTo use suggested name "{alt}", just press enter'.format(alt=suggested),fg='blue')
        try:
            dataset_uid = click.prompt(prompt_msg, default="", type=str, show_default=False)
        except click.Abort:
            return None
        if len(dataset_uid) == 0:
            dataset_uid = suggested
        if not vc.is_uid_valid(dataset_uid):
            click.echo("Invalid dataset name. Please try again.")
            return None
    init_dataset(ctx, None, dataset_uid, os.getcwd())


@datasets.command('create', help='Create dataset in new directory.')
@click.argument('name', type=str)
@click.pass_context
@login_required
def datasets_create(ctx, name):
    vc = ctx.obj['vc']
    target_dir = os.getcwd()
    dataset_uid = name
    if not vc.is_uid_valid(dataset_uid):
        click.echo('Dataset name {} is invalid, please enter a valid name.'.format(dataset_uid))
        click.echo(
            'Name should be 3 to 25 characters long, lower case alphanumeric or \'-\' and must start and end with an alphanumeric character.')
        suggested = dataset_uid.lower()
        suggested = suggested.replace('_', '-')
        prompt_msg = 'Dataset name [{alt}]'.format(alt=suggested)
        try:
            dataset_uid = click.prompt(prompt_msg, default="", type=str, show_default=False)
        except click.Abort:
            return None
        if len(dataset_uid) == 0:
            dataset_uid = suggested
        if not vc.is_uid_valid(dataset_uid):
            click.echo("Dataset name still invalid. Please try again.")
            return None

    account_uid = ctx.obj['connection'].account_uid

    if not check_dataset_exists_remotely(ctx, account_uid, dataset_uid):
        # Attach the desired directory to the current dir
        target_dir += os.sep + dataset_uid
        outcome = create_dataset(ctx, account_uid, dataset_uid, target_dir)
        if outcome is not None:
            click.echo('Dataset is created in directory {}.'.format(outcome))


@datasets.command('push', help='Push up dataset changes')
@click.option(
    '-m', '--message',
    type=str,
    default=None,
    help='Datasets only: Add a message to this version. Up to 255 chars.\"text\".'
)
@click.option(
    '-n', '--name',
    type=str,
    default=None,
    help='Datasets only: Add a name to this version. Use \"text\".'
)
@click.option(
    '-u', '--update-version',
    is_flag=True,
    default=False,
    help='Datasets only, pushes up a new version.'
)
@click.option(
    '-q', '--quiet',
    is_flag=True,
    help='Minimize chatter from executed commands.'
)
@click.option(
    '-b', '--background',
    is_flag=True,
    help='Run the download in the background. Will work even if SSH session is terminated.'
)
@click.option(
    '-w', '--watch',
    is_flag=True,
    help='Datasets only: Syncs up local files to remote. Does not create new dataset versions.'
)
@click.option(
    '-t', '--threads',
    type=int,
    help='Datasets only, when doing a watch: Number of threads allowed.'
)
@click.option(
    '-y', '--yes',
    is_flag=True,
    default=False,
    help='Automatic yes to prompts'
)
@click.pass_context
@login_required
def datasets_push(ctx, message, name, update_version, quiet, background, watch, threads, yes):
    _datasets_push(ctx, message, name, update_version, quiet, background, watch, threads, yes)


def _datasets_push(ctx, message, name, update_version, quiet, background, watch, threads, yes):
    if threads is None:
        threads = 10

    if update_version and background:
        cmd_list = ['onepanel', 'dataset-background-push']
        if message is not None:
            cmd_list.append('--message')
            cmd_list.append('\"' + message + '\"')
        if name is not None:
            cmd_list.append('--name')
            cmd_list.append('\"' + name + '\"')
        if quiet:
            cmd_list.append('-q')
        if background:
            cmd_list.append('-b')

        run_in_background(cmd_list)

        click.echo("Starting upload in the background.")
        return

    if update_version and not background:
        general_push(ctx, message, name, quiet, background)
        return

    if watch and not background:
        click.echo('Starting watch')
        _watch_sync(ctx, threads)
        return

    if watch and background:
        cmd_list = ['onepanel', 'datasets', 'watch', '-t', str(threads)]
        run_in_background(cmd_list)
        click.echo('Starting watch in the background')

        return

    if not update_version and not watch:
        sync(ctx, yes, threads=threads)

@datasets.command('pull', help='Pull down dataset changes')
@click.option(
    '-y', '--yes',
    is_flag=True,
    default=False,
    help='Automatic yes to prompts'
)
@click.option(
    '-t', '--threads',
    type=int,
    help='Number of threads allowed for network requests.'
)
@click.pass_context
@login_required
def datasets_pull(ctx, yes, threads):
    sync(ctx, yes, FileSynchronizer.REMOTE, threads)


@datasets.command(
    'watch',
    hidden=True,
    help='Syncs up local files to remote. Does not create new dataset versions.')
@click.option(
    '-t', '--threads',
    type=int,
    help='Number of threads allowed for network requests.'
)
@click.pass_context
@login_required
def watch(ctx, threads=10):
    _watch_sync(ctx, threads)


def partial_download(ctx, path, destination, version, threads, skip_prompt, delete, include):
    # Path is {account_uid}/datasets/{dataset_uid}/path/to/folder
    parts = path.split('/', 3)

    if len(parts) < 3:
        click.echo('Path must be account/datasets/dataset/path/to/download')
        return

    account_uid = parts[0]
    dataset_uid = parts[2]
    path = parts[3]

    if destination is None:
        destination = '.'
    download_path = os.path.abspath(os.path.expanduser(destination))

    # +1 for path separator
    cwd_length = len(os.getcwd()) + 1

    ctx.obj['vc'] = DatasetViewController(ctx.obj['connection'])
    vc = ctx.obj['vc']
    vc.account_uid = account_uid
    vc.dataset_uid = dataset_uid
    vc.init_endpoint()

    if threads is None:
        threads = 10

    if version is None:
        version = 'current'

    current_version = vc.get(field_path='/version/' + version)
    if current_version['data'] is None and current_version['status_code'] != 404:
        click.echo('Could not get information about dataset.')
        return

    if current_version['data']['provider']['uid'] != 'aws-s3':
        click.echo('Unsupported dataset provider')
        return

    if path == '/':
        path = ''

    dataset_path = current_version['data']['version']['path'] + '/'

    # todo implement for gcp
    connection = services.get_connection()
    endpoint = '{}/accounts/{}/datasets/{}/credentials/aws'.format(connection.URL, vc.account_uid, vc.dataset_uid)
    authenticator = APIProviderAWS(connection, endpoint)
    s3_wrapper = S3.Wrapper(credentials_provider=authenticator)

    ignore_file_states = []
    if not delete:
        ignore_file_states.append(FileDifference.State.DELETED)

    master = FileSynchronizer.REMOTE
    synchronizer = FileSynchronizer(download_path, dataset_path, s3_wrapper, master, dataset_path + path, ignore_file_states)
    synchronizer = ThreadedFileSynchronizer(synchronizer, threads, [print_status(cwd_length, master)])

    if not skip_prompt:
        click.echo('Finding file differences...')
    else:
        click.echo('Downloading...')

    differences = synchronizer.find_difference()
    if include is not None:
        differences = FileSynchronizer.filter(differences, include, dataset_path)

    if len(differences) == 0 and not skip_prompt:
        click.echo('No file differences')
        return

    if not skip_prompt:
        for filepath, value in differences.items():
            local_path = filepath[cwd_length:]
            click.echo('{} - {}'.format(local_path, value.state))

        click.confirm('Sync files from remote dataset?', abort=True)

    synchronizer.synchronize(differences.values())
    synchronizer.shutdown()

    click.echo('The files have been downloaded to: {}'.format(download_path))


def datasets_clone(ctx, path, directory, suppress_output=False, run_as_background=False, delete=False):
    conn = ctx.obj['connection']
    vc = DatasetViewController(conn)

    values = path.split('/')

    if len(values) == 3:
        try:
            account_uid, datasets_dir, dataset_uid = values
            assert (datasets_dir == 'datasets')
        except:
            click.echo('Invalid dataset path. Please use <account_uid>/datasets/<uid>')
            return
    else:
        click.echo('Invalid dataset path. Please use <account_uid>/datasets/<uid>')
        return

    vc.account_uid = account_uid
    vc.dataset_uid = dataset_uid

    # check dataset path, account_uid, dataset_uid
    if directory is None:
        home = os.path.join(os.getcwd(), dataset_uid)
    elif directory == '.':
        home = os.getcwd()
    else:
        home = os.path.join(os.getcwd(), directory)

    # check if the dataset exists
    url_dataset_check = '/accounts/{}/datasets/{}'.format(account_uid, dataset_uid)
    response_data = vc.get(uid='', field_path='', params=url_dataset_check)
    response_code = response_data['status_code']
    if response_code == 200:
        remote_dataset = response_data['data']
    elif response_code == 401 or response_code == 404:
        print('Dataset does not exist.')
        return
    else:
        print('Error: {}'.format(response_code))
        return None

    if not vc.exists_remote(dataset_uid, remote_dataset):
        click.echo('There is no dataset {}/datasets/{} on the server'.format(account_uid, dataset_uid))
        return

    if not run_as_background:
        can_create = True
        if vc.exists_local(home):
            can_create = click.confirm('Dataset already exists, overwrite?')
        if not can_create:
            return

    creds = CredsUtility.get_credentials(ctx.obj['connection'],account_uid,'datasets',dataset_uid)
    util = CloudStorageUtility.get_utility(creds)

    util.suppress_output = suppress_output
    vc.init_endpoint()

    current_version = vc.get(field_path='/version/current')

    if current_version['data'] is None:
        if current_version['status_code'] == 404:
            click.echo('Dataset is without files.')
            vc.save(home)
            return 0
        else:
            click.echo('Could not get information about dataset.')
            return

    if current_version['data']['provider']['uid'] != 'aws-s3':
        click.echo('Unsupported dataset provider')
        return

    vc.save(home)
    # todo test the delete
    cloud_storage_from_dir = current_version['data']['version']['path']
    util.run_cmd_background = run_as_background
    exit_code = util.download_all(home, cloud_storage_from_dir, delete)
    if exit_code != 0:
        click.echo('\nError with downloading files.')
        return

    return 0


def general_push(ctx, comment='', name='', suppress_output=False, run_as_background=False):
    num_files = 0
    size_in_bytes_total = 0
    for root, subdirs, files in os.walk(os.getcwd()):
        inside_onepanel_dir = False
        file_path_list = root.split(os.path.sep)
        for path_chunk in file_path_list:
            if '.onepanel' == path_chunk:
                inside_onepanel_dir = True
                break
        if inside_onepanel_dir:
            continue
        for filename in files:
            file_path = os.path.join(root, filename)
            num_files += 1
            size_in_bytes_total += os.path.getsize(file_path)

    if num_files < 1:
        click.echo("Cannot find any files in current dir, exiting.")
        return

    ctx.obj['vc'] = DatasetViewController(ctx.obj['connection'])
    vc = ctx.obj['vc']
    vc.init_credentials_retrieval()
    vc.init_endpoint()

    try:
        # Before trying to do any upload, make sure user has permission
        # For example, we don't want them to modify a public dataset

        url_dataset_member_check = '/is_member'
        response_data = vc.head(uid='', field_path='', params=url_dataset_member_check)

        if response_data['status_code'] == 404:
            click.echo('You are not authorized to push to this dataset.')
            return

        post_obj = {
            'comment': comment,
            'name': name
        }
        update_dataset_resp = vc.put(field_path='/update_version', post_object=post_obj)
        update_dataset_resp_status_code = update_dataset_resp['status_code']
        if (update_dataset_resp_status_code == 201 or update_dataset_resp_status_code == 200) == False:
            click.echo('\nError with calling the API. Contact support if this error continues.')
            return

        if update_dataset_resp_status_code != 201 and update_dataset_resp['data'] is None:
            click.echo('Could not get information about dataset.')
            return

        # Get information about the version, such as the path.
        version_resp = vc.get(field_path='/version/current')
        if version_resp['data'] is None:
            click.echo('Could not get information about dataset.')
            return

        if version_resp['data']['provider']['uid'] != 'aws-s3':
            click.echo('Unsupported dataset provider')
            return

        curr_version = version_resp['data']['version']['version']

        # Start the dataset upload, and check if the dataset is locked from uploading
        data = {
            'bytesTotal': size_in_bytes_total,
            'filesTotal': num_files,
        }
        url_start_upload = '/start_upload'
        try:
            response_data = vc.post(data, params=url_start_upload)
        except ValueError:
            click.echo("Error with POST, No JSON Object could be decoded.")

        if response_data['status_code'] != 200:
            click.echo(response_data['data'])
            return

        # Notify the user, by email, that their background upload is starting
        if run_as_background:
            notify_user_url = '/update_user_for_upload'
            notify_data = {
                'emailType': 'update',
                'emailMsg': 'Expect to see another email once the upload completes.',
            }

            try:
                response_data = vc.post(notify_data, params=notify_user_url)
            except ValueError:
                click.echo("Error with POST, No JSON Object could be decoded.")

            if response_data['status_code'] != 200:
                click.echo(response_data['data'])
                return

        creds = CredsUtility.get_credentials(ctx.obj['connection'], vc.account_uid, 'datasets', vc.dataset_uid)
        util = CloudStorageUtility.get_utility(creds)

        dataset_dir = os.curdir
        provider_storage_push_to_dir = version_resp['data']['version']['path']
        util.suppress_output = suppress_output
        util.run_cmd_background = run_as_background
        uploadThread = UploadUpdateThread(1, 'updater', vc, util, provider_storage_push_to_dir)
        uploadThread.start()
        exit_code = util.upload_dir(dataset_dir, provider_storage_push_to_dir, '.onepanel/*')
        if exit_code != 0:
            click.echo('\nError with pushing up files.')
            return

        # Notify the API that the dataset push was completed
        # Need the final dataset information from the provider storage.
        file_info_cloud_provider = util.get_cs_path_details(provider_storage_push_to_dir)

        url_finish_upload = '/finish_upload'
        upload_data = {
            'bytesCurrent': int(file_info_cloud_provider['data']['total_bytes']),
            'filesCurrent': int(file_info_cloud_provider['data']['total_files']),
        }
        try:
            response_data = vc.post(upload_data, params=url_finish_upload)
        except ValueError:
            click.echo("Error with POST, No JSON Object could be decoded.")

        if response_data['status_code'] != 200:
            click.echo(response_data['data'])
            return

        uploadThread.exitFlag = True

        if run_as_background:
            notify_user_url = '/update_user_for_upload'
            notify_data = {
                'emailType': 'update',
                'emailMsg': 'Your dataset has finished uploading.',
            }

            try:
                response_data = vc.post(notify_data, params=notify_user_url)
            except ValueError:
                click.echo("Error with POST, No JSON Object could be decoded.")

            if response_data['status_code'] != 200:
                click.echo(response_data['data'])
                return

        if run_as_background:
            click.echo('\nPushing up version ' + str(curr_version))
        else:
            click.echo('\nPushed up version ' + str(curr_version))
    except Exception as e:
        response_data = {}
        email_msg = [
            'An error occurred during upload.',
            'Details follow',
            e
        ]
        # Notify the user, by email, that their background upload encountered an error
        if True:
            notify_user_url = '/update_user_for_upload'
            notify_data = {
                'emailType': 'error',
                'emailMsg': ' '.join(email_msg),
            }

            try:
                response_data = vc.post(notify_data, params=notify_user_url)
            except ValueError:
                click.echo("Error with POST, No JSON Object coulzd be decoded.")

            if response_data['status_code'] != 200:
                click.echo(response_data['data'])
                return


def datasets_download(ctx, path, directory, suppress_output=False, run_as_background=False, delete=False):
    if directory is None or directory == '.':
        home = os.getcwd()
    else:
        home = os.path.join(os.getcwd(), directory)

    code = datasets_clone(ctx, path, home, suppress_output=suppress_output, run_as_background=run_as_background, delete=delete)
    if code != 0:
        print("Unable to download!")
        return False

    if run_as_background is False:
        print('The files have been downloaded to: {dir}'.format(dir=home))
    return True


def sync(ctx, skip_check, master=FileSynchronizer.LOCAL, threads=10):
    # +1 for path separator
    cwd_length = len(os.getcwd()) + 1

    ctx.obj['vc'] = DatasetViewController(ctx.obj['connection'])
    vc = ctx.obj['vc']
    vc.init_credentials_retrieval()
    vc.init_endpoint()

    if threads is None:
        threads = 10

    current_version = vc.get(field_path='/version/current')
    if current_version['data'] is None and current_version['status_code'] != 404:
        click.echo('Could not get information about dataset.')
        return

    if current_version['data']['provider']['uid'] != 'aws-s3':
        click.echo('Unsupported dataset provider')
        return

    dataset_path = current_version['data']['version']['path'] + '/'

    connection = services.get_connection()
    cloud_provider = os.getenv('CLOUD_PROVIDER', 'AWS')
    if cloud_provider == 'GCP':
        # Todo update endpoint when api implements GCP tokens
        endpoint = '{}/accounts/{}/datasets/{}/credentials/aws'.format(connection.URL, vc.account_uid, vc.dataset_uid)
        authenticator = APIProviderGCP(connection, endpoint)
        gcp_cs_wrapper = GCP_CS.Wrapper(credentials_provider=authenticator)
        synchronizer = FileSynchronizerGCP(os.getcwd(), dataset_path, gcp_cs_wrapper, master)
        synchronizer = ThreadedFileSynchronizerGCP(synchronizer, threads, [print_status(cwd_length, master)])

    elif cloud_provider == "AWS":
        endpoint = '{}/accounts/{}/datasets/{}/credentials/aws'.format(connection.URL, vc.account_uid, vc.dataset_uid)
        authenticator = APIProviderAWS(connection, endpoint)
        s3_wrapper = S3.Wrapper(credentials_provider=authenticator)
        synchronizer = FileSynchronizer(os.getcwd(), dataset_path, s3_wrapper, master)
        synchronizer = ThreadedFileSynchronizer(synchronizer, threads, [print_status(cwd_length, master)])

    click.echo('Finding file differences...')

    differences = synchronizer.find_difference()

    if len(differences) == 0:
        click.echo('No file differences')
        return

    if not skip_check:
        for filepath, value in differences.items():
            local_path = filepath[cwd_length:]
            click.echo('{} - {}'.format(local_path, value.state))

        if master == FileSynchronizer.LOCAL:
            click.confirm('Sync files to remote dataset?', abort=True)
        else:
            click.confirm('Sync files from remote dataset?', abort=True)

    synchronizer.synchronize(differences.values())
    synchronizer.shutdown()

    vc.mark_version_dirty(current_version['data']['version']['version'])


def _watch_sync(ctx, threads=10):
    """Watches the current directory dataset for changes, and syncs them up to remote dataset"""
    # +1 for path separator
    cwd_length = len(os.getcwd()) + 1
    cwd = os.getcwd()

    ctx.obj['vc'] = DatasetViewController(ctx.obj['connection'])
    vc = ctx.obj['vc']
    vc.init_credentials_retrieval()
    vc.init_endpoint()

    current_version = vc.get(field_path='/version/current')
    if current_version['data'] is None and current_version['status_code'] != 404:
        click.echo('Could not get information about dataset.')
        return

    if current_version['data']['provider']['uid'] != 'aws-s3':
        click.echo('Unsupported dataset provider')
        return

    dataset_path = current_version['data']['version']['path'] + '/'
    observer = Observer()
    def update_api_on_success(file_event):
        if file_event.state != FileEvent.FAILED:
            vc.mark_version_dirty(current_version['data']['version']['version'])

    connection = services.get_connection()
    cloud_provider = os.getenv('CLOUD_PROVIDER', 'AWS')
    if cloud_provider == 'GCP':
        # Todo update endpoint when api implements GCP tokens
        endpoint = '{}/accounts/{}/datasets/{}/credentials/aws'.format(connection.URL, vc.account_uid, vc.dataset_uid)
        authenticator = APIProviderGCP(connection, endpoint)
        gcp_cs_wrapper = GCP_CS.Wrapper(credentials_provider=authenticator)
        synchronizer = FileSynchronizerGCP(os.getcwd(), dataset_path, gcp_cs_wrapper)
        synchronizer = ThreadedFileSynchronizerGCP(synchronizer, threads,
                                                   [print_status(cwd_length), update_api_on_success])
        observer.schedule(FileWatchSynchronizerEventHandlerGCP(cwd, dataset_path, synchronizer,
                                                            ignore_patterns=['.*', '*.swx', '*.swpx', '*.swp', '*~',
                                                                             '*.sb-']),
                          path=cwd, recursive=True)


    elif cloud_provider == "AWS":
        endpoint = '{}/accounts/{}/datasets/{}/credentials/aws'.format(connection.URL, vc.account_uid, vc.dataset_uid)
        authenticator = APIProviderAWS(connection, endpoint)
        s3_wrapper = S3.Wrapper(credentials_provider=authenticator)
        synchronizer = FileSynchronizer(os.getcwd(), dataset_path, s3_wrapper)
        synchronizer = ThreadedFileSynchronizer(synchronizer, threads,
                                                [print_status(cwd_length), update_api_on_success])
        observer.schedule(FileWatchSynchronizerEventHandler(cwd, dataset_path, synchronizer, ignore_patterns=['.*', '*.swx', '*.swpx', '*.swp', '*~', '*.sb-']),
                          path=cwd, recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()

    observer.join()


def print_status(cwd_length, master=FileSynchronizer.LOCAL):
    """Returns a function that takes in a file_difference and prints the action on the input file
    Uses the current working directory length to print relative filenames.
    """

    def print_status_internal_local(file_event):
        """

         :param file_event:
         :type file_event FileEvent
         :return:
         """
        file_difference = file_event.file_difference

        local_path = file_difference.source_path[cwd_length:]

        if file_difference.state == FileDifference.State.MOVED:
            local_source_path = file_difference.original_source_path[cwd_length:]

            if file_event.state == FileEvent.FINISHED:
                click.echo('Moved {} to {}'.format(local_source_path, local_path))
            elif file_event.state == FileEvent.FAILED:
                click.echo('(FAILED) Moving {} to {}'.format(local_source_path, local_path))
            else:
                click.echo('Moving {} to {}'.format(local_source_path, local_path))

            return

        action = 'Uploading'

        if file_difference.state == FileDifference.State.DELETED:
            action = 'Deleting'

        if file_difference.state == FileDifference.State.MODIFIED:
            action = 'Uploading Modified'

        if file_event.state == FileEvent.FINISHED:
            action = action.replace('ing', 'ed')
        elif file_event.state == FileEvent.FAILED:
            action = '(FAILED) {} - {}'.format(action, file_event.result)

        click.echo('{} - {}'.format(action, local_path))

    def print_status_internal_remote(file_event):
        """

        :param file_event:
        :type file_event FileEvent
        :return:
        """
        file_difference = file_event.file_difference

        local_path = file_difference.source_path[cwd_length:]

        if file_difference.state == FileDifference.State.MOVED:
            local_source_path = file_difference.original_source_path[cwd_length:]
            click.echo('Moving {} to {}'.format(local_source_path, local_path))
            return

        action = 'Downloading'

        if file_difference.state == FileDifference.State.DELETED:
            action = 'Deleting'

        if file_difference.state == FileDifference.State.MODIFIED:
            action = 'Downloading Modified'

        if file_event.state == FileEvent.FINISHED:
            action = action.replace('ing', 'ed')
        elif file_event.state == FileEvent.FAILED:
            action = '(FAILED) {} - {}'.format(action, file_event.result)

        click.echo('{} - {}'.format(action, local_path))

    if master == FileSynchronizer.LOCAL:
        return print_status_internal_local

    return print_status_internal_remote
