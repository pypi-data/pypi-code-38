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
from __future__ import (print_function, division, unicode_literals,
                        absolute_import)
from sympathy.api import table
from sympathy.api import adaf
import numpy as np
import six
from nose.tools import assert_raises


def test_table_set_column():
    table1 = table.File()

    # Expected to succeed.
    table1.set_column_from_array('t', np.arange(3))

    table1.set_column_attributes('t', {'a': 'b'})
    table1.set_column_attributes('t', {'a': 1})
    table1.set_column_attributes('t', {'a': False})

    table1.set_table_attributes({'a': 'a'})
    table1.set_table_attributes({'a': 1})
    table1.set_table_attributes({'a': False})

    table1.set_name('a')
    # Expected to fail.
    try:
        table1.set_column_from_array(0, np.arange(3))
    except ValueError:
        pass
    else:
        assert(False)

    try:
        table1.set_column_from_array(False, np.arange(3))
    except ValueError:
        pass
    else:
        assert(False)

    if six.PY2:
        try:
            table1.set_column_from_array(b'\xc3\xa4', np.arange(3))
        except ValueError:
            pass
        else:
            assert(False)

        try:
            table1.set_column_attributes('t', {b'\xc3\xa4': 'b'})
        except ValueError:
            pass
        else:
            assert(False)

        try:
            table1.set_column_attributes('t', {'b': b'\xc3\xa4'})
        except ValueError:
            pass
        else:
            assert(False)

        try:
            table1.set_table_attributes({b'\xc3\xa4': 'a'})
        except ValueError:
            pass
        else:
            assert(False)

        try:
            table1.set_table_attributes({'a': b'\xc3\xa4'})
        except ValueError:
            pass
        else:
            assert(False)

    try:
        table1.set_column_attributes('t', {0: 'b'})
    except ValueError:
        pass
    else:
        assert(False)

    try:
        table1.set_column_attributes('t', {False: False})
    except ValueError:
        pass
    else:
        assert(False)



def test_adaf_create_column():
    adaf1 = adaf.File()
    sys = adaf1.sys.create('systemname')
    raster = sys.create('rastername')
    try:
        raster.create_basis(np.arange(3), {'unit': 3})
    except ValueError:
        pass
    else:
        assert(False)
    try:
        raster.create_basis(np.arange(3), {'description': 3})
    except ValueError:
        pass
    else:
        raster.create_signal('t', np.arange(3), {'unit': 3})

    raster.create_basis(
        np.arange(3), {'unit': 's', 'description': 'howto basis'})
    raster.create_signal('t', np.arange(3),
                         {'unit': 'm', 'description': 'howto signal'})


def test_sytable__getitem__():
    table1 = table.File()
    table2 = table.File()

    for i in range(5):
        table1.set_column_from_array(str(i), i + np.arange(5))
        table2.set_column_from_array(str(i + 2), i + 2 + np.arange(5 + 2))

    # Test of empty row slice.
    assert(table1[:0].to_matrix().tolist() == [])
    assert(table1[5:].to_matrix().tolist() == [])

    # Test of non-empty row slice.
    assert((table1[0].to_matrix() ==
            np.matrix([np.arange(5)])).all())
    assert((table1[1:2].to_matrix() ==
            np.matrix([np.arange(5) + 1])).all())

    # Test of empty column slice.
    assert(table1[:, :0].to_matrix().tolist() == [])
    assert(table1[:, 5:].to_matrix().tolist() == [])

    # Test of non-empty column slice.
    assert((table1[:, 0].to_matrix() ==
            np.matrix([np.arange(5)]).T).all())
    assert((table1[:, 1:2].to_matrix() ==
            np.matrix([np.arange(5) + 1]).T).all())

    # Test of empty subcube slice.
    assert(table1[:0, :0].to_matrix().tolist() == [])
    assert(table1[5:, 5:].to_matrix().tolist() == [])
    assert(table1[:0, 5:].to_matrix().tolist() == [])
    assert(table1[5:, :0].to_matrix().tolist() == [])

    # Test of subcube slice.
    assert((table1[:, 2:].to_matrix() ==
            table2[:5, :3].to_matrix()).all())
    assert((table1[2:-1, 2:-1].to_matrix() ==
            np.matrix([[4, 5],
                       [5, 6]])).all())

    # Test of single item slice.
    assert(table1[0, 0].to_matrix() == np.matrix([[0]]))
    assert(table1[1, 1].to_matrix() == np.matrix([[2]]))
    assert(table1[4, 4].to_matrix() == np.matrix([[8]]))

    # Test of index array slice.
    assert((table1[[1, 3]].to_matrix() ==
           np.matrix([[1, 2, 3, 4, 5], [3, 4, 5, 6, 7]])).all())
    assert((table1[:, [1, 3]].to_matrix() ==
           np.matrix([[1, 3], [2, 4], [3, 5], [4, 6], [5, 7]])).all())
    assert((table1[range(5), range(5)].to_matrix() ==
            table1.to_matrix()).all())

    # Test of negative row slice indices
    assert((table1[-1, :].to_matrix() == np.matrix([4, 5, 6, 7, 8])).all())
    assert((table1[-2:, :].to_matrix() ==
           np.matrix([[3, 4, 5, 6, 7], [4, 5, 6, 7, 8]])).all())
    assert((table1[-2:-1, :].to_matrix() ==
           np.matrix([3, 4, 5, 6, 7])).all())


