# -*- coding: utf-8 -*-
import os
import errno
from contextlib import closing

import sys

import six
from missinglink.core import ApiCaller
from missinglink.core.eprint import eprint

from ..dulwich.errors import NotGitRepository
from ..data_volume_config import DataVolumeConfig, SHARED_STORAGE_VOLUME_FIELD_NAME
from .repo import MlRepo


def default_data_volume_path(volume_id):
    return os.path.join(os.path.expanduser('~'), '.MissingLinkAI', 'data_volumes', str(volume_id))


def update_config_file(volume_id, params):
    path = default_data_volume_path(volume_id)

    try:
        os.makedirs(path)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise

    config = DataVolumeConfig(path)

    config.update_and_save(params)

    return config


def create_data_volume2(volume_id, linked, display_name, description, **kwargs):
    params = {
        'general': {
            'id': volume_id,
            'embedded': not linked,
            'display_name': display_name,
            'description': description
        }
    }

    params.update(**kwargs)
    return update_config_file(volume_id, params)


def create_data_volume(volume_id, data_path, linked, display_name, description, **kwargs):
    return create_data_volume2(volume_id, linked, display_name, description, **kwargs)


def get_data_volume_details(ctx, volume_id):
    from missinglink.core.api import default_api_retry

    endpoint = 'data_volumes/{volume_id}'.format(volume_id=volume_id)
    retry = default_api_retry()
    return ApiCaller.call(ctx.obj, ctx.obj.session, 'get', endpoint, retry=retry)


def map_volume(ctx, volume_id):
    result = get_data_volume_details(ctx, volume_id)

    bucket_name = result.get('bucket_name')
    storage_volume_id = result.get(SHARED_STORAGE_VOLUME_FIELD_NAME)

    params = {}
    object_store = __get_object_store(bucket_name, storage_volume_id)

    if object_store:
        params['object_store'] = object_store

    config = create_data_volume2(
        result['id'],
        not result.get('embedded', True),
        result.get('display_name'),
        result.get('description'),
        **params)

    if bucket_name is None and storage_volume_id is None:
        config.remove_option('object_store', 'bucket_name')
        config.save()

    return config


def __get_object_store(bucket_name, storage_volume_id):
    object_store = {}
    if bucket_name is not None:
        object_store['bucket_name'] = bucket_name
    if storage_volume_id is not None:
        object_store[SHARED_STORAGE_VOLUME_FIELD_NAME] = storage_volume_id
    return object_store


def __data_volume_config_from_path(config, repo_root):
    general_config_path = config.config_file_abs_path if config is not None else None

    return DataVolumeConfig(repo_root, general_config_path=general_config_path)


def __repo_dynamic_map_if_needed(ctx, config, volume_id, data_volume_config, **kwargs):
    session = ctx.obj.session
    repo_config_root = default_data_volume_path(volume_id)

    if data_volume_config is None:
        data_volume_config = map_volume(ctx, volume_id)

    return MlRepo(config, repo_config_root, data_volume_config, session=session, **kwargs)


def repo_dynamic(ctx, data_volume_config_or_volume_id, **kwargs):
    valid_volume_id_types = six.string_types + six.integer_types

    config = ctx.obj.config

    data_volume_config = data_volume_config_or_volume_id if not isinstance(data_volume_config_or_volume_id,
                                                                           valid_volume_id_types) else None
    volume_id = data_volume_config_or_volume_id if isinstance(data_volume_config_or_volume_id,
                                                              valid_volume_id_types) else data_volume_config.volume_id

    return __repo_dynamic_map_if_needed(ctx, config, volume_id, data_volume_config, **kwargs)


def with_repo_dynamic(ctx, data_volume_config_or_volume_id, _remove_me=None, **kwargs):
    return closing(repo_dynamic(ctx, data_volume_config_or_volume_id, **kwargs))


def create_repo(config, repo_config_root, data_volume_config=None, read_only=False, require_map=True, **kwargs):
    if data_volume_config is None:
        data_volume_config = __data_volume_config_from_path(config, repo_config_root)

    return MlRepo(config, repo_config_root, data_volume_config, read_only=read_only, require_path=require_map, **kwargs)


def with_repo(config, volume_id, read_only=False, require_map=True, **kwargs):
    """

    :param config:
    :param int volume_id:
    :param read_only:
    :param require_map:
    :return: the repo
    :rtype: MlRepo
    """
    repo_root = default_data_volume_path(volume_id)

    try:
        return closing(create_repo(config, repo_root, read_only=read_only, require_map=require_map, **kwargs))
    except NotGitRepository:
        msg = 'Data volume {0} was not mapped on this machine, you should call "ml data map {0} --data-path [root path of data]" in order to work with the volume locally'.format(
            volume_id)
        eprint(msg)
        sys.exit(1)
