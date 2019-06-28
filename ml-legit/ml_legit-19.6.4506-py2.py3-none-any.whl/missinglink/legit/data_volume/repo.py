# -*- coding: utf-8 -*-
import os

from missinglink.core import ApiCaller

from ..db_index import BackendMLIndex
from ..metadata_db import BackendMetadataDB
from ..db import BackendConnection
from ..ref_container import BackendRefContainer
from ..path_utils import get_moniker, remove_moniker
from ..dulwich import objects
from ..dulwich.repo import Repo
from ..data_volume_config import DataVolumeConfig


class MLIgnoreFilterManager(object):
    # noinspection SpellCheckingInspection,PyMethodMayBeStatic
    def is_ignored(self, relpath):
        return False


DEFAULT_ENCODING = 'utf-8'


def make_bytes(c):
    if not isinstance(c, bytes):
        return c.encode(DEFAULT_ENCODING)

    return c


class MlRepo(Repo):
    def __init__(self, config, repo_config_root, data_volume_config, read_only=False, **kwargs):
        self.__data_volume_config = data_volume_config
        self.__in_transactions = False
        self.__config = config
        self.__connections = {}
        self.__read_only = read_only
        self.__metadata = None
        self.__session = kwargs.pop('session', None)
        self.__extra_repo_params = kwargs
        self.__multi_process_control = None

        super(MlRepo, self).__init__(repo_config_root)

    @property
    def _config(self):
        return self.__config

    def close(self):
        for connection in self.__connections.values():
            connection.close()

        super(MlRepo, self).close()

    # noinspection PyUnusedLocal
    def __create_connection(self, name, **kwargs):
        kwargs.update(self.data_volume_config.db_config)
        kwargs['read_only'] = self.__read_only
        kwargs['session'] = self.__session
        kwargs['data_volume_config'] = self.data_volume_config

        kwargs.update(self.__extra_repo_params)

        connection_class = BackendConnection

        return connection_class(**kwargs)

    def start_transactions(self):
        for connection in self.__connections.values():
            connection.start_transactions()

        self.__in_transactions = True

    def end_transactions(self):
        for connection in self.__connections.values():
            connection.end_transactions()

        self.__in_transactions = False

    def rollback_transactions(self):
        for connection in self.__connections.values():
            connection.rollback_transactions()

        self.__in_transactions = False

    def _connection_by_name(self, name, **kwargs):
        if name not in self.__connections:
            connection = self.__create_connection(name, **kwargs)

            if self.__in_transactions:
                connection.start_transactions()

            self.__connections[name] = connection

        return self.__connections[name]

    def __create_metadata(self):
        return BackendMetadataDB(self._connection_by_name('metadata'), self._config, self.__session, **self.__extra_repo_params)

    @property
    def metadata(self):
        if self.__metadata is None:
            self.__metadata = self.__create_metadata()

        return self.__metadata

    @property
    def data_volume_config(self):
        return self.__data_volume_config

    def open_index(self):
        index = BackendMLIndex(self._connection_by_name('main'), self._config, self.__session)
        index.set_multi_process_control(self.__multi_process_control)

        return index

    def set_multi_process_control(self, multi_process_control):
        self.__multi_process_control = multi_process_control

    @property
    def direct_bucket_upload(self):
        return self.data_volume_config.bucket_name is not None

    def create_object_store(self):
        from ..object_store import NullObjectStore, BackendGCSObjectStore, GCSObjectStore, DiskObjectStore

        bucket_name = self.data_volume_config.bucket_name

        disk_type = get_moniker(bucket_name) == 'file'

        ml_secure_bucket = bucket_name is None and self.data_volume_config.embedded

        if disk_type:
            bucket_name = remove_moniker(bucket_name)
            store = DiskObjectStore(self.data_volume_config.volume_id, bucket_name,
                                    self.data_volume_config.embedded, self.data_volume_config.storage_volume_id)
        elif self.data_volume_config.object_store_type in ['null']:
            store = NullObjectStore()
        elif ml_secure_bucket:
            store = BackendGCSObjectStore(
                self._connection_by_name('backend'),
                self._config, self.__session)
        else:
            store = GCSObjectStore(self._connection_by_name('gcs'), bucket_name)

        store.set_multi_process_control(self.__multi_process_control)

        return store

    def get_config_stack(self):
        return DataVolumeConfig(self.repo_root)

    def get_ignore_filter_manager(self):
        return MLIgnoreFilterManager()

    def _get_user_identity(self):
        import jwt

        data = jwt.decode(self._config.id_token, verify=False) if self.__config.id_token else {}

        return '{name} <{email}>'.format(**data).encode('utf8')

    def has_change_set(self, ref='HEAD'):
        ref = ref.encode('ascii')

        try:
            ref_sha = self.refs[ref]

            head_tree_sha = self[ref_sha].tree
        except KeyError:  # in case of empty tree
            head_tree_sha = objects.Tree().id

        index = self.open_index()

        commit_id = index.get_commit_id()

        return None if commit_id == head_tree_sha else commit_id

    def remote_commit(self, message, isolation_token):
        msg = {
            'message': message,
            'isolation_token': isolation_token,
        }

        url = "data_volumes/{volume_id}/commit".format(volume_id=self.data_volume_config.volume_id)

        return ApiCaller.call(self._config, self.__session, 'post', url, msg, is_async=True)

    def commit(self, message, isolation_token=None):
        return self.remote_commit(message, isolation_token)
