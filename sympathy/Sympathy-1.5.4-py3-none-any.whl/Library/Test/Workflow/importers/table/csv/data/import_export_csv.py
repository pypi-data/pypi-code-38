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
import six
from sympathy.api import table_wrapper

TEST_COLUMNS_DT_DICT = {'Float': 'f',
                        'Integers': 'i',
                        'Floats_mixed_with_integers': 'f',
                        'Integers_mixed_with_text': 'U',
                        'Integers_mixed_with_empty_slots': 'f',
                        'Floats_mixed_with_text': 'U',
                        'Floats_mixed_with_empty_slots': 'f',
                        'Booleans': 'i',
                        'DateTime': 'U',
                        'Symbols': 'U',
                        'Empty_Column': 'f'}
TEST_LENGTH_COLUMN = list(TEST_COLUMNS_DT_DICT.keys())[0]
NO_COLUMNS = len(TEST_COLUMNS_DT_DICT.keys())
COLUMN_LENGTH = 6
ASCII_COL_ROW_STR = [
    (1, 0, 0x41), (3, 1, 0x23), (5, 2, 0x24), (7, 0, 0x2a)]
ISO_8859_1_COL_ROW_STR = [
    (1, 0, 0x41), (3, 1, 0xa7), (5, 2, 0xa5), (7, 0, 0xb0)]
ISO_8859_15_COL_ROW_STR = [
    (1, 0, 0x41), (3, 1, 0xa7), (5, 2, 0x20ac), (7, 0, 0xb0)]
UTF_8_COL_ROW_STR = [
    (1, 0, 0x41), (3, 1, 0xa7), (5, 2, 0xa5), (7, 0, 0xb0)]
UTF_16_COL_ROW_STR = [
    (1, 0, 0x41), (3, 1, 0xa7), (5, 2, 0xa5), (7, 0, 0xb0)]
Windows_1252_COL_ROW_STR = [
    (1, 0, 0x41), (3, 1, 0xa7), (5, 2, 0xa5), (7, 0, 0xb0)]


class TestSignalLengths(table_wrapper.TableWrapper):
    """Tests the length of the imported table."""
    _ERROR_MESSAGE = 'TestSignalLengths'

    def execute(self):
        float_col = self.in_table.get_column_to_array(TEST_LENGTH_COLUMN)
        if float_col.size != COLUMN_LENGTH:
            raise Exception(self._ERROR_MESSAGE)


class TestNoColumns(table_wrapper.TableWrapper):
    """Test the number of imported columns."""
    _ERROR_MESSAGE = 'TestNoColumns'

    def execute(self):
        no_table_columns = len(self.in_table.column_names())
        if no_table_columns != NO_COLUMNS:
            raise Exception(self._ERROR_MESSAGE)


class TestColumnDataTypes(table_wrapper.TableWrapper):
    """Test the datatypes of a selecetion of columns."""
    _ERROR_MESSAGE = 'TestColumnDataTypes'

    def execute(self):
        for column_name, column_dt_kind in six.iteritems(TEST_COLUMNS_DT_DICT):
            column = self.in_table.get_column_to_array(column_name)
            if column.dtype.kind != column_dt_kind:
                raise Exception(self._ERROR_MESSAGE)


class TestASCIIEncoding(table_wrapper.TableWrapper):
    """Test import from a csv file in ascii encoding."""
    _ERROR_MESSAGE = 'ASCII Encoding'

    def execute(self):
        colnames = self.in_table.column_names()
        for col, row, hex_str in ASCII_COL_ROW_STR:
            char = self.in_table.get_column_to_array(colnames[col])[row]
            if ord(char) != hex_str:
                raise Exception(self._ERROR_MESSAGE)


class ISO_8859_1(table_wrapper.TableWrapper):
    """Test import from a csv file in ascii encoding."""
    _ERROR_MESSAGE = 'ISO_8859-1 Encoding'

    def execute(self):
        colnames = self.in_table.column_names()
        for col, row, hex_str in ISO_8859_1_COL_ROW_STR:
            char = self.in_table.get_column_to_array(colnames[col])[row]
            if ord(char) != hex_str:
                raise Exception(self._ERROR_MESSAGE)


class ISO_8859_15(table_wrapper.TableWrapper):
    """Test import from a csv file in ascii encoding."""
    _ERROR_MESSAGE = 'ISO_8859-15 Encoding'

    def execute(self):
        colnames = self.in_table.column_names()
        for col, row, hex_str in ISO_8859_15_COL_ROW_STR:
            char = self.in_table.get_column_to_array(colnames[col])[row]
            if ord(char) != hex_str:
                raise Exception(self._ERROR_MESSAGE)


class UTF_8(table_wrapper.TableWrapper):
    """Test import from a csv file in ascii encoding."""
    _ERROR_MESSAGE = 'UTF-8 Encoding'

    def execute(self):
        colnames = self.in_table.column_names()
        for col, row, hex_str in UTF_8_COL_ROW_STR:
            char = self.in_table.get_column_to_array(colnames[col])[row]
            if ord(char) != hex_str:
                raise Exception(self._ERROR_MESSAGE)


class UTF_16(table_wrapper.TableWrapper):
    """Test import from a csv file in ascii encoding."""
    _ERROR_MESSAGE = 'UTF-16 Encoding'

    def execute(self):
        colnames = self.in_table.column_names()
        for col, row, hex_str in UTF_16_COL_ROW_STR:
            char = self.in_table.get_column_to_array(colnames[col])[row]
            if ord(char) != hex_str:
                raise Exception(self._ERROR_MESSAGE)


class Windows_1252(table_wrapper.TableWrapper):
    """Test import from a csv file in ascii encoding."""
    _ERROR_MESSAGE = 'Windows_1252 Encoding'

    def execute(self):
        colnames = self.in_table.column_names()
        for col, row, hex_str in Windows_1252_COL_ROW_STR:
            char = self.in_table.get_column_to_array(colnames[col])[row]
            if ord(char) != hex_str:
                raise Exception(self._ERROR_MESSAGE)
