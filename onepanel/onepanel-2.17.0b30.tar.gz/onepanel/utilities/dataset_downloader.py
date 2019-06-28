import os
import threading
import time
import logging
import configobj

import click
from threading import Thread, Event
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from onepanel.utilities.cloud_storage_utility import CloudStorageUtility
from onepanel.utilities.creds_utility import CredsUtility
from onepanel.utilities.timer import Timer
from onepanel.utilities.original_connection import Connection
from onepanel.utilities.dataset_api import DatasetAPI
from onepanel.utilities.s3.file_sync import FileSynchronizer


LOGGER = 'dataset-downloader'
# This is the directory datasets will be downloaded to if they are aliased.
DATASET_DOWNLOAD_DIRECTORY_IF_ALIAS = '.onepanel-datasets'

class DatasetDownloadStatus:
    """Watches a directory for files downloaded and keeps track of how many were downloaded
        and their statistics, like size.
    """
    def __init__(self, path):
        self.file_count = 0
        self.byte_count = 0
        self.path = path
        self.files_downloading = []

    def add_files(self, files):
        lock = threading.Lock()
        with lock:
            self.file_count += files

    def add_bytes(self, bytes_to_add):
        lock = threading.Lock()
        with lock:
            self.byte_count += bytes_to_add

    def set_files(self, value):
        lock = threading.Lock()
        with lock:
            self.file_count = value

    def set_bytes(self, value):
        lock = threading.Lock()
        with lock:
            self.byte_count = value

    def get_file_count(self):
        return self.file_count

    def get_byte_count(self):
        return self.byte_count

    def get_files_downloading(self):
        return self.files_downloading

    def add_file_downloading(self, file_path):
        lock = threading.Lock()
        with lock:
            self.files_downloading.append(file_path)

    def remove_file_downloading(self, file_path):
        lock = threading.Lock()
        with lock:
            self.files_downloading.remove(file_path)


class DatasetMountIdentifier:
    def __init__(self, account_uid, project_uid, resource_type, resource_uid):
        self.account_uid = account_uid
        self.project_uid = project_uid
        self.resource_type = resource_type
        self.resource_uid = resource_uid
        self.dataset_uid = ''
        self.dataset_version = 0
        self.dataset_mount_uuid = ''
        self.alias = None


class DatasetMountProgressUpdater:
    def __init__(self, api, stats, account_uid, project_uid, dataset_mount_uuid):
        self.stats = stats
        self.api = api
        self.account_uid = account_uid
        self.project_uid = project_uid
        self.dataset_mount_uuid = dataset_mount_uuid

    def update(self):
        total_bytes = self.calculate_total_bytes()
        total_files = self.stats.get_file_count()

        logging.getLogger(LOGGER).info('Sending Update to API files/bytes {}/{}'.format(total_files, total_bytes))
        response = self.api.update_dataset_mount_downloader(
            account_uid=self.account_uid,
            project_uid=self.project_uid,
            dataset_mount_uuid=self.dataset_mount_uuid,
            files_downloaded=total_files,
            bytes_downloaded=total_bytes)

        if response['status_code'] != 200:
            logging.getLogger(LOGGER).warning('Unable to update API. Response code is {}'.format(response['status_code']))

    def calculate_total_bytes(self):
        total_byte_count = self.stats.get_byte_count()

        for file_path in self.stats.get_files_downloading():
            try:
                total_byte_count += os.stat(file_path).st_size
            except:
                pass

        return total_byte_count


class DatasetDownloadStatusPrinter:
    def __init__(self, stats):
        self.stats = stats

    def print_stats(self):
        stats_string = 'Files: {files} Bytes: {bytes}'.format(files=self.stats.get_file_count(), bytes=self.stats.get_byte_count())
        click.echo(stats_string)


