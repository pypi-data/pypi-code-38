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
"""
API for working with the Table type.

Import this module like this::

    from sympathy.api import table

A Table with columns, where each column has a name and a data type.
All columns in the Table must always be of the same length.

Any node port with the *Table* type represents an object of this class.

Accessing the data
------------------
There are multiple APIs in the Table for adding and reading columns. The
simplest one is to use indexing with column names::

    >>> from sympathy.api import table
    >>> mytable = table.File()
    >>> mytable['foo'] = np.array([1,2,3])
    >>> print(mytable['foo'])
    [1 2 3]

It is also possible to convert between a Table and a pandas DataFrame
(:meth:`to_dataframe`, :meth:`from_dataframe`), a numpy recarray
(:meth:`to_recarray`, :meth:`from_recarray`), or a generator/list of rows
(:meth:`to_rows`, :meth:`from_rows`).

The size of the table can easily be found with the methods
:meth:`number_of_rows` and :meth:`number_of_columns`. The column names are
available via the method :meth:`column_names`.


.. _`table_attributes`:

Column and Table attributes
---------------------------
Both the Table itself and any of its columns can have attributes attached
to it. Attributes can be either scalar values or one-dimensional numpy arrays,
but not masked arrays. If the attribute value is :class:`bytes` (:class:`str`
in python 2) the value must contain only ASCII characters.

There is currently no support for storing datetimes or timedeltas in
attributes. As a workaround, you can convert the datetimes or timedeltas to
either string or floats and store those instead.

.. _`table_name_restrictions`:

Name restrictions
-----------------
Column names, attribute names and table names can be almost any unicode
strings. For column names an empty string or a single period (.) are not
allowed. For attribute names only the empty string is not allowed. The names of
table attributes must also not be of the format :obj:`__table_*__` since this
is reserved for storing attributes internal to the Sympathy platform.

If any of these names are set using :class:`bytes` (:class:`str` in python 2),
the name must contain only ASCII characters.



Class :class:`table.File`
-------------------------
.. autoclass:: File
   :members:
   :special-members:

Class :class:`table.Column`
---------------------------
.. autoclass:: Column
   :members:

"""
from __future__ import (print_function, division, unicode_literals,
                        absolute_import)

import collections
from itertools import islice
import re

import six
from six.moves import zip as izip
import numpy as np

from .. types import sybase
from .. types import sylist
from .. types import types
from .. types import exception as type_exc
from .. utils import filebase
from .. utils.context import (deprecated_method,
                              inherit_doc)
from .. platform import exceptions as exc


RES_RE = re.compile('^__table_.*__$')
_TABLE_VERSION = '__table_version__'


def table_sql():
    """Avoid pre-loading table_sql."""
    from . import table_sql
    return table_sql


def _pandas():
    """
    Avoid pre-loading pandas.
    Pandas loads matplotlib taking loads of time.

    Matplotlib import has issues loading when python is installed on a unicode
    path causing unnecessary errors.
    """
    import pandas
    return pandas


def is_table(scheme, filename):
    """Return ``True`` if file at ``filename`` is represents a Table."""
    return File.is_type(filename, scheme)


def is_tables(scheme, filename):
    """
    Return ``True`` if file at ``filename`` is represents a list of Tables.
    """
    return FileList.is_type(filename, scheme)


def _reserved(name):
    return RES_RE.match(name)


def _reserved_attributes(attributes):
    return {k: v for k, v in attributes.items() if _reserved(k)}


def _ordinary_attributes(attributes):
    return {k: v for k, v in attributes.items() if not _reserved(k)}


