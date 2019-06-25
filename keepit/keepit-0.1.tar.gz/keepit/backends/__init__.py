import os
import pickle
import time
import sqlite3

from glob import glob

from pathlib import Path

ROOT = os.path.join(Path.home(), '.keepit')


ROOT = os.path.abspath(os.path.basename(__file__))
CACHE_DIR = os.environ.get('CACHE_DIR', os.path.join(ROOT, '_cache'))


class NotFound(Exception):
    pass


class BackEnd():

    def exists(self, oid):
        raise NotImplementedError()

    def read(self, oid):
        raise NotImplementedError()

    def put(self, entry):
        raise NotImplementedError()

    def remove(self, oid):
        raise NotImplementedError()

    def find(self, *args, **kwargs):
        return list(self.ifind(*args, **kwargs))

    def ifind(self, oid=None, tags=[]):
        raise NotImplementedError()

    def erase_all(self):
        for entry in self.find():
            self.remove(entry.id)


class Entry:

    def __init__(self, id, content, tags=[], timestamp=None):
        self.id = id
        self.timestamp = time.localtime(timestamp or time.time())
        self.content = content
        self.tags = set(tags)

    def __repr__(self):
        return str(self)

    def __str__(self):
        return '{} @ {} [{}]'.format(self.id, time.strftime('%Y-%m-%d %H:%M', self.timestamp), ','.join(self.tags))


class Pickle(BackEnd):
    res_folder = 'results'

    def __init__(self):
        pass

    def _filename(self, oid):
        return os.path.join(self.res_folder, "{}.pickle".format(oid))

    def _open(self, fpath, abs=False):
        if not abs:
            fpath = self._filename(fpath)
        with open(fpath, 'rb') as f:
            return pickle.load(f)

    def put(self, entry):
        if not os.path.exists(self.res_folder):
            os.makedirs(self.res_folder)
        with open(self._filename(entry.id), 'wb') as f:
            pickle.dump(entry, f)

    def exists(self, oid):
        return os.path.exists(self._filename(oid))

    def get(self, oid):
        s = self._open(oid)
        return s

    def remove(self, oid):
        return os.remove(self._filename(oid))

    def ifind(self, oid=None, tags=[]):
        target = set(tags)
        for f in glob(os.path.join(self.res_folder, '*')):
            e = self._open(f, abs=True)
            if (not oid or f.id == oid) and e.tags.issuperset(tags):
                yield e
