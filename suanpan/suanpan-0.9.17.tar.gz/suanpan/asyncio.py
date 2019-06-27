# coding=utf-8
from __future__ import absolute_import, print_function

import contextlib
import multiprocessing
from multiprocessing import Pool as ProcessPool
from multiprocessing.dummy import Pool as ThreadPool

from suanpan.utils import pbar as spbar

WORKERS = multiprocessing.cpu_count()


@contextlib.contextmanager
def multiThread(workers=None, join=False):
    workers = workers or WORKERS
    pool = ThreadPool(processes=workers)
    yield pool
    pool.close()
    if join:
        pool.join()


@contextlib.contextmanager
def multiProcess(workers=None, join=False):
    workers = workers or WORKERS
    pool = ProcessPool(processes=workers)
    yield pool
    pool.close()
    if join:
        pool.join()


class StarmapRunner(object):
    def __init__(self, func):
        self.func = func

    def __call__(self, args):
        return self.func(*args)


def map(func, iterable, chunksize=1, workers=None, pbar=None, thread=False, total=None):
    return list(
        imap(
            func,
            iterable,
            chunksize=chunksize,
            workers=workers,
            pbar=pbar,
            thread=thread,
            total=total,
        )
    )


def imap(
    func, iterable, chunksize=1, workers=None, pbar=None, thread=False, total=None
):
    iterable, total = spbar.getIterableLen(iterable, config=pbar, total=total)
    poolClass = multiThread if thread else multiProcess
    with poolClass(workers, join=True) as pool:
        return spbar.one(
            pool.imap(func, iterable, chunksize=chunksize), config=pbar, total=total
        )


def starmap(
    func, iterable, chunksize=1, workers=None, pbar=None, thread=False, total=None
):
    return list(
        istarmap(
            func,
            iterable,
            chunksize=chunksize,
            workers=workers,
            pbar=pbar,
            thread=thread,
            total=total,
        )
    )


def istarmap(
    func, iterable, chunksize=1, workers=None, pbar=None, thread=False, total=None
):
    return imap(
        StarmapRunner(func),
        iterable,
        chunksize=chunksize,
        workers=workers,
        pbar=pbar,
        thread=thread,
        total=total,
    )


def run(funcs, args=(), kwds=None, thread=False, wait=False, **kwargs):
    kwds = kwds or {}
    funcs = funcs if isinstance(funcs, (list, tuple)) else [funcs]
    poolClass = multiThread if thread else multiProcess
    with poolClass(len(funcs), join=wait) as pool:
        results = [
            pool.apply_async(func, args=args, kwds=kwds, **kwargs) for func in funcs
        ]
    if wait:
        results = [r.get() for r in results]
    return results
