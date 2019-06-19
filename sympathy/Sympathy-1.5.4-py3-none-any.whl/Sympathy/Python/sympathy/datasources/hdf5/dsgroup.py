# Copyright (c) 2013, Combine Control Systems AB
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of the Combine Control Systems AB nor the
#       names of its contributors may be used to endorse or promote products
#       derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.
# IN NO EVENT SHALL COMBINE CONTROL SYSTEMS AB BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""HDF5 group."""
from __future__ import (print_function, division, unicode_literals,
                        absolute_import)
import sys
import json
import math
import warnings
from collections import OrderedDict

# Ignore a warning from numpy>=1.14 when importing h5py<=2.7.1:
with warnings.catch_warnings():
    warnings.simplefilter('ignore', FutureWarning)
    import h5py

from sympathy.platform.state import hdf5_state
from sympathy.version import __version__ as platform_version
_fs_encoding = sys.getfilesystemencoding()


UTF8 = 'utf-8'
REPLACE_SLASH = chr(0x01)
USERBLOCK_MIN_SIZE = 512
VERSION = 'Version'
VERSION_NUMBER = '1.0'
TYPE = 'Type'
TYPEALIAS = 'TypeAlias'
IDENTIFIER = 'SFD HDF5'
PLATFORM = 'Platform'


def read_header(filepath):
    """
    Read the header from hdf5 file and return an ordered dict with its content.
    """
    with open(filepath, 'rb') as hdf5:
        identifier = hdf5.read(len(IDENTIFIER))
        line = hdf5.readline()
        assert(identifier == IDENTIFIER.encode('ascii'))
        header_data = json.loads(
            line.decode('ascii'), object_pairs_hook=OrderedDict)
        return header_data


def write_header(filepath, header_data):
    """
    Write header_data dictionary to the file at filepath.
    The file must have sufficient space in its userblock.
    """
    with open(filepath, 'r+b') as hdf5:
        hdf5.write(header_data)
        hdf5.write(b'\x00' * (
            _header_data_size(header_data) - len(header_data)))


def _header_data(datatype, type):
    """Return dictionary of header data with data type included."""
    return '{}{}\n'.format(
        IDENTIFIER,
        json.dumps(OrderedDict(
            [(VERSION, VERSION_NUMBER), (TYPE, datatype),
             (TYPEALIAS, type),
             (PLATFORM, platform_version)]))).encode('ascii')


def _header_data_size(header_data):
    """Return length of header data with data type included."""
    length = len(header_data)
    return max(2 ** int(math.ceil(math.log(length, 2))), USERBLOCK_MIN_SIZE)


def replace_slash(string):
    """
    Replace special '/' character with very rare unicode character 0xFFFF.
    """
    return string.replace('/', REPLACE_SLASH)


def restore_slash(string):
    """
    Restore special '/' character replaced with very rare unicode character
    0xFFFF.
    """
    return string.replace(REPLACE_SLASH, '/')


def create_path(h5file, path):
    """Create path in file returning the group at h5file[path]."""
    curr_group = h5file

    for component in [x for x in path.split('/') if x]:
        try:
            next_group = curr_group[component]
        except KeyError:
            next_group = curr_group.create_group(component)
        curr_group = next_group
    return curr_group


def get_path(h5file, path):
    """Create path in file returning the group at h5file[path]."""
    curr_group = h5file
    for component in [x for x in path.split('/') if x]:
        curr_group = curr_group[component]
    return curr_group


