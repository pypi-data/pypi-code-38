# Copyright (C) 2017-2018  The Software Heritage developers
# See the AUTHORS file at the top-level directory of this distribution
# License: GNU General Public License version 3, or any later version
# See top-level LICENSE file for more information

"""This document contains various helper classes used in converting Mercurial
bundle files into SWH Contents, Directories, etc.
"""

import binascii
import copy
import os
import sys
import pickle
import sqlite3
import zlib

from collections import OrderedDict
from sqlitedict import SqliteDict

from swh.model import identifiers

OS_PATH_SEP = os.path.sep.encode('utf-8')


def _encode(obj):
    return sqlite3.Binary(zlib.compress(
        pickle.dumps(obj, pickle.HIGHEST_PROTOCOL)))


def _decode(obj):
    return pickle.loads(
        zlib.decompress(bytes(obj)))


class SimpleBlob:
    """Stores basic metadata of a blob object.when constructing deep trees from
    commit file manifests.

    args:
        file_hash: unique hash of the file contents
        is_symlink: (bool) is this file a symlink?
        file_perms: (string) 3 digit permission code as a string or bytestring,
                    e.g. '755' or b'755'
    """

    kind = 'file'

    def __init__(self, file_hash, is_symlink, file_perms):
        self.hash = file_hash
        self.perms = 0o100000 + int(file_perms, 8)
        if is_symlink:
            self.perms += 0o020000

    def __str__(self):
        return ('SimpleBlob: ' + str(self.hash) + ' -- ' + str(self.perms))

    def __eq__(self, other):
        return ((self.perms == other.perms) and (self.hash == other.hash))

    def size(self):
        """Return the size in byte."""
        return sys.getsizeof(self) + sys.getsizeof(self.__dict__)


class SimpleTree(dict):
    """ Stores data for a nested directory object. Uses shallow cloning to stay
    compact after forking and change monitoring for efficient re-hashing.
    """

    kind = 'dir'
    perms = 0o040000

    def __init__(self):
        self.hash = None
        self._size = None

    def __eq__(self, other):
        return ((self.hash == other.hash) and (self.items() == other.items()))

    def _new_tree_node(self, path):
        """Deeply nests SimpleTrees according to a given subdirectory path and
        returns a reference to the deepest one.

        args:
            path: bytestring containing a relative path from self to a deep
                  subdirectory. e.g. b'foodir/bardir/bazdir'

        returns:
            the new node
        """
        node = self
        for d in path.split(OS_PATH_SEP):
            if node.get(d):
                if node[d].hash is not None:
                    node[d] = copy.copy(node[d])
                    node[d].hash = None
                    node[d]._size = None
            else:
                node[d] = SimpleTree()
            node = node[d]
        return node

    def remove_tree_node_for_path(self, path):
        """Deletes a SimpleBlob or SimpleTree from inside nested SimpleTrees
        according to the given relative file path, and then recursively removes
        any newly depopulated SimpleTrees. It keeps the old history by doing a
        shallow clone before any change.

        args:
            path: bytestring containing a relative path from self to a nested
                  file or directory. e.g. b'foodir/bardir/bazdir/quxfile.txt'

        returns:
            the new root node
        """
        node = self
        if node.hash is not None:
            node = copy.copy(node)
            node.hash = None
            node._size = None
        first, sep, rest = path.partition(OS_PATH_SEP)
        if rest:
            node[first] = node[first].remove_tree_node_for_path(rest)
            if len(node[first]) == 0:
                del node[first]
        else:
            del node[first]

        return node

    def add_blob(self, file_path, file_hash, is_symlink, file_perms):
        """Shallow clones the root node and then deeply nests a SimpleBlob
        inside nested SimpleTrees according to the given file path, shallow
        cloning all all intermediate nodes and marking them as changed and
        in need of new hashes.

        args:
            file_path: bytestring containing the relative path from self to a
                       nested file
            file_hash: primary identifying hash computed from the blob contents
            is_symlink: True/False whether this item is a symbolic link
            file_perms: int or string representation of file permissions

        returns:
            the new root node
        """
        root = self
        if root.hash is not None:
            root = copy.copy(root)
            root.hash = None
            root._size = None
        node = root
        fdir, fbase = os.path.split(file_path)
        if fdir:
            node = root._new_tree_node(fdir)
        node[fbase] = SimpleBlob(file_hash, is_symlink, file_perms)
        return root

    def yield_swh_directories(self):
        """Converts nested SimpleTrees into a stream of SWH Directories.

        yields:
            an SWH Directory for every node in the tree
        """
        for k, v in sorted(self.items()):
            if isinstance(v, SimpleTree):
                yield from v.yield_swh_directories()

        yield {
            'id': self.hash,
            'entries': [
                {
                    'name': k,
                    'perms': v.perms,
                    'type': v.kind,
                    'target': v.hash
                }
                for k, v in sorted(self.items())
            ]
        }

    def hash_changed(self, new_dirs=None):
        """Computes and sets primary identifier hashes for unhashed subtrees.

        args:
            new_dirs (optional): an empty list to be populated with the SWH
                                 Directories for all of the new (not previously
                                 hashed) nodes

        returns:
            the top level hash of the whole tree
        """
        if self.hash is None:
            directory = {
                'entries': [
                    {
                        'name': k,
                        'perms': v.perms,
                        'type': v.kind,
                        'target': (v.hash if v.hash is not None
                                   else v.hash_changed(new_dirs))
                    }
                    for k, v in sorted(self.items())
                ]
            }

            self.hash = binascii.unhexlify(
                identifiers.directory_identifier(directory)
            )
            directory['id'] = self.hash
            if new_dirs is not None:
                new_dirs.append(directory)

        return self.hash

    def flatten(self, _curpath=None, _files=None):
        """Converts nested sub-SimpleTrees and SimpleBlobs into a list of
        file paths. Useful for counting the number of files in a manifest.

        returns:
            a flat list of all of the contained file paths
        """
        _curpath = _curpath or b''
        _files = _files or {}
        for k, v in sorted(self.items()):
            p = os.path.join(_curpath, k)
            if isinstance(v, SimpleBlob):
                _files[p] = (v.hash, v.perms)
            else:
                v.flatten(p, _files)
        return _files

    def size(self):
        """Return the (approximate?) memory utilization in bytes of the nested
        structure.
        """
        if self._size is None:
            self._size = (
                sys.getsizeof(self) + sys.getsizeof(self.__dict__)
                + sum([
                    sys.getsizeof(k)+v.size()
                    for k, v in self.items()
                ])
            )
        return self._size


