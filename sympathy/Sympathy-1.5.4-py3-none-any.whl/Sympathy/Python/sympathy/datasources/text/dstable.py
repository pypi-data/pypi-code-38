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
from collections import OrderedDict
import six
import numpy as np
from . import dsgroup

NAME = '__sy_name__'


class TextTable(dsgroup.TextGroup):
    """Abstraction of an Text-table."""
    def __init__(self,
                 factory,
                 create_content,
                 datapointer,
                 group=None,
                 can_write=False,
                 container_type=None,
                 create_path=None):
        super(TextTable, self).__init__(
            factory, create_content, datapointer, group, can_write,
            container_type, create_path)
        self._data = self.group.setdefault('columns', OrderedDict())

    def read_column_attributes(self, column_name):
        return self._data[column_name][2]

    def write_column_attributes(self, column_name, properties):
        self._data[column_name][2] = dict(properties)

    def read_column(self, column_name, index=None):
        """Return np.rec.array with data from the given column name."""
        def bool_index(length, int_index):
            """Return bool index vector from int index vector."""
            result = np.zeros(length, dtype=bool)
            result[int_index] = True
            return result

        def indexed(column, index):
            if isinstance(index, list):
                index = bool_index(len(column), index)
            return column[index]

        # Construct the table as numpy array.
        column = np.array(*self._data[column_name][:2])
        return indexed(column, index) if index is not None else column

    def write_column(self, column_name, column):
        """
        Stores table in the Text file, at path,
        with data from the given table
        """
        # Write column data to the group.
        self._data[column_name] = [column.tolist(), str(column.dtype), {}]

    def write_started(self, number_of_rows, number_of_columns):
        pass

    def write_finished(self):
        pass

    def columns(self):
        """Return a list contaning the available column names."""
        return list(self._data)

    def column_type(self, column_name):
        return np.dtype(self._data[column_name][1])

    def number_of_rows(self):
        try:
            return len(six.next(six.itervalues(self._data))[0])
        except StopIteration:
            return 0

    def number_of_columns(self):
        return len(self._data)

    def write_name(self, name):
        self.group[NAME] = name

    def read_name(self):
        return self.group.get(NAME, '')

    def read_table_attributes(self):
        return dict(self.group.get('attributes', {}))

    def write_table_attributes(self, properties):
        if properties:
            self.group['attributes'] = dict(properties)