class GroupWrapper(object):
    def __init__(self, group):
        self.__group = group
        file_ = group.file
        self.filename = file_.filename
        self.mode = file_.mode
        self.name = group.name
        self._files = {}
        self._cache = {}

    @property
    def _group(self):
        if self.is_closed():
            self.__group = hdf5_state().open(self.filename, 'r')[self.name]
        return self.__group

    def create_group(self, name):
        assert name not in self._cache
        group = GroupWrapper(
            self._group.create_group(name))
        self._cache[name] = group
        return group

    def create_dataset(self, name, **kwargs):
        assert name not in self._cache
        return self._group.create_dataset(name, **kwargs)

    def __getitem__(self, key):
        res = self._cache.get(key)
        group = self._group
        if not res:
            lnk = group.get(key, getlink=True)
            if not isinstance(lnk, h5py.ExternalLink):
                res = group[key]
                if isinstance(res, h5py.Group):
                    res = GroupWrapper(res)
                    self._cache[key] = res
            else:
                lnk_filename = lnk.filename
                file_group = self._files.get(lnk_filename)
                if not file_group:
                    file_group = GroupWrapper(hdf5_state().open(
                        lnk_filename, 'r'))
                    self._files[lnk_filename] = file_group

                full_path = tuple([x for x in lnk.path.split('/') if x])
                res = file_group._group
                for path in full_path:
                    res = res[path]

                if isinstance(res, h5py.Group):
                    res = GroupWrapper(res)
                    self._cache[key] = res
        return res

    def __setitem__(self, key, value):
        assert not (isinstance(value, GroupWrapper) or
                    isinstance(value, h5py.Group))
        assert key not in self._cache
        self._group[key] = value

    def __contains__(self, key):
        return key in self._group

    def __len__(self):
        return len(self._group)

    def get(self, key, default=None):
        if key in self:
            return self[key]
        return default

    def getlink(self, key):
        lnk = self._group.get(key, getlink=True)
        if isinstance(lnk, h5py.ExternalLink):
            return lnk

    def keys(self):
        return self._group.keys()

    @property
    def attrs(self):
        return self._group.attrs

    def is_closed(self):
        return not bool(self)

    def __bool__(self):
        return False if self.__group is None else bool(self.__group)

    def __nonzero__(self):
        return self.__bool__()

    @property
    def file(self):
        return self.__group.file


class Hdf5Group(object):
    """Abstraction of an HDF5-group."""
    def __init__(self, factory, group, datapointer, can_write, can_link):
        self.factory = factory
        self._group = group
        self._header_data = None

        if self._group is not None:
            self.can_link = can_link
            self.can_write = can_write
            self.datatype = None
            self.type = None
            self.filepath = None
            self.mode = None
            self.path = None
            self.util = None
            if not isinstance(group, GroupWrapper):
                self._group = GroupWrapper(group)
        else:
            util = datapointer.util()
            self.mode = util.mode()
            self.can_link = util.can_link()
            self.can_write = can_write or self.mode in ['r+', 'w']
            self.datatype = util.datatype()
            self.type = util.abstype()
            self.filepath = util.file_path()
            self.path = util.path()
            self.util = util

            if self.mode == 'r':
                try:
                    h5file = hdf5_state().open(self.filepath, 'r')
                    group = GroupWrapper(h5file)
                except ValueError:
                    raise IOError(
                        'Could not open assumed hdf5-file : "{}"'.format(
                            self.filepath))
                self._group = get_path(group, self.path)

            elif self.mode == 'w':
                # Create new hdf5 file with userblock set.
                self._header_data = _header_data(
                    self.util.datatype(), self.util.abstype())

                h5file = h5py.File(
                    self.filepath, self.mode,
                    userblock_size=_header_data_size(
                        self._header_data))
                hdf5_state().add(self.filepath, h5file)
                group = GroupWrapper(h5file)
                self._group = create_path(group, self.path)

    @property
    def group(self):
        return self._group

    def _group_get_or_create(self, key):
        group = self.group
        if key in group:
            chldgroup = group[key]
        else:
            chldgroup = group.create_group(key)
        return chldgroup

    def transferable(self, other):
        """
        Returns True if the content from datasource can be linked directly,
        and False otherwise.
        """
        return (self.can_link and other.can_link and
                isinstance(other, Hdf5Group))

    def transfer(self, name, other, other_name):
        """
        Performs linking if possible, this is only allowed if transferrable()
        returns True.
        """
        pass

    def link(self):
        group = self.group
        return h5py.ExternalLink(
            group.filename,
            group.name)

    def shares_origin(self, other):
        """
        Checks if two datasources originate from the same resource.
        """
        try:
            group = self.group
            other_group = other.group

            return (
                group.filename ==
                other_group.filename and
                group.name == other_group.name)
        except Exception:
            return False

    def write_link(self, name, other, other_name):
        lnk = other.group.getlink(other_name)
        if lnk is None:
            group = other.group
            lnk = h5py.ExternalLink(
                group.filename,
                group.name + '/' + other_name)

        self.group[name] = lnk
        return True

    def close(self):
        """Close the hdf5 file using the group member."""
        # If open fails, avoid causing argument exception on close.
        if self._group is not None:
            hdf5_state()._close_file(self.group)
            if self.mode == 'w':
                write_header(self.filepath, self._header_data)

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()
