# -*- coding: utf-8 -*-
import os

from missinglink_kernel.callback.auth_params import AuthParams
from missinglink_kernel.data_management import MLDataGenerator


class MLDataGeneratorFactory(object):
    def __init__(self, query, data_callback, volume_id=None, cache_directory=None, batch_size=32, use_threads=None,
                 processes=-1, shuffle=True, cache_limit=None, drop_last=True, disable_caching=False, is_infinite=True):

        self._query = query
        self._data_callback = data_callback
        self._volume_id = volume_id
        self._cache_directory = cache_directory
        self._batch_size = batch_size
        self._use_threads = use_threads
        self._processes = processes
        self._shuffle = shuffle
        self._cache_limit = cache_limit
        self._drop_last = drop_last
        self._is_infinite = is_infinite
        self.__config_prefix = None
        self._disable_caching = disable_caching

    def set_config_prefix(self, config_prefix):
        self.__config_prefix = config_prefix

    def create(self):
        if self._volume_id is None:
            self._volume_id = AuthParams(config_prefix=self.__config_prefix).select_volume_id()

        cache_limit = self._cache_limit or os.environ.get('ML_CACHE_LIMIT')

        gen = MLDataGenerator(self._volume_id, self._query, self._data_callback, self._cache_directory,
                              self._batch_size, self._use_threads, self._processes, self._shuffle, cache_limit,
                              self._drop_last, self._disable_caching, is_infinite=self._is_infinite)

        gen.set_config_prefix(self.__config_prefix)
        return gen
