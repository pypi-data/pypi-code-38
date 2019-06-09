#!/usr/bin/env python
# -*- coding: utf-8
import hashlib
import logging
import os
import pickle
from collections import namedtuple
from datetime import datetime, timedelta

import appdirs
import six
import time
from six.moves import zip_longest

LOG = logging.getLogger(__name__)

Entry = namedtuple("Entry", ("timestamp", "data"))


class FileCache(object):
    def __init__(self, name):
        self._cache_dir = os.path.join(appdirs.user_cache_dir("dockerma"), name)

    def get(self, key):
        entry_path = self._get_entry_path(key)
        entry = self._get_entry(entry_path)
        if entry:
            return entry.data

    def _get_entry(self, entry_path):
        if not os.path.exists(entry_path):
            return None
        with open(entry_path, "rb") as fobj:
            return pickle.load(fobj)

    def set(self, key, value):
        expires = datetime.now() + timedelta(days=7)
        timestamp = int(time.mktime(expires.timetuple()))
        entry_path = self._get_entry_path(key)
        dir_path = os.path.dirname(entry_path)
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
        with open(entry_path, "wb") as fobj:
            pickle.dump(Entry(timestamp, value), fobj)

    def delete(self, key):
        entry_path = self._get_entry_path(key)
        self._delete_entry(entry_path)

    def _delete_entry(self, entry_path):
        if os.path.exists(entry_path):
            os.unlink(entry_path)
            directory = os.path.dirname(entry_path)
            while len(directory) > 3 and len(os.listdir(directory)) == 0:
                os.rmdir(directory)
                directory = os.path.dirname(directory)

    def clean_expired(self):
        now = time.time()
        n = 0

        for root, dirs, files in os.walk(self._cache_dir):
            for fname in files:
                entry_path = os.path.join(root, fname)
                entry = self._get_entry(entry_path)
                if entry.timestamp <= now:
                    self._delete_entry(entry_path)
                    n += 1
        return n

    def _get_entry_path(self, key):
        if not isinstance(key, six.binary_type):
            key = key.encode("utf-8")
        entry_key = hashlib.sha256(key).hexdigest()
        args = [iter(entry_key)] * 3
        names = ("".join(z) for z in zip_longest(*args, fillvalue=""))
        return os.path.join(self._cache_dir, *names)
