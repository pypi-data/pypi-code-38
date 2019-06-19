# Copyright (c) 2013-2016, Combine Control Systems AB
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

"""Sympathy table."""
from __future__ import (print_function, division, unicode_literals,
                        absolute_import)
from collections import OrderedDict
import six
import warnings
import numpy as np
import dask.array as da
import datetime
from . import sybase
from . import exception as exc

_max_guard_repr_chars = 200


def _get_none_object_dtype(arr, name):
    def nparray(a, dtype):
        if isinstance(a, np.ma.MaskedArray):
            return np.ma.array(a.data, mask=a.mask, dtype=dtype)
        else:
            return np.array(a, dtype=dtype)

    # Attempting to create a specific non-object based numpy type.
    if isinstance(arr, np.ma.MaskedArray):
        # Need to avoid getting np.ma.masked as first value.
        idata = iter(arr.data)
    else:
        idata = iter(arr)

    first = None

    for first in idata:
        if first is not None:
            break

    if first is None:
        return np.array([])

    try:
        # Determining type from the first element.
        if isinstance(first, datetime.datetime):
            # Datetime.
            arr = nparray(arr, dtype='datetime64[us]')
        elif isinstance(first, datetime.timedelta):
            # Timedelta.
            # Avoid exception that can occur in numpy when converting zero
            # value timedeltas.
            # These problems vary with the numpy version, hinting at some
            # bug.
            temp_arr = np.zeros_like(arr, dtype='timedelta64[us]')
            indices = np.where(arr != datetime.timedelta(0))[0]
            for i in indices:
                temp_arr[i] = arr[i]
            arr = temp_arr
        else:
            # No conversion possible.
            raise ValueError()
    except (ValueError, TypeError):
        raise exc.DatasetTypeError(
            'Unsupported object type in column {}'.format(name))
    return arr


def _column_factory(datasource, column, nrows):
    assert(datasource != sybase.NULL_SOURCE)
    return Column(source=OnDiskColumnSource(datasource, column, nrows))


class Source(object):

    def get(self):
        raise NotImplementedError

    def link(self, name, datasource):
        raise NotImplementedError

    def write(self, name, datasource):
        raise NotImplementedError

    @property
    def dirty(self):
        raise NotImplementedError


class InMemoryColumnSource(Source):

    def __init__(self, obj, attrs=None):
        self._obj = obj
        self._attrs = attrs or {}

    def get(self, index=None, get_array=True):
        res = self._obj
        if index is not None:
            res = self._obj[index]
        return res

    def link(self, name, attrs, datasource):
        self.write(name, attrs, datasource)

    def write(self, name, attrs, datasource):
        datasource.write_column(name, self.get())
        datasource.write_column_attributes(name, attrs)

    @property
    def dirty(self):
        return True

    @property
    def dtype(self):
        return self._obj.dtype

    @property
    def attrs(self):
        return {}

    def __len__(self):
        return len(self._obj)


class OnDiskColumnSource(Source):

    def __init__(self, datasource, key, nrows=None):
        self._datasource = datasource
        self._key = key
        self._nrows = nrows

    def __hash__(self):
        return hash(self._datasource.file.filename,
                    self._datasource.group.name,
                    self._key)

    def get(self, index=None, get_array=True):
        res = self._datasource.read_column(self._key)
        if index is not None:
            with warnings.catch_warnings():
                warnings.simplefilter('ignore', FutureWarning)
                res = res[index]
        return res

    def link(self, name, attrs, datasource):
        if datasource.transferable(self._datasource):
            if not datasource.shares_origin(self._datasource):
                datasource.transfer(name, self._datasource, self._key)
            # else:
            #     Asked to write something clean to itself, nothing to do.

        else:
            self.write(name, attrs, datasource)

    def write(self, name, attrs, datasource):
        datasource.write_column(name, self.get())
        datasource.write_column_attributes(name, attrs)

    @property
    def dirty(self):
        return False

    @property
    def dtype(self):
        return self._datasource.column_type(self._key)

    @property
    def attrs(self):
        return dict(self._datasource.read_column_attributes(self._key) or {})

    def __len__(self):
        if self._nrows is None:
            self._nrows = self._datasource.number_of_rows()
        return self._nrows


