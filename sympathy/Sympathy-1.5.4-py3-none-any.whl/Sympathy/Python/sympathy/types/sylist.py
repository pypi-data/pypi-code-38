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
"""Sympathy list type."""
from . import sybase
from . import exception as exc


def set_write_through(sylist_instance):
    assert(isinstance(sylist_instance, sylist))
    assert(sylist_instance._datasource is not sybase.NULL_SOURCE)
    sylistWriteThrough(sylist_instance)


def set_read_through(sylist_instance):
    assert(isinstance(sylist_instance, sylist))
    assert(sylist_instance._datasource is not sybase.NULL_SOURCE)
    sylistReadThrough(sylist_instance)


class sylistReadThrough(sybase.sygroup):

    def __init__(self, sylist_instance):
        self.__indices = range(len(self))

    def __new__(cls, sylist_instance):
        obj = sylist_instance
        obj.__class__ = cls
        return obj

    def create(self):
        return self._factory.from_type(self.content_type)

    def append(self, item):
        raise ValueError('Method not available on read-through.')

    def extend(self, other_list):
        raise ValueError('Method not available on read-through.')

    def source(self, other, shallow=False):
        raise ValueError('Method not available on read-through.')

    def visit(self, group_visitor):
        raise ValueError('Method not available on read-through.')

    def __copy__(self):
        obj = object.__new__(sylistReadThrough)
        obj.container_type = self.container_type
        obj._datasource = self._datasource
        obj._factory = self._factory
        obj._dirty = self._dirty
        obj._content_type = self._content_type
        obj.content_type = self.content_type
        obj.__indices = list(self.__indices)
        obj._cache = list(self._cache)

        return obj

    def __deepcopy__(self, memo=None):
        obj = self.__copy__()
        obj._cache = [None if v is None else v.__deepcopy__()
                      for v in self._cache]
        return obj

    def __len__(self):
        return len(self._cache)

    def __getitem__(self, index):
        """
        Returns a single sygroup by index if it exists in the datasource,
        otherwise None.
        """
        value = self._cache[index]
        if value is None:
            index = self.__indices[index]
            return self._factory.from_datasource(
                self._datasource.read_with_type(index, self._content_type),
                self.content_type)
        else:
            return value

    def __setitem__(self, index, item):
        raise ValueError('Method not available on read-through.')

    def __iter__(self):
        for i in range(len(self)):
            yield self[i]

    def __delitem__(self, index):
        raise ValueError('Method not available on read-through.')

    def __repr__(self):
        return str(self._cache)

    def writeback(self):
        pass

    def _writeback(self, datasource, link=None):
        writeback(self, datasource, link)


class sylistWriteThrough(sybase.sygroup):

    def __init__(self, sylist_instance):
        pass

    def __new__(cls, sylist_instance):
        length = len(sylist_instance)
        if length:
            raise Exception('Write-through requires empty list.')
        obj = sylist_instance
        obj.__class__ = cls
        obj.__count = length
        return obj

    def create(self):
        return self._factory.from_type(self.content_type)

    def append(self, item):
        """Append item to list."""
        # Ensure correct type?
        sybase.assert_type(self, item.container_type,
                           self.content_type)
        target = self._datasource
        content_type = self._content_type

        if item is not None:
            if not item._writeback(target, str(self.__count)):
                new_target = target.write_with_type(
                    str(self.__count), item, content_type)
                item._writeback(new_target)
            self.__count += 1
        self._dirty = True

    def extend(self, other_list):
        for item in other_list:
            self.append(item)

    def source(self, other, shallow=False):
        if self.__count:
            raise ValueError(
                'Method not available on write-through of modified table.')
        else:
            self.extend(other)

    def __copy__(self):
        raise ValueError('Method not available on write-through.')

    def __deepcopy__(self, memo=None):
        raise ValueError('Method not available on write-through.')

    def visit(self, group_visitor):
        raise ValueError('Method not available on write-through.')

    def __len__(self):
        return self.__count

    def __getitem__(self, index):

        return self._factory.from_datasource(
            self._datasource.read_with_type(index, self._content_type),
            self.content_type)

    def __setitem__(self, index, item):
        raise ValueError('Method not available on write-through.')

    def __iter__(self):
        for i in range(len(self)):
            yield self[i]

    def __delitem__(self, index):
        raise ValueError('Method not available on write-through.')

    def __repr__(self):
        raise ValueError('Method not available on write-through.')

    def writeback(self):
        pass

    def _writeback(self, datasource, link=None):
        pass


