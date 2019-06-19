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
import unittest

import numpy as np

from sympathy.api.exceptions import SyDataError
from sympathy.api import table
from Gui.interactive import load_library


class NoEventTestCase(unittest.TestCase):
    """
    Test cases where the lookup table node should give an error, when there is
    no event column.
    """

    def setUp(self):
        self.library = load_library()

        self._lookupee_table = table.File()
        self._lookupee_table.set_column_from_array(
            'color', np.array(['green', 'blue', 'blue', 'red', 'blue']))

        self._template_table = table.File()
        self._template_table.set_column_from_array(
            'color', np.array(['yellow', 'red', 'blue', 'green']))

        self.lookup_node = self.library.node('Lookup Table')
        proot = self.lookup_node.parameters.data
        proot['perfect_match'].value = True
        proot['lookupee_columns'].list = ['color']
        proot['lookupee_columns'].value_names = ['color']
        proot['template_columns'].list = ['color']
        proot['template_columns'].value_names = ['color']

    def test_empty_lookupee_table(self):
        self.assertRaises(SyDataError, self.lookup_node.execute,
                          (self._template_table, table.File()))

    def test_empty_template_table(self):
        self.assertRaises(SyDataError, self.lookup_node.execute,
                          (table.File(), self._lookupee_table))

    def test_missing_lookup_column_lookupee_table(self):
        # Create a table with a column that isn't used.
        missing_column = table.File()
        missing_column.set_column_from_array('a', np.array(['a']))

        self.assertRaises(SyDataError, self.lookup_node.execute,
                          (self._template_table, missing_column))

    def test_missing_lookup_column_template_table(self):
        # Create a table with a column that isn't used.
        missing_column = table.File()
        missing_column.set_column_from_array('a', np.array(['a']))

        self.assertRaises(SyDataError, self.lookup_node.execute,
                          (missing_column, self._lookupee_table))

    def test_no_rows_template_table(self):
        # Create a template table with the correct column, but no rows.
        template_table = table.File()
        template_table.set_column_from_array(
            'color', np.array([]))

        self.assertRaises(SyDataError, self.lookup_node.execute,
                          (template_table, self._lookupee_table))

    def test_unmatched_row(self):
        # Create a lookupee table with a row ('magenta') that can't be matched.
        lookupee_table = table.File()
        lookupee_table.set_column_from_array(
            'color', np.array(['green', 'blue', 'blue', 'red', 'magenta']))

        self.assertRaises(SyDataError, self.lookup_node.execute,
                          (self._template_table, lookupee_table))

    def test_multiple_matching_rows(self):
        # Create a template table with two 'red' rows.
        template_table = table.File()
        template_table.set_column_from_array(
            'color', np.array(['yellow', 'red', 'red', 'green']))

        self.assertRaises(SyDataError, self.lookup_node.execute,
                          (template_table, self._lookupee_table))


class EventTestCase(unittest.TestCase):
    """
    Test cases where the lookup table node should give an error, when there is
    an event column.
    """

    def setUp(self):
        self.library = load_library()

        self._lookupee_table = table.File()
        self._lookupee_table.set_column_from_array(
            'date', np.array([2.1, 3.5, 3, 1, 0.1]))
        self._lookupee_table.set_column_from_array(
            'color', np.array(['green', 'yellow', 'yellow', 'red', 'green']))

        self._template_table = table.File()
        self._template_table.set_column_from_array(
            'date', np.array([0, 1, 2, 3, 3, 3]))
        self._template_table.set_column_from_array(
            'color', np.array(['green', 'red', 'green', 'yellow', 'red',
                               'green']))

        self.lookup_node = self.library.node('Lookup Table')
        proot = self.lookup_node.parameters.data
        proot['perfect_match'].value = True
        proot['lookupee_columns'].list = ['date', 'color']
        proot['lookupee_columns'].value_names = ['date', 'color']
        proot['template_columns'].list = ['date', 'color']
        proot['template_columns'].value_names = ['date', 'color']
        proot['event_column'].value = 0

    def test_empty_lookupee_table(self):
        self.assertRaises(SyDataError, self.lookup_node.execute,
                          (self._template_table, table.File()))

    def test_empty_template_table(self):
        self.assertRaises(SyDataError, self.lookup_node.execute,
                          (table.File(), self._lookupee_table))

    def test_no_rows_template_table(self):
        # Create a template table with the correct columns, but no rows.
        template_table = table.File()
        template_table.set_column_from_array(
            'date', np.array([]))
        template_table.set_column_from_array(
            'color', np.array([]))

        self.assertRaises(SyDataError, self.lookup_node.execute,
                          (template_table, self._lookupee_table))

    def test_too_early_event(self):
        lookupee_table = table.File()
        lookupee_table.set_column_from_array(
            'date', np.array([2.1, 3.5, 3, 1, 0.1, -1]))
        lookupee_table.set_column_from_array(
            'color', np.array(['green', 'yellow', 'yellow', 'red', 'green',
                               'green']))

        self.assertRaises(SyDataError, self.lookup_node.execute,
                          (self._template_table, lookupee_table))

    def test_unmatched_row(self):
        # Create a template table with the correct columns, but no rows.
        lookupee_table = table.File()
        lookupee_table.set_column_from_array(
            'date', np.array([2.1, 3.5, 3, 1, 0.1, 0]))
        lookupee_table.set_column_from_array(
            'color', np.array(['green', 'yellow', 'yellow', 'red', 'green',
                               'magenta']))

        self.assertRaises(SyDataError, self.lookup_node.execute,
                          (self._template_table, lookupee_table))

    def test_identical_events(self):
        self._template_table.set_column_from_array(
            'date', np.array([0, 1, 2, 3, 3, 0]))
        self.assertRaises(SyDataError, self.lookup_node.execute,
                          (self._template_table, self._lookupee_table))
