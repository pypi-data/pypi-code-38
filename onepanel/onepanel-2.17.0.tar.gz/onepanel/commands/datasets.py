""" Command line interface for the OnePanel Machine Learning platform

'Datasets' commands group.
"""
import os
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
from onepanel.utilities.cloud_storage_utility import CloudStorageUtility
from onepanel.utilities.dataset_strings import sanitize_dataset_uid
from onepanel.utilities.dataset_downloader import DatasetDownloadListener
from onepanel.utilities.dataset_api import DatasetAPI

from onepanel.utilities.s3.file_sync import FileSynchronizer, ThreadedFileSynchronizer, FileDifference, FileEvent
from onepanel.utilities.gcp_cs.file_sync import FileSynchronizer as FileSynchronizerGCP, \
    ThreadedFileSynchronizer as ThreadedFileSynchronizerGCP
from onepanel.utilities.s3.file_watch_sync import FileWatchSynchronizerEventHandler
from onepanel.utilities.gcp_cs.file_watch_sync import FileWatchSynchronizerEventHandler \
    as FileWatchSynchronizerEventHandlerGCP
from onepanel.utilities.s3.authentication import APIProvider as APIProviderAWS
from onepanel.utilities.gcp_cs.authentication import APIProvider as APIProviderGCP
from onepanel.utilities.process import run_in_background

import onepanel.utilities.s3.wrapper as S3
import onepanel.utilities.gcp_cs.wrapper as GCP_CS
import onepanel.services as services


class DatasetIdentifier:
    """
    Represents a path to a dataset. Each path must have an account_uid that owns the dataset, and a
    dataset_uid, identifying the dataset for the account.
    """

    class InvalidPath(Exception):
        """
        Represents an invalid DatasetPath.
        """
        def __init__(self, path):
            Exception.__init__(self, 'Invalid dataset path {}. Please use <account_uid>/datasets/<uid>'.format(path))

    def __init__(self, path, version=None):
        if version is None:
            version = 'current'

        self._version = version

        values = path.split('/')

        if values[1] != 'datasets':
            raise DatasetIdentifier.InvalidPath(path)

        self._account_uid, self._dataset_uid = values[0], values[2]

        self._subpath = None
        if len(values) > 3:
            self._subpath = '/'.join(values[3:])

    @property
    def account_uid(self):
        return self._account_uid

    @account_uid.setter
    def account_uid(self, value):
        self._account_uid = value

    @property
    def dataset_uid(self):
        return self._dataset_uid

    @dataset_uid.setter
    def dataset_uid(self, value):
        self._dataset_uid = value

    @property
    def subpath(self):
        return self._subpath

    @property
    def version(self):
        return self._version

    def __str__(self):
        result = '{}/datasets/{}'.format(self.account_uid, self.dataset_uid)

        if self.subpath:
            result += '/' + self.subpath

        if self.version:
            result += " : {}".format(self.version)

        return result


class UploadUpdateThread(threading.Thread):
    def __init__(self, thread_id, thread_name, vc, version):
        threading.Thread.__init__(self)
        self.stop_flag = threading.Event()
        self.thread_id = thread_id
        self.thread_name = thread_name
        self.sleep_time = 5  # seconds
        self.vc = vc
        self.version = version

    def run(self):
        response_data = {}
        while not self.stop_flag.wait(self.sleep_time):
            util = CloudStorageUtility.get_utility(self.vc.account_uid, 'datasets', self.vc.dataset_uid)
            stats = util.get_prefix_stats('{}/datasets/{}/{}'.format(self.vc.account_uid, self.vc.dataset_uid, self.version))

            update_upload_url = '/update_upload'
            upload_data = {
                'bytesCurrent': stats['size'],
                'filesCurrent': stats['files']
            }
            response_data['status_code'] = 500
            try:
                response_data = self.vc.post(upload_data, params=update_upload_url)
            except ValueError:
                click.echo("Error with POST, No JSON Object could be decoded.")

            if response_data['status_code'] != 200:
                click.echo(response_data['data'])
                return

    def stop(self):
        self.stop_flag.set()


