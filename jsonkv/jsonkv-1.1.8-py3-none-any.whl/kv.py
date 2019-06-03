# coding: utf-8

import json
from copy import deepcopy
import os
from datetime import date, datetime

from .filelock import FileLock, FileLockException


class JsonKV(object):
    def __init__(self, path: str, mode: str = "r+", dumps_kwargs=None, encoding='utf8', no_lock=False):
        self.path = path
        self.mode = mode
        self.encoding = encoding
        self.dumps_kwargs = dumps_kwargs
        self.no_lock = no_lock
        self.data = {}
        self.file_lock = FileLock(self.path)

    def __enter__(self):
        if not self.no_lock:
            try:
                self.file_lock.acquire()
            except FileLockException as e:
                raise FileLockException(
                    f"json file is locked, try remove {self.file_lock.lockfile}"
                )

        if not os.path.isfile(self.path):
            open(self.path, "w").close()

        self.f = open(self.path, self.mode, encoding=self.encoding)
        try:
            content = self.f.read()
            self.data = json.loads(content)
        except json.decoder.JSONDecodeError as e:
            # print('Warning: {}'.format(e))
            pass
        self.origin_data = deepcopy(self.data)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.save()
        self.close()
        if not self.no_lock:
            self.file_lock.release()

    def __getitem__(self, item):
        if item in self.data:
            return self.data[item]

    def __setitem__(self, key, value):
        self.data[key] = value

    def __iter__(self):
        return dict.__iter__(self.data)

    def save(self):
        if self.f.writable():
            self.f.truncate(0)
            self.f.seek(0)
            self.f.write(
                json.dumps(
                    self.data,
                    ensure_ascii=False,
                    default=self.json_serial,
                    **(self.dumps_kwargs or {}),
                )
            )

    def close(self):
        self.f.close()

    def restore(self):
        self.data = deepcopy(self.origin_data)

    @staticmethod
    def json_serial(obj):
        """JSON serializer for objects not serializable by default json code"""

        if isinstance(obj, datetime):
            return obj.strftime("%Y-%m-%d %X")
        elif isinstance(obj, date):
            return obj.strftime("%Y-%m-%d")

        raise TypeError("Type %s not serializable" % type(obj))