class SelectiveCache(OrderedDict):
    """Special cache for storing past data upon which new data is known to be
    dependent. Optional hinting of how many instances of which keys will be
    needed down the line makes utilization more efficient. And, because the
    distance between related data can be arbitrarily long and the data
    fragments can be arbitrarily large, a disk-based secondary storage is used
    if the primary RAM-based storage area is filled to the designated capacity.

    Storage is occupied in three phases:
        1) The most recent key/value pair is always held, regardless of other
           factors, until the next entry replaces it.
        2) Stored key/value pairs are pushed into a randomly accessible
           expanding buffer in memory with a stored size function, maximum size
           value, and special hinting about which keys to store for how long
           optionally declared at instantiation.
        3) The in-memory buffer pickles into a randomly accessible disk-backed
           secondary buffer when it becomes full.

    Occupied space is calculated by default as whatever the len() function
    returns on the values being stored. This can be changed by passing in a new
    size_function at instantiation.

    The cache_hints parameter is a dict of key/int pairs recording how many
    subsequent fetches that particular key's value should stay in storage for
    before being erased. If you provide a set of hints and then try to store a
    key that is not in that set of hints, the cache will store it only while it
    is the most recent entry, and will bypass storage phases 2 and 3.
    """
    DEFAULT_SIZE = 800*1024*1024  # bytes or whatever

    def __init__(self, max_size=None, cache_hints=None,
                 size_function=None, filename=None):
        """args:
                max_size: integer value indicating the maximum size of the part
                          of storage held in memory
                cache_hints: dict of key/int pairs as described in the class
                             description
                size_function: callback function that accepts one parameter and
                               returns one int, which should probably be the
                               calculated size of the parameter
        """
        self._max_size = max_size or SelectiveCache.DEFAULT_SIZE
        self._disk = None
        if size_function is None:
            self._size_function = sys.getsizeof
        else:
            self._size_function = size_function
        self._latest = None
        self._cache_size = 0
        self._cache_hints = copy.copy(cache_hints) or None
        self.filename = filename

    def store(self, key, data):
        """Primary method for putting data into the cache.

        args:
            key: any hashable value
            data: any python object (preferably one that is measurable)

        """
        self._latest = (key, data)

        if (self._cache_hints is not None) and (key not in self._cache_hints):
            return

        # cache the completed data...
        self._cache_size += self._size_function(data) + 53

        # ...but limit memory expenditure for the cache by offloading to disk
        should_commit = False
        while (
            self._cache_size > self._max_size
            and len(self) > 0
        ):
            should_commit = True
            k, v = self.popitem(last=False)
            self._cache_size -= self._size_function(v) - 53
            self._diskstore(k, v)

        if should_commit:
            self._disk.commit(blocking=False)

        self[key] = data

    def _diskstore(self, key, value):
        if self._disk is None:
            self._disk = SqliteDict(
                autocommit=False, journal_mode='OFF',
                filename=self.filename, tablename='swh',
                encode=_encode, decode=_decode)
            self._disk.in_temp = True  # necessary to force the disk clean up
        self._disk[key] = value

    def has(self, key):
        """Tests whether the data for the provided key is being stored.

        args:
            key: the key of the data whose storage membership property you wish
                 to discover

        returns:
            True or False
        """
        return (
            (self._latest and self._latest[0] == key)
            or (key in self)
            or (self._disk and (key in self._disk))
        )

    def fetch(self, key):
        """Pulls a value out of storage and decrements the hint counter for the
            given key.

        args:
            key: the key of the data that you want to retrieve

        returns:
            the retrieved value or None
        """
        retval = None
        if self._latest and self._latest[0] == key:
            retval = self._latest[1]
        if retval is None:
            retval = self.get(key)
            if (retval is None) and self._disk:
                self._disk.commit(blocking=False)
                retval = self._disk.get(key) or None
            self.dereference(key)
        return retval

    def dereference(self, key):
        """Remove one instance of expected future retrieval of the data for the
        given key. This is called automatically by fetch requests that aren't
        satisfied by phase 1 of storage.

        args:
            the key of the data for which the future retrievals hint is to be
            decremented
        """
        newref = self._cache_hints and self._cache_hints.get(key)
        if newref:
            newref -= 1
            if newref == 0:
                del self._cache_hints[key]
                if key in self:
                    item = self[key]
                    self._cache_size -= self._size_function(item)
                    del self[key]
                else:
                    if self._disk:
                        del self._disk[key]
            else:
                self._cache_hints[key] = newref

    def keys(self):
        yield from self.keys()
        if self._disk:
            yield from self._disk.keys()

    def values(self):
        yield from self.values()
        if self._disk:
            yield from self._disk.values()

    def items(self):
        yield from self.items()
        if self._disk:
            yield from self._disk.items()