@filebase.typeutil('sytypealias table = sytable')
@inherit_doc
class File(filebase.TypeAlias):
    """
    A Table with columns, where each column has a name and a data type.
    All columns in the Table must always be of the same length.
    """

    VERSION = '1.2'

    def __init__(self, mode=None, **kwargs):
        super(File, self).__init__(mode=mode, **kwargs)

        if mode != 'r':
            attributes = self._data.get_table_attributes()
            if _TABLE_VERSION not in attributes:
                attributes[_TABLE_VERSION] = self.VERSION
                self._data.set_table_attributes(attributes)
            else:
                self.version()

    def clear(self):
        """Clear the table. All columns and attributes will be removed."""
        for column_name in self.column_names():
            del self._data[column_name]
        self.set_table_attributes({})
        self.set_name(None)

    @deprecated_method('1.5.0')
    def columns(self):
        """
        Return a list with the names of the table columns.

        .. deprecated:: 1.0
           Use :meth:`column_names` instead.
        """
        return self.column_names()

    def version(self):
        """
        Return the version as a string.
        This is useful when loading existing files from disk.

        .. versionadded:: 1.2.5
        """
        return self._data.get_table_attributes().get(_TABLE_VERSION, '1.2')

    def column_names(self):
        """Return a list with the names of the table columns."""
        return self._data.columns()

    def column_type(self, column):
        """Return the dtype of column named ``column``."""
        return self._data.column_type(column)

    def number_of_rows(self):
        """Return the number of rows in the table."""
        return self._data.number_of_rows()

    def number_of_columns(self):
        """Return the number of columns in the table."""
        return self._data.number_of_columns()

    def is_empty(self):
        """Returns ``True`` if the table is empty."""
        return self._data.is_empty()

    @deprecated_method('1.5.0')
    def value(self):
        """
        Return numpy.recarray object with the table content.

        .. deprecated:: 1.0
           Use :meth:`to_recarray` instead.
        """
        return self.to_recarray()

    @staticmethod
    def from_recarray(recarray):
        """
        Return a new :class:`table.File` with data from numpy.recarray object
        ``recarray``.
        """
        result = File()
        result._data.set(recarray)
        return result

    def to_recarray(self):
        """
        Return numpy.recarray object with the table content or None if there
        are no columns.
        """
        return self._data.value()

    @staticmethod
    def from_dataframe(dataframe):
        """
        Return a new :class:`table.File` with data from pandas dataframe
        ``dataframe``.
        """
        result = File()
        for key, value in six.iteritems(dataframe):
            result._data.set_column(key, np.array(value.tolist()))

        return result

    def to_dataframe(self):
        """Return pandas DataFrame object with all columns in table."""
        return _pandas().DataFrame(collections.OrderedDict(
            (column, self.get_column_to_array(column))
            for column in self.column_names()), copy=True)

    @staticmethod
    def from_matrix(column_names, matrix):
        """
        Return a new :class:`table.File` with data from numpy matrix
        ``matrix``. ``column_names`` should be a list of strings which are
        used to name the resulting columns.
        """
        result = File()
        matrix = matrix.T
        if len(matrix) != len(column_names):
            raise ValueError(
                "The number of columns in matrix is not the same as the "
                "number of column names.")
        for key, value in zip(column_names, matrix):
            result._data.set_column(key, np.squeeze(np.asarray(value), 0))
        return result

    def to_matrix(self):
        """Return numpy matrix with all the columns in the table."""
        return np.mat(
            [self.get_column_to_array(column)
             for column in self.column_names()]).T

    @staticmethod
    def from_rows(column_names, rows):
        """
        Return new :class:`table.File` with data from iterable rows.
        ``column_names`` should be a list of strings which are used to name
        the resulting columns.
        """
        def tableiter(maxrows):
            rowiter = iter(rows)
            column_data = list(zip(*islice(rowiter, maxrows)))

            if column_data:
                while column_data:
                    column_table = File()
                    for key, value in zip(column_names, column_data):
                        arr = np.array(value)
                        if arr.dtype.kind == 'O':
                            # For older numpy, otherwise, arr == None.
                            mask = np.equal(arr, None)
                            if np.all(mask):
                                # No information about the actual type.
                                pass
                            elif np.any(mask):
                                fill = arr[np.nonzero(~mask)[0][0]]
                                arr[mask] = fill
                                arr = np.ma.MaskedArray(arr.tolist(), mask)
                                column_table.set_column_from_array(key, arr)
                            else:
                                column_table.set_column_from_array(key, arr)
                        else:
                            column_table.set_column_from_array(key, arr)

                    yield column_table
                    column_data = list(zip(*islice(rowiter, maxrows)))
            else:
                column_table = File()
                void = np.array([], dtype=np.void)
                for key in column_names:
                    column_table.set_column_from_array(key, void)
                yield column_table

        # Set the size of the sub tables (in rows).
        # This will only be one row in the case where
        # number_of_columns >= maxcells.
        # Intended to limit memory use.
        maxcells = 2 ** 15
        number_of_columns = len(column_names)
        maxrows = maxcells // number_of_columns if number_of_columns else 1
        result = File()
        result.vjoin(tableiter(maxrows), '', '', None, 0)
        return result

    def to_rows(self):
        """
        Return a generator over the table's rows.

        Each row will be represented as a tuple of values.
        """
        # Set the size of the sub tables (in rows).
        # This will only be one row in the case where
        # number_of_columns >= maxcells.
        # Intended to limit memory use.
        maxcells = 2 ** 15
        number_of_columns = self.number_of_columns()
        maxrows = maxcells // number_of_columns if number_of_columns else 1
        column_names = self.column_names()
        for i in range(0, self.number_of_rows(), maxrows):
            column_table = self[i: i + maxrows]
            for row in izip(*[column_table.get_column_to_array(key).tolist()
                              for key in column_names]):
                yield row

    @deprecated_method('1.5.0')
    def set(self, recarray):
        """
        Write rec array.

        .. deprecated:: 1.0
           Use :meth:`from_recarray` instead.
        """
        table = self.from_recarray(recarray)
        for column_name in table.column_names():
            self.set_column_from_array(column_name,
                                       table.get_column_to_array(column_name))

    @deprecated_method('1.5.0')
    def get(self, column_name):
        """
        Return numpy rec array.

        .. deprecated:: 1.0
           Use :meth:`to_recarray` instead.
        """
        return self[:][column_name].to_recarray()

    @deprecated_method('1.5.0')
    def set_column(self, column_name, column):
        """
        Set a column.

        .. deprecated:: 1.0
           Use :meth:`set_column_from_array` instead.
        """
        return self.set_column_from_array(column_name, column)

    @deprecated_method('1.5.0')
    def get_column(self, column_name):
        """
        Return numpy array.

        .. deprecated:: 1.0
           Use :meth:`get_column_to_array` instead.
        """
        return self.get_column_to_array(column_name)

    def set_column_from_array(self, column_name, array, attributes=None):
        """
        Write numpy array to column named by column_name.
        If the column already exists it will be replaced.
        """
        try:
            self._data.set_column(column_name, array)
        except type_exc.DatasetTypeError:
            raise exc.SyColumnTypeError(
                'Input array contains unsupported objects')

        if attributes is not None:
            self.set_column_attributes(column_name, attributes)

    def get_column_to_array(self, column_name, index=None, kind='numpy'):
        """
        Return named column as an array.

        Return type is numpy.array when kind is 'numpy' (by default)
        and dask.array.Array when kind is 'dask'.

        Dask arrays can be used to reduce memory use in locked subflows by
        handling data more lazily.
        """
        return self._data.get_column(column_name, index, kind=kind)

    def set_column_from_series(self, series):
        """
        Write pandas series to column named by series.name.
        If the column already exists it will be replaced.
        """
        if series.name is None:
            raise Exception('Series needs to have a name; assign series.name.')
        self._data.set_column(series.name, series.values)

    def get_column_to_series(self, column_name):
        """Return named column as pandas series."""
        return _pandas().Series(
            self._data.get_column(column_name), name=column_name, copy=True)

    def set_name(self, name):
        """Set table name. Use None to unset the name."""
        self._data.set_name(name)

    def get_name(self):
        """Return table name or None if name is not set."""
        return self._data.get_name()

    def get_column_attributes(self, column_name):
        """Return dictionary of attributes for column_name."""
        return self._data.get_column_attributes(column_name).get()

    def set_column_attributes(self, column_name, attributes):
        """
        Set dictionary of scalar attributes for column_name.

        Attribute values can be any numbers or strings.
        """
        self._data.get_column_attributes(column_name).set(attributes)

    def get_table_attributes(self):
        """Return dictionary of attributes for table."""
        return _ordinary_attributes(self._data.get_table_attributes())

    def set_table_attributes(self, attributes):
        """
        Set table attributes to those in dictionary attributes.

        Attribute values can be any numbers or strings. Replaces any old table
        attributes.

        Example::

            >>> from sympathy.api import table
            >>> mytable = table.File()
            >>> mytable.set_table_attributes(
            ...     {'Thou shall count to': 3,
            ...      'Ingredients': 'Spam'})
        """
        attributes = dict(attributes)
        reserved = _reserved_attributes(self._data.get_table_attributes())
        attributes.update(reserved)
        self._data.set_table_attributes(attributes)

    def get_attributes(self):
        """
        Get all table attributes and all column attributes.

        Returns a tuple where the first element contains all the table
        attributes and the second element contains all the column attributes.
        """
        return (self.get_table_attributes(),
                {column: self.get_column_attributes(column)
                 for column in self.column_names()})

    def set_attributes(self, attributes):
        """Set table attributes and column attrubutes at the same time.

        Input should be a tuple of dictionaries where the first element of the
        tuple contains the table attributes and the second element contains the
        column attributes.
        """
        if not (isinstance(attributes, tuple) or isinstance(attributes, list)):
            raise ValueError(
                "attributes must be either list or tuple not {}.".format(
                    type(attributes)))
        if len(attributes) != 2:
            raise ValueError("attributes must have exactly two elements.")

        self.set_table_attributes(attributes[0])
        for column in set(self.column_names()) & set(attributes[1].keys()):
            self.set_column_attributes(column, attributes[1][column])

    def update(self, other_table):
        """
        Updates the columns in the table with columns from other table keeping
        the old ones.

        If a column exists in both tables the one from other_table is used.
        Creates links where possible.
        """
        self._data.update(other_table._data)

    def update_column(self, column_name, other_table, other_name=None):
        """
        Updates a column from a column in another table.

        The column other_name from other_table will be copied into column_name.
        If column_name already exists it will be replaced.

        When other_name is not used, then column_name will be used instead.
        """
        if other_name is None:
            other_name = column_name

        self._data.update_column(
            column_name, other_table._data, other_name)

    def __getitem__(self, index):
        """
        :rtype: table.File

        Return a new :class:`table.File` object with a subset of the table
        data.

        This method fully supports both one- and two-dimensional single indices
        and slices.

        Examples::

            >>> from sympathy.api import table
            >>> mytable = table.File.from_rows(
            ...     ['a', 'b', 'c'],
            ...     [[1, 2, 3], [4, 5, 6], [7, 8, 9]])
            >>> mytable.to_dataframe()
               a  b  c
            0  1  2  3
            1  4  5  6
            2  7  8  9
            >>> mytable[1].to_dataframe()
               a  b  c
            0  4  5  6
            >>> mytable[:,1].to_dataframe()
               b
            0  2
            1  5
            2  8
            >>> mytable[1,1].to_dataframe()
               b
            0  5
            >>> mytable[:2,:2].to_dataframe()
               a  b
            0  1  2
            1  4  5
            >>> mytable[::2,::2].to_dataframe()
               a  c
            0  1  3
            1  7  9
            >>> mytable[::-1,:].to_dataframe()
               a  b  c
            0  7  8  9
            1  4  5  6
            2  1  2  3


        If the key (index) is a string, it is assumed to be a column name and
        that column array will be returned.
        """
        if isinstance(index, six.string_types):
            return self.get_column_to_array(index)
        else:
            return File(data=self._data[index])

    def __setitem__(self, index, other_table):
        """
        Update the values at index with the values from other_table.

        This method fully supports both one- and two-dimensional single indices
        and slices, but the dimensions of the slice must be the same as the
        dimensions of other_table.

        If the key (index) is a string, it is assumed to be a column name and
        the value (other_table) argument an array.
        """

        if isinstance(index, six.string_types):
            self.set_column_from_array(index, other_table)
        else:
            self._data[index] = other_table._data

    def __contains__(self, key):
        """
        Return True if table contains a column named key.

        Equivalent to :meth:`has_column`.
        """
        return self._data.has_column(key)

    def has_column(self, key):
        """
        Return True if table contains a column named key.

        .. versionadded:: 1.1.3
        """
        return self._data.has_column(key)

    def hjoin(self, other_table, mask=False, rename=False):
        """
        Add the columns from other_table.

        Analoguous to :meth:`update`.
        """
        sybase.hjoin(self._data, other_table._data, mask=mask, rename=rename)

    def vjoin(self, other_tables, input_index='', output_index='', fill=True,
              minimum_increment=1):
        """
        Add the rows from the other_tables at the end of this table.

        Parameters
        ----------
        other_tables: [table]
        input_index: six.text_type
                     Column name for specified index column (deprecated).
        output_index: six.text_type
                      Column name for output index column generated
        fill: bool or None
              When True, attempt to fill with NaN or a zero-like value.
              When False, discard columns not present in all other_tables.
              When None, mask output.
        minimum_increment: int
                           Index increment added for empty tables.

        Returns
        -------
        table

        """
        input_list = sylist(types.from_string('[sytable]'))
        for other_table in other_tables:
            input_list.append(other_table._data)
        try:
            sybase.vjoin(self._data, input_list, input_index, output_index,
                         fill, minimum_increment)
        except type_exc.DatasetTypeError:
            raise exc.SyColumnTypeError(
                'Input columns to stack have incompatible types')

    def vsplit(self, output_list, input_index, remove_fill):
        """Split the current table to a list of tables by rows."""
        temp_list = []
        sybase.vsplit(
            self._data, temp_list, input_index, remove_fill)
        for pair in temp_list:
            output_list.append(File(data=pair[1]))

    def source(self, other_table, shallow=False):
        self._data.source(other_table._data, shallow=False)

    @deprecated_method('1.5.0')
    def set_source_id(self, identifier):
        """Set source identifier. Not implemented."""
        pass

    def __copy__(self):
        obj = super(File, self).__copy__()
        obj._data = self._data.__copy__()
        return obj

    def __deepcopy__(self, memo=None):
        obj = super(File, self).__copy__()
        obj._data = self._data.__deepcopy__()
        return obj

    @classmethod
    def viewer(cls):
        from .. platform import table_viewer
        return table_viewer.TableViewer

    @classmethod
    def icon(cls):
        return 'ports/table.svg'

    @property
    def name(self):
        name = self._data.get_name()
        return name if name is not None else ''

    @name.setter
    def name(self, value):
        self.set_name(value)

    def names(self, kind=None, **kwargs):
        """
        The names that can be automatically adjusted from an adaf.

        kind should be one of 'cols' (all column names), 'attrs' (all table
        attribute names), or 'name' (the table name).
        """
        def calc_quote(name):
            return name.replace("'", "\\'")

        kind = kind or 'cols'
        res = []
        if kind == 'cols':
            res = self.column_names()
        elif kind == 'calc':
            res = ["['{}']".format(calc_quote(name))
                   for name in self.column_names()]

        elif kind == 'attrs':
            res = list(self.attrs().keys())
        elif kind == 'name':
            res = [self.name()]
        return res

    def types(self, kind=None, **kwargs):
        """Return types associated with names."""
        kind = kind or 'cols'
        res = []
        if kind == 'cols':
            res = [self.column_type(name) for name in self.names(kind)]
        elif kind == 'calc':
            res = self.types('cols')
        return res

    def attr(self, name):
        """Get the tables attribute with `name`."""
        attributes = _ordinary_attributes(self._data.get_table_attributes())
        return attributes.get(name, '')

    def set_attr(self, name, value):
        assert not _reserved(name)
        attributes = self._data.get_table_attributes()
        attributes[name] = value
        self.set_table_attributes(attributes)

    @property
    def attrs(self):
        """
        Return dictionary of attributes for table.

        .. versionadded:: 1.3.4
        """
        return self._data.get_table_attributes()

    def cols(self):
        """
        Get a list of all columns as :class:`Column` objects.

        .. versionadded:: 1.3.4
        """
        return [self.col(name) for name in self.column_names()]

    def col(self, name):
        """
        Get a :class:`Column` object for column with `name`.

        .. versionadded:: 1.3.4
        """
        return Column(name, self._data)


@inherit_doc
class FileList(filebase.FileListBase):
    """
    FileList has been changed and is now just a function which creates
    generators to sybase types.

    Old documentation follows:

    The :class:`FileList` class is used when working with lists of Tables.

    The main interfaces in :class:`FileList` are indexing or iterating for
    reading (see the :meth:`__getitem__()` method) and the :meth:`append()`
    method for writing.
    """

    sytype = '[table]'
    scheme = 'hdf5'


class Column(object):
    """
    The :class:`Column` class provides a read-only interface to a column in a
    Table.
    """

    def __init__(self, name, parent_data):
        self._name = name
        self._data = parent_data

    @property
    def data(self):
        """
        The data of the column as a numpy array. Equivalent to calling
        :meth:`File.get_column_to_array`.
        """
        return self._data.get_column(self._name)

    @property
    def name(self):
        """The name of the column."""
        return self._name

    def attr(self, name):
        """Return the value of the column attribute ``name``."""
        return self._data.get_column_attributes(self._name).get_attribute(name)

    @property
    def attrs(self):
        """A dictionary of all column attributes of this column."""
        return self._data.get_column_attributes(self._name).get()
