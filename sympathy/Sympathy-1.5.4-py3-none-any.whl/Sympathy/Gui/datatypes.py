# This file is part of Sympathy for Data.
# Copyright (c) 2013 Combine Control Systems AB
#
# Sympathy for Data is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Sympathy for Data is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Sympathy for Data.  If not, see <http://www.gnu.org/licenses/>.
"""
Primitive handling of data types
"""
from __future__ import (print_function, division, unicode_literals,
                        absolute_import)
import six
from sympathy.types import types

_types = {}
_icons = {}
_cache = {}


def replace_types(string):
    if string == 'adafs':
        return '[adaf]'
    elif string == 'tables':
        return '[table]'
    elif string == 'datasources':
        return '[datasource]'
    elif string == 'texts':
        return '[text]'
    elif string == 'reports':
        return '[report]'
    return string


class DataType(object):
    """Data type wrapper, contains information on icon etc."""

    def __init__(self, datatype):
        super(DataType, self).__init__()
        self._list = False
        assert(datatype is not None)
        self._datatype = datatype
        self._generics = None

    @classmethod
    def from_datatype(cls, datatype):
        return cls(types.copy(datatype.datatype))

    @classmethod
    def from_str(cls, datatype):
        string = replace_types(datatype)
        dt = _cache.get(string)
        if dt is None:
            dt = types.parse_base_line(string)
            _cache[string] = dt
        else:
            dt = types.copy(dt)
        return cls(dt)

    @property
    def datatype(self):
        return self._datatype

    @property
    def icon(self):
        from .flowview import port_icon
        return port_icon.icon(self._datatype, _icons)

    def identify(self, generics_map):
        types.identify(self._datatype, generics_map)

    def match(self, other, mapping=None):
        return types.match(self._datatype, other._datatype, mapping)

    def instantiate(self, mapping):
        self._datatype = types.instantiate(self._datatype, mapping)

    def generics(self):
        if self._generics is None:
            self._generics = types.generics(self._datatype)
        return self._generics

    @classmethod
    def from_datatypes_function(cls, datatypes):

        if len(datatypes) == 1:
            return datatypes[0]

        types_ = [datatype.datatype for datatype in datatypes]

        rdtypeiter = reversed(types_)
        result = six.next(rdtypeiter)

        for arg in rdtypeiter:
            result = types.TypeFunction(arg, result)

        return DataType(result)

    @classmethod
    def from_length_function(cls, length):
        assert length > 1
        return cls.from_datatypes_function(
            [cls.from_str('<t{}>'.format(i)) for i in range(length)])

    def __str__(self):
        return str(self._datatype)

    @property
    def html(self):
        return str(self).replace(
            '->', '&rarr;').replace('<', '&lt;').replace('>', '&gt;')


def register_datatype(datatype, icon=None):
    _types[datatype] = DataType.from_str(datatype)
    _icons[datatype] = icon
    return _types[datatype]


def _from_str(datatype, icon=None):
    try:
        return _types[datatype]
    except KeyError:
        return register_datatype(datatype, icon)


Lambda = DataType.from_str('a -> b')
Any = _from_str('<a>')
