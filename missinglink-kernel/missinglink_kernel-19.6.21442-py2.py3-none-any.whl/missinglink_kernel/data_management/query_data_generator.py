# -*- coding: utf-8 -*-
import multiprocessing
import random
from functools import partial
import logging
import threading
from collections import OrderedDict
import six
from missinglink_kernel.data_management.http_session import create_http_session
from missinglink.core.context import build_context
from missinglink.core.config import default_missing_link_cache_folder
from missinglink.legit.data_sync import DataSync
from missinglink.legit.data_volume import with_repo_dynamic, repo_dynamic
import numpy as np
import os

logger = logging.getLogger('missinglink')


class QueryDataGeneratorFactory(object):
    def __init__(self, processes, use_threads, cache_folder, cache_limit, data_callback, volume_id, batch_size, seed, drop_last, disable_caching=False,
                 is_infinite=True):
        self.data_callback = data_callback
        self.volume_id = volume_id
        self.processes = processes
        self.use_threads = use_threads
        self.batch_size = batch_size
        self._cache_folder = cache_folder
        self._cache_limit = cache_limit
        self.seed = seed
        self.__config_prefix = None
        self.__disable_caching = disable_caching
        self.drop_last = drop_last
        self.is_infinite = is_infinite

    def set_config_prefix(self, config_prefix):
        self.__config_prefix = config_prefix

    @property
    def cache_folder(self):
        return self._cache_folder

    @property
    def cache_limit(self):
        return self._cache_limit

    def create(self, query, shuffle):
        gen = QueryDataGenerator(self, query, shuffle, disable_caching=self.__disable_caching)
        gen.set_config_prefix(self.__config_prefix)

        return gen


class MetadataIndex(object):
    def __init__(self, ctx, volume_id, query, cache_folder, batch_size):
        self._full_index = None
        self._downloaded_items_index = -1
        self._downloaded_items_index_batch_bound = -1
        self.__is_grouped = None
        self.__batch_size = batch_size
        self.download_all(ctx, volume_id, query, cache_folder)

    @property
    def total_items(self):
        return len(self._full_index or [])

    def __get_item(self, index):
        if index >= self._downloaded_items_index_batch_bound:
            raise ValueError()

        if index >= self._downloaded_items_index:
            return None

        return self._full_index[index]

    @property
    def is_grouped(self):
        return self.__is_grouped

    def get_items_flat(self, indexes):
        for i in indexes:
            items = self.__get_item(i)

            if self.is_grouped:
                for item in (items or []):
                    yield item, i

                continue

            yield items, i

    @classmethod
    def _add_results_using_datapoint(cls, group_key):
        def add_results(data_iter):
            full_index = OrderedDict()

            for normalized_item in cls.__stable_in_line_sort(data_iter.fetch_all()):
                group_value = normalized_item.get(group_key)

                if group_value is None:
                    continue

                full_index.setdefault(group_value, []).append(normalized_item)

            return list(full_index.values())

        return add_results

    @classmethod
    def __stable_in_line_sort(cls, data_iter):
        return sorted(data_iter, key=lambda i: i['@id'])

    @classmethod
    def _add_results_individual_results(cls, data_iter):
        full_index = [None] * data_iter.total_data_points

        downloaded_items_index = 0

        for normalized_item in cls.__stable_in_line_sort(data_iter.fetch_all()):
            full_index[downloaded_items_index] = normalized_item
            downloaded_items_index += 1

        if len(full_index) > 0 and len(full_index) > downloaded_items_index:
            full_index = full_index[:downloaded_items_index]

        return full_index

    @classmethod
    def _get_datapoint_by_key_if_present(cls, query):
        from missinglink.legit.scam import QueryParser, visit_query, DatapointVisitor

        tree = QueryParser().parse_query(query)

        group_visitor = visit_query(DatapointVisitor, tree)

        return group_visitor.datapoint

    @classmethod
    def _get_repo(cls, ctx, volume_id, **kwargs):
        return with_repo_dynamic(ctx, volume_id, **kwargs)

    def _get_data_iter(self, ctx, volume_id, query, cache_folder):
        with self._get_repo(ctx, volume_id, cache_folder=cache_folder) as repo:
            data_sync = DataSync(ctx, repo, no_progressbar=True)

            # batch_size==-1 means async and all results
            return data_sync.create_download_iter(query, batch_size=-1, silent=True)

    def download_all(self, ctx, volume_id, query, cache_folder):
        logger.debug('download metadata items started')

        datapoint_key = self._get_datapoint_by_key_if_present(query)
        self.__is_grouped = datapoint_key is not None
        add_results = self._add_results_using_datapoint(datapoint_key) if self.is_grouped else self._add_results_individual_results

        data_iter = self._get_data_iter(ctx, volume_id, query, cache_folder)

        self._full_index = add_results(data_iter)
        self._downloaded_items_index = len(self._full_index)
        self._downloaded_items_index_batch_bound = int(np.ceil(self._downloaded_items_index / float(self.__batch_size)) * self.__batch_size)

        logger.debug('download metadata items finished')


