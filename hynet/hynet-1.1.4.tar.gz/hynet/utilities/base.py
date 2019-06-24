"""
General utilities.
"""

import logging
from timeit import default_timer

import numpy as np
from scipy.sparse import diags

from hynet.types_ import hynet_int_, hynet_float_, hynet_complex_, hynet_sparse_

_log = logging.getLogger(__name__)


def create_sparse_matrix(i, j, data, m, n, dtype=hynet_complex_):
    """
    Return an ``m``-by-``n`` sparse matrix ``A`` with ``A[i[k], j[k]] = data[k]``.
    """
    return hynet_sparse_((data, (i, j)), shape=(m, n), dtype=dtype)


def create_sparse_zero_matrix(m, n, dtype=hynet_float_):
    """Return an ``m``-by-``n`` all-zeros matrix."""
    return hynet_sparse_((m, n), dtype=dtype)


def create_sparse_diag_matrix(diagonal, dtype=hynet_complex_):
    """Return a diagonal matrix."""
    return hynet_sparse_(diags(diagonal), dtype=dtype)


def create_dense_vector(i, data, n, dtype=hynet_complex_):
    """Create ``n``-dim. vector ``x`` with ``x[i] = data[i]``."""
    # This is somewhat hacky... May be revised if performance is bad ;)
    return create_sparse_matrix(np.zeros(len(i)), i, data, 1, n,
                                dtype=dtype).toarray()[0]


def truncate_with_ellipsis(string, max_len):
    """
    Truncate the string with an ellipsis if its length exceeds ``max_len``.
    """
    return (string[:max_len-3] + '...') if len(string) > max_len else string


def partition_iterable(iterable, num_blocks):
    """
    Partition the iterable into the specified number of consecutive blocks.

    Parameters
    ----------
    iterable : Iterable
        Iterable to be partitioned.
    num_blocks : .hynet_int_
        Number of blocks into which the iterable shall be partitioned.

    Yields
    ------
    blocks : Iterable
        Blocks of the iterable.
    """
    num_elements = len(iterable)
    if num_elements < 1:
        raise ValueError("The iterable is empty.")
    if num_blocks < 1:
        raise ValueError("The number of blocks must be strictly positive.")
    if num_blocks > num_elements:
        raise ValueError("The number of blocks exceeds the iterable's length.")

    block_size = hynet_int_(np.ceil(num_elements / num_blocks))
    if block_size * (num_blocks - 1) >= num_elements:
        block_size -= 1

    partition = block_size * np.arange(num_blocks, dtype=hynet_int_)
    i = 1
    while num_elements - partition[-1] > block_size:
        partition[i:] += 1
        i += 1

    for i in range(num_blocks - 1):
        yield iterable[partition[i]:partition[i + 1]]
    yield iterable[partition[-1]:]


class Timer:
    """
    Measure time since ``Timer`` object creation or time measurements.
    """
    def __init__(self):
        self._start_time = self._last_time = default_timer()

    def interval(self):
        """
        Return the time in seconds since the last measurement or object creation.

        For the first measurement, the time elapsed since object creation is
        returned. From the second measurement onwards, the time elapsed since
        the last measurement is returned.
        """
        current_time = default_timer()
        time_elapsed = current_time - self._last_time
        self._last_time = current_time
        return time_elapsed

    def total(self):
        """Return the time in seconds since object creation."""
        return default_timer() - self._start_time

    def reset(self):
        """Reset the timer."""
        self._start_time = self._last_time = default_timer()
