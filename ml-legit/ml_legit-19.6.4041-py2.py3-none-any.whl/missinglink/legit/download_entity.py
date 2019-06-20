# -*- coding: utf-8 -*-
import threading
import json
import requests
import importlib
from missinglink.core.config import Config
import logging

from missinglink.core.context import create_empty_context, build_context_from_config

logger = logging.getLogger(__name__)


class DownloadEntity(object):
    local_data = threading.local()

    @classmethod
    def __object_from_data(cls, data, creator):
        data_key = json.dumps(data, sort_keys=True)

        data_key += creator.__name__

        try:
            return cls.local_data.__data_sync_objects[data_key]
        except KeyError:
            cls.local_data.__data_sync_objects[data_key] = creator(data)
        except AttributeError:
            cls.local_data.__data_sync_objects = {data_key: creator(data)}

        return cls.local_data.__data_sync_objects[data_key]

    @classmethod
    def _import_storage(cls, storage_class):
        module_name, class_name = storage_class.rsplit('.', 1)
        m = importlib.import_module(module_name)
        return getattr(m, class_name)

    @classmethod
    def _get_storage(cls, current_data):
        current_data_clone = dict(current_data)
        storage_class = current_data_clone.pop('class')
        return cls._import_storage(storage_class).init_from_config(**current_data_clone)

    @classmethod
    def _get_config(cls, current_data):
        return Config(**current_data)

    @classmethod
    def _get_item_data(cls, repo, storage, metadata):
        if storage.has_item(metadata):
            logger.debug('already exists %s', metadata)
            return

        _, current_data = repo.object_store.get_raw(metadata)
        return current_data

    @classmethod
    def download(cls, config, storage, data_volume_config, metadata, headers):
        from .data_volume import with_repo_dynamic

        session = requests.session()
        session.headers.update(headers)

        ctx = create_empty_context()
        build_context_from_config(ctx, session, config)

        with with_repo_dynamic(ctx, data_volume_config, read_only=True) as repo:
            data = cls._get_item_data(repo, storage, metadata)
            if data is not None:
                storage.add_item(metadata, data)