class AWSDownloadFileTracker(FileSystemEventHandler):
    def __init__(self, stats):
        self.stats = stats

    def is_temporary_file(self, file_path):
        # With AWS S3 CLI last dot has 8 hexadecimal characters after it.
        if file_path.count('.') == 0:
            return False

        last_dot_index = file_path.rfind('.')
        return len(file_path[last_dot_index + 1:]) == 8

    def on_created(self, event):
        if event.is_directory:
            return

        if self.is_temporary_file(event.src_path):
            self.stats.add_file_downloading(event.src_path)
            return

        # Otherwise, we have a full fledged downloaded file
        self.update_statistic(event.src_path)

    def on_moved(self, event):
        """For AWS, the file is downloaded as a temporary file if it's big.
           When it finishes, it renames it.
        """
        if event.is_directory:
            return

        self.stats.remove_file_downloading(event.src_path)
        self.update_statistic(event.dest_path)

    def update_statistic(self, file_path):
        logging.getLogger(LOGGER).info('Updating statistics with file {}'.format(file_path))

        self.stats.add_files(1)

        try:
            self.stats.add_bytes(os.stat(file_path).st_size)
        except Exception as argument:
            logging.getLogger(LOGGER).warning('Exception trying to update statistics {}'.format(argument))
            # Don't do anything
            pass


class DatasetDownloader(Thread):
    def __init__(self, owner_uid, dataset_mount, path, heartbeat=6.0, timer_delay=5.0):
        Thread.__init__(self)

        self.owner_uid = owner_uid
        self.path = path
        self.stop_flag = Event()
        self.heartbeat = heartbeat
        self.timer_delay = timer_delay
        self.timer = None
        self.dataset_mount = dataset_mount

        self.file_stats = None
        self.observer = None

        self.started = False

        self.api = None
        self.downloader_thread = None

    def start(self):
        Thread.start(self)

        conn = Connection()
        conn.load_credentials()

        self.api = DatasetAPI(conn)

        if not os.path.exists(self.path):
            os.makedirs(self.path)

        self.file_stats = DatasetDownloadStatus(self.path)
        self.observer = Observer()
        self.observer.schedule(AWSDownloadFileTracker(self.file_stats), self.path, True)

        self.downloader_thread = self.start_downloading_dataset(conn, self.path, self.dataset_mount.account_uid,
                                                                self.dataset_mount.dataset_uid,
                                                                self.dataset_mount.dataset_version)

        self.start_monitoring_files()
        self.start_updating_api(self.owner_uid, self.dataset_mount.project_uid,
                                self.dataset_mount.dataset_mount_uuid)

        self.started = True

    def run(self):
        while not self.stop_flag.wait(self.heartbeat):
            if self.started:
                self.downloader_thread.join()
                self.finished_downloading_hook()
                self.stop()

    def finished_downloading_hook(self):
        response = self.api.finish_dataset_mount_downloader(self.owner_uid, self.dataset_mount.project_uid,
                                                            self.dataset_mount.dataset_mount_uuid)

        response_code = response['status_code']
        if response_code != 200:
            logging.getLogger(LOGGER).warning('Error from finish mount: {}'.format(response_code))

        onepanel_dir = os.path.join(self.path, '.onepanel')
        if not os.path.exists(onepanel_dir):
            os.makedirs(onepanel_dir)

        dataset_file = os.path.join(self.path, os.path.join('.onepanel','dataset'))

        cfg = configobj.ConfigObj(dataset_file)
        cfg['uid'] = self.dataset_mount.dataset_uid
        cfg['account_uid'] = self.owner_uid
        cfg.write()

        if self.dataset_mount.alias is not None:
            symlink_path = self.dataset_mount.alias
            os.symlink(self.path, symlink_path, True)
            logging.getLogger(LOGGER).info('Created symlink {} -> {}'.format(self.path, symlink_path))

    def join(self, timeout=None):
        if self.downloader_thread is not None:
            self.downloader_thread.join()

        if self.timer is not None:
            self.timer.join()

        if self.observer is not None:
            try:
                self.observer.stop()
            except RuntimeError:
                print('observer was not started')

        Thread.join(self, timeout)

    def stop(self):
        if self.timer is not None:
            self.timer.stop()

        if self.observer is not None:
            try:
                self.observer.stop()
            except RuntimeError:
                print('observer was not started')

        self.stop_flag.set()

    def start_monitoring_files(self):
        self.observer.start()

    def start_updating_api(self, account_uid, project_uid, dataset_mount_uuid):
        updater = DatasetMountProgressUpdater(self.api, self.file_stats, account_uid, project_uid, dataset_mount_uuid)
        self.timer = Timer(self.timer_delay, updater.update)
        self.timer.start()

    def start_downloading_dataset(self, connection, download_to_path, account_uid, dataset_uid, dataset_version):
        current_version = self.api.get_dataset_version(account_uid, dataset_uid, dataset_version)

        if current_version['data'] is None:
            if current_version['status_code'] == 404:
                logging.getLogger(LOGGER).info('Dataset is without files.')
                return -1
            else:
                logging.getLogger(LOGGER).warning('Could not get information about dataset.')
                return -1

        if current_version['data']['provider']['uid'] != 'aws-s3':
            logging.getLogger(LOGGER).warning('Unsupported dataset provider')
            return -1

        cloud_storage_from_dir = current_version['data']['version']['path']
        remote_dataset_path = current_version['data']['version']['path'] + '/'
        t = Thread(target=CloudStorageUtility.sync_files, args=(account_uid, 'datasets', dataset_uid, download_to_path, remote_dataset_path,),
                                       kwargs={'master': FileSynchronizer.REMOTE, 'quiet': True, 's3_full_path': cloud_storage_from_dir, 'refresh': True})
        t.start()
        return t


