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
                        'Integers': 'f',
                        'Floats_mixed_with_integers': 'f',
                        'Integers_mixed_with_text': 'U',
                        'Integers_mixed_with_empty_slots': 'f',
                        'Floats_mixed_with_text': 'U',
                        'Floats_mixed_with_empty_slots': 'f',
                        'Booleans': 'b',
                        'xls_error_message': 'U',
                        'DateTime': 'M',
                        'DateTime_mixed_with_text': 'U',
                        'DateTime_mixed_with_empty': 'M',
                        'Time': 'm',
                        'Time_mixed_with_text': 'U',
                        'Time_mixed_with_empty': 'm',
                        'Symbols': 'U',
                        'Empty_Column': 'U'}
TEST_LENGTH_COLUMN = list(TEST_COLUMNS_DT_DICT.keys())[0]
NO_COLUMNS = len(TEST_COLUMNS_DT_DICT.keys())
COLUMN_LENGTH = 6


class TestSignalLengths(table_wrapper.TableWrapper):
    """ Tests the length of the imported table. """
    def __init__(self, fq_infilename, fq_outfilename):
        super(TestSignalLengths, self).__init__(fq_infilename, fq_outfilename)

        self._error_message = ('TestSignalLengths')

    def execute(self):
        try:
            float_col = self.in_table.get_column_to_array(TEST_LENGTH_COLUMN)
            if float_col.size != COLUMN_LENGTH:
                raise Exception(self._error_message)

        except KeyError as e:
            raise Exception(e)


class TestNoColumns(table_wrapper.TableWrapper):
    """ Test the number of imported columns. """
    def __init__(self, fq_infilename, fq_outfilename):
        super(TestNoColumns, self).__init__(fq_infilename, fq_outfilename)

        self._error_message = ('TestNoColumns')

    def execute(self):
        no_table_columns = len(self.in_table.column_names())
        if  no_table_columns != NO_COLUMNS:
            raise Exception(self._error_message)


class TestColumnDataTypes(table_wrapper.TableWrapper):
    """ Test the datatypes of a selecetion of columns. """
    def __init__(self, fq_infilename, fq_outfilename):
        super(TestColumnDataTypes, self).__init__(
            fq_infilename, fq_outfilename)

        self._error_message = ('TestColumnDataTypes')

    def execute(self):
        for column_name, column_dt_kind in six.iteritems(TEST_COLUMNS_DT_DICT):
            column = self.in_table.get_column_to_array(column_name)
            if column.dtype.kind != column_dt_kind:
                raise Exception(self._error_message)
