# Copyright (c) 2015-2017 Combine Control Systems AB
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
import numpy as np
import os
import unittest
from sylib.matlab import matlab
from sympathy.api import table
from sympathy.api.exceptions import SyDataError, NoDataError


class TestMatlab(unittest.TestCase):
    def setUp(self):  # noqa
        self.longMessage = True

    def test_read_write_matfile(self):
        in_table = table.File()
        signal1 = np.arange(10)
        signal2 = np.arange(10)
        attribute = {'attribute': 'value'}
        in_table.set_table_attributes(attribute)
        in_table.set_column_from_array('data1', signal1, attribute)
        in_table.set_column_from_array('data2', signal2)

        in_matlab_name = matlab.allocate_mat_file()
        matlab.write_table_to_matfile(in_table, in_matlab_name)

        in_table = matlab.read_matfile_to_table(in_matlab_name)
        self.assertEquals(
            in_table.get_table_attributes(), attribute,
            "Table attributes don't match")
        self.assertEquals(
            in_table.get_column_attributes('data1'), attribute,
            "Column attributes don't match")
        self.assertEquals(
            in_table.get_column_attributes('data2'), {},
            "Column attributes don't match")

        test_signal1 = in_table.get_column_to_array('data1')
        test_signal2 = in_table.get_column_to_array('data2')
        for i in range(len(test_signal1)):
            self.assertEquals(
                test_signal1[i], signal1[i], "Column data don't match")
            self.assertEquals(
                test_signal2[i], signal2[i], "Column data don't match")

    def test_validate_ok(self):
        data = {'names': [], 'col': [], 'table_attr': [],
                'col_attr': [], 'col_attr_values': []}

        try:
            matlab.validate(data)
        except:
            self.fail("validate(data) raised exception unexpectedly!")

    def test_validate_missing_key(self):
        data = {'col': [], 'table_attr': [],
                'col_attr': [], 'col_attr_values': []}

        with self.assertRaises(SyDataError,
                               msg='validate(data) didn\'t raise SyDataError '
                                   'when key names were missing'):
            matlab.validate(data)

        data['names'] = []
        data.pop('col')
        with self.assertRaises(SyDataError,
                               msg='validate(data) didn\'t raise SyDataError '
                                   'when key col were missing'):
            matlab.validate(data)

        with self.assertRaises(NoDataError,
                               msg='validate(data) didn\'t raise SyDataError '
                                   'when data is none'):
            matlab.validate(None)

    def test_allocate_files(self):
        file = matlab.allocate_mat_file()
        self.assertTrue(os.path.isfile(file), "File is not created correctly")
        self.assertTrue('matlab_' in file,
                        "File doesn't have correct prefix")
        self.assertTrue('.mat' in file,
                        "File doesn't have correct suffix")
        os.remove(file)