class DatasetDownloadListener(Thread):
    """
        continue_listening: Whether the thread should continue waiting and check for new dataset mounts.
    """
    def __init__(self, connection, download_path, account_uid, project_uid,
                 resource_type, resource_uid, continue_listening=True, verbose=False):
        Thread.__init__(self)

        self.identifier = DatasetMountIdentifier(account_uid, project_uid, resource_type, resource_uid)
        self.api = DatasetAPI(connection)
        self.download_path = download_path
        self.continue_listening = continue_listening

        if verbose:
            logger = logging.getLogger(LOGGER)
            logger.setLevel(logging.DEBUG)
            ch = logging.StreamHandler()
            ch.setLevel(logging.DEBUG)
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            ch.setFormatter(formatter)
            logger.addHandler(ch)

    def get_dataset_mount(self):
        if self.identifier.resource_type == 'instance':
            return self.api.claim_instance_mount(
                        account_uid=self.identifier.account_uid,
                        project_uid=self.identifier.project_uid,
                        instance_uid=self.identifier.resource_uid,
                        downloader_id=os.getcwd(),
                        downloader_pid=os.getpid())
        elif self.identifier.resource_type == 'job':
            return self.api.claim_job_mount(
                        account_uid=self.identifier.account_uid,
                        project_uid=self.identifier.project_uid,
                        job_uid=self.identifier.resource_uid,
                        downloader_id=os.getcwd(),
                        downloader_pid=os.getpid())
        else:
            raise ValueError('Resource Type {} not supported'.format(self.identifier.resource_type))

    def run(self):
        logger = logging.getLogger(LOGGER)

        while True:
            logger.info('Listening for Dataset Mounts')

            try:
                response = self.get_dataset_mount()
            except Exception as Argument:
                # On exception, try again in 10 seconds
                logger.warning('Got an exception trying to claim an instance mount {}. Trying again in 10 seconds'.format(Argument))

                time.sleep(10)
                continue

            response_code = response['status_code']
            if response_code != 200:
                if response_code != 404:
                    logger.warning('Error from dataset mount: {}'.format(response_code))
                elif response_code == 404:
                    if not self.continue_listening:
                        logger.info('No more datasets to mount. Done.')
                        return
                    logger.info('No datasets to mount. Checking again in 30 seconds')
                # API says there is no more. Try back later.
                time.sleep(30)
                continue

            dataset_mount = response['data']

            download_identifier = DatasetMountIdentifier(dataset_mount['dataset']['account']['uid'],
                                                         self.identifier.project_uid,
                                                         self.identifier.resource_type,
                                                         self.identifier.resource_uid)

            download_identifier.dataset_mount_uuid = dataset_mount['uuid']
            download_identifier.dataset_uid = dataset_mount['dataset']['uid']
            download_identifier.dataset_version = dataset_mount['dataset_versioning']['version']

            path = os.path.join(self.download_path,
                                download_identifier.account_uid,
                                download_identifier.dataset_uid,
                                str(download_identifier.dataset_version))

            if dataset_mount['alias']:
                download_identifier.alias = os.path.join(self.download_path, dataset_mount['alias'])
                path = os.path.join(self.download_path, 
                                DATASET_DOWNLOAD_DIRECTORY_IF_ALIAS,
                                download_identifier.account_uid,
                                download_identifier.dataset_uid,
                                str(download_identifier.dataset_version))

            logger.info('Obtained dataset mount. Downloading to {}'.format(path))

            downloader = DatasetDownloader(self.identifier.account_uid, download_identifier, path)

            downloader.start()
            downloader.join()

            logger.info('Dataset {} Finished downloading'.format(path))