class sylist(sybase.sygroup):
    """A type representing a list."""
    def __init__(self, container_type, datasource=sybase.NULL_SOURCE,
                 items=None):
        """Init."""
        super(sylist, self).__init__(container_type,
                                     datasource or sybase.NULL_SOURCE)
        self.content_type = container_type[0]
        # __indices is used to distinguish between data in the sylist's
        # own datasource and external data which is only in the cache.
        # None values mean that the data is only in the cache.
        # Integer values mean that the data is found in the datasource using
        # the values as indices.
        self._content_type = self.content_type

        try:
            while True:
                self._content_type = self._content_type.get()
        except AttributeError:
            pass

        if datasource is sybase.NULL_SOURCE:
            self._cache = [] if items is None else items
            self.__indices = [None] * len(self._cache)
        else:
            size = self._datasource.size()
            self._cache = [None] * size
            self.__indices = list(range(size))

    def create(self):
        return self._factory.from_type(self.content_type)

    def append(self, item):
        """Append item to list."""
        # Ensure correct type?
        sybase.assert_type(self, item.container_type,
                           self.content_type)
        self._cache.append(item)
        self.__indices.append(None)

    def extend(self, other_list):
        """Extend list with other list."""
        try:
            other_container_type = other_list.container_type
        except AttributeError:
            # Assume well typed iterator.
            other_list = list(other_list)
        else:
            sybase.assert_type(self, other_container_type,
                               self.container_type)
        self._cache.extend(other_list)
        self.__indices.extend([None] * len(other_list))

    def source(self, other, shallow=False):
        self._cache = []
        self.__indices = []
        if shallow:
            self.extend(other)
        else:
            self.extend(other.__deepcopy__())

    def __copy__(self):
        obj = super(sylist, self).__copy__()
        obj._content_type = self._content_type
        obj.content_type = self.content_type
        obj.__indices = list(self.__indices)
        obj._cache = list(self._cache)
        return obj

    def __deepcopy__(self, memo=None):
        obj = self.__copy__()
        obj._cache = [None if v is None else v.__deepcopy__()
                      for v in self._cache]
        return obj

    def visit(self, group_visitor):
        """Accept group visitor."""
        group_visitor.visit_list(self)

    def __getitem__(self, index):
        """Get item."""
        def get_single_item(index):
            """
            Returns a single sygroup by index if it exists int the datasource,
            otherwise None.
            """
            index = self.__indices[index]
            return self._factory.from_datasource(
                self._datasource.read_with_type(index, self._content_type),
                self.content_type)

        if isinstance(index, slice):
            # Read slice from datasource.
            # Use cache for cached items.
            if self._datasource:
                # Make concrete list from slice index
                # and read each index separately.
                items = []
                for i in range(len(self._cache))[index]:
                    value = self._cache[i]
                    if value is not None:
                        items.append(value)
                    else:
                        value = get_single_item(i)
                        self._cache[i] = value
                    items.append(value)
                return sylist(self.container_type, items=items)
            else:
                # Read slice from cache.
                return sylist(
                    self.container_type, items=list(self._cache[index]))
        else:
            value = self._cache[index]
            if value is None:
                value = get_single_item(index)
                self._cache[index] = value
            return value

    def __setitem__(self, index, item):
        """Set item."""
        if isinstance(item, slice):
            sybase.assert_type(self, item.container_type,
                               self.container_type)
            self.__indices[index] = [None] * len(item)
        else:
            sybase.assert_type(self, item.container_type,
                               self.content_type)
            self.__indices[index] = None
        self._cache[index] = item

    def __iter__(self):
        self[:]
        return iter(self._cache)

    def __delitem__(self, index):
        del self._cache[index]
        del self.__indices[index]

    def __len__(self):
        return len(self._cache)

    def __repr__(self):
        return str(self._cache)

    def writeback(self):
        super(sylist, self).writeback()

    def _writeback(self, datasource, link=None):
        writeback(self, datasource, link)


def writeback(self, datasource, link=None):
    origin = self._datasource
    target = datasource

    exc.assert_exc(target.can_write, exc=exc.WritebackReadOnlyError)
    shared_origin = target.shares_origin(origin)
    content_type = self._content_type
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
                key, value, content_type)
            value._writeback(new_target)
    return True