class UploadDataset:
    """
    An algorithm to upload a dataset.
    Created as a class so it can be subclassed and parts of the algorithm modified.
    """

    def __init__(self):
        """
        We don't set these values in it constructor here in case we want to upload a dataset
        on a separate thread or process. Passing the parameters in the upload method makes this easier.
        """
        self.account_uid = None
        self.dataset_uid = None
        self._directory = None
        self.vc = None

    @property
    def directory(self):
        if self._directory is None:
            self._directory = os.getcwd()

        return self._directory

    @directory.setter
    def directory(self, value):
        if value is None or value == '.':
            value = os.getcwd()

        self._directory = value

    def check_upload(self):
        """
        Checks if we should upload the dataset.
        If not, return False, or throw an exception if there is some error.
        If we should, return information in a map.
        :return:
        """
        directory_stats = DatasetViewController.get_directory_stats(self.directory)
        if directory_stats['num_files'] < 1:
            return False

        # Before trying to do any upload, make sure user has permission
        # For example, we don't want them to modify a public dataset
        self.vc.check_is_user_member()

        # Get information about the version, such as the path.
        version = self.vc.get_version()

        return {
            'directory_stats': directory_stats,
            'version': version
        }

    def start_upload(self, directory_stats):
        data = {
            'bytesTotal': directory_stats['size'],
            'filesTotal': directory_stats['num_files'],
        }

        response_data = self.vc.post(data, params='/start_upload')
        if response_data['status_code'] != 200:
            raise APIViewController.APIException(response_data['status_code'], 'start_upload')

    def upload_started(self, version):
        pass

    def upload(self, version, quiet=False):
        provider_storage_push_to_dir = version['data']['version']['path']
        ignore_file_states = [FileDifference.State.DELETED]
        CloudStorageUtility.sync_files(self.account_uid, 'datasets', self.dataset_uid, self.directory,
                                       provider_storage_push_to_dir, quiet=quiet, ignore_file_states=ignore_file_states)

    def upload_finished(self, version):
        util = CloudStorageUtility.get_utility(self.vc.account_uid, 'datasets', self.vc.dataset_uid)
        stats = util.get_prefix_stats(
            '{}/datasets/{}/{}'.format(self.vc.account_uid, self.vc.dataset_uid, version['data']['version']['version']))

        upload_data = {
            'bytesCurrent': stats['size'],
            'filesCurrent': stats['files']
        }

        response_data = self.vc.post(upload_data, params='/finish_upload')

        if response_data['status_code'] != 200:
            raise APIViewController.APIException(response_data['status_code'], 'finish_upload')

    def handle_upload_error(self, exception):
        email_msg = [
            'An error occurred during upload.',
            'Details follow',
            str(exception)
        ]

        # Notify the user, by email, that their background upload encountered an error
        self.vc.email_user_upload_status('error', ' '.join(email_msg))

    def run(self, vc, account_uid, dataset_uid, directory=None, quiet=False):
        """
        :param vc:
        :type vc: DatasetViewController
        :param account_uid:
        :param dataset_uid:
        :param directory:
        :param quiet:
        :return:
        """
        self.account_uid = account_uid
        self.dataset_uid = dataset_uid
        self.directory = directory
        self.vc = vc

        upload_info = self.check_upload()
        if not upload_info:
            return

        try:
            self.start_upload(upload_info['directory_stats'])
            self.upload_started(upload_info['version'])
            self.upload(upload_info['version'], quiet)
            self.upload_finished(upload_info['version'])
        except Exception as e:
            self.handle_upload_error(e)


class InformedUploadDataset(UploadDataset):
    """
    Updates API with status on how upload is going on a separate thread.
    """
    def __init__(self):
        UploadDataset.__init__(self)
        self.status_uploader = None

    def upload_started(self, version):
        UploadDataset.upload_started(self, version)

        self.status_uploader = UploadUpdateThread(1, 'updater', self.vc, version['data']['version']['version'])
        self.status_uploader.start()

    def upload_finished(self, version):
        UploadDataset.upload_finished(self, version)
        self.status_uploader.stop()


class BackgroundUploadDataset(InformedUploadDataset):
    def upload_started(self, version):
        InformedUploadDataset.upload_started(self, version)
        self.vc.email_user_upload_status('update', 'Expect to see another email once the upload completes.')

    def upload_finished(self, version):
        InformedUploadDataset.upload_finished(self, version)
        self.vc.email_user_upload_status('update', 'Your dataset has finished uploading.')


