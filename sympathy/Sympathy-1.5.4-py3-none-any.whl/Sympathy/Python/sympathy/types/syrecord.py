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
"""Sympathy record type."""
import six
from six.moves import zip as izip
from . import sybase
from . import exception as exc


def get_field(fields, field):
    """Returns fields[field], raises AttributeError on KeyError."""
    try:
        return fields[field]
    except KeyError:
        raise AttributeError(
            "'syrecord' object has no attribute '{0}'".format(field))


def get_fields(self):
    """
    Returns the fields element or an empty dictionary when the attribute does
    not exist.
    Used internally, for __getattr__ and __setattr__ only.
    """
    try:
        fields = self.__getattribute__('_fields')
    except AttributeError:
        fields = {}
    return fields


class syrecord(sybase.sygroup):
    """A type representing a list."""
    def __init__(self, container_type, datasource=sybase.NULL_SOURCE):
        """Init."""
        keys = container_type.keys()
        super(syrecord, self).__init__(container_type,
                                       datasource or sybase.NULL_SOURCE)
        self.content_types = {}
        self._content_types = {}
        for key in keys:
            content_type = container_type[key]
            self.content_types[key] = content_type
            try:
                while True:
                    content_type = content_type.get()
            except AttributeError:
                self._content_types[key] = content_type

        self._fields = keys
        self._cache = dict.fromkeys(keys)

    def __getattr__(self, field):
        """Get attribute."""
        if field not in get_fields(self):
            return super(syrecord, self).__getattribute__(field)

        try:
            value = self._cache[field]
            if value is None:
                # Value is not cached, read it from datasource.
                content_type = self.content_types[field]
                try:
                    # Read from datasource.
                    source = self._datasource.read_with_type(
                        field, self._content_types[field])
                except KeyError:
                    # Create content without datasource.
                    value = self._factory.from_type(content_type)
                else:
                    # Create content from datasource.
                    source = source or sybase.NullSource
                    value = self._factory.from_datasource(
                        source, content_type)
                self._cache[field] = value
            return value
        except KeyError:
            raise AttributeError()

    def __setattr__(self, field, value):
        """Set attribute."""
        if field in get_fields(self):
            content_type = get_field(self.content_types, field)
            sybase.assert_type(
                self, value.container_type, content_type)
            self._cache[field] = value
        else:
            super(syrecord, self).__setattr__(field, value)

    def __repr__(self):
        return str(self._cache)

    def keys(self):
        """Returns a list of all record keys."""
        return list(self._fields)

    def values(self):
        """Returns a list of all values."""
        return [getattr(self, field) for field in self._fields]

    def items(self):
        """Return generator iterator over key, value pairs."""
        return izip(self.keys(), self.values())

    def update(self, other):
        """
        Updates current record with items from 'other record', replacing values
        with the same key; update requires the item types to match.
        """
        for other_key, other_value in other.items():
            setattr(self, other_key, other_value)

    def source(self, other, shallow=False):
        if shallow:
            self.update(other)
        else:
            self.update(other.__deepcopy__())

    def __copy__(self):
        obj = super(syrecord, self).__copy__()
        obj.content_types = self.content_types
        obj._content_types = self._content_types
        obj._fields = self._fields
        obj._cache = dict(self._cache)
        return obj

    def __deepcopy__(self, memo=None):
        obj = self.__copy__()
        obj._cache = {k: None if v is None else v.__deepcopy__()
                      for k, v in six.iteritems(self._cache)}
        return obj

    def __iter__(self):
        for k in self.keys:
            yield k

    def visit(self, group_visitor):
        """Accept group visitor."""
        group_visitor.visit_record(self)

    def writeback(self):
        super(syrecord, self).writeback()

    def _writeback(self, datasource, link=None):
        origin = self._datasource
        target = datasource
        exc.assert_exc(target.can_write, exc=exc.WritebackReadOnlyError)
        shared_origin = target.shares_origin(origin)
        linkable = not shared_origin and target.transferable(origin)

        if link:
            return False

        for key in self._fields:
            value = self._cache.get(key)
            if value is None:
                if linkable and target.write_link(key, origin, key):
                    pass
                else:
                    value = getattr(self, key)

            if value is not None:
                if not value._writeback(target, key):
                    new_target = target.write_with_type(
                        key, value, self._content_types[key])
                    value._writeback(new_target)

        return True
