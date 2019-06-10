# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Classes for automl cache store."""
from typing import Any, Callable, cast, Dict, Iterable, Optional
import logging
import os
import sys  # noqa F401 # dynamically evaluated to get caller
import tempfile
import copy

from abc import ABC, abstractmethod

from .pickler import DefaultPickler
from .logging_utilities import log_traceback
from .activity_logger import ActivityLogger, DummyActivityLogger

# default task timeout
DEFAULT_TASK_TIMEOUT_SECONDS = 900

# Flag for cache enabled for all scenarios
SDK_HAS_DEFAULT_CACHE_CAPABILITY = True


class CacheStore(ABC):
    """ABC for cache store."""

    def __init__(self,
                 max_retries: int = 3,
                 module_logger: Optional[logging.Logger] = None,
                 activity_logger: Optional[ActivityLogger] = None) -> None:
        """
        Cache store constructor.

        :param max_retries: max retries to get/put from/to store
        :param module_logger: logger
        :param activity_logger: activity logger
        """
        self.cache_items = {}   # type: Dict[Any, Any]
        self.max_retries = max_retries
        self.module_logger = module_logger or logging.getLogger()
        self.activity_logger = activity_logger or DummyActivityLogger()

    def __getstate__(self) -> Dict[str, Optional[Any]]:
        """
        Get this cache store's state, removing unserializable objects in the process.

        :return: a dict containing serializable state.
        """
        return {'module_logger': None,
                'activity_logger': None,
                'cache_items': self.cache_items,
                'max_retries': self.max_retries}

    def __setstate__(self, state: Dict[str, Optional[Any]]) -> None:
        """
        Deserialize this cache store's state, using the default logger.

        :param state: dictionary containing object state
        :type state: dict
        """
        self.module_logger = logging.getLogger()
        self.activity_logger = DummyActivityLogger()
        self.cache_items = cast(Dict[Any, Any], state['cache_items'])
        self.max_retries = cast(int, state['max_retries'])

    @abstractmethod
    def load(self):
        """Load - abstract method."""
        pass

    @abstractmethod
    def unload(self):
        """Unload - abstract method."""
        pass

    def add(self, keys: Iterable[Any], values: Iterable[Any]) -> None:
        """Add to store.

        :param keys: store key
        :param values: store value
        """
        for k, v in zip(keys, values):
            self.cache_items[k] = v

    def add_or_get(self, key: Any, value: Any) -> Any:
        """
        Add or get from store.

        :param key: store key
        :param value: store value
        :return: value
        """
        val = self.cache_items.get(key, None)
        if val is not None:
            return val

        self.add([key], [value])
        return value

    def get(self, keys: Iterable[Any], default: Optional[Any] = None) -> Dict[Any, Optional[Any]]:
        """
        Get value from store.

        :param default: default value
        :param keys: store keys
        :return: values
        """
        return {k: self.cache_items.get(k, default) for k in keys}

    def set(self, key, value):
        """
        Set value to store.

        :param key: store key
        :param value: store value
        """
        self.add([key], [value])

    def remove(self, key):
        """
        Remove from store.

        :param key: store key
        """
        obj = self.cache_items.pop(key)
        del obj

    def remove_all(self):
        """Remove all entry from store."""
        for k, v in self.cache_items.items():
            del v

        self.cache_items.clear()

    def __iter__(self):
        """
        Store iterator.

        :return: cache items
        """
        return iter(self.cache_items.items())

    @staticmethod
    def _function_with_retry(fn: 'Callable[..., Optional[Any]]',
                             max_retries: int,
                             logger: logging.Logger,
                             *args: Any,
                             **kwargs: Any) -> Optional[Any]:
        """
        Call function with retry capability.

        :param fn: function to be executed
        :param max_retries: number of retries
        :param logger: logger
        :param args: args
        :param kwargs: kwargs
        :return: Exception if failure, otherwise returns value from function call
        """
        retry_count = 0
        ex = None
        while retry_count < max_retries:
            try:
                return fn(*args, **kwargs)
            except Exception as e:
                logger.warning("Execution failed {}".format(e))
                ex = e
            finally:
                retry_count += 1

        error_raised = cast(BaseException, ex)
        raise error_raised.with_traceback(error_raised.__traceback__)

    # Need to disable type checking because ContextManager is not available in typing before Python 3.5.4
    def log_activity(self, custom_dimensions: Optional[Dict[str, Any]] = None) -> Any:
        """
        Log activity collects the execution latency.

        :param custom_dimensions: custom telemetry dimensions
        :return: log activity
        """
        get_frame_expr = 'sys._getframe({}).f_code.co_name'
        caller = eval(get_frame_expr.format(2))
        telemetry_values = dict()
        telemetry_values['caller'] = caller

        if custom_dimensions is not None:
            telemetry_values.update(custom_dimensions)

        return self.activity_logger.log_activity(
            logger=self.module_logger, activity_name=caller, custom_dimensions=telemetry_values)


class MemoryCacheStore(CacheStore):
    """MemoryCacheStore - stores value in memory."""

    def load(self):
        """Load from memory - NoOp."""
        pass

    def add(self, keys, values):
        """
        Add to store by creating a deep copy.

        :param keys: store key
        :param values: store value
        """
        for k, v in zip(keys, values):
            self.cache_items[k] = copy.deepcopy(v)

    def unload(self):
        """Unload from memory."""
        self.cache_items.clear()


