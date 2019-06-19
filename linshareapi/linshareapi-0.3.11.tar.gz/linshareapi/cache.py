#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""TODO"""

from __future__ import unicode_literals
import os
import time
import json
import logging
import datetime
import hashlib
import tempfile
from functools import wraps
from ordereddict import OrderedDict

# pylint: disable=missing-docstring

def compute_key(cli, familly, discriminant=None):
    """This function is used to compute a unique key from all connection parametters."""
    hash_key = hashlib.sha256()
    hash_key.update(familly)
    hash_key.update(cli.host)
    hash_key.update(cli.user)
    hash_key.update(cli.password)
    if discriminant:
        if isinstance(discriminant, list):
            for i in discriminant:
                if i is not None and i is not False:
                    hash_key.update(str(i))
        elif isinstance(discriminant, tuple):
            for i in discriminant:
                if i is not None and i is not False:
                    hash_key.update(str(i))
        else:
            hash_key.update(discriminant)
    hash_key = hash_key.hexdigest()
    cli.log.debug("hash_key: " + hash_key)
    return hash_key


# pylint: disable=too-few-public-methods
class Cache(object):
    """Anotaton to cache resources."""

    # pylint: disable=too-many-arguments
    def __init__(self, cache_manager, familly=None, discriminant=None,
                 arguments=False, cache_duration=None):
        """Anotaton to cache resources.

           Keyword arguments:
           cache_manager    -- instance of a CacheManager that will store all data.
           familly          -- each kind of resource must have its own kind of familly.
           discriminant     -- how to store different data in the same familly.
                               it will be used to compute a different cache key.
           arguments        -- add all the arguments (query params) of the
                               current function as discriminant for cache key
           cache_duration   -- Time to live for the cache.
        """
        self.cman = cache_manager
        self.familly = familly
        self.discriminant = discriminant
        self.arguments = arguments
        self.cache_duration = cache_duration

    def __call__(self, original_func):
        """TODO"""
        def wrapper(*args, **kwargs):
            """TODO"""
            resourceapi = args[0]
            cache_cfg = resourceapi.cache
            if cache_cfg.has_key('familly'):
                self.familly = cache_cfg['familly']
            if self.familly is None:
                raise Exception("Invalid familly value for Cache decorator.")
            cli = resourceapi.core
            func_args = []
            if self.arguments:
                if len(args) > 1:
                    func_args = list(args[1:])
            if self.discriminant:
                func_args.append(self.discriminant)
            nocache = cli.nocache
            if nocache:
                cli.log.debug("cache disabled.")
                return original_func(*args, **kwargs)
            hash_key = compute_key(cli, self.familly, func_args)
            if self.cman.has_key(hash_key, self.familly, self.cache_duration):
                res = self.cman.get(hash_key, self.familly)
            else:
                res = original_func(*args, **kwargs)
                self.cman.put(hash_key, res, self.familly)
            return res
        return wrapper


class Invalid(object):
    def __init__(self, cache_manager, familly=None, discriminant=None,
                 whole_familly=False):
        """Anotaton to invalid cached resources.

           Keyword arguments:
           cache_manager    -- instance of a CacheManager that will store all data.
           familly          -- each kind of resource must have its own kind of familly.
           discriminant     -- how to store different data in the same familly.
                               it will be used to compute a different cache key.
           whole_familly    -- invalid familly and all related cached resources
                               cf discriminant options
        """
        self.cman = cache_manager
        self.familly = familly
        self.whole_familly = whole_familly
        if whole_familly:
            if not isinstance(familly, list):
                self.familly = [familly,]
        self.discriminant = discriminant

    def override_familly(self, args):
        """Look in the current wrapped object to find a cache configuration to
        override the current default configuration."""
        resourceapi = args[0]
        cache_cfg = resourceapi.cache
        if cache_cfg.has_key('familly'):
            self.familly = cache_cfg['familly']
        if cache_cfg.has_key('whole_familly'):
            self.whole_familly = cache_cfg['whole_familly']
        if self.familly is None:
            raise Exception("Invalid familly value for Cache decorator.")

    def __call__(self, original_func):
        if self.whole_familly:
            return self.get_invalid_whole_familly(original_func)
        return self.get_invalid_one_key(original_func)

    def get_invalid_whole_familly(self, original_func):
        def wrapper(*args, **kwargs):
            self.override_familly(args)
            for familly in self.familly:
                self.cman.evict(group=familly)
            return original_func(*args, **kwargs)
        return wrapper

    def get_invalid_one_key(self, original_func):
        def wrapper(*args, **kwargs):
            self.override_familly(args)
            if self.whole_familly:
                if not isinstance(self.familly, list):
                    self.familly = [self.familly,]
                for familly in self.familly:
                    self.cman.evict(group=familly)
            else:
                resourceapi = args[0]
                cli = resourceapi.core
                hash_key = compute_key(cli, self.familly, self.discriminant)
                self.cman.evict(hash_key, self.familly)
            return original_func(*args, **kwargs)
        return wrapper