class DatasetViewController(APIViewController):
    class UnsupportedProviderException(Exception):
        def __init__(self, msg):
            Exception.__init__(self, msg)

    class UpdateVersionException(Exception):
        def __init__(self, msg):
            Exception.__init__(self, msg)

    """ DatasetViewController data model
    """

    DATASET_FILE = os.path.join('.onepanel', 'dataset')
    EXCLUSIONS = [os.path.join('.onepanel', 'dataset')]

    def __init__(self, conn):
        APIViewController.__init__(self, conn)
        self.endpoint = '{}'.format(
            self.conn.URL,
        )

        self.account_uid = None
        self.dataset_uid = None

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

    def get_version(self, version='current'):
        response = self.get(field_path='/version/{}'.format(version))

        response_code = response['status_code']
        if response_code == 404:
            raise APIViewController.NotFoundException("Dataset version")
        elif response_code != 200:
            raise APIViewController.APIException(response_code, "Get Current Version Error")

        if response['data']['provider']['uid'] != 'aws-s3':
            raise DatasetViewController.UnsupportedProviderException(response['data']['provider']['uid'])

        return response

    def email_user_upload_status(self, email_type, message):
        # Notify the user, by email, that their background upload is starting
        notify_data = {
            'emailType': email_type,
            'emailMsg': message,
        }

        response_data = self.post(notify_data, params='/update_user_for_upload')

        if response_data['status_code'] != 200:
            raise APIViewController.APIException(200, 'email user')

    def is_user_member(self):
        """
        API request to check if the currently logged in user is a member of the dataset.
        :return:
        """

        return self.head(uid='', field_path='', params='/is_member')

    def check_is_user_member(self):
        """
        Checks if the currently logged in user is a member of the dataset.

        If not, an exception is thrown.
        :return:
        """

        response_data = self.is_user_member()
        response_code = response_data['status_code']

        if response_code == 200:
            return response_data
        elif response_code == 401:
            raise APIViewController.UnauthorizedException("Dataset {}/datasets/{}".format(self.account_uid, self.dataset_uid))
        elif response_code == 404:
            raise APIViewController.NotFoundException("Dataset {}/datasets/{}".format(self.account_uid, self.dataset_uid))
        else:
            raise APIViewController.APIException(response_code, '')

    def exists(self, account_uid=None, dataset_uid=None):
        url_dataset_check = '/accounts/{}/datasets/{}'.format(account_uid, dataset_uid)
        return self.get(uid='', field_path='', params=url_dataset_check)

    def check_exists(self, account_uid=None, dataset_uid=None):
        """
        Checks if the dataset for the given account and dataset uid exist.
        If it does not, an exception is thrown.
        """
        if account_uid is None:
            account_uid = self.account_uid

        if dataset_uid is None:
            dataset_uid = self.dataset_uid

        response_data = self.exists(account_uid, dataset_uid)
        response_code = response_data['status_code']
        if response_code == 200:
            remote_dataset = response_data['data']
        elif response_code == 401:
            raise APIViewController.UnauthorizedException("Dataset {}/datasets/{}".format(account_uid, dataset_uid))
        elif response_code == 404:
            raise APIViewController.NotFoundException("Dataset {}/datasets/{}".format(account_uid, dataset_uid))
        else:
            raise APIViewController.APIException(response_code, '')

        if not self.exists_remote(dataset_uid, remote_dataset):
            # TODO is this needed?
            raise APIViewController.NotFoundException("Dataset {}/datasets/{}".format(account_uid, dataset_uid))

    def download(self, dataset_identifier, directory=None, quiet=False, delete=False, include=None):
        self.account_uid = dataset_identifier.account_uid
        self.dataset_uid = dataset_identifier.dataset_uid

        self.check_exists(self.account_uid, self.dataset_uid)
        self.init_endpoint()

        current_version = self.get_version(dataset_identifier.version)

        remote_dataset_path = current_version['data']['version']['path'] + '/'
        cloud_storage_from_dir = remote_dataset_path

        if dataset_identifier.subpath:
            cloud_storage_from_dir = remote_dataset_path + dataset_identifier.subpath

        if cloud_storage_from_dir[-1] != '/':
            cloud_storage_from_dir += '/'

        ignore_file_states = []
        if not delete:
            ignore_file_states.append(FileDifference.State.DELETED)

        directory += '/'

        CloudStorageUtility.sync_files(self.account_uid, 'datasets', self.dataset_uid, directory,
                                       remote_dataset_path, master=FileSynchronizer.REMOTE, quiet=quiet,
                                       ignore_file_states=ignore_file_states, s3_full_path=cloud_storage_from_dir,
                                       include=include)

    def clone(self, dataset_identifier, directory=None, quiet=False):
        self.account_uid = dataset_identifier.account_uid
        self.dataset_uid = dataset_identifier.dataset_uid
        # TODO this logic is also in `init` or `create`
        if directory is None:
            home = os.path.join(os.getcwd(), self.dataset_uid)
        elif directory == '.':
            home = os.getcwd()
        else:
            home = os.path.join(os.getcwd(), directory)

        self.save(home)

        self.download(dataset_identifier, directory, quiet)

    def update_version(self, account_uid=None, dataset_uid=None, message='', name='', quiet=False):
        """
        Update's the dataset version with a message and a specific name to identify it.

        :param account_uid: the dataset owner's account_uid. If None, self.account_uid is used.
        :type account_uid str
        :param dataset_uid: the dataset's uid. If None, self.dataset_uid is used.
        :type dataset_uid str
        :param message: a message about this upload. Similar to a git commit message.
        :type message str
        :param name: a name to associate with this upload
        :type name str
        :param quiet: if true, suppresses output from this command.
        :return:
        """

        if account_uid is not None:
            self.account_uid = account_uid

        if dataset_uid is not None:
            self.dataset_uid = dataset_uid

        post_obj = {
            'comment': message,
            'name': name
        }
        update_dataset_resp = self.put(field_path='/update_version', post_object=post_obj)
        code = update_dataset_resp['status_code']

        if code not in [200, 201]:
            raise APIViewController.APIException(code, 'Error with calling the API. Contact support if this error continues.')

        if code != 201 and update_dataset_resp['data'] is None:
            raise DatasetViewController.UpdateVersionException('Could not get information about dataset.')

        return update_dataset_resp

    def from_json(self, data):
        self.account_uid = data['account']['uid']
        self.dataset_uid = data['uid']

    @staticmethod
    def is_uid_valid(uid):
        pattern = re.compile('^[a-z0-9][-a-z0-9]{1,23}[a-z0-9]$')
        if pattern.match(uid):
            return True
        else:
            return False

    @staticmethod
    def exists_local(home):
        dataset_file = os.path.join(home, DatasetViewController.DATASET_FILE)
        return os.path.isfile(dataset_file)

    @staticmethod
    def exists_at_directory(directory):
        dataset_file = os.path.join(directory, DatasetViewController.DATASET_FILE)
        return os.path.isfile(dataset_file)

    @staticmethod
    def exists_remote(dataset_uid, data):
        return data['uid'] == dataset_uid

    @staticmethod
    def get_directory_stats(directory=None):
        """
        Get's the statistics of the input directory.
            num_files: the total number of files
            size: size, in bytes, of all the files.

        the .onepanel subdirectory is ignored, if it exists.

        :param directory: the directory to get stats of, the current working directory is used if none is provided.
        :type directory str
        :return: a dictionary with two keys: num_files - the total number of files and size, in bytes of all the files.
        """
        if directory is None:
            directory = os.getcwd()

        num_files = 0
        size_in_bytes = 0

        for root, subdirs, files in os.walk(directory):
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
                size_in_bytes += os.path.getsize(file_path)

        return {
            'num_files': num_files,
            'size': size_in_bytes
        }


