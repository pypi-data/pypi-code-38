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
"""Table Data source module."""
from __future__ import (print_function, division, unicode_literals,
                        absolute_import)
import re
import json
import warnings
from collections import OrderedDict
import six
import numpy as np
import dask.array as da
from . import dsgroup

# Ignore a warning from numpy>=1.14 when importing h5py<=2.7.1:
with warnings.catch_warnings():
    warnings.simplefilter('ignore', FutureWarning)
    import h5py


ORDER = '__sy_order__'
NAME = '__sy_name__'
EXT = '__sy_ext__'
EXT_COL_INDEX = 'col_index'
EXT_COL_ATTR = 'col_attr'

table_attributes = [ORDER, NAME]

ENCODING = '__sy_encoding__'
ENCODING_TYPE = '__sy_encoding_type__'
MASK = '__sy_mask__'
MASK_REC = 'rec'
NUMPY_TYPE = '__sy_numpy_type__'

RES_RE = re.compile('^__sy_.*__$')

column_attributes = [ENCODING, ENCODING_TYPE, NUMPY_TYPE, MASK]

UTF8 = 'utf-8'

encoded_types = {'datetime64[ns]': 'f8',
                 'datetime64[us]': 'f8',
                 'datetime64[D]': 'f8',
                 'timedelta64[us]': 'f8'}
encoded_types_matches = set(encoded_types.keys())


# See http://docs.h5py.org/en/latest/high/dataset.html:
#
#   Keep the total size of your chunks between 10 KiB and 1 MiB, larger for
#   larger datasets.

_h5py_chunk_size = 2 ** 16  # 64 KiB

_h5py_compress_threshold = _h5py_chunk_size


# See http://dask.pydata.org/en/latest/faq.html:
#
#   Generally I shoot for 10MB-100MB sized chunks

_dask_chunk_size = 2 ** 24  # 16 MiB


int_compress = dict(compression='lzf', shuffle=True)
ext_compress = dict(compression='gzip', shuffle=True, compression_opts=9)