def test_sytable__setitem__():
    table1 = table.File()
    table2 = table.File()
    table3 = table.File()
    table4 = table.File()

    for i in range(5):
        table1.set_column_from_array(str(i), i + np.arange(5))
        table2.set_column_from_array(str(i + 2), i + 2 + np.arange(5 + 2))

    # Test full slice.
    for i in range(2):
        for value in [table1, table2, table3]:
            table4[:] = value
            assert((table4.to_matrix() == value.to_matrix()).all())

    # Test row slice.
    for value in [table1, table2]:
        table4[:] = table3
        for i in range(value.number_of_rows()):
            table4[i:i + 1] = value[i:i + 1]
        assert((table4.to_matrix() == value.to_matrix()).all())

    # Test column slice.
    for value in [table1, table2]:
        table4[:] = table3
        for i in range(value.number_of_columns()):
            table4[:, i:i + 1] = value[:, i:i + 1]
        assert((table4.to_matrix() == value.to_matrix()).all())

    test_matrix = (np.matrix([[6, 6, 6, 6, 6],
                              [7, 7, 7, 7, 7]]))

    # Test index array slice.
    table4[:] = table1
    table4[[1, 2]] = table.File.from_matrix(
        ['0', '1', '2', '3', '4'], test_matrix)
    assert((table4[[1, 2]].to_matrix() == test_matrix).all())

    table4[:] = table1
    table4[[1, 3]] = table.File.from_matrix(
        ['0', '1', '2', '3', '4'], test_matrix)
    assert((table4[[1, 3]].to_matrix() == test_matrix).all())

    table4[:] = table1
    table4[:, [1, 3]] = table.File.from_matrix(
        ['1', '3'], test_matrix.T)
    assert((table4[:, [1, 3]].to_matrix() == test_matrix.T).all())

    table4[:] = table1
    table4[:, [0, 1]] = table.File.from_matrix(
        ['0', '1'], test_matrix.T)
    assert((table4[:, [0, 1]].to_matrix() == test_matrix.T).all())

    # Test of subcube slice.
    table4[:] = table2
    table4[2:4, 2:4] = table1[2:4, 2:4]
    assert((table4.to_matrix() ==
            np.matrix([[2, 3, 4, 5, 6],
                       [3, 4, 5, 6, 7],
                       [4, 5, 4, 5, 8],
                       [5, 6, 5, 6, 9],
                       [6, 7, 8, 9, 10],
                       [7, 8, 9, 10, 11],
                       [8, 9, 10, 11, 12]])).all())


def test_sytable_column_dims():
    t = table.File()

    t.set_column_from_array('a', np.array([1]))
    assert t.number_of_rows() == 1
    assert t.number_of_columns() == 1

    # Test adding zero- and two-dimensional columns
    with assert_raises(ValueError):
        t.set_column_from_array('b', np.array(1))
    with assert_raises(ValueError):
        t.set_column_from_array('c', np.array([[1]]))
    assert t.number_of_rows() == 1
    assert t.number_of_columns() == 1


def test_sytable_column_lengths():
    t = table.File()

    t.set_column_from_array('a', np.array([1, 2, 3]))
    assert t.number_of_rows() == 3

    # Test adding a column of other length
    with assert_raises(ValueError):
        t.set_column_from_array('b', np.array([1, 2, 3, 4]))
    with assert_raises(ValueError):
        t.set_column_from_array('b', np.array([1, 2]))
    assert t.number_of_rows() == 3

    # Test overwriting a single column with different length
    t.set_column_from_array('a', np.array([1, 2]))
    assert t.number_of_rows() == 2
    t.set_column_from_array('a', np.array([1, 2, 3, 4]))
    assert t.number_of_rows() == 4

    # Test updating a single column from another Table
    t2 = table.File()
    t2.set_column_from_array('a', np.array([1, 2, 3]))
    with assert_raises(ValueError):
        t.update_column('b', t2, 'a')
    assert t.number_of_rows() == 4
    t.update_column('a', t2, 'a')
    assert t.number_of_rows() == 3

    # Test updating all columns from another Table
    t.set_column_from_array('b', np.array([1, 2, 3]))
    t2.clear()
    t2.set_column_from_array('b', np.array([1, 2]))
    t2.set_column_from_array('c', np.array([1, 2]))
    with assert_raises(ValueError):
        t.update(t2)
    assert t.number_of_rows() == 3
    t2.set_column_from_array('a', np.array([1, 2]))
    t.clear()

    t.update(t2)

    assert t.number_of_rows() == 2


def test_table_from_rows_to_rows():
    # Test of table.File.from_rows and table.File.to_rows
    # table.File.from_rows(column_names, row_data).to_rows() should be
    # equal to row_data when iterated.

    cells = 2 ** 10

    for i in [0, 2, 4, 8]:
        columns = 2 ** i
        rows = cells // columns
        column_names = [str(j) for j in range(columns)]

        row_data = [np.random.rand(columns).tolist()
                    for j in range(rows)]

        for rowa, rowb in six.moves.zip(
                table.File.from_rows(column_names, row_data).to_rows(),
                row_data):
            assert(list(rowa) == rowb)