# TODO MOVE
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
    help='Add a message to this push.'
)
@click.option(
    '-n', '--name',
    type=str,
    default=None,
    help='Add a name to this push.'
)
@click.option(
    '-u', '--update-version',
    is_flag=True,
    default=False,
    help='Create a new version and push.'
)
@click.option(
    '-q', '--quiet',
    is_flag=True,
    help='Minimize chatter from executed commands.'
)
@click.option(
    '-b', '--background',
    is_flag=True,
    help='Run in background. Will work even if SSH session is terminated.'
)
@click.option(
    '-w', '--watch',
    is_flag=True,
    help='Watches and pushes any changes to local files.'
)
@click.option(
    '--in-background',
    is_flag=True,
    default=False,
    hidden=True
)
@click.pass_context
@login_required
def datasets_push(ctx, message, name, update_version, quiet, background, watch, in_background):
    _datasets_push(ctx, message, name, update_version, quiet, background, watch, in_background)


def _datasets_push(ctx, message, name, update_version, quiet, background, watch, in_background):
    if background and not in_background:
        if watch:
            click.echo('Starting watch in background')
        else:
            click.echo('Running in background')

        cmd_list = sys.argv
        cmd_list.append('--in-background')
        run_in_background(cmd_list)
        return

    if watch:
        click.echo('Starting watch')
        _watch_sync(ctx)
        return

    vc = DatasetViewController(ctx.obj['connection'])
    vc.init_credentials_retrieval()
    vc.init_endpoint()

    if update_version:
        vc.update_version(message=message, name=name)

    dataset_update = InformedUploadDataset()
    if in_background:
        dataset_update = BackgroundUploadDataset()

    dataset_update.run(vc, vc.account_uid, vc.dataset_uid, quiet=quiet)


