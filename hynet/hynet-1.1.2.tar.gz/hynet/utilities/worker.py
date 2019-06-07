"""
Management of worker processes in *hynet*.

Parameters
----------
workers : WorkerManager
    Worker manager created at import time for parallel processing within the
    *hynet* package.
"""

import logging
from os import cpu_count
import multiprocessing
import numbers
import functools
from itertools import starmap

from hynet.utilities.base import Timer
import hynet.config as config

_log = logging.getLogger(__name__)


def pool_operation(method):
    """
    Decorates a worker operation method with a pool state verification.

    The worker manager maintains its pool of workers lazily, i.e., it is only
    created on demand. Due to this, every potential pool operation in the
    worker manager class has to verify and, if necessary, update the pool
    state prior to the operation itself. This decorator manages this task. In
    the worker operation method, the code only needs to adapt to the
    availability of the pool.
    """
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        self._check_pool()
        return method(self, *args, **kwargs)
    return wrapper


class WorkerManager:
    """
    Manage operations on a pool of workers.

    This class provides operations on a pool of worker processes in case that
    parallel processing in *hynet* is enabled and, otherwise, it performs the
    operations in the current process. The pool of workers is maintained
    lazily, i.e., it is created on demand.

    See Also
    --------
    hynet.config
    """
    def __init__(self):
        self._pool = None
        self._num_workers = cpu_count()
        if self._num_workers is None:
            self._num_workers = 1

    @property
    def num_workers(self):
        """
        Return the number of worker processes.

        **These workers are only active if parallel processing is enabled.**

        See Also
        --------
        hynet.config
        """
        return self._num_workers

    @num_workers.setter
    def num_workers(self, value):
        """
        Set the number of worker processes.

        **These workers are only active if parallel processing is enabled.** If
        a pool with a different number of worker processes is already open, it
        is closed immediately and reopened on demand with the updated number of
        workers.

        See Also
        --------
        hynet.config
        """
        if not isinstance(value, numbers.Integral) or value < 1:
            raise ValueError("The number of workers must be a positive integer.")
        if value == self._num_workers:
            return
        self._num_workers = value
        self.close_pool()

    def _open_pool(self):
        """Open a pool of worker processes."""
        if self._pool is not None:
            raise RuntimeError("There is already an open pool of workers.")
        if self._num_workers == 1:
            _log.debug("Skipping pool creation due to use of a single worker.")
            return
        timer = Timer()
        self._pool = multiprocessing.Pool(processes=self._num_workers)
        _log.debug("Opened pool with {:d} workers ({:.3f} sec.)"
                   .format(self._num_workers, timer.total()))

    def close_pool(self):
        """Close the pool of worker processes."""
        if self._pool is None:
            return
        timer = Timer()
        self._pool.close()
        self._pool.join()
        self._pool = None
        _log.debug("Closed worker pool ({:.3f} sec.)".format(timer.total()))

    def _check_pool(self):
        """
        Verify and, if necessary, update the state of the worker pool.

        See Also
        --------
        hynet.utilities.worker.pool_operation:
            Decorator for a worker operation method.
        """
        if config.GENERAL['parallelize']:
            if self._pool is None:
                self._open_pool()
        else:
            if self._pool is not None:
                _log.debug("Parallel processing was disabled. Closing the pool.")
            self.close_pool()

    @property
    def is_multiprocessing(self):
        """Return True if the operations utilize multiprocessing."""
        self._check_pool()
        return self._pool is not None

    @pool_operation
    def map(self, func, iterable, **kwds):
        """
        Apply the function to every item (single argument) in the iterable.

        Parameters
        ----------
        func : function
            Function that shall be applied to the items in the iterable.
        iterable : iterable
            Iterable containing the function arguments. An item in this
            iterable is the single argument passed to the function.
        kwds : dict, optional
            If parallel processing is enabled, the keyword arguments are passed
            to the ``map``-method of ``multiprocessing.Pool``.

        Returns
        -------
        result : list
            List of the function result for every item in the iterable.

        See Also
        --------
        multiprocessing.Pool.map
        """
        if self._pool is None:
            return list(map(func, iterable))
        return self._pool.map(func, iterable, **kwds)

    @pool_operation
    def starmap(self, func, iterable, **kwds):
        """
        Apply the function to every item (argument tuple) in the iterable.

        Parameters
        ----------
        func : function
            Function that shall be applied to the items in the iterable.
        iterable : iterable
            Iterable containing the function arguments. An item in this
            iterable is a tuple of the arguments passed to the function.
        kwds : dict, optional
            If parallel processing is enabled, the keyword arguments are passed
            to the ``starmap``-method of ``multiprocessing.Pool``.

        Returns
        -------
        result : list
            List of the function result for every item in the iterable.

        See Also
        --------
        multiprocessing.Pool.starmap
        """
        if self._pool is None:
            return list(starmap(func, iterable))
        return self._pool.starmap(func, iterable, **kwds)


workers = WorkerManager()   # One instance for use within the *hynet* package.
