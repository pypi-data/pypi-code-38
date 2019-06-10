# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Implementations of datastore."""
import logging
import os
import re
import requests

from abc import ABCMeta, abstractmethod
from azureml._vendor.azure_storage.blob import BlockBlobService
from azureml._vendor.azure_storage.file import FileService, models

from azureml._base_sdk_common.utils import create_retry, common_path, to_unix_path, accumulate
from azureml._history.utils.async_task import AsyncTask
from azureml._history.utils.task_queue import TaskQueue
from azureml.data.abstract_datastore import AbstractDatastore
from azureml.data.data_reference import DataReference

module_logger = logging.getLogger(__name__)


FOLDER = 0
EMPTY_FILE = 1
FILE = 2


class AbstractAzureStorageDatastore(AbstractDatastore):
    """Azure Storage Container datastore class.

    You should only create this class by calling Datastore() or Datastore.register*.
    """

    __metaclass__ = ABCMeta

    def __init__(self, workspace, name, datastore_type, container_name, account_name,
                 sas_token=None, account_key=None, protocol=None, endpoint=None):
        """Constructor.

        :param workspace:
        :param name:
        :param datastore_type:
        :param container_name:
        :param account_name:
        :param sas_token:
        :param account_key:
        :param protocol:
        :param endpoint:
        """
        super(AbstractAzureStorageDatastore, self).__init__(workspace, name, datastore_type)
        self.container_name = container_name
        self.account_name = account_name
        self.sas_token = sas_token
        self.account_key = account_key
        self.credential_type = 'None'
        self.protocol = protocol
        self.endpoint = endpoint

        if account_key:
            self.credential_type = 'AccountKey'
        if sas_token:
            self.credential_type = 'Sas'

        self._num_workers = 32

        self._data_reference = DataReference(datastore=self)

    def path(self, path=None, data_reference_name=None):
        """Return corresponding data reference object.

        :param path: the relative path on the datastore
        :type path: str
        :param data_reference_name: the name of the data reference
        :type data_reference_name: str
        :return: the data reference object
        :rtype: DataReference
        """
        return self._data_reference.path(path, data_reference_name)

    def as_download(self, path_on_compute=None):
        """Return data reference object with download mode.

        :param path_on_compute: the relative path on the compute
        :type path_on_compute: str
        :return: the data reference object
        :rtype: DataReference
        """
        return self._data_reference.as_download(path_on_compute)

    def as_upload(self, path_on_compute=None):
        """Return data reference object with upload mode.

        :param path_on_compute: the relative path on the compute
        :type path_on_compute: str
        :return: the data reference object
        :rtype: DataReference
        """
        return self._data_reference.as_upload(path_on_compute)

    def as_mount(self):
        """Return data reference object with mount mode.

        :param path_on_compute: the relative path on the compute
        :type path_on_compute: str
        :return: the data reference object
        :rtype: DataReference
        """
        return self._data_reference.as_mount()

    @abstractmethod
    def download(self, target_path, prefix=None, overwrite=False, show_progress=True):
        """Download paths with prefix to target_path.

        :param target_path:
        :param prefix:
        :param overwrite:
        :param show_progress:
        :return:
        """
        raise NotImplementedError()

    @abstractmethod
    def upload(self, src_dir, target_path=None, overwrite=False, show_progress=True):
        """Upload src_dir to target_path.

        :param src_dir:
        :param target_path:
        :param overwrite:
        :param show_progress:
        :return:
        """
        raise NotImplementedError()

    @abstractmethod
    def upload_files(self, files, relative_root=None, target_path=None, overwrite=False, show_progress=True):
        """Upload files to target_path.

        :param files:
        :param relative_root: relative path in target
        :param target_path:
        :param overwrite:
        :param show_progress:
        :return:
        """
        raise NotImplementedError()

    def _get_data_reference(self):
        return self._data_reference

    @property
    def is_sas(self):
        """(Deprecated) use credential_type property.

        This property is deprecated, please use the property "credential_type" to determine the credential type.
        """
        module_logger.warning("This property is deprecated, please use the property \"credential_type\"" +
                              " to determine the credential type.")
        return bool(self.sas_token)

    def _as_dict(self, hide_secret=True):
        output = super(AbstractAzureStorageDatastore, self)._as_dict()
        output["container_name"] = self.container_name
        output["account_name"] = self.account_name
        output["protocol"] = self.protocol
        output["endpoint"] = self.endpoint

        if not hide_secret:
            output["credential_type"] = self.credential_type
            output["sas_token"] = self.sas_token
            output["account_key"] = self.account_key

        return output

    def _get_default_request_session(self):
        a = requests.adapters.HTTPAdapter(pool_connections=self._num_workers, pool_maxsize=self._num_workers * 2,
                                          max_retries=create_retry())
        s = requests.Session()
        s.mount("http://", a)
        s.mount("https://", a)
        return s

    def _get_upload_from_dir(self, src_path, target_path):
        if not os.path.isdir(src_path):
            raise Exception("src_path must be a directory")

        paths_to_upload = []
        for dirpath, dirnames, filenames in os.walk(src_path):
            paths_to_upload += self._get_upload_from_files(
                map(lambda f: os.path.join(dirpath, f), filenames),
                target_path,
                src_path,
                True)
        return paths_to_upload

    def _get_upload_from_files(self, file_paths, target_path, relative_root, skip_root_check):
        paths_to_upload = []
        for file_path in file_paths:
            if not skip_root_check and relative_root not in file_path and relative_root != "/":
                raise Exception("relative_root: '{}' is not part of the file_path: '{}'".format(
                    relative_root, file_path))
            if not os.path.isfile(file_path):
                err_msg = "'{}' does not point to a file. " + \
                    "Please upload the file to cloud first if running in a cloud notebook."
                raise Exception(err_msg.format(file_path))

            target_file_path = to_unix_path(file_path)
            if relative_root != "/":
                # need to do this because Windows doesn't support relpath if the partition is different
                target_file_path = os.path.relpath(target_file_path, to_unix_path(relative_root))
            else:
                # strip away / otherwise we will create a folder in the container with no name
                target_file_path = target_file_path.lstrip("/")

            if target_path:
                target_file_path = os.path.join(target_path, target_file_path)

            paths_to_upload.append((file_path, target_file_path))

        return paths_to_upload

    def _start_upload_task(self, paths_to_upload, overwrite, exists, show_progress, task_generator):
        # it's an estimated total because we might skip some files
        estimated_total = len(paths_to_upload)
        counter = _Counter()

        module_logger.info("Uploading an estimated of {} files".format(estimated_total))

        with TaskQueue(__name__, module_logger, num_workers=self._num_workers) as tq:
            for (src_file_path, target_file_path) in paths_to_upload:
                if not overwrite:
                    if exists(target_file_path):
                        estimated_total -= 1
                        module_logger.warning("Target already exists. Skipping upload for {}".format(target_file_path))
                        continue

                task_fn = task_generator(target_file_path, src_file_path)
                task = AsyncTask(
                    "task_upload_{}".format(target_file_path),
                    task_fn,
                    module_logger,
                    handler=self._get_task_handler(src_file_path, counter, estimated_total, show_progress, "Upload"))
                tq.add(task)

        module_logger.info("Uploaded {} files".format(counter.count()))
        return counter.count()

    def _get_task_handler(self, f, counter, total, show_progress, action):
        def handler(fn, logger):
            def print_progress(message):
                logger.info(message)
                if show_progress:
                    self._get_console_logger().write("{}\n".format(message))

            try:
                print_progress("{}ing {}".format(action, f))
                result = fn()
                # thanks to GIL no need to use lock here
                counter.increment()
                print_progress("{}ed {}, {} files out of an estimated total of {}".format(
                    action, f, counter.count(), total))
                return result
            except Exception as e:
                logger.error("Task Exception", e)

        return handler


