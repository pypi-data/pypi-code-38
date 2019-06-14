# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Cache store implementation that utilizes Azure files for backend storage."""
import logging
import pickle
import os

from io import BytesIO

from azureml import _async
from automl.client.core.common.activity_logger import DummyActivityLogger
from automl.client.core.common.cache_store import CacheStore, CacheException, _create_temp_dir, \
    DEFAULT_TASK_TIMEOUT_SECONDS, _try_remove_dir
from automl.client.core.common.pickler import DefaultPickler, DEFAULT_PICKLE_PROTOCOL_VERSION
from azureml._vendor.azure_storage.file import FileService, models, ContentSettings


class AzureFileCacheStore(CacheStore):
    """Cache store based on azure file system."""

    def __init__(self,
                 path,
                 account_name=None,
                 account_key=None,
                 pickler=None,
                 task_timeout=DEFAULT_TASK_TIMEOUT_SECONDS,
                 module_logger=logging.getLogger(__name__),
                 temp_location=None,
                 file_service=None):
        """
        Cache based on azure file system.

        :param path: path of the store
        :param account_name: account name
        :param account_key: account key
        :param pickler: pickler, default is cPickler
        :param task_timeout: task timeout
        :param module_logger: logger
        :param file_share: file share instance if provided
        """
        super(AzureFileCacheStore, self).__init__(module_logger=module_logger)

        if pickler is None:
            pickler = DefaultPickler()

        self.task_timeout = task_timeout
        self.pickler = pickler
        self.account_name = account_name
        self.account_key = account_key
        self.cache_items = dict()
        self._num_workers = os.cpu_count()
        self.module_logger = module_logger if module_logger is not None else logging.getLogger()
        self.temp_location = _create_temp_dir(temp_location)
        self.activity_prefix = "_AzureFileCacheStore"
        self.file_service = file_service if file_service is not None else \
            FileService(account_name=account_name, account_key=account_key)
        self.path = path.lower().replace('_', '-')
        self.file_service.create_share(self.path)

    def __getstate__(self):
        return {'task_timeout': self.task_timeout,
                'pickler': self.pickler,
                'account_name': self.account_name,
                'account_key': self.account_key,
                'cache_items': self.cache_items,
                'num_workers': self._num_workers,
                'module_logger': None,
                'temp_location': self.temp_location,
                'activity_prefix': self.activity_prefix,
                'path': self.path,
                'max_retries': self.max_retries}

    def __setstate__(self, state):
        self.path = state['path']
        self.pickler = state['pickler']
        self.account_name = state['account_name']
        self.account_key = state['account_key']
        self.cache_items = state['cache_items']
        self._num_workers = state['num_workers']
        self.module_logger = logging.getLogger()
        self.temp_location = _create_temp_dir()
        self.activity_prefix = state['activity_prefix']
        self.task_timeout = state['task_timeout']
        self.max_retries = state['max_retries']
        self.activity_logger = DummyActivityLogger()
        self.file_service = FileService(account_name=self.account_name, account_key=self.account_key)

    def add(self, keys, values):
        """Add to azure file store.

        :param keys: keys
        :param values: values
        """
        self.module_logger.info('Adding {} to Azure file store cache'.format(keys))
        with self.log_activity():
            try:
                for k, v in zip(keys, values):
                    self._function_with_retry(self._pickle_and_upload,
                                              self.max_retries, self.module_logger, k, v)
            except Exception as e:
                raise CacheException("Cache failure {}".format(e))

    def add_or_get(self, key, value):
        """
        Add or gets from azure file store.

        :param key:
        :param value:
        :return: unpickled value
        """
        val = self.cache_items.get(key, None)
        if val is None:
            self.add([key], [value])
            return {key: value}

        return self.get([key], None)

    def get(self, keys, default=None):
        """
        Get from azure file store & unpickles.

        :param default: default value
        :param keys: store key
        :return: unpickled object
        """
        with self.log_activity():
            ret = dict()
            for key in keys:
                try:
                    ret[key] = self._function_with_retry(self._download_and_unpickle, self.max_retries,
                                                         self.module_logger, key)[key]
                except Exception as e:
                    self.module_logger.warning('Failed to retrieve key "{}" from cache: {}'.format(key, e))
                    ret[key] = default

        return ret

    def set(self, key, value):
        """
        Set values to store.

        :param key: key
        :param value: value
        """
        self.add([key], [value])

    def remove(self, key):
        """
        Remove from store.

        :param key: store key
        """
        with self.log_activity():
            self._remove(self.path, [key])

    def remove_all(self):
        """Remove all the file from cache."""
        with self.log_activity():
            self._remove(self.path, self.cache_items.keys())

    def load(self):
        """Load from azure file store."""
        with self.log_activity():
            self._function_with_retry(self._get_azure_file_lists,
                                      self.max_retries, self.module_logger, self.path)

    def unload(self):
        """Unload the cache."""
        try:
            self.file_service.delete_share(share_name=self.path)
        except Exception as e:
            self.module_logger.warning('Failed to delete share "{}", {}'.format(self.path, e))

        self.cache_items.clear()
        _try_remove_dir(self.temp_location)

    def _remove(self, path, files):
        worker_pool = _async.WorkerPool(max_workers=self._num_workers)
        tasks = []

        with _async.TaskQueue(worker_pool=worker_pool, _ident=__name__,
                              flush_timeout_seconds=self.task_timeout,
                              _parent_logger=self.module_logger) as tq:
            for file in files:
                tasks.append(tq.add(self._function_with_retry,
                                    self._remove_from_azure_file_store,
                                    self.max_retries,
                                    self.module_logger,
                                    path,
                                    file))

        for task in tasks:
            task.wait()
        worker_pool.shutdown()

    def _remove_from_azure_file_store(self, path, key):
        self.file_service.delete_file(path, directory_name=None, file_name=key)
        self.cache_items.pop(key)

    def _get_azure_file_lists(self, path):
        """
        Get list of files available from azure file store. similar to dir.

        :param path: path
        """
        self.module_logger.debug('Getting list of files in "{}" in Azure file store'.format(path))
        for dir_or_file in self.file_service.list_directories_and_files(share_name=path):
            if isinstance(dir_or_file, models.File):
                self.cache_items[dir_or_file.name] = dir_or_file.name

    def _download_file(self, file):
        """
        Download from azure file store.

        :param file:
        """
        self.module_logger.debug('Downloading "{}" from cache'.format(file))
        temp_path = os.path.join(self.temp_location, file)
        try:
            self.file_service.get_file_to_path(share_name=self.path,
                                               directory_name=None,
                                               file_name=file,
                                               file_path=temp_path)
            self.cache_items[file] = temp_path
        except Exception:
            # get_file_to_path created temp file if file doesnt exists
            self._try_remove_temp_file(temp_path)
            raise

        return {file: temp_path}

    def _upload(self, file, obj):
        self.module_logger.debug('Uploading "{}" to cache'.format(file))
        temp_path = os.path.join(self.temp_location, file)
        try:
            self.pickler.dump(obj, temp_path)
            self.file_service.create_file_from_path(share_name=self.path,
                                                    file_name=file,
                                                    directory_name=None,
                                                    content_settings=ContentSettings('application/x-binary'),
                                                    local_file_path=temp_path)
            self.cache_items[file] = file
        finally:
            self._try_remove_temp_file(temp_path)

    def _try_remove_temp_file(self, path):
        self.module_logger.debug('Removing temp file "{}"'.format(path))
        try:
            os.remove(path)
        except OSError as e:
            self.module_logger.warning("failed to remove temp file {}".format(e))

    def _pickle_and_upload(self, file_name, obj):
        self.module_logger.debug('Pickling and uploading "{}" to cache'.format(file_name))
        with BytesIO() as bio:
            pickle.dump(obj, bio, protocol=DEFAULT_PICKLE_PROTOCOL_VERSION)
            count = bio.tell()
            bio.seek(0)
            self.file_service.create_file_from_stream(share_name=self.path,
                                                      file_name=file_name,
                                                      directory_name=None,
                                                      content_settings=ContentSettings('application/x-binary'),
                                                      stream=bio,
                                                      count=count)
            self.cache_items[file_name] = file_name

    def _download_and_unpickle(self, file_name):
        self.module_logger.debug('Downloading and unpickling "{}" from cache'.format(file_name))
        with BytesIO() as bio:
            self.file_service.get_file_to_stream(share_name=self.path,
                                                 directory_name=None,
                                                 file_name=file_name,
                                                 stream=bio)
            bio.seek(0)
            self.cache_items[file_name] = file_name
            return {file_name: pickle.load(bio)}