class FileCacheStore(CacheStore):
    """FileCacheStore - cache store based on file system."""

    def __init__(self, path=None, pickler=None,
                 task_timeout=DEFAULT_TASK_TIMEOUT_SECONDS,
                 module_logger=None):
        """
        File based cache store - constructor.

        :param path: store path
        :param pickler: pickler, defaults to cPickler
        :param task_timeout: task timeout
        :param module_logger:
        """
        super(FileCacheStore, self).__init__(module_logger=module_logger)

        if pickler is None:
            pickler = DefaultPickler()

        self.task_timeout = task_timeout
        self.pickler = pickler
        self._num_workers = os.cpu_count()
        self.path = path
        if not path:
            self.path = _create_temp_dir()

    def __getstate__(self):
        """
        Get this cache store's state, removing unserializable objects in the process.

        :return: a dict containing serializable state.
        """
        return super().__getstate__(), {
            'path': self.path,
            'pickler': self.pickler,
            'task_timeout': self.task_timeout,
            '_num_workers': self._num_workers
        }

    def __setstate__(self, state):
        """
        Deserialize this cache store's state, using the default logger.

        :param state: dictionary containing object state
        :type state: dict
        """
        super_state, my_state = state
        self.path = my_state['path']
        self._num_workers = my_state['_num_workers']
        self.task_timeout = my_state['task_timeout']
        self.pickler = my_state['pickler']
        super().__setstate__(super_state)

    def log_debug_messages(self, message):
        """
        Log a message in the logfile.

        :param message: message to be logged
        """
        if self.module_logger:
            self.module_logger.info(message)

    def add(self, keys, values):
        """
        Pickles the object and adds to cache.

        :param keys: store keys
        :param values: store values
        """
        with self.log_activity():
            for k, v in zip(keys, values):
                self.log_debug_messages("Uploading key: " + k)
                self._upload(k, v)

    def add_or_get(self, key, value):
        """
        Add or gets from the store.

        :param key: store key
        :param value: store value
        :return: UnPickled object
        """
        val = self.cache_items.get(key, None)
        if val is not None:
            return self.get([key])

        self.add([key], [value])
        return value

    def get(self, keys, default=None):
        """
        Get unpickled object from store.

        :param keys: store keys
        :param default: returns default value if not present
        :return: unpickled objects
        """
        res = dict()

        with self.log_activity():
            for key in keys:
                path = self.cache_items.get(key, None)
                obj = default
                self.log_debug_messages("Getting data for key: " + key)
                if path is not None:
                    obj = self.pickler.load(path)
                res[key] = obj

        return res

    def set(self, key, value):
        """
        Set to store.

        :param key: store key
        :param value: store value
        """
        self.add([key], [value])

    def remove(self, key):
        """
        Remove from store.

        :param key: store key
        """
        with self.log_activity():
            try:
                self.log_debug_messages("Deleting data for key: " + key)
                self.cache_items.pop(key)
                self._delete_file(key)
            except Exception as e:
                self.module_logger.warning("remove from store failed {}".format(e))

    def remove_all(self):
        """Remove all the cache from store."""
        length = self.cache_items.__len__()

        with self.log_activity():
            while length > 0:
                length -= 1
                k, v = self.cache_items.popitem()
                self._delete_file(k)

    def load(self):
        """Load from store."""
        self.log_debug_messages("Loading from file cache")
        with self.log_activity():
            for f in os.listdir(self.path):
                if self.pickler.is_meta_file(f):
                    path = os.path.join(self.path, f)
                    val = self.pickler.get_name_without_extn(path)
                    key = self.pickler.get_name_without_extn(f)
                    self.cache_items[key] = val

    def unload(self):
        """Unload from store."""
        # load to make sure all the meta files are loaded
        self.load()

        self.log_debug_messages("UnLoading from file cache")
        self.remove_all()
        _try_remove_dir(self.path)

    def _upload(self, key, obj):
        try:
            path = os.path.join(self.path, key)
            self.pickler.dump(obj, path=path)
            self.cache_items[key] = path
            self.log_debug_messages("Uploaded key: " + key)
        except Exception as e:
            log_traceback(
                e,
                self.module_logger,
                override_error_msg="Uploading {} failed with {}".format(key, e),
                is_critical=False
            )
            raise

    def _delete_file(self, k):
        try:
            path = os.path.join(self.path, k)
            chunk_files = self.pickler.get_pickle_files(path)
            for chunk_file in chunk_files:
                os.remove(chunk_file)
        except Exception as e:
            self.module_logger.warning("remove from store failed {}".format(e))


def _create_temp_dir(temp_location=None):
    """
    Create temp dir.

    :return: temp location
    """
    try:
        return tempfile.mkdtemp(dir=temp_location)
    except OSError as e:
        raise CacheException("Failed to create temp folder {}. You can disable the "
                             "cache if space is concern. Setting to disable cache enable_cache=False".format(e))


def _try_remove_dir(path):
    """
    Remove directory.

    :param path: path to be removed
    """
    try:
        os.rmdir(path)
    except OSError:
        return False

    return True


class CacheException(Exception):
    """Cache exceptions."""

    pass
