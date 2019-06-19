# -*- coding:utf-8 -*-
# Copyright (c) 2017, Combine Control Systems AB
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
import numpy as np
import datetime

from sympathy.api import table_wrapper


class DateTimeCreator(object):
    def create_data_strategy(self, value, dtype, result):
        raise NotImplementedError

    def create_data(self):
        dt1 = datetime.datetime(1, 1, 1)
        dt2 = datetime.datetime(1, 2, 1)
        result = []
        for value, dtype in [(dt1, 'datetime64[us]'),
                             (dt2 - dt1, 'timedelta64[us]')]:
            self.create_data_strategy(value, dtype, result)
        return result


class DateTimeCreatorLengthZero(DateTimeCreator):
    def create_data_strategy(self, value, dtype, result):
            result.append((dtype + '0', np.array([], dtype=dtype)))


class DateTimeCreatorLengthUnit(DateTimeCreator):
    def create_data_strategy(self, value, dtype, result):
        result.append((dtype + '1', np.array([value],
                                             dtype=dtype)))
        result.append((dtype + '2', np.array([value])))


class TestCreateDateTimeLengthZero(table_wrapper.TableWrapper):
    def execute(self):
        for key, value in DateTimeCreatorLengthZero().create_data():
            self.out_table.set_column_from_array(key, value)


class TestCreateDateTimeLengthUnit(table_wrapper.TableWrapper):
    def execute(self):
        for key, value in DateTimeCreatorLengthUnit().create_data():
            self.out_table.set_column_from_array(key, value)


class TestPropagateDateTime(table_wrapper.TableWrapper):
    def execute(self):
        for name in self.in_table.column_names():
            self.out_table.set_column_from_array(
                name, self.in_table.get_column_to_array(name))


class TestCheckDateTimeLengthZero(table_wrapper.TableWrapper):
    def execute(self):
        for key, value in DateTimeCreatorLengthZero().create_data():
            column = self.in_table.get_column_to_array(key)
            assert(np.all(column == value.astype(column.dtype)))


class TestCheckDateTimeLengthUnit(table_wrapper.TableWrapper):
    def execute(self):
        for key, value in DateTimeCreatorLengthUnit().create_data():
            column = self.in_table.get_column_to_array(key)
            assert(np.all(column == value.astype(column.dtype)))