def chunks(column):
    # TODO(erik): Share chunk calc between sytable and dstable.
    chunk_size = 2 ** 24
    return (max(1, (chunk_size // column.dtype.itemsize)),)


class Column(object):
    def __init__(self, data=None, source=None, attrs=None):
        assert(data is not None or source is not None)

        if isinstance(data, np.ndarray):
            source = InMemoryColumnSource(data)
        elif isinstance(data, da.Array):
            source = InMemoryColumnSource(data)

        self._source = source
        self._dirty = source.dirty
        self._attrs = attrs

    def get(self, index=None, kind='numpy'):
        res = self._source.get(index)
        if kind == 'numpy':
            if isinstance(res, da.Array):
                res = res.compute()
        elif kind == 'dask':
            if not isinstance(res, da.Array):
                res = da.from_array(res, chunks=chunks(res), asarray=False)
        else:
            assert False, 'Unknown kind: "{}" requested.'.format(kind)
        return res

    def _link(self, name, datasource):
        self._source.link(name, self.attrs, datasource)

    def _write(self, name, datasource):
        self._source.write(name, self.attrs, datasource)

    @property
    def dirty(self):
        return self._dirty

    @property
    def dtype(self):
        return self._source.dtype

    @property
    def attrs(self):
        if self._attrs is None:
            self._attrs = self._source.attrs
        return dict(self._attrs)

    @attrs.setter
    def attrs(self, value):
        if value is not None:
            for k, v in value.items():
                _attrib_name_guard(k, 'Column attribute name')
                _attrib_value_guard(v, 'Column attribute value')

        self._attrs = value
        self._dirty = True

    def __len__(self):
        return len(self._source)

    def __copy__(self):
        obj = Column(source=self._source)
        obj._dirty = self._dirty
        obj._attrs = self._attrs
        return obj

    def __deepcopy__(self, memo=None):
        return self.__copy__()


def _srepr(v):
    r = repr(v)
    if len(r) > _max_guard_repr_chars:
        r = '{}...'.format(r[:_max_guard_repr_chars - 3])
    return r


def _ascii_guard(string, name):
    if isinstance(string, six.binary_type):
        try:
            return six.text_type(string, encoding='ascii')
        except UnicodeDecodeError:
            raise ValueError(
                '{} contains bad characters, when it is of binary type '
                'it must contain only ASCII: {}'.format(
                    name, _srepr(string)))
    return string


def _str_guard(string, name):
    if not isinstance(string, six.string_types):
        raise ValueError(
            '{} must be a string, it is: {}'.format(name, _srepr(string)))
    return _ascii_guard(string, name)


def _table_name_guard(name):
    _str_guard(name, 'Table name')


def _column_name_guard(key, name, exception=ValueError):
    if _str_guard(key, name) in ['.', '']:
        raise exception('{} cannot be: {}'.format(name, _srepr(key)))


def _attrib_name_guard(key, name):
    if _str_guard(key, name) == '':
        raise ValueError('{} cannot be: {}'.format(
            name, _srepr(key)))


def _attrib_value_guard(v, name):
    if isinstance(v, six.string_types):
        _str_guard(v, name)
    elif hasattr(v, '__len__'):
        # Non-scalar.
        if isinstance(v, np.ndarray):
            if isinstance(v, np.ma.MaskedArray):
                raise ValueError(
                    '{}  cannot be Masked Array: {}'.format(name, _srepr(v)))
        else:
            v = np.array(v)
        if v.ndim > 1:
            raise ValueError(
                '{}  cannot be multi-dimensional: {}'.format(name, _srepr(v)))
        if len(v.dtype) != 0:
            raise ValueError(
                '{}  cannot be multi-field: {}'.format(name, _srepr(v)))
        if v.dtype.kind == 'O':
            raise ValueError(
                '{}  cannot be object type: {}'.format(name, _srepr(v)))
        elif v.dtype.kind == 'S':
            for vi in v:
                _ascii_guard(v, name)
    elif np.array([v]).dtype == 'O':
        # Scalar, accept all values normal numpy representation.
        raise ValueError(
            '{}  cannot be object type: {}'.format(name, _srepr(v)))


class syattributes(object):
    """A interface to attributes stored in sytables."""
    def __init__(self, column):
        self._column = column

    def delete(self):
        """Delete all attributes."""
        self._column.attrs = None

    def get(self):
        """Returns all attributes."""
        return self._column.attrs

    def set(self, properties):
        """Set the attributes to the values in the properties dictionary."""
        for k in properties:
            _attrib_name_guard(k, 'Attribute name')

        self._column.attrs = properties

    def delete_attribute(self, name):
        """Delete named attribute."""
        attrs = self._column.attrs
        del attrs[name]
        self._column.attrs = attrs

    def get_attribute(self, name):
        """Returns named attribute."""
        return self._column.attrs[name]

    def set_attribute(self, name, value):
        """Set named attribute to the given value."""
        attrs = self._column.attrs
        attrs[name] = value
        self._column.attrs = attrs

    def __getitem__(self, name):
        return self.get_attribute(name)

    def __setitem__(self, name, value):
        self.set_attribute(name, value)

    def __delitem__(self, name):
        self.delete_attribute(name)

    def __iter__(self):
        for key in self._column.attrs:
            yield key

    def __len__(self):
        try:
            return len(self._column.attrs)
        except Exception:
            return 0


class sytable(sybase.sygroup):
    """A type representing a table."""

    def __init__(self, container_type, datasource=sybase.NULL_SOURCE):
        """
        Init. container_type parameter is not used, needed to
        conform factory interface.
        """
        super(sytable, self).__init__(container_type,
                                      datasource or sybase.NULL_SOURCE)
        columns = datasource.columns()
        self._name = None
        self._attributes = None
        self._number_of_rows = None
        self.__datasource_number_of_rows = None
        self._columns = OrderedDict.fromkeys(columns)
        self._column_attributes = dict.fromkeys(columns)
        self._dirty = False
        self._write_hooks = set()

    def _create_column(self, column):
        """
        Create a cache object for the named column.
        This method does not actually cache the column data, it just creates an
        object that can store such a cache.
        This method is a noop if the column doesn't exist in the datasource.
        """
        try:
            if self._columns[column] is not None:
                return
        except KeyError:
            # Don't raise KeyError here. Instead let the caller figure it out.
            return

        self._columns[column] = _column_factory(
            self._datasource, column, self._datasource_number_of_rows())

    def _create_columns(self):
        """
        Creates cache objects for all columns.
        This method does not actually cache any column data, it just creates
        objects that can store such caches.
        """
        for column in self._columns.keys():
            self._create_column(column)

    def columns(self):
        """Return a list with the names of the table columns."""
        return list(self._columns.keys())

    def number_of_rows(self):
        """Return the number table rows."""
        if self.number_of_columns():
            if self._number_of_rows is None:
                self._number_of_rows = self._datasource_number_of_rows()
            return self._number_of_rows
        else:
            return 0

    def _datasource_number_of_rows(self):
        """Return the number table rows in the datasource."""
        if self.__datasource_number_of_rows is None:
            self.__datasource_number_of_rows = (
                self._datasource.number_of_rows())
        return self.__datasource_number_of_rows

    def number_of_columns(self):
        """Return the number of table columns."""
        return len(self._columns)

    def column_type(self, name):
        return self._get_column_column(name).dtype

    def get_name(self):
        if self._name is None:
            self._name = self._datasource.read_name() or ''
        return self._name

    def set_name(self, name):
        name = name or ''
        _table_name_guard(name)
        self._dirty = True
        self._name = name

    def get_table_attributes(self):
        if self._attributes is None:
            self._attributes = self._datasource.read_table_attributes() or {}
        return self._attributes

    def set_table_attributes(self, attributes):
        """
        Set scalar attributes for the table,
        attributes argument is a dictionary.
        """
        self._dirty = True
        if attributes is not None:
            for k, v in attributes.items():
                _attrib_name_guard(k, 'Table attribute name')
                _attrib_value_guard(v, 'Table attribute value')
        self._attributes = attributes

    def get(self, column_name):
        """Return numpy rec array."""
        if column_name is None:
            raise ValueError(
                'column_name=None is not valid for column(), use value()')
        column = self.get_column(column_name)
        return np.rec.array(column, {'names': [column_name],
                                     'formats': [column.dtype]})

    def _get_column_index(self, name, index, kind='numpy'):
        # Workaround for a bug in dask where an exception is raised whenever a
        # dask array of length one is indexed with [True].
        # See: https://github.com/dask/dask/issues/3290
        if isinstance(index, (np.ndarray, list)) and len(index) == 1:
            index_a = np.array(index)
            if index_a.dtype.kind == 'b' and index_a:
                index = np.array([0])

        return self._get_column_column(name).get(index, kind)

    def _get_column(self, name, kind='numpy'):
        return self._get_column_column(name).get(kind=kind)

    def _get_column_column(self, name):
        self._create_column(name)
        try:
            column = self._columns[name]
        except KeyError:
            _column_name_guard(name, 'Column name', exception=KeyError)
            raise KeyError('Column: "{}" not found.'.format(name))
        return column

    def get_column(self, column_name, index=None, kind='numpy'):
        if index is None:
            return self._get_column(column_name, kind=kind)
        return self._get_column_index(column_name, index, kind=kind)

    def value(self):
        """Return numpy rec array or None."""
        columns = list(self._columns.keys())

        if not columns:
            return None
        self._create_columns()
        datacolumns = list(self._columns.values())
        # Construct the table from numpy array.
        return np.rec.array(
            [datacolumn.get() for datacolumn in datacolumns],
            {'names': columns,
             'formats': [six.text_type(column.dtype)
                         for column in datacolumns]})

    def visit(self, group_visitor):
        """Accept group visitor."""
        group_visitor.visit_table(self)

    def has_column(self, column_name):
        """Returns True if a column name exists in table, False otherwise."""
        return column_name in self._columns

    def __contains__(self, column_name):
        """Not implemented. Use :meth:`has_column` instead."""
        raise NotImplementedError("Use method has_column instead.")

    def set(self, table):
        """Write numpy rec array."""
        if table is None:
            return
        for name in table.dtype.names:
            self._set_column(name, table[name])

    def _set_column_length_guard(self, column_name, length):
        if self.number_of_columns() == 0:
            return
        elif self.number_of_columns() == 1 and self.has_column(column_name):
            return
        elif length != self.number_of_rows():
            raise ValueError('Can not add column of length {}'
                             ' to table of length {}'.format(
                                 length, self.number_of_rows()))

    def set_column(self, column_name, column):
        """Write numpy array column to a column named column_name."""
        _column_name_guard(column_name, 'Column name')
        self._set_column(column_name, column)

    def _set_column(self, column_name, column):
        """Write numpy array column to a column named column_name.
        Does not perform any dimension checks on column."""
        self._dirty = True

        if column.ndim != 1:
            raise ValueError("Can only add one-dimensional columns.")
        if column.dtype.hasobject:
            column = _get_none_object_dtype(column, column_name)

        if isinstance(column, da.Array):
            column = Column(column)
        elif isinstance(column, np.ma.core.MaskedArray):
            column = Column(np.ma.masked_array(column))
        else:
            column = Column(np.array(column))

        self._set_column_column(column_name, column)
        self._number_of_columns = len(column)

    def _set_column_column(self, name, column):
        len_column = len(column)
        self._set_column_length_guard(name, len_column)
        self._set_column_column_nocheck(name, column, len_column)

    def _set_column_column_nocheck(self, name, column, nrows):
        self._dirty = True
        try:
            self._columns[name] = column.__copy__()
        except Exception:
            self._columns[name] = column
        self._number_of_rows = nrows

    def update(self, other):
        """
        Write all columns from other table. Creates links if possible.
        """
        # Check if any columns will remain with their original length. If so
        # also check if the lengths of the tables are the same.
        self._dirty = True
        nrows = other.number_of_rows()

        if (other._columns and
            set(self._columns) - set(other._columns) and
                other.number_of_rows() != self.number_of_rows()):

            raise ValueError('Can not add columns of length {}'
                             ' to table of length {}'.format(
                                 other.number_of_rows(),
                                 self.number_of_rows()))

        other._create_columns()
        for name, column in other._columns.items():
            self._set_column_column_nocheck(name, column, nrows)

        self.set_table_attributes(other.get_table_attributes())
        self.set_name(other.get_name())

    def source(self, other, shallow=False):
        self._name = other._name
        self._attributes = {}
        self._columns = OrderedDict()
        self._number_of_rows = other.number_of_rows()
        self.__datasource_number_of_rows = other._datasource_number_of_rows()

        if shallow:
            self.update(other)
        else:
            self.update(other.__deepcopy__())

        if other._datasource.can_write:
            self._dirty = True
        else:
            self._dirty = other._dirty
            self._datasource = other._datasource

    def __copy__(self):
        obj = super(sytable, self).__copy__()
        obj._name = self._name
        obj._attributes = self._attributes
        obj._number_of_rows = self._number_of_rows
        obj.__datasource_number_of_rows = self.__datasource_number_of_rows
        obj._columns = OrderedDict(self._columns)
        obj._write_hooks = list(self._write_hooks)
        return obj

    def __deepcopy__(self, memo=None):
        obj = self.__copy__()
        obj._columns = OrderedDict(
            [(k, v.__deepcopy__() if v is not None else None)
             for k, v in self._columns.items()])
        return obj

    def update_column(self, cache_name, other, other_name):
        """
        Write column with other_name from other table as cache_name in the
        current table. Create links if possible.
        """
        _column_name_guard(cache_name, 'Column name')
        if cache_name != other_name:
            _column_name_guard(other_name, 'Column name target')
        self._update_column(cache_name, other, other_name)

    def _update_column(self, cache_name, other, other_name):
        """
        Write column with other_name from other table as cache_name in the
        current table. Create links if possible. Doesn't check column length
        consistency.
        """
        self._set_column_column(
            cache_name, other._get_column_column(other_name))

    def is_empty(self):
        """Returns ``True`` if the table is empty."""
        return (self.number_of_rows() == 0 and
                self.number_of_columns() == 0)

    def __getitem__(self, index):
        def identity_slice(index, size):
            if not isinstance(index, slice):
                return False
            explicit_index = slice(index.start or 0,
                                   size if index.stop is None else index.stop,
                                   1 if index.step is None else index.step)
            return explicit_index == slice(0, size, 1)

        result = sytable(self.container_type)

        if isinstance(index, tuple):
            if len(index) is not 2:
                # The table is only two dimensional so it would not make sense
                # to go beyond two indices.
                raise TypeError('Invalid index.')
            row_index, col_index = index

            if isinstance(col_index, int):
                if col_index >= len(self.columns()):
                    raise IndexError(
                        'Column index {} is out of bound. '
                        'There are only {} columns in this table.'
                        ''.format(col_index, len(self.columns())))
                col_index = slice(col_index, col_index + 1)
            elif isinstance(col_index, slice):
                pass
            else:
                # Allowing 1D iterable indices.
                assert(len(col_index))
                col_index = np.array(col_index)

                assert(col_index.ndim is 1)
                # Convert to list after asserting dimension.
                col_index = col_index.tolist()

            columns = np.array(self.columns())[col_index].tolist()

        else:
            row_index = index
            columns = self.columns()

        if isinstance(row_index, int):
            start = row_index
            if row_index < 0:
                start += self.number_of_rows()
            if row_index >= self.number_of_rows():
                raise IndexError(
                    'Row index {} is out of bound. '
                    'There are only {} rows in this table.'
                    ''.format(row_index, self.number_of_rows()))
            row_index = slice(start, start + 1)

        elif isinstance(row_index, slice):
            # raw_index = row_index
            number_of_rows = self.number_of_rows()
            start = row_index.start
            stop = row_index.stop
            if start is not None and start < 0:
                start += number_of_rows
            if stop is not None and stop < 0:
                stop += number_of_rows
            row_index = slice(start, stop, row_index.step)
        elif isinstance(row_index, np.ndarray):
            # Allowing 1D iterable indices.
            assert(row_index.ndim == 1)
        else:
            # Allowing 1D iterable indices.
            row_index = np.array(row_index)

            assert(row_index.ndim == 1)
            # Convert to list after asserting dimension.
            row_index = row_index.tolist()

        rows = self.number_of_rows()
        if identity_slice(row_index, rows):
            # The whole table is requested, copying can be avoided in
            # favor of an update operation.
            for column_name in columns:
                result.update_column(column_name, self, column_name)
        else:
            # Copy data creating reduced table.
            for column_name in columns:
                result.set_column(
                    column_name,
                    self._get_column_index(column_name, row_index, 'dask'))
                result.get_column_attributes(column_name).set(
                    self.get_column_attributes(column_name).get())
        return result

    def __setitem__(self, index, other_table):
        self._dirty = True

        def identity_slice(index, size):
            return (
                [index.start or 0,
                 1 if index.step is None else index.step] == [0, 1] and
                (size if index.stop is None else index.stop) >= size)

        def positive_slice(index, length):
            if not isinstance(index, slice):
                return True
            start = index.start or 0
            stop = length if index.stop is None else index.stop
            step = 1 if index.step is None else index.step
            return (start >= 0 and
                    step >= 1 and
                    stop >= start)

        def slice_length(index, length):
            if isinstance(index, np.ndarray):
                return len(index)
            start = index.start or 0
            stop = length if index.stop is None else index.stop
            step = 1 if index.step is None else index.step
            return abs((stop - start) // step)

        def replace_data(col_slice, row_slice):
            columns = self.columns()

            if (slice_length(col_slice, self.number_of_columns()) !=
                    other_table.number_of_columns()):
                raise ValueError('Table column length mismatch.')
            if (slice_length(row_slice, self.number_of_rows()) !=
                    other_table.number_of_rows()):
                raise ValueError('Table row length mismatch.')

            for other_column, column in zip(other_table.columns(),
                                            np.array(columns)[col_slice]):
                attrs = self._get_column_column(column).attrs
                current = np.array(self.get_column(column))
                current[row_slice] = other_table.get_column(other_column)
                self._columns[column] = Column(
                    source=InMemoryColumnSource(current, attrs))

        new_columns = other_table.columns()
        curr_columns = self.columns()

        full_col = False
        full_row = False

        cols = self.number_of_columns()
        rows = self.number_of_rows()

        if isinstance(index, tuple):
            if len(index) is not 2:
                # The table is only two dimensional so it would not make sense
                # to go beyond two indices.
                raise TypeError('Invalid index.')
            row_index, col_index = index

            if isinstance(col_index, int):
                slice_col_index = slice(col_index, col_index + 1)
            elif isinstance(col_index, slice):
                full_col = identity_slice(col_index, cols)
                slice_col_index = col_index
            else:
                # Allowing 1D iterable indices.
                slice_col_index = (
                    np.array(col_index)
                    if col_index is not None else np.array([], dtype=int))
                if slice_col_index.ndim != 1:
                    raise TypeError('Index iterable must be 1D.')
        else:
            row_index = index
            full_col = True
            col_index = slice(0, None, None)
            slice_col_index = col_index

        if isinstance(row_index, int):
            row_index = slice(row_index, row_index + 1)
            slice_row_index = row_index
        elif isinstance(row_index, slice):
            slice_row_index = row_index
            full_row = identity_slice(slice_row_index, rows)
        else:
            # Allowing 1D iterable indices.
            slice_row_index = (
                np.array(row_index)
                if col_index is not None else np.array([], dtype=int))
            if slice_row_index.ndim != 1:
                raise TypeError('Invalid index.')

        if not positive_slice(slice_col_index, cols):
            raise ValueError('Negative slice notation unsupported.')

        if not positive_slice(slice_row_index, rows):
            raise ValueError('Negative slice notation unsupported.')

        if full_row and full_col:
            # Replace the table entirely with other_table.
            for column in curr_columns:
                del self[column]
            self.update(other_table)

        elif full_row:
            if isinstance(col_index, slice):
                col_step = (1 if slice_col_index.step is None
                            else slice_col_index.step)
            else:
                col_step = None

            if col_step is 1:
                # Replace the columns selected entirely by other_table.
                remove_columns = curr_columns[slice_col_index]
                kept_columns = set(curr_columns).difference(remove_columns)

                if other_table.number_of_rows() != rows:
                    raise ValueError('Table row length mismatch.')

                if kept_columns.intersection(new_columns):
                    raise ValueError('Overlapping column names.')

                for column in remove_columns:
                    del self[column]
                col_start = slice_col_index.start or 0
                col_stop = ((col_start if slice_col_index.stop is None
                             else slice_col_index.stop) +
                            other_table.number_of_columns())
                for column in new_columns:
                    self.update_column(column, other_table, column)
                self._create_columns()
                columns = [(k, v.get()) for k, v in self._columns.items()]
                self._columns = OrderedDict(
                    (k, Column(v)) for k, v in
                    (columns[:col_start] +
                     columns[len(kept_columns):] +
                     columns[col_stop:len(kept_columns)]))

            else:
                replace_data(slice_col_index, slice_row_index)
        elif full_col:
            if isinstance(row_index, slice):
                row_step = (1 if slice_row_index.step is None
                            else slice_row_index.step)
            else:
                row_step = None

            if row_step is 1:
                # Replace the rows selected entirely by other_table.
                if (other_table.number_of_columns() != cols):
                    raise ValueError('Table column length mismatch.')

                row_start = slice_row_index.start or 0
                row_stop = ((row_start if slice_row_index.stop is None
                             else slice_row_index.stop) +
                            other_table.number_of_rows())

                for column in curr_columns:
                    attrs = self._get_column_column(column).attrs
                    current = self.get_column(column)
                    self._columns[column] = Column(source=InMemoryColumnSource(
                        np.hstack([current[:row_start],
                                   other_table.get_column(column),
                                   current[row_stop:]]), attrs))

            else:
                replace_data(slice_col_index, slice_row_index)
        else:
            # Sub-selection used.
            # Replace the selected data by other_table, keeping dimensions etc.
            replace_data(slice_col_index, slice_row_index)

    def writeback(self):
        super(sytable, self).writeback()

    def _link(self, datasource, key):
        return (not any(v.dirty for v in self._columns.values()
                        if v is not None) and
                super(sytable, self)._link(datasource, key))

    def _writeback(self, datasource, link=None):
        # Transfer relies on direct compatiblity, for example, in the hdf5
        # datasource case both sources need to be hdf5 and the source needs to
        # be read only.
        origin = self._datasource
        target = datasource
        exc.assert_exc(target.can_write, exc=exc.WritebackReadOnlyError)

        if link:
            return self._link(target, link)

        target.write_started(self.number_of_rows(), self.number_of_columns())
        for hook in self._write_hooks:
            hook(target)

        shares_origin = target.shares_origin(origin)

        target.write_table_attributes(self.get_table_attributes())
        name = self.get_name()
        if name:
            target.write_name(name)

        self._create_columns()
        dirty_cols = any(v.dirty for v in self._columns.values())

        if shares_origin and not (self._dirty or dirty_cols):
            # There is no point in writeback of unmodified data to the
            # original datasource.
            return

        # Linking transfer must be considered for each column.
        for key, col in self._columns.items():
            if col.dirty:
                col._write(key, target)
            else:
                col._link(key, target)

        target.write_finished()

    def get_column_attributes(self, column):
        return syattributes(self._get_column_column(column))

    def __delitem__(self, column):
        del self._columns[column]
        self._dirty = True

    def __repr__(self):
        return "sytable()"