def _h5py_chunks(column):
    return (max(1, (_h5py_chunk_size // column.dtype.itemsize)),)


def _dask_chunks(column):
    return (max(1, (_dask_chunk_size // column.dtype.itemsize)),)


class Column(object):

    def __init__(self, table, name, dataset):
        self._table = table
        self._name = name
        self._dataset = dataset
        self.dtype = table._dataset_column_type(dataset)
        self.shape = dataset.shape

    def __getitem__(self, index):

        def get_bool_index(length, int_index):
            """Return bool index vector from int index vector."""
            result = np.zeros(length, dtype=bool)
            result[int_index] = True
            return result

        def get_sort_index(index):
            return np.unique(index, return_inverse=True)[1]

        def slice_int_index(column, index):
            # Slicing with bool index is faster than list of integers.
            # See https://github.com/h5py/h5py/issues/368
            bool_index = get_bool_index(len(column), index)

            # If the list of integers was non-increasing, that information
            # gets lost when converting to a boolean index, so we need to
            # work around that.
            if not (np.diff(index) > 0).all():
                return column[bool_index][get_sort_index(index)]
            else:
                return column[bool_index]

        def indexed(column, index):
            res = column

            if isinstance(index, list):
                index = np.array(index)

            if isinstance(index, slice):
                # H5py can't handle negative strides so we read it increasing
                # order and reverse it afterwards.
                if index.step is not None and index.step < 0:
                    increasing_index = slice(
                        index.start, index.stop, -index.step)
                    res = column[increasing_index][::-1]
                else:
                    res = column[index]
            elif isinstance(index, np.ndarray):
                if index.dtype.kind == 'b':
                    parts = []
                    for i in range(0, len(index), _h5py_chunk_size):
                        part = column[
                            i:i + _h5py_chunk_size][
                                index[i:i + _h5py_chunk_size]]
                        if len(part):
                            parts.append(part)
                    if parts:
                        res = np.hstack(parts)
                    else:
                        res = np.array([], dtype=column.dtype)
                elif index.dtype.kind == 'i':
                    res = slice_int_index(column, index)
                else:
                    raise TypeError(
                        'Invalid type in slice index array {}.'.format(
                            index.dtype))
            else:
                res = column[index]
            return res

        if not self._dataset:
            self._dataset = self._table[self._name]

        obj = self._dataset

        attrs = obj.attrs

        masked = False
        mask = None

        if MASK in attrs:
            masked = True

        if obj.shape == (0,):
            # Avoid zero size selection problem in h5py.
            result = np.array([], dtype=obj.dtype
                              if not masked
                              else obj.dtype[1])

        else:
            if index is not None:
                result = indexed(obj, index)
            else:
                result = obj

            if masked:
                mask = result['mask']
                result = result['data']

            encoding = attrs.get(ENCODING)

            if encoding:
                result = decode(result, encoding)

        encoding_type = attrs.get(ENCODING_TYPE)

        if encoding_type:
            result = result.astype(encoding_type)

        if mask is not None:
            result = np.ma.masked_array(result, mask)

        return result


def encode_index(index):
    """
    Encode python index.

    Return encoded object.

    >>> encode_index(1)
    '1'
    >>> encode_index(-1)
    '-1'
    >>> encode_index(slice(1, None, 2))
    '1::2'
    >>> encode_index(Ellipsis)
    '...'
    >>> encode_index((1, slice(1, None, 2), Ellipsis))
    '1,1::2,...'
    """
    def inner(index):
        if isinstance(index, int):
            return str(index)
        elif isinstance(index, slice):
            return '{}:{}:{}'.format(
                *
                ('' if v is None else v
                 for v in (index.start, index.stop, index.step)))
        elif index == Ellipsis:
            return '...'
        else:
            assert False

    if isinstance(index, tuple):
        return ','.join(inner(v) for v in index)
    return inner(index)


def decode_index(index):
    """
    Decode a python index.
    This is not implemented to behave exactly as __getitem__ but should
    return similar results when used with valid indices consisting of
    tuples, integers, slices and elipsis.

    Return decoded object.

    >>> decode_index('1')
    1
    >>> decode_index('-1')
    -1
    >>> decode_index('1::2')
    slice(1, None, 2)
    >>> decode_index('...')
    Ellipsis
    >>> decode_index('1,1::2,...')
    (1, slice(1, None, 2), Ellipsis)
    """
    index = index.replace(' ', '')

    def inner_part(index):
        if index == '':
            return None
        try:
            return int(index)
        except ValueError:
            if index == '...':
                return Ellipsis
        assert False

    def inner(index):
        parts = index.split(':')
        length = len(parts)

        if length == 1:
            return inner_part(parts[0])
        elif length > 1:
            return slice(*(inner_part(part) for part in parts))
        assert False
    parts = index.split(',')
    length = len(parts)

    if length == 1:
        return inner(parts[0])
    elif length > 1:
        return tuple(inner(part) for part in parts if part != '')
    assert False


def __monkeypatch_externallink_init():
    """
    TODO! Track changes in h5py.
    Patch enables unicode datasets in h5py.ExternalLink.
    This makes it possible to use .get(name, getlink=True) without causing
    an exception.

    However, if the behavior of h5py.External link __init__ changes, then
    so must this patch.
    """
    def patch(self, filename, path):
        self._filename = filename
        self._path = path
    try:
        h5py.ExternalLink.__init__ = patch
    except AttributeError:
        pass


if h5py.version.version_tuple[:3] < (2, 8, 0):
    __monkeypatch_externallink_init()


def encode(array, encoding=UTF8):
    """
    Encode numpy unicode typed array (array.dtype.kind == 'U') as a numpy
    string array.
    """
    return np.char.encode(array, encoding)


def decode(array, encoding=UTF8):
    """
    Decode string array dataset encoded in utf-8 as a numpy unicode typed array
    (array.dtype.kind == 'U').
    """
    try:
        encoding = encoding.decode('ascii')
    except AttributeError:
        pass
    return np.char.decode(array, encoding)


def decode_attribute(attribute):
    """
    Decode attribute encoded in utf-8 as a list of unicode strings or as a
    single unicode string.
    """
    try:
        # Eliminate arrays.
        data = attribute.tolist()
    except:
        data = attribute
    if isinstance(data, six.binary_type):
        data = data.decode(UTF8)
    elif isinstance(data, list):
        if np.array(data).dtype.kind == 'U':
            data = [x.encode(UTF8) for x in data]
    return data


def encode_attribute(attribute, encoding=UTF8):
    """
    Encode string or possibly numpy unicode typed array
    (array.dtype.kind == 'U') as string array.
    """
    try:
        # Eliminate arrays.
        data = attribute.tolist()
    except:
        data = attribute
    if isinstance(data, six.text_type):
        data = data.encode(encoding)
    elif isinstance(data, list):
        if np.array(data).dtype.kind == 'U':
            data = [x.encode(encoding) for x in data]
    return data


class Hdf5TableBase(dsgroup.Hdf5Group):
    """Abstraction of an HDF5-table."""
    def __init__(self, group, can_write, can_link):
        self._group = group
        self.can_write = can_write
        self.can_link = can_link
        self.compress = int_compress if can_link else ext_compress

        keys = sorted(key for key in self.group.keys()
                      if not RES_RE.match(key))

        order = self.group.get(ORDER, None)
        # TODO(erik): Remove this after version 1.3 is released.
        if order is None:
            order = self.group.attrs.get(ORDER, None)
            if order is None:
                order = range(len(self.group))

        stored_columns = np.array(
            keys)[order[...]].tolist() if len(order) else []

        user_columns = [dsgroup.restore_slash(key)
                        for key in stored_columns]

        ext = self.group.get(EXT, None)
        self._col_attrs = {}
        self._col_indices = {}

        if ext is not None:
            ext = json.loads(ext[...].tostring())

            self._col_indices = {
                stored_columns[i]: decode_index(v)
                for i, v in ext.get(EXT_COL_INDEX, [])}

            self._col_attrs = {stored_columns[i]: v
                               for i, v in ext.get(EXT_COL_ATTR, [])}

        self._columns = OrderedDict(zip(stored_columns, user_columns))
        self._length = None

    def read_column_attributes(self, column_name):
        store_name = dsgroup.replace_slash(column_name)
        attrs = self._col_attrs.get(store_name)

        if attrs is not None:
            return attrs

        dataset = self.group[store_name]
        attrs = {decode_attribute(key): decode_attribute(value.tolist())
                 for key, value in dataset.attrs.items()
                 if key not in column_attributes}
        return attrs

    def write_column_attributes(self, column_name, properties):
        if properties:
            attrs = self.group[dsgroup.replace_slash(column_name)].attrs
            for key, value in properties.items():
                attrs.create(encode_attribute(key),
                             encode_attribute(value))

    def read_column(self, column_name, index=None):
        """Return numpy array with data from the given column name."""
        # Named column selection used.
        store_name = dsgroup.replace_slash(column_name)
        column = self.group[store_name]
        column = da.from_array(Column(self, store_name, column),
                               chunks=_dask_chunks(column), asarray=False)

        index_ = self._col_indices.get(store_name)
        if index_ is not None:
            # TODO(erik): Merge slice operation with index to avoid
            # intermediate memory use.
            column = column[index_]
        return column

    def write_column(self, column_name, column):
        """
        Stores table in the hdf5 file, at path,
        with data from the given table
        """

        if isinstance(column, da.Array):
            column = column.compute()

        if column.ndim == 1:
            # 1D dataset.
            length = len(column)
        elif column.ndim == 0:
            # Scalar dataset.
            length = -1
        else:
            # Multi-dimensional columns are not allowed.
            assert(False)

        if self._length is not None:
            # Check that the table length is consistent.
            assert self._length == length, (
                'len({}) = {} != {}'.format(column_name, length, self._length))
        self._length = length

        if isinstance(column, np.ma.core.MaskedArray):
            data = column.data
            mask = column.mask
        else:
            data = column
            mask = None

        # Write column data to the group.
        name = dsgroup.replace_slash(column_name)
        attrs = {}

        if column.dtype.kind == 'U':
            data = encode(data)
            attrs[ENCODING] = UTF8
            attrs[ENCODING_TYPE] = column.dtype.str
        else:
            dtype_name = column.dtype.name
            if dtype_name in encoded_types_matches:
                data = data.astype(encoded_types[dtype_name])
                attrs[ENCODING_TYPE] = column.dtype.str

        boolmask = isinstance(mask, np.bool_)
        if mask is not None and (not boolmask or mask) and len(data):

            if boolmask and mask:
                mask_data = np.ones(len(data), dtype='?')
            else:
                mask_data = mask

                data = np.rec.array(
                    [data, mask_data],
                    formats=[data.dtype.str, mask.dtype.str],
                    names=['data', 'mask'])

            attrs[MASK] = MASK_REC

        if column.nbytes > _h5py_compress_threshold:
            self.group.create_dataset(
                name, data=data, chunks=_h5py_chunks(column), **self.compress)
        else:
            self.group[name] = data

        for k, v in attrs.items():
            self.group[name].attrs[k] = v
        self._columns[name] = column_name

    def transferable(self, other):
        return (isinstance(other, Hdf5Table) and
                self.can_link and other.can_link)

    def transfer(self, name, other, other_name, index=None, attrs=None):
        user_name = name
        store_name = dsgroup.replace_slash(name)
        other_name = dsgroup.replace_slash(other_name)

        if isinstance(other, h5py.Dataset):
            dataset = other
        else:
            dataset = other.group[other_name]
            # Propagate index and attrs.
            index = other._table._col_indices.get(other_name)
            attrs = other._table._col_attrs.get(other_name)
        try:
            length = len(dataset)
        except TypeError:
            # Assuming scalar dataset.
            length = -1

        if self._length is not None:
            # Check that the table length is consistent.
            assert(self._length == length)
        self._length = length
        self.group[store_name] = h5py.ExternalLink(
            dataset.file.filename, dataset.name)

        if index is not None:
            self._col_indices[store_name] = index

        if attrs is not None:
            self._col_attrs[store_name] = attrs

        self._columns[store_name] = user_name

    def write_link(self, name, other, other_name):
        return False

    def write_started(self, number_of_rows, number_of_columns):
        pass

    def write_finished(self):
        """Finish writing table."""
        lookup = {key: i for i, key in
                  enumerate(sorted(key for key in self.group.keys()
                                   if not RES_RE.match(key)))}
        order = [lookup[key] for key in self._columns.keys()]
        if order:
            if ORDER in self.group:
                del self.group[ORDER]

            self.group.create_dataset(ORDER, data=order, dtype='i')
            try:
                # TODO(erik): Remove this after version 1.3 is released.
                self.group.attrs.create(ORDER, order, dtype='i')
            except RuntimeError:
                # Ignoring ordering due to size restrictions.
                pass

        ext = {}

        if self._col_indices:
            ext[EXT_COL_INDEX] = [(lookup[k], encode_index(v))
                                  for k, v in self._col_indices.items()]
        if self._col_attrs:
            ext[EXT_COL_ATTR] = [(lookup[k], v)
                                 for k, v in self._col_attrs.items()]
        if ext:
            self.group.create_dataset(
                EXT, data=np.array(json.dumps(ext), dtype=np.void))

    def columns(self):
        """Return a list contaning the available column names."""
        return self._columns.values()

    def column_type(self, name):
        return self._dataset_column_type(
            self.group[dsgroup.replace_slash(name)])

    def _dataset_column_type(self, dataset):
        mask = dataset.attrs.get(MASK)
        if ENCODING_TYPE in dataset.attrs:
            return np.dtype(dataset.attrs[ENCODING_TYPE])
        elif mask:
            return dataset.dtype['data']
        else:
            return dataset.dtype

    def number_of_rows(self):
        try:
            name = six.next(iter(self._columns))
            column = self.group[name]
            # Check for scalar value which has no length.
            # .size is not available for older h5py.
            if column.shape == tuple():
                return 1
            else:
                index = self._col_indices.get(name)
                if index is not None:
                    return len(column[index])

                return len(column)
        except StopIteration:
            return 0

    def number_of_columns(self):
        return len(self._columns)

    def write_name(self, name):
        if name is not None:
            self.group.attrs.create(NAME, encode_attribute(name))

    def read_name(self):
        name = decode_attribute(self.group.attrs.get(NAME, None))
        return name

    def read_table_attributes(self):
        return {decode_attribute(key): decode_attribute(value.tolist())
                for key, value in self.group.attrs.items()
                if key not in table_attributes}

    def write_table_attributes(self, properties):
        if properties:
            attrs = self.group.attrs
            for key, value in properties.items():
                attrs.create(encode_attribute(key),
                             encode_attribute(value))


class Hdf5Table(dsgroup.Hdf5Group):
    """Abstraction of an HDF5-table."""
    def __init__(self, factory, group=None, datapointer=None, can_write=False,
                 can_link=False):
        super(Hdf5Table, self).__init__(factory, group, datapointer, can_write,
                                        can_link)
        self._table = Hdf5TableBase(self.group, self.can_write, self.can_link)

    def read_column_attributes(self, column_name):
        return self._table.read_column_attributes(column_name)

    def write_column_attributes(self, column_name, properties):
        return self._table.write_column_attributes(column_name, properties)

    def read_column(self, column_name, index=None):
        return self._table.read_column(column_name, index)

    def write_column(self, column_name, column):
        return self._table.write_column(column_name, column)

    def transferable(self, other):
        return self._table.transferable(other)

    def transfer(self, name, other, other_name, index=None, attrs=None):
        return self._table.transfer(name, other, other_name, index, attrs)

    def write_started(self, number_of_rows, number_of_columns):
        return self._table.write_started(number_of_rows, number_of_columns)

    def write_finished(self):
        return self._table.write_finished()

    def write_link(self, name, other, other_name):
        raise self._table.write_link(name, other, other_name)

    def columns(self):
        return self._table.columns()

    def column_type(self, name):
        return self._table.column_type(name)

    def number_of_rows(self):
        return self._table.number_of_rows()

    def number_of_columns(self):
        return self._table.number_of_columns()

    def write_name(self, name):
        return self._table.write_name(name)

    def read_name(self):
        return self._table.read_name()

    def read_table_attributes(self):
        return self._table.read_table_attributes()

    def write_table_attributes(self, properties):
        return self._table.write_table_attributes(properties)
