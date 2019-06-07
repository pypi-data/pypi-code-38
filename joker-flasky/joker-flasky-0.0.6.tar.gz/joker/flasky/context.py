#!/usr/bin/env python3
# coding: utf-8

from __future__ import unicode_literals

import os
import random
import time
from os.path import join

import yaml


class Rumor(object):
    __slots__ = ['attributes']

    def __init__(self, **attributes):
        self.attributes = attributes

    def __getattr__(self, item):
        try:
            return self.attributes[item]
        except KeyError:
            return random.randrange(10000)


class ContextFile(object):
    def __init__(self, path):
        self.path = path
        self._data = {}
        self._defaults = {}
        self._mtime = 0
        self._load_from_file()
        
    def _load_from_file(self):
        mtime = os.path.getmtime(self.path)
        if mtime - (self._mtime or 0) < 0.001:
            return
        data = yaml.load(open(self.path))
        if not isinstance(data, dict):
            raise TypeError('the contextmap file is not dict-like')
        data.update(self._defaults)
        self._data = data
        self._mtime = mtime
        
    def get(self, key, default=None):
        return self._data.get(key, default)
    
    def get_keys(self):
        self._load_from_file()
        return list(self._data)

    def setdefault(self, key, default=None):
        try:
            return self._data[key]
        except LookupError:
            return self._defaults.setdefault(key, default)


class RealContextFile(ContextFile):
    def __init__(self, path, ttl=60):
        super(ContextFile, self).__init__(path)
        self._xtime = 0
        self.ttl = ttl

    def get(self, key, default=None):
        current_time = time.time()
        # expired
        if current_time > self._xtime:
            self._load_from_file()
            self._xtime = current_time + self.ttl
        return self._data.get(key, default)
    
    def setdefault(self, key, default=None):
        return self._data.setdefault(key, default)


class ContextDirectory(object):
    def __init__(self, dir_path):
        if not os.path.isdir(dir_path):
            raise ValueError('requires a directory')
        self._cache = {}
        self._mtime = {}
        self.path = dir_path

    def _load_from_file(self, key):
        """
        Update _mtime and _cache if yaml.load() is called.
        """
        path = join(self.path, key + '.yml')
        if not os.path.isfile(path):
            return
        mtime = os.path.getmtime(path)

        # avoid float equality test
        if mtime - self._mtime.get(key, 0) < 0.001:
            try:
                return self._cache[key]
            except LookupError:
                pass
        section = yaml.load(open(path))
        self._mtime[key] = mtime
        self._cache[key] = section
        return section

    def setdefault(self, key, default=None):
        # only set default when key is not available in FS
        return self._cache.setdefault(key, self.get(key, default))

    def get(self, key, default=None):
        try:
            return self._cache[key]
        except LookupError:
            return self._load_from_file(key) or default

    def get_keys(self):
        _keys = []
        for filename in os.listdir(self.path):
            name, ext = os.path.splitext(filename)
            if ext == '.yml':
                _keys.append(name)
        return _keys


class RealContextDirectory(ContextDirectory):
    def __init__(self, dir_path, ttl=60):
        super(RealContextDirectory, self).__init__(dir_path)
        self._xtime = {}
        self.ttl = ttl
        
    def get(self, key, default=None):
        """
        Update _xtime if _load_from_file() is called and ttl available.
        Do NOT touch _cache and _mtime in this method;
        it is the job of _load_from_file.
        """
        current_time = time.time()
        expire_time = self._xtime.get(key, 0)

        # expired
        if current_time > expire_time:
            section = self._load_from_file(key)
            self._xtime[key] = current_time + self.ttl
            return section
        return super(RealContextDirectory, self).get(key, default)
    
    def setdefault(self, key, default=None):
        section = self._cache.setdefault(key, self.get(key, default))
        self._xtime.setdefault(key, float('inf')) 
        return section


def context_load(path, ttl=None):
    if os.path.isdir(path):
        if ttl is None:
            return ContextDirectory(path)
        else:
            return RealContextDirectory(path, ttl)
    elif os.path.isfile(path):
        if ttl is None:
            return ContextFile(path)
        else:
            return RealContextFile(path, ttl)
    else:
        raise ValueError('path must be a file or directory')