class AzureFileDatastore(AbstractAzureStorageDatastore):
    """Datastore for Azure file storage."""

    def __init__(self, workspace, name, container_name, account_name, sas_token=None,
                 account_key=None, protocol=None, endpoint=None, request_session=None):
        """Initialize a new Azure File Share Datastore.

        :param workspace: the workspace this datastore belongs to.
        :type workspace: Workspace
        :param name: the name of the datastore. It can only contain alphanumeric
        characters or - or _
        :type name: str
        :param container_name: the file share name
        :type container_name: str
        :param account_name: the storage account name
        :type account_name: str
        :param sas_token: the SAS token for accessing this container, defaults to None
        :type sas_token: str, optional
        :param account_key: the storage account key, defaults to None
        :type account_key: str, optional
        :param protocol: Protocol to use to connect to the storage account. If None, defaults to https.
        :type protocol: str, optional
        :param endpoint: The endpoint of the blob container. If None, defaults to core.windows.net.
        :type endpoint: str, optional
        :param request_session: the session object to use for http requests, defaults to None
        :type request_session: requests.Session, optional
        """
        super(AzureFileDatastore, self).__init__(workspace, name, 'AzureFile', container_name, account_name,
                                                 sas_token, account_key, protocol, endpoint)
        self.file_service = FileService(
            account_name=self.account_name,
            account_key=self.account_key,
            sas_token=self.sas_token,
            request_session=request_session or self._get_default_request_session(),
            protocol=protocol,
            endpoint_suffix=endpoint
        )

    def download(self, target_path, prefix=None, overwrite=False, show_progress=True):
        """Download the data from the file share to the local file system.

        :param target_path: the local directory to download the file to
        :type target_path: str
        :param prefix: path to the folder in the file share to download. If set to None, will
            download everything in the file share. Defaults to None.
        :type prefix: str, optional
        :param overwrite: overwrite existing file, defaults to False
        :type overwrite: bool, optional
        :param show_progress: show progress of download in the console, defaults to True
        :type show_progress: bool, optional
        :return: The number of files successfully downloaded
        :rtype: int
        """
        module_logger.info("Called AzureFileDatastore.download")
        if not os.path.exists(target_path):
            os.makedirs(target_path)
        total = 0
        counter = _Counter()
        remaining_paths = []

        with TaskQueue(__name__, module_logger, num_workers=self._num_workers) as tq:
            for file_or_dir in self.file_service.list_directories_and_files(
                    share_name=self.container_name,
                    prefix=prefix):
                remaining_paths.append((file_or_dir, ""))
            total = len(remaining_paths)
            while len(remaining_paths) > 0:
                file_or_dir, parent_path = remaining_paths.pop()
                if isinstance(file_or_dir, models.File):
                    file = file_or_dir
                    if not self._download_file(tq, parent_path, file.name, target_path,
                                               overwrite, total, counter, show_progress):
                        total -= 1
                else:
                    directory = file_or_dir
                    path = os.path.join(parent_path, directory.name)
                    for file_or_dir in self.file_service.list_directories_and_files(
                            share_name=self.container_name,
                            directory_name=path):
                        remaining_paths.append((file_or_dir, path))
                        total += 1
        module_logger.info("Finished AzureFileDatastore.download. Downloaded {} files.".format(counter.count()))
        return counter.count()

    def upload(self, src_dir, target_path=None, overwrite=False, show_progress=True):
        """Upload the data from the local file system to the file share this datastore points to.

        :param src_dir: the local directory to upload
        :type src_dir: str
        :param target_path: the location in file share to upload to, if None then upload to root,
            defaults to None
        :type target_path: str
        :param overwrite: overwrite existing file, defaults to False
        :type overwrite: bool, optional
        :param show_progress: show progress of upload in the console, defaults to True
        :type show_progress: bool, optional
        :return: The DataReference instance for the target path uploaded
        :rtype: DataReference
        """
        module_logger.info("Called AzureFileDatastore.upload")
        target_path = target_path or ""
        count = self._start_upload_task(
            self._get_upload_from_dir(src_dir, target_path),
            overwrite,
            lambda target_file_path: self.file_service.exists(
                self.container_name,
                os.path.split(target_file_path)[0],
                os.path.split(target_file_path)[1]),
            show_progress,
            self._file_share_upload
        )
        module_logger.info("Finished AzureFileDatastore.upload with count={0}.".format(count))
        return DataReference(datastore=self, path_on_datastore=target_path)

    def upload_files(self, files, relative_root=None, target_path=None, overwrite=False, show_progress=True):
        """Upload the data from the local file system to the file share this datastore points to.

        :param files: list of absolute path to files to upload
        :type files: List[str]
        :param relative_root: the base path from which is used to determine the path
            of the files in the file share. For example, if we upload /path/to/file.txt, and we define
            base path to be /path, when file.txt is uploaded to the file share, it will have
            the path of /to/file.txt. If target_path is also given, then it will be used as
            the prefix for the derived path from above. The base path must be a common path of
            all of the files, otherwise an exception will be thrown, defaults to None, which will find
            the common path.
        :type relative_root: str, optional
        :param target_path: location in the file share to upload the data to, defaults to None, the root
        :type target_path: str, optional
        :param overwrite: overwrites, defaults to False
        :type overwrite: bool, optional
        :param show_progress: show progress of upload in the console, defaults to True
        :type show_progress: bool, optional
        :return: The DataReference instance for the target path uploaded
        :rtype: DataReference
        """
        module_logger.info("Called AzureFileDatastore.upload_files")
        target_path = target_path or ""
        relative_root = relative_root or common_path(files)
        count = self._start_upload_task(
            self._get_upload_from_files(files, target_path, relative_root, False),
            overwrite,
            lambda target_file_path: self.file_service.exists(
                self.container_name,
                os.path.split(target_file_path)[0],
                os.path.split(target_file_path)[1]),
            show_progress,
            self._file_share_upload
        )
        module_logger.info("Finished AzureFileDatastore.upload_files with count={0}.".format(count))
        return DataReference(datastore=self, path_on_datastore=target_path)

    def _download_file(self, tq, dirpath, filename, target_path, overwrite, total, counter, show_progress):
        file_path = os.path.join(target_path, dirpath, filename)
        if not overwrite and os.path.exists(file_path):
            module_logger.warning("Path already exists. Skipping download for {}".format(file_path))
            return False

        if not os.path.exists(os.path.join(target_path, dirpath)):
            os.makedirs(os.path.join(target_path, dirpath))
        src_file_path = os.path.join(dirpath, filename)
        task = AsyncTask(
            "task_download_{}".format(src_file_path),
            lambda: self.file_service.get_file_to_path(
                share_name=self.container_name,
                directory_name=dirpath,
                file_name=filename,
                file_path=file_path),
            module_logger,
            handler=self._get_task_handler(src_file_path, counter, total, show_progress, "Download"))
        tq.add(task)
        return True

    def _file_share_upload(self, target, source):
        # file share does not automatically create directory
        dirs_to_create = []
        prev_dirpath = None
        dirpath = os.path.split(target)[0]
        while dirpath != prev_dirpath and os.path.dirname(dirpath) != dirpath:
            if not self.file_service.exists(self.container_name, dirpath):
                dirs_to_create.append(dirpath)
                prev_dirpath = dirpath
                dirpath = os.path.split(dirpath)[0]
            else:
                break

        for dirpath in dirs_to_create[::-1]:
            self.file_service.create_directory(self.container_name, dirpath)

        def upload():
            self.file_service.create_file_from_path(
                self.container_name,
                os.path.split(target)[0],
                os.path.split(target)[1],
                source)

        return upload


