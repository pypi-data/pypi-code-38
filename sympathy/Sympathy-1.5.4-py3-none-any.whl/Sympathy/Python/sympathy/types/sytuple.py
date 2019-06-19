# -*- coding:utf-8 -*-
# Copyright (c) 2017, Combine Control Systems AB
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
from . import sybase
from . import exception as exc


def _int_index_guard(index):
    if not isinstance(index, int):
        raise TypeError(
            u'Only basic integer indexing is supported, not: "{}"'
            .format(index))


class sytuple(sybase.sygroup):
    def __init__(self, container_type, datasource=sybase.NULL_SOURCE):
        super(sytuple, self).__init__(container_type,
                                      datasource or sybase.NULL_SOURCE)
        self.content_types = []
        self._content_types = []

        for content_type in container_type:
            self.content_types.append(content_type)
            try:
                while True:
                    content_type = content_type.get()
            except AttributeError:
                self._content_types.append(content_type)

        self._cache = [None] * len(container_type)

    def __repr__(self):
        return str(self._cache)

    def __len__(self):
        return len(self._cache)

    def __iter__(self):
        for i in range(len(self._cache)):
            yield self.__getitem__(i)

    def __getitem__(self, index):
        _int_index_guard(index)

        value = self._cache[index]
        if value is None:
            content_type = self.content_types[index]
            try:
                # Read from datasource.
                source = self._datasource.read_with_type(
                    str(index), self._content_types[index])
            except KeyError:
                # Create content without datasource.
                value = self._factory.from_type(content_type)
            else:
                # Create content from datasource.
                source = source or sybase.NullSource
                value = self._factory.from_datasource(
                    source,
                    content_type)
            self._cache[index] = value
        return value

    def __setitem__(self, index, value):
        _int_index_guard(index)
        content_type = self.content_types[index]
        sybase.assert_type(
            self, value.container_type, content_type)
        self._cache[index] = value

    def __copy__(self):
        obj = super(sytuple, self).__copy__()
        obj.content_types = self.content_types
        obj._content_types = self._content_types
        obj._datasource = self._datasource
        obj._cache = list(self._cache)
        return obj

    def __deepcopy__(self, memo=None):
        obj = self.__copy__()
        obj._cache = [None if v is None else v.__deepcopy__()
                      for v in self._cache]
        return obj

    def update(self, other):
        sybase.assert_type(
            self, self.container_type, other.container_type)
        self._cache = list(other)

    def source(self, other, shallow=False):
        if shallow:
            self.update(other)
        else:
            self.update(other.__deepcopy__())

    def writeback(self):
        super(sytuple, self).writeback()

    def _writeback(self, datasource, link=None):
        origin = self._datasource
        target = datasource
        exc.assert_exc(target.can_write, exc=exc.WritebackReadOnlyError)
        shared_origin = target.shares_origin(origin)
        linkable = not shared_origin and target.transferable(origin)

        if link:
            return False

        for i, value in enumerate(self._cache):
            key = str(i)
            if value is None:
                if linkable and target.write_link(key, origin, key):
                    pass
                else:
                    value = self[i]

            if value is not None and not value._writeback(target, key):
                new_target = target.write_with_type(
                    key, value, self._content_types[i])
                value._writeback(new_target)
        return True