@datasets.command('pull', help='Pull down dataset changes')
@click.option(
    '-y', '--yes',
    is_flag=True,
    default=False,
    help='Automatic yes to prompts'
)
@click.pass_context
@login_required
def datasets_pull(ctx, yes):
    sync(ctx, yes, FileSynchronizer.REMOTE)


@datasets.command(
    'watch',
    hidden=True,
    help='Syncs up local files to remote. Does not create new dataset versions.')
@click.pass_context
@login_required
def watch(ctx):
    _watch_sync(ctx)


def sync(ctx, skip_check, master=FileSynchronizer.LOCAL):
    # +1 for path separator
    cwd_length = len(os.getcwd()) + 1

    ctx.obj['vc'] = DatasetViewController(ctx.obj['connection'])
    vc = ctx.obj['vc']
    vc.init_credentials_retrieval()
    vc.init_endpoint()

    current_version = vc.get_version('current')
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
        synchronizer = ThreadedFileSynchronizerGCP(synchronizer, 10, [FileSynchronizer.print_status(cwd_length, master)])

    elif cloud_provider == "AWS":
        endpoint = '{}/accounts/{}/datasets/{}/credentials/aws'.format(connection.URL, vc.account_uid, vc.dataset_uid)
        authenticator = APIProviderAWS(connection, endpoint)
        s3_wrapper = S3.Wrapper(credentials_provider=authenticator)
        synchronizer = FileSynchronizer(os.getcwd(), dataset_path, s3_wrapper, master)
        synchronizer = ThreadedFileSynchronizer(synchronizer, [FileSynchronizer.print_status(cwd_length, master)])

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


def _watch_sync(ctx):
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
        synchronizer = ThreadedFileSynchronizerGCP(synchronizer, 10,
                                                   [FileSynchronizer.print_status(cwd_length), update_api_on_success])
        observer.schedule(FileWatchSynchronizerEventHandlerGCP(cwd, dataset_path, synchronizer,
                                                               ignore_patterns=['.*', '*.swx', '*.swpx', '*.swp', '*~',
                                                                                '*.sb-']),
                          path=cwd, recursive=True)
    elif cloud_provider == "AWS":
        endpoint = '{}/accounts/{}/datasets/{}/credentials/aws'.format(connection.URL, vc.account_uid, vc.dataset_uid)
        authenticator = APIProviderAWS(connection, endpoint)
        s3_wrapper = S3.Wrapper(credentials_provider=authenticator)
        synchronizer = FileSynchronizer(os.getcwd(), dataset_path, s3_wrapper)
        synchronizer = ThreadedFileSynchronizer(synchronizer,
                                                [FileSynchronizer.print_status(cwd_length), update_api_on_success])
        observer.schedule(FileWatchSynchronizerEventHandler(cwd, dataset_path, synchronizer, ignore_patterns=['.*', '*.swx', '*.swpx', '*.swp', '*~', '*.sb-']),
                          path=cwd, recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()

    observer.join()


@datasets.command('clone', help='Clone a remote dataset')
@click.argument('path', type=click.Path())
@click.argument('directory', type=click.Path(), required=False)
@click.option(
    '-q', '--quiet',
    is_flag=True,
    help='Minimize chatter from executed commands.'
)
@click.option(
    '-v', '--version',
    type=str,
    help='The version of the dataset. If none is provided, latest is used.')
@click.pass_context
@login_required
def clone(ctx, path, directory, quiet, version):
    vc = DatasetViewController(ctx.obj['connection'])
    identifier = DatasetIdentifier(path, version)

    if directory is None or directory == '.':
        directory = os.getcwd()
    else:
        directory = os.path.join(os.getcwd(), directory)

    vc.clone(identifier, directory, quiet)