class AzureBlobDatastore(AbstractAzureStorageDatastore):
    """Datastore for azure blob storage."""

    def __init__(self, workspace, name, container_name, account_name, sas_token=None,
                 account_key=None, protocol=None, endpoint=None, request_session=None):
        """Initialize a new Azure Blob Datastore.

        :param workspace: the workspace this datastore belongs to.
        :type workspace: Workspace
        :param name: the name of the datastore. It can only contain alphanumeric
        characters or - or _
        :type name: str
        :param container_name: the blob container name
        :type container_name: str
        :param account_name: the storage account name
        :type account_name: str
        :param sas_token: the SAS token for accessing this container, defaults to None
        :type sas_token: str, optional
        :param account_key: the storage account key, defaults to None
        :type account_key: str, optional
        :param protocol: Protocol to use to connect to the storage account. If None, defaults to https.
        :type protocol: str, optional
        :param endpoint: The endpoint of the blob container. If None, defaults to core.windows.net.
        :type endpoint: str, optional
        :param request_session: the session object to use for http requests, defaults to None
        :type request_session: requests.Session, optional
        """
        super(AzureBlobDatastore, self).__init__(workspace, name, 'AzureBlob', container_name, account_name,
                                                 sas_token, account_key, protocol, endpoint)
        self.blob_service = BlockBlobService(
            account_name=self.account_name,
            account_key=account_key,
            sas_token=self.sas_token,
            request_session=request_session or self._get_default_request_session(),
            protocol=protocol,
            endpoint_suffix=endpoint
        )

    def download(self, target_path, prefix=None, overwrite=False, show_progress=True):
        """Download the data from the blob container to the local file system.

        :param target_path: the local directory to download the file to
        :type target_path: str
        :param prefix: path to the folder in the blob container to
            download. If set to None, will download everything in the blob defaults to None
        :type prefix: str, optional
        :param overwrite: overwrite existing file, defaults to False
        :type overwrite: bool, optional
        :param show_progress: show progress of download in the console, defaults to True
        :type show_progress: bool, optional
        :return: The number of files successfully downloaded
        :rtype: int
        """
        def download(blob, dest):
            return lambda: self.blob_service.get_blob_to_path(self.container_name, blob.name, dest)

        module_logger.info("Called AzureBlobDatastore.download")
        if not os.path.exists(target_path):
            os.makedirs(target_path)
        blobs = list(self.blob_service.list_blobs(container_name=self.container_name, prefix=prefix))
        blobs = AzureBlobDatastore._filter_conflicting_blobs(blobs)
        total = len(blobs)
        if total == 0:
            return 0
        counter = _Counter()
        with TaskQueue(__name__, module_logger, num_workers=self._num_workers) as tq:
            for blob in blobs:
                file_path = os.path.join(target_path, blob.name)
                if not overwrite and os.path.exists(file_path):
                    module_logger.warning("Path already exists. Skipping download for {}".format(file_path))
                    total -= 1
                    continue

                dirname = os.path.dirname(file_path)
                if not os.path.exists(dirname):
                    os.makedirs(dirname)

                task = AsyncTask(
                    "task_download_{}".format(blob.name),
                    download(blob, file_path),
                    module_logger,
                    handler=self._get_task_handler(blob.name, counter, total, show_progress, "Download"))
                tq.add(task)

        module_logger.info("Finished AzureBlobDatastore.download. Downloaded {} files.".format(counter.count()))
        return counter.count()

    def upload(self, src_dir, target_path=None, overwrite=False, show_progress=True):
        """Upload the data from the local file system to blob container this data store points to.

        :param src_dir: the local directory to upload
        :type src_dir: str
        :param target_path: the location in blob container to upload to, if None then upload to
            root, defaults to None
        :type target_path: str
        :param overwrite: overwrite existing file, defaults to False
        :type overwrite: bool, optional
        :param show_progress: show progress of upload in the console, defaults to True
        :type show_progress: bool, optional
        :return: The DataReference instance for the target path uploaded
        :rtype: DataReference
        """
        module_logger.info("Called AzureBlobDatastore.upload")
        target_path = target_path or ""
        count = self._start_upload_task(
            self._get_upload_from_dir(src_dir, target_path),
            overwrite,
            lambda target_file_path: self.blob_service.exists(self.container_name, target_file_path),
            show_progress,
            lambda target, source: lambda: self.blob_service.create_blob_from_path(self.container_name, target, source)
        )
        module_logger.info("Finished AzureBlobDatastore.upload with count={0}.".format(count))
        return DataReference(datastore=self, path_on_datastore=target_path)

    def upload_files(self, files, relative_root=None, target_path=None, overwrite=False, show_progress=True):
        """Upload the data from the local file system to the blob container this datastore points to.

        :param files: list of absolute path to files to upload
        :type files: List[str]
        :param relative_root: the root from which is used to determine the path
            of the files in the blob. For example, if we upload /path/to/file.txt, and we define
            base path to be /path, when file.txt is uploaded to the blob storage, it will have
            the path of /to/file.txt. If target_path is also given, then it will be used as
            the prefix for the derived path from above. The base path must be a common path of
            all of the files, otherwise an exception will be thrown, defaults to None, which will find
            the common path.
        :type relative_root: str, optional
        :param target_path: location in the blob container to upload the data to, defaults to None, the root
        :type target_path: str, optional
        :param overwrite: overwrites, defaults to False
        :type overwrite: bool, optional
        :param show_progress: show progress of upload in the console, defaults to True
        :type show_progress: bool, optional
        :return: The DataReference instance for the target path uploaded
        :rtype: DataReference
        """
        module_logger.info("Called AzureBlobDatastore.upload_files")
        target_path = target_path or ""
        relative_root = relative_root or common_path(files)
        count = self._start_upload_task(
            self._get_upload_from_files(files, target_path, relative_root, False),
            overwrite,
            lambda target_file_path: self.blob_service.exists(self.container_name, target_file_path),
            show_progress,
            lambda target, source: lambda: self.blob_service.create_blob_from_path(self.container_name, target, source)
        )
        module_logger.info("Finished AzureBlobDatastore.upload with count={0}.".format(count))
        return DataReference(datastore=self, path_on_datastore=target_path)

    @staticmethod
    def _filter_conflicting_blobs(blobs):
        def conflict_path(segment, throw):
            if throw:
                raise RuntimeError('Found non empty file {} that has the same name as a folder'.format(segment))
            else:
                module_logger.info(
                    'Found empty file {} that has the same name as a folder, skipping it.'.format(segment))

        trie_dict = {}

        for blob in blobs:
            segments = list(accumulate(re.split('/|\\\\', blob.name), lambda acc, cur: '{}/{}'.format(acc, cur)))

            for segment in segments[:-1]:
                if segment in trie_dict:
                    conflict_path(segment, throw=trie_dict[segment] == FILE)
                trie_dict[segment] = FOLDER

            if segments[-1] in trie_dict:
                conflict_path(segments[-1], throw=blob.properties.content_length != 0)
            else:
                trie_dict[segments[-1]] = EMPTY_FILE if blob.properties.content_length == 0 else FILE

        return list(filter(lambda blob: trie_dict[blob.name] != FOLDER, blobs))


class _Counter(object):
    def __init__(self):
        self._count = 0

    def increment(self, by=1):
        self._count += by

    def count(self):
        return self._count