class _QueryDataGenerator(object):
    pass


GENERATORS_QUERY_WORKERS = {}


class QueryDataGenerator(_QueryDataGenerator):
    _ctx_store = threading.local()

    def __init__(self, creator, query, shuffle, disable_caching=None):
        self.__repo = None
        self.__metadata_index = None
        self.__storage = None
        self.__multi_process_control = None
        self.__prefetching_multi_process_control = None
        self.__iter = None
        self.__iterator_shuffle = None
        self.__query = None
        self.__shuffle = shuffle
        self.__query = query
        self.__config_prefix = None
        self.__seed = creator.seed
        self.__prefetching_processes = 1
        self.__prefetching_multiprocess = False

        if disable_caching is None:
            self.__disable_caching = os.environ.get('ML_DISABLE_CACHE') == '1'
        else:
            self.__disable_caching = disable_caching

        self.__prefetching_processes = 1

        self.__drop_last = creator.drop_last
        self.__processes = creator.processes
        self.__use_threads = creator.use_threads
        self.__volume_id = creator.volume_id
        self.__cache_folder = creator.cache_folder
        self.__batch_size = creator.batch_size
        self.__cache_limit = creator.cache_limit
        self.__data_callback = creator.data_callback
        self.__is_infinite = creator.is_infinite

        self.__worker_id = random.random()
        self.__download_futures = {}
        self.__download_futures_lock = multiprocessing.RLock()

    def close(self):
        for item in [self.__multi_process_control, self.__prefetching_multi_process_control, self.__storage]:
            if item is None:
                continue

            item.close()

    def set_config_prefix(self, config_prefix):
        self.__config_prefix = config_prefix

    def set_prefetching(self, prefetching_processes, prefetching_multiprocess):
        self.__prefetching_processes = prefetching_processes
        self.__prefetching_multiprocess = prefetching_multiprocess

    def __getstate__(self):
        state = self.__dict__.copy()

        def del_inner_state_prop(name):
            del state['_{}{}'.format(QueryDataGenerator.__name__, name)]

        del_inner_state_prop('__multi_process_control')
        del_inner_state_prop('__prefetching_multi_process_control')
        del_inner_state_prop('__download_futures')
        del_inner_state_prop('__download_futures_lock')
        del_inner_state_prop('__iter')

        return state

    def __setstate__(self, state):
        self.__dict__.update(state)
        # Add baz back since it doesn't exist in the pickle
        self.__multi_process_control = None
        self.__prefetching_multi_process_control = None
        self.__iter = None
        self.__prefetching_multi_process_control = None
        self.__download_futures = {}
        self.__download_futures_lock = multiprocessing.RLock()

    def reset(self):
        self.__iter = None

    def __iter__(self):
        from .iterator import _InfiniteIterator, _FiniteIterator

        return _InfiniteIterator(self) if self.__is_infinite else _FiniteIterator(self)

    @property
    def _iterator_shuffle(self):
        from .iterator import _IteratorShuffle

        if self.__iterator_shuffle is None:
            self.__iterator_shuffle = _IteratorShuffle(self.__shuffle, len(self), self.__seed)

        return self.__iterator_shuffle

    def __next__(self):
        if self.__iter is None:
            self.__iter = iter(self)

        return next(self.__iter)

    next = __next__
    iter = __iter__

    def on_epoch_end(self):
        self._iterator_shuffle.reset()

    def as_keras_sequence(self):
        import keras

        QueryDataGenerator.__bases__ = (_QueryDataGenerator, keras.utils.Sequence, )

        return self

    def ___inner_get_multi_process_control(self, member_name, prefix_name, processes, use_threads):
        from missinglink.core.multi_process_control import get_multi_process_control

        inner_member_name = '_{}{}'.format(QueryDataGenerator.__name__, member_name)
        cache_name = '{}{}'.format(prefix_name, self.__worker_id)

        multi_process_control = getattr(self, inner_member_name)

        if multi_process_control is None:
            multi_process_control = GENERATORS_QUERY_WORKERS.get(cache_name)

            if multi_process_control is None:
                multi_process_control = get_multi_process_control(processes, use_threads)

                GENERATORS_QUERY_WORKERS[cache_name] = multi_process_control

            setattr(self, inner_member_name, multi_process_control)

        return multi_process_control

    def _get_multi_process_control(self):
        return self.___inner_get_multi_process_control('__multi_process_control',
                                                       'multi',
                                                       self.__processes,
                                                       self.__use_threads)

    def _get_prefetching_multi_process_control(self):
        return self.___inner_get_multi_process_control('__prefetching_multi_process_control',
                                                       'prefetching',
                                                       self.__prefetching_processes or 1,
                                                       not self.__prefetching_multiprocess)

    def __create_cache_storage(self):
        from .cache_storage import CacheStorage

        cache_folder = self.__cache_folder or os.environ.get('ML_CACHE_FOLDER', default_missing_link_cache_folder())
        self.__cache_folder = cache_folder

        return CacheStorage(cache_folder, self.__cache_limit)

    def _get_storage(self):
        if self.__storage is None:
            self.__storage = self.__create_cache_storage()

        return self.__storage

    def _get_metadata_index(self):
        if self.__metadata_index is None:
            self.__metadata_index = self._create_metadata_index()

        return self.__metadata_index

    def __len__(self):
        round_method = np.floor if self.__drop_last else np.ceil
        return int(round_method(self._get_metadata_index().total_items / float(self.__batch_size)))

    def __wait_for_idx(self, batch):
        actual_idx = self._iterator_shuffle[batch]

        with self.__download_futures_lock:
            val = self.__download_futures.get(actual_idx)

        if val is None:
            val = self._schedule_download_batch(batch)

        if val is not True:
            val.wait()
            val.get()

        with self.__download_futures_lock:
            self.__download_futures[actual_idx] = True

    def __getitem__(self, batch):
        self.__wait_for_idx(batch)

        actual_idx = self._iterator_shuffle[batch]

        start_idx = actual_idx * self.__batch_size
        end_idx = start_idx + self.__batch_size

        return self._get_batches_of_transformed_samples(list(range(start_idx, end_idx)))

    @property
    def _ctx(self):
        ctx = getattr(self._ctx_store, '__ctx', None)

        if ctx is None or getattr(ctx, 'pid', None) != os.getpid():
            ctx = self.build_context(self.__config_prefix)
            ctx.pid = os.getpid()
            setattr(self._ctx_store, '__ctx', ctx)

        return ctx

    def _create_metadata_index(self):
        return MetadataIndex(
            self._ctx,
            self.__volume_id,
            self.__query,
            self.__cache_folder,
            self.__batch_size)

    def _get_batches_of_transformed_samples(self, index_array):
        results = self._download_data(index_array)

        batch_data = None

        def create_batch_array(obj):
            if isinstance(obj, six.integer_types + (float, )):
                return np.zeros(len(index_array), dtype=type(obj))

            # noinspection PyUnresolvedReferences
            if hasattr(obj, 'shape'):
                if 'torch' in str(obj.dtype):
                    import torch
                    return torch.zeros((len(index_array),) + obj.shape, dtype=obj.dtype)
                else:
                    return np.zeros((len(index_array), ) + obj.shape, dtype=obj.dtype)

            return [0] * len(index_array)

        i = 0
        for file_name, metadata in results:
            if len(file_name) == 0:
                continue

            vals = self.__data_callback(file_name, metadata)

            if len(results) == 1:
                return vals

            if vals is None or vals[0] is None:
                continue

            if batch_data is None:
                batch_data = [create_batch_array(vals[j]) for j in range(len(vals))]

            for j in range(len(vals)):
                batch_data[j][i] = vals[j]

            i += 1

        return None if batch_data is None else tuple(batch_data)

    def _get_schedule_download_batch_future(self, batch, _=None):
        if batch >= len(self):
            return

        actual_idx = self._iterator_shuffle[batch]

        start_idx = actual_idx * self.__batch_size
        end_idx = start_idx + self.__batch_size
        index_array = list(range(start_idx, end_idx))
        if len(index_array) > 0:
            future = self._schedule_download_indexes(batch, index_array)
            return future

    def _schedule_download_batch(self, batch, _=None):
        future = self._get_schedule_download_batch_future(batch)

        if future is not None:
            with self.__download_futures_lock:
                self.__download_futures[batch] = future

        return future

    def _schedule_download_indexes(self, batch, index_array):
        next_batch_download = batch + 1
        callback = partial(self._schedule_download_batch, next_batch_download) if self.__prefetching_processes else None

        prefetching_multi_process_control = self._get_prefetching_multi_process_control()

        return prefetching_multi_process_control.execute(self._download_data,
                                                         args=(index_array, ),
                                                         callback=callback)

    @classmethod
    def build_context(cls, config_prefix=None):
        config_prefix = os.environ.get('ML_CONFIG_PREFIX', config_prefix)
        config_file = os.environ.get('ML_CONFIG_FILE')
        session = create_http_session()

        return build_context(session, config_prefix=config_prefix, config_file=config_file)

    @classmethod
    def _get_repo(cls, ctx, volume_id):
        return repo_dynamic(ctx, volume_id)

    @classmethod
    def _group_by_index(cls, data, indices):
        results_grouped = []
        prev_index = None
        for i, d in enumerate(data):
            index = indices[i]
            if prev_index != index:
                results_grouped.append(([], []))
                prev_index = index

            filename, = d[0]
            metadata, = d[1]
            results_grouped[-1][0].append(filename)
            results_grouped[-1][1].append(metadata)

        return results_grouped

    @property
    def _repo(self):
        if self.__repo is None:
            self.__repo = self._get_repo(self._ctx, self.__volume_id)

        return self.__repo

    def __cache_items_if_needed(self, normalized_download_items):
        if self.__disable_caching:
            return

        data_sync = DataSync(self._ctx, self._repo, no_progressbar=True)
        storage = self._get_storage()
        multi_process_control = self._get_multi_process_control()
        data_sync.download_items(normalized_download_items, storage, multi_process_control)

    def _download_data(self, index_array):
        results = []

        download_items_with_index = self._get_metadata_index().get_items_flat(index_array)
        normalized_download_items, indices = zip(*list(download_items_with_index))

        self.__cache_items_if_needed(normalized_download_items)

        for normalized_item in normalized_download_items:
            if normalized_item is None:
                results.append(((), ()))
                continue

            if self.__disable_caching:
                full_path = self._repo.object_store.get_source_path(normalized_item)
            else:
                full_path = self._get_storage().filename(normalized_item)

            results.append(((full_path, ), (normalized_item, )))

        if self._get_metadata_index().is_grouped:
            return self._group_by_index(results, indices)

        return results
