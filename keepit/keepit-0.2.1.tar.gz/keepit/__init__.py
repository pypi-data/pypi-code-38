import os
import unicodedata
import inspect
import re
import pandas as pd
from functools import wraps, partial
from glob import glob
import logging
import pickle
import hashlib

from collections import namedtuple

from .backends import Pickle, Entry

logger = logging.getLogger(__name__)


def _slugify(value):
    """
    Normalizes string, converts to lowercase, removes non-alpha characters,
    and converts spaces to hyphens.
    Source:
    http://stackoverflow.com/questions/295135/turn-a-string-into-a-valid-filename-in-python
    """
    value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore')
    value = re.sub(r'[^\w\s-]', '', value.decode('utf-8', 'ignore'))
    value = value.strip().lower()
    value = re.sub(r'[-\s]+', '-', value)
    return value


def hash_df(df):
    '''Hashes a pandas dataframe'''
    return hashlib.sha256(pd.util.hash_pandas_object(df, index=True).values).hexdigest()


def hash_object(obj):
    return hashlib.sha256(pickle.dumps(obj)).hexdigest()


def hash_element(elem):
    if isinstance(elem, pd.DataFrame):
        return hash_df(elem)
    pick = pickle.dumps(elem)
    return hashlib.sha256(pick).hexdigest()


def func_hasher(f, *args, fname=None, element_hasher=hash_element, **kwargs):

    sig = inspect.signature(f)
    func = partial(f, *args, **kwargs)
    bound = sig.bind_partial(*args, **kwargs)
    bound.apply_defaults()

    reqs = {}
    for k, v in bound.arguments.items():
        reqs[k] = v

    fname = fname or '{}_{}'.format(f.__name__, f.__module__)

    args_hash = hash_object(reqs)
    name = '{}_{}'.format(fname, args_hash)

    return _slugify(name), func, reqs


Result = namedtuple('Result', ['func', 'args', 'value'])


class HashedFunc:

    def __init__(self, func, fname=None, tags=[], backend=Pickle()):
        self.func = func
        self.tags = tags
        self.backend = backend
        self.sig = inspect.signature(func)
        self.fname = fname or '{}_{}'.format(self.func.__name__,
                                             self.func.__module__)

    def hash(self, *args, **kwargs):
        return func_hasher(self.func, *args, fname=self.fname, **kwargs, element_hasher=self.hash_element)

    def hash_element(self, elem):
        return hash_element(elem)

    def __call__(self, *args, cache_force=False, tags=[], **kwargs):

        if os.environ.get('no_cache'):
            return self.func(*args, **kwargs)

        func_id, func, requirements = self.hash(*args, **kwargs)
        print(func_id)

        if cache_force or not self.backend.exists(func_id):
            res = func()
            e = Entry(tags=[self.fname, ],
                      id=func_id,
                      content=Result(func_id, requirements, res))
            self.backend.put(e)
            # hash = self.hash_element(res)
            # self.backend.put(hash, res, tags=self.tags+tags)
            # for req_hash, req_value in requirements.items():
            #     if not self.backend.find(req_hash):
            #         self.backend.put(req_hash, req_value)
        else:
            res = self.backend.get(func_id).content.value
        return res

    def drop(self, *args, **kwargs):
        func_id, func, requirements = self.hash(*args, **kwargs)
        if self.backend.exists(func_id):
            self.backend.remove(func_id)

    def drop_all(self):
        for f in self.list():
            self.backend.remove(f.id)

    def list(self):
        return list(self.backend.find(tags=[self.fname, ]))


def keepit(fname=None, hasher=HashedFunc, **kwargs):
    def outer(of):
        return hasher(of, fname=fname, **kwargs)
    return outer


def diff(df1, df2):
    return pd.concat([df1, df2]).drop_duplicates(keep=False)