class CacheManager(object):
    def __init__(self, cache_duration=60,
                 logger_name="linshareapi.cachemanager"):
        self.log = logging.getLogger(logger_name)
        self.rootcachedir = tempfile.gettempdir() + "/" + "linshare-cache"
        if not os.path.isdir(self.rootcachedir):
            os.makedirs(self.rootcachedir)
        self.urls = OrderedDict()
        self.cache_duration = cache_duration

    def _get_cachedir(self, group=None):
        res = [self.rootcachedir,]
        if group:
            res.append(group)
        res = "/".join(res)
        if not os.path.isdir(res):
            os.makedirs(res)
        self.log.debug("cachedir :" + str(res))
        return res

    def _get_cachefile(self, key, group=None):
        return self._get_cachedir(group) + "/" + key

    def _has_key(self, key, group=None):
        cachefile = self._get_cachefile(key, group)
        if os.path.isfile(cachefile):
            return True
        return False

    def has_key(self, key, group=None, cache_duration=None):
        if self._has_key(key, group):
            cachefile = self._get_cachefile(key, group)
            file_time = os.stat(cachefile).st_mtime
            form = "{da:%Y-%m-%d %H:%M:%S}"
            self.log.debug("cached data : " + str(
                form.format(da=datetime.datetime.fromtimestamp(file_time))))
            if not cache_duration:
                cache_duration = self.cache_duration
            self.log.debug("cache_duration : %s", cache_duration)
            if time.time() - cache_duration < file_time:
                return True
            else:
                self.evict(key, group)
        return False

    def evict(self, key=None, group=None):
        if key is None:
            if group:
                cachedir = self._get_cachedir(group)
                for i in os.listdir(cachedir):
                    self.log.debug("cached data eviction : %s : %s", group, i)
                    os.remove(cachedir + "/" + i)
                return True
        else:
            if self._has_key(key, group):
                cachefile = self._get_cachefile(key, group)
                self.log.debug("cached data eviction : %s : %s", group, key)
                os.remove(cachefile)
                return True
            if not group:
                for l_group in os.listdir(self.rootcachedir):
                    if self._has_key(key, l_group):
                        cachefile = self._get_cachefile(key, l_group)
                        self.log.debug("cached data eviction : %s : %s",
                                       l_group, key)
                        os.remove(cachefile)
                        return True
        return False

    def get(self, key, group=None):
        res = None
        self.log.debug("loading cached data : %s : %s", group, key)
        cachefile = self._get_cachefile(key, group)
        with open(cachefile, 'rb') as fde:
            res = json.load(fde)
        return res

    def put(self, key, data, group=None):
        self.log.debug("caching data : %s : %s", group, key)
        cachefile = self._get_cachefile(key, group)
        with open(cachefile, 'wb') as fde:
            json.dump(data, fde)


class Time(object):
    def __init__(self, logger_name, return_time=False, info=None,
                 label="execution time : %(time)s"):
        self.log = logging.getLogger(logger_name)
        self.return_time = return_time
        self.info = info
        self.label = label

    def __call__(self, original_func):
        @wraps(original_func)
        def time_wrapper(*args, **kwargs):
            start = time.time()
            res = original_func(*args, **kwargs)
            end = time.time()
            diff = end - start
            resourceapi = args[0]
            info = self.info
            self.log.debug(self.label, {'time': diff})
            if info is None:
                info = getattr(resourceapi, "verbose", False)
            if info:
                print self.label % {'time': diff}
            if self.return_time:
                return (diff, res)
            return res
        return time_wrapper
