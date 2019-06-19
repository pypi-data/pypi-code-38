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
This module contains classes that wrap tables or lists of tables for use in
various function selector, F(x), nodes in Sympathy for Data.
"""
from sympathy.platform import exceptions as syexceptions
from sympathy.api import table  # NOQA
from .. utils.context import deprecated_method
from . import fx_wrapper


class TableWrapper(fx_wrapper.FxWrapper):
    """
    TableWrapper should be used as the parent class for classes to be used
    in the table F(x) nodes.

    Interact with the table through in_table and out_table.
    """
    arg_types = ['table']
    list_wrapper = False

    def __init__(self, in_table, out_table, extra_table=None):
        self.in_table = in_table
        self.out_table = out_table
        self.extra_table = extra_table

    def execute(self):
        """Execute is called from the F(x) node."""
        raise syexceptions.SyConfigurationError(
            "This f(x) script doesn't implement an execute method.")

    @deprecated_method('1.5.0')
    def column(self, name):
        """Return column 'name' as a numpy array."""
        return self.in_table.get_column_to_array(name)

    @deprecated_method('1.5.0')
    def columns(self):
        """Return a list with the names of the table columns."""
        return self.in_table.column_names()

    @deprecated_method('1.5.0')
    def number_of_rows(self):
        """Return the number of rows in the table."""
        return self.in_table.number_of_rows()

    @deprecated_method('1.5.0')
    def set(self, in_table):
        """Write rec array."""
        self.out_table.update(self.out_table.from_recarray(in_table))

    @deprecated_method('1.5.0')
    def set_column(self, column_name, column):
        """Set a column from an numpy.array."""
        self.out_table.set_column_from_array(column_name, column)

    @deprecated_method('1.5.0')
    def value(self):
        """Return numpy rec array."""
        return self.in_table.to_recarray()

    @deprecated_method('1.5.0')
    def to_dataframe(self):
        """
        Return pandas DataFrame object with chosen table columns.
        columns is a list of selected columns or None if all columns are
        desired.
        """
        return self.in_table.to_dataframe()

    @deprecated_method('1.5.0')
    def from_dataframe(self, dataframe):
        """
        Write columns contained in pandas DataFrame object, dataframe, to
        table.
        """
        self.out_table.update(self.out_table.from_dataframe(dataframe))

    @deprecated_method('1.5.0')
    def to_matrix(self):
        """
        Return numpy Matrix with chosen table columns.
        columns is a list of selected columns or None if all columns are
        desired.
        """
        return self.in_table.to_matrix()

    @deprecated_method('1.5.0')
    def from_matrix(self, matrix, columns):
        """
        Write columns contained in numpy Matrix object, matrix, to
        table.

        columns is a list of the column names to give each matrix column.
        If columns is None then all current column names will be used for the
        matrix columns.
        """
        self.out_table.update(self.out_table.from_matrix(matrix, columns))

    @deprecated_method('1.5.0')
    def get_name(self):
        """Return name of input table or None if name is not set."""
        return self.in_table.get_name()

    @deprecated_method('1.5.0')
    def set_name(self, name):
        """Set name of output table."""
        self.out_table.set_name(name)

    @deprecated_method('1.5.0')
    def get_column_attributes(self, column_name):
        """Return dictionary of attributes for column_name."""
        return self.in_table.get_column_attributes(column_name)

    @deprecated_method('1.5.0')
    def set_column_attributes(self, column_name, attributes):
        """Set attributes for column_name to attributes."""
        return self.out_table.set_column_attributes(
            column_name, attributes)


class TablesWrapper(TableWrapper):
    """TablesWrapper should be used as the parent class for classes to be used
    in the tables F(x) nodes.

    Interact with the tables through in_table_list and out_table_list.
    """
    arg_types = ['[table]']
    list_wrapper = True

    def __init__(self, in_table, out_table, extra_table=None):
        super(TablesWrapper, self).__init__(in_table, out_table, extra_table)
        self.in_table_list = in_table
        self.out_table_list = out_table
