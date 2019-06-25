"""
Compare different implementations of merging sorted iterators.

It shows that
* if only a few items (about 10%) are consumed the heapq is superior,
* if only some items are consumed and retrieval is slow heapq is superior,
* otherwise concat-sort strategy is superior.
* heapq and recursive implementations perform similarly
"""
import itertools
import time

import pytest

from sprig import iterutils


def _imerge_recusive(iterables, key):
    if len(iterables) == 1:
        yield from iterables[0]
    else:
        split = len(iterables) // 2
        ls = _imerge_recusive(iterables[:split], key)  # left
        rs = _imerge_recusive(iterables[split:], key)  # right
        try:
            l = next(ls)
        except StopIteration:
            yield from rs
            return

        try:
            r = next(rs)
        except StopIteration:
            yield l
            yield from ls
            return

        while True:
            if key(l) < key(r):
                yield l
                try:
                    l = next(ls)
                except StopIteration:
                    yield r
                    yield from rs
                    return
            else:
                yield r
                try:
                    r = next(rs)
                except StopIteration:
                    yield l
                    yield from ls
                    return


def imerge_recursive(iterables, key=lambda x: x):
    yield from _imerge_recusive(iterables, key)


def imerge_concat_sort(iterables, key=lambda x: x):
    yield from sorted(itertools.chain(*iterables), key=key)


class List:
    def __init__(self, xs, io_bound):
        self.xs = list(xs)
        self.io_bound = io_bound

    def __iter__(self):
        if self.io_bound is not None:
            return ListIterIO(self.xs)
        else:
            return ListIterCPU(self.xs)


class ListIterIO:
    def __init__(self, xs):
        self.xs = iter(xs)

    def __next__(self):
        time.sleep(2 ** -14)  # Simulate disk access or other expensive operation
        return next(self.xs)


class ListIterCPU:
    def __init__(self, xs):
        self.xs = iter(xs)

    def __next__(self):
        return next(self.xs)


id2func = {
    'recursive': imerge_recursive,
    'concat_sort': imerge_concat_sort,
    'heapq': iterutils.imerge,
}

id2iterables = {
    'small': [list(range(2 ** 4)) for _ in range(2 ** 4)],
    'medium': [list(range(2 ** 6)) for _ in range(2 ** 6)],
    'large': [list(range(2 ** 8)) for _ in range(2 ** 8)],
    'tall': [list(range(2 ** 12)) for _ in range(2 ** 4)],  # Same size as large
    'wide': [list(range(2 ** 12)) for _ in range(2 ** 4)],  # Same size as large
    'slant': [list(range(i * 2)) for i in range(2 ** 8)],  # Same size as large, almost
}

cpu_iterables = [
    [List(xs, False) for xs in xss]
    for xss in id2iterables.values()
]

io_iterables = [
    [List(xs, True) for xs in xss]
    for xss in id2iterables.values()
]


@pytest.mark.parametrize('func', list(id2func.values()), ids=list(id2func.keys()))
@pytest.mark.parametrize('iterables', list(id2iterables.values()), ids=list(id2iterables.keys()))
def test_performance_eager(func, iterables):
    list(func(iterables))


@pytest.mark.parametrize('func', list(id2func.values()), ids=list(id2func.keys()))
@pytest.mark.parametrize('iterables', list(id2iterables.values()), ids=list(id2iterables.keys()))
def test_performance_lazy(func, iterables):
    list(itertools.islice(func(iterables), 2 ** 18))


@pytest.mark.parametrize('func', list(id2func.values()), ids=list(id2func.keys()))
@pytest.mark.parametrize('iterables', cpu_iterables, ids=list(id2iterables.keys()))
def test_performance_lazy_custom_cpu_bound(func, iterables):
    list(itertools.islice(func(iterables), 2 ** 8))


@pytest.mark.parametrize('func', list(id2func.values()), ids=list(id2func.keys()))
@pytest.mark.parametrize('iterables', io_iterables, ids=list(id2iterables.keys()))
def test_performance_lazy_custom_io_bound(func, iterables):
    list(itertools.islice(func(iterables), 2 ** 8))
