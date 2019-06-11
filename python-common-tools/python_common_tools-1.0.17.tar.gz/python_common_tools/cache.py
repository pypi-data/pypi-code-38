# -*- coding: utf-8 -*-
__author__ = '陈章'
__date__ = '2019-04-25 11:34'
import logging
import os
import pickle
from datetime import datetime
from functools import wraps
from urllib.parse import quote_plus

logger = logging.getLogger("python_common_tools")

from python_common_tools.compress import get_md5


class Cache:

    @classmethod
    def cache_function(cls, cache_dir, is_method=False):
        def outer(f):
            @wraps(f)
            def inner(*args, **kwargs):
                # prepare cache_file
                fname = f.__qualname__
                argv_str = cls.get_argv_str(args, kwargs, is_method)
                cache_dir_real = f'{cache_dir}/{fname}'
                os.makedirs(cache_dir_real, exist_ok=True)
                cache_file = f'{cache_dir_real}/{get_md5(argv_str)}.pkl'
                r = cls.exec_func(cache_file, fname, f, args, kwargs)
                return r

            return inner

        return outer

    @classmethod
    def get_argv_str(cls, args, kwargs, is_method=False):
        if is_method:
            return f'{quote_plus(str(args[1:]))}_{quote_plus(str(kwargs))}'
        else:
            return f'{quote_plus(str(args))}_{quote_plus(str(kwargs))}'

    @classmethod
    def exec_func(cls, cache_file, fname, f, args, kwargs):
        # exec func
        if not os.path.exists(cache_file):
            logger.debug(f'exec func {fname} {args} {kwargs}')
            r = f(*args, **kwargs)
            cls.write_to_cache_file(cache_file, r)
        r = cls.read_from_cache_file(cache_file)
        return r

    @classmethod
    def cache_daily_function(cls, cache_dir, is_method=False):
        def outer(f):
            @wraps(f)
            def inner(*args, **kwargs):
                # prepare cache file
                fname = f.__qualname__
                today = datetime.now().strftime("%Y%m%d")
                argv_str = cls.get_argv_str(args, kwargs, is_method)
                cache_dir_real = f'{cache_dir}/{fname}/{today}'
                os.makedirs(cache_dir_real, exist_ok=True)
                cache_file = f'{cache_dir_real}/{get_md5(argv_str)}.pkl'
                r = cls.exec_func(cache_file, fname, f, args, kwargs)
                return r

            return inner

        return outer

    @classmethod
    def read_from_cache_file(cls, cache_file):
        r_cache_file = open(cache_file, 'rb')
        r = pickle.load(r_cache_file)
        r_cache_file.close()
        return r

    @classmethod
    def write_to_cache_file(cls, cache_file, r):
        w_cache_file = open(cache_file, 'wb')
        pickle.dump(r, w_cache_file)
        w_cache_file.close()


cache_function = Cache.cache_function
cache_daily_function = Cache.cache_daily_function
