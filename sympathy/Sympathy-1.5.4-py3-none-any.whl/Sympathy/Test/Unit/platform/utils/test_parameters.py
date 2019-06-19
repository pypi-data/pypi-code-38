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
import unittest

import six

from sympathy.platform import gennode, exceptions


list_a = ['A', 'B', 'C', 'D', 'E']


def test_editors():
    """Testing that all editors can indeed be created."""
    min_ = 0
    max_ = 2000
    decimals = 3
    step = 1
    selection = 'multiselect'
    filter_ = ['Any files (*)']
    states = ['abs', ('test', 'Custom rel state', six.moves.getcwd())]

    gennode.editors.lineedit_editor().value()
    gennode.editors.textedit_editor().value()
    gennode.editors.code_editor().value()
    gennode.editors.bounded_lineedit_editor(min_, max_).value()
    gennode.editors.spinbox_editor(step).value()
    gennode.editors.bounded_spinbox_editor(min_, max_, step).value()
    gennode.editors.decimal_spinbox_editor(step, decimals).value()
    gennode.editors.bounded_decimal_spinbox_editor(
        min_, max_, step, decimals).value()
    gennode.editors.filename_editor(filter_).value()
    gennode.editors.filename_editor(filter_, states=states).value()
    gennode.editors.savename_editor().value()
    gennode.editors.savename_editor(states=states).value()
    gennode.editors.directory_editor().value()
    gennode.editors.directory_editor(states=states).value()
    gennode.editors.list_editor().value()
    gennode.editors.selectionlist_editor(selection).value()
    gennode.editors.combo_editor().value()


class TestList(unittest.TestCase):
    """
    Test the interactions between value, value_names, and selection for
    parameter lists.
    """

    def setUp(self):
        self._params = gennode.parameters()

    def _assert_list(self, value=None, names=None, plist=None):
        if plist is None:
            plist = list_a
        if value is None and names is not None:
            value = [plist.index(n) for n in names if n in plist]
        elif value is not None and names is None:
            names = [plist[i] for i in value]
        else:
            raise ValueError("Exactly one of value and names should be used.")

        test_list = self._params['test']
        self.assertEqual(test_list.list, plist)
        self.assertEqual(test_list.value, value)
        self.assertEqual(test_list.value_names, names)
        if len(names) == 0:
            self.assertEqual(test_list.selected, None)
        elif len(names) == 1:
            self.assertEqual(test_list.selected, names[0])
        else:
            # This part of the API is pretty questionable:
            self.assertEqual(test_list.selected, names[0])
            # I wouldn't mind an error here instead  //Magnus

    def _assert_no_update_list(self, value=None, names=None, plist=None,
                               test_selected=True):
        if plist is None:
            plist = list_a
        if value is None:
            value = []
        if names is None:
            names = []

        test_list = self._params['test']
        self.assertEqual(test_list.list, plist)
        self.assertEqual(test_list.value, value)
        self.assertEqual(test_list.value_names, names)
        if not test_selected:
            return
        if len(value) == 0:
            self.assertEqual(test_list.selected, None)
        elif len(value) == 1:
            self.assertEqual(test_list.selected, plist[value[0]])
        else:
            # This part of the API is pretty questionable:
            self.assertEqual(test_list.selected, plist[value[0]])
            # I wouldn't mind an error here instead  //Magnus

    def test_init_no_args(self):
        """Create list with an empty list argument."""
        self._params.set_list('test')
        self._assert_list(value=[], plist=[])

    def test_init_plist(self):
        """Create list with only plist argument. Check that first element is
        selected."""
        self._params.set_list('test', plist=list_a)
        self._assert_list([0])

    def test_init_list(self):
        """Create list with only the list argument."""
        self._params.set_list('test', list=list_a)
        self._assert_list([0])

    def test_init_list_plist(self):
        """Create list with both list and plist args."""
        with self.assertRaises(Exception):
            self._params.set_list(
                'test', plist=list_a, list=[1, 2, 3])

    def test_init_empty_list(self):
        """Create list with an empty list argument."""
        self._params.set_list('test', list=[])
        self._assert_list(value=[], plist=[])

    def test_init_empty_value(self):
        """Create list with empty value arguments."""
        self._params.set_list('test', list=list_a, value=[])
        self._assert_list([])

    def test_init_single_value(self):
        """Create list with single-item value arguments."""
        self._params.set_list('test', list=list_a, value=[1])
        self._assert_list([1])

    def test_init_multi_value(self):
        """Create list with multi-item value arguments."""
        self._params.set_list('test', list=list_a, value=[1, 2])
        self._assert_list([1, 2])

    def test_init_out_of_bounds_value(self):
        """Create list with an out of bounds value argument."""
        self._params.set_list('test', value=[0])
        self._assert_list(value=[], plist=[])

    @unittest.skip('Expected failure')
    def test_init_repeated_value(self):
        """Create list with a repeated value argument."""
        self._params.set_list('test', list=list_a, value=[0, 0])
        self._assert_list(value=[0])

    def test_init_string_value(self):
        """Create list with a value argument of string type."""
        with self.assertRaises(TypeError):
            self._params.set_list('test', value=['A'])

    def test_init_empty_value_names(self):
        """Create list with empty value_names arguments."""
        self._params.set_list('test', list=list_a, value_names=[])
        self._assert_list([])

    def test_init_single_value_names(self):
        """Create list with single-item value_names arguments."""
        self._params.set_list('test', list=list_a, value_names=[list_a[1]])
        self._assert_list([1])

    def test_init_multi_value_names(self):
        """Create list with multi-item value_names arguments."""
        self._params.set_list('test', list=list_a, value_names=list_a[1:3])
        self._assert_list([1, 2])

    def test_init_non_existant_value_names(self):
        """Create list with a value_names arguments which isn't in the list."""
        self._params.set_list('test', list=list_a, value_names=['X'])
        self._assert_list(names=['X'])

    @unittest.skip('Expected failure')
    def test_init_repeated_value_names(self):
        """Create list with a repeaeted value_names arguments."""
        self._params.set_list('test', list=list_a, value_names=['A', 'A'])
        self._assert_list(names=['A'])

    def test_init_conflicting_value_value_names(self):
        """Create list with conflicting value and value_names arguments."""
        # This should trigger a warning, but otherwise be accepted with
        # value_names being favored.
        self._params.set_list(
            'test', list=list_a, value=[0], value_names=['B'])
        self._assert_list(names=['B'])

    def test_modify_value_empty(self):
        """Modify value to empty list."""
        self._params.set_list('test', list=list_a, value=[1, 2])
        self._params['test'].value = []
        self._assert_list([])

    def test_modify_value_single(self):
        """Modify value in single-valued list."""
        self._params.set_list('test', list=list_a, value=[1, 2])
        self._params['test'].value = [2]
        self._assert_list([2])

    def test_modify_value_multi(self):
        """Modify value in multiple-valued list."""
        self._params.set_list('test', list=list_a, value=[1])
        self._params['test'].value = [1, 2]
        self._assert_list([1, 2])

    def test_modify_value_nonexistant(self):
        """Modify value to an index outside of the list."""
        self._params.set_list('test', list=list_a, value=[1, 2])
        with self.assertRaises(IndexError):
            self._params['test'].value = [len(list_a)]
        # Check that the failing operation didn't mutate the parameter:
        self._assert_list([1, 2])

    def test_modify_value_inplace(self):
        """Attempt to modify value inplace."""
        self._params.set_list('test', list=list_a, value=[1, 2])
        self._params['test'].value.append(3)
        # Check that the operation didn't actually mutate the parameter:
        self._assert_list([1, 2])

    def test_modify_value_names_empty(self):
        """Modify value_names to empty list."""
        self._params.set_list('test', list=list_a, value=[1, 2])
        self._params['test'].value_names = []
        self._assert_list([])

    def test_modify_value_names_single(self):
        """Modify value_names to single-valued list."""
        self._params.set_list('test', list=list_a, value=[1, 2])
        self._params['test'].value_names = [list_a[2]]
        self._assert_list([2])

    def test_modify_value_names_multi(self):
        """Modify value_names to multiple-valued list."""
        self._params.set_list('test', list=list_a, value=[1])
        self._params['test'].value_names = list_a[1:3]
        self._assert_list([1, 2])

    def test_modify_value_names_nonexistant(self):
        """Modify value_names to a value that doesn't exist in the list."""
        self._params.set_list('test', list=list_a, value=[1, 2])
        self._params['test'].value_names = ['X']
        self._assert_list(names=['X'])

    def test_modify_value_names_inplace(self):
        """Attempt to modify value_names inplace."""
        self._params.set_list('test', list=list_a, value=[1, 2])
        self._params['test'].value_names.append('D')
        # Check that the operation didn't actually mutate the parameter:
        self._assert_list([1, 2])

    def test_modify_selected_none(self):
        """Modify selected to None."""
        self._params.set_list('test', list=list_a, value=[1, 2])
        self._params['test'].selected = None
        self._assert_list([])

    def test_modify_selected_single(self):
        """Modify selected."""
        self._params.set_list('test', list=list_a, value=[1, 2])
        self._params['test'].selected = list_a[2]
        self._assert_list([2])

    def test_modify_selected_nonexistant(self):
        """Modify selected to a value that doesn't exist in the list."""
        self._params.set_list('test', list=list_a, value=[1, 2])
        self._params['test'].selected = 'X'
        self._assert_list(names=['X'])

    def test_modify_list_grow(self):
        """Modify list to have all the elements that it had plus a few more."""
        self._params.set_list('test', list=list_a[:3], value=[1])
        self._params['test'].list = list_a
        self._assert_list([1])

        self._params['test'].adjust(list_a)
        self._assert_list([1])

    def test_modify_list_shrink(self):
        """Modify list to have only some of the elements that it had."""
        self._params.set_list('test', list=list_a, value=[1])
        self._params['test'].list = list_a[:3]
        self._assert_list([1], plist=list_a[:3])

        self._params['test'].adjust(list_a[:3])
        self._assert_list([1], plist=list_a[:3])

    def test_modify_list_shrink_nonexistant(self):
        """Modify list to remove the selected element."""
        self._params.set_list('test', list=list_a, value_names=['A', 'D'])
        self._params['test'].list = list_a[:3]
        self._assert_list(names=['A', 'D'], plist=list_a[:3])

        self._params['test'].adjust(list_a[:3])
        self._assert_list(names=['A', 'D'], plist=list_a[:3])

    def test_reorder_list_should_update_value(self):
        """Reorder list and see if value is updated correctly."""
        self._params.set_list('test', list=list_a, value_names=['A'])
        list_rev = list(reversed(list_a))
        self._assert_list(names=['A'])
        self._params['test'].list = list_rev
        self._assert_list(names=['A'], plist=list_rev)

        self._params['test'].adjust(list_a)
        self._assert_list(names=['A'])

    def test_modify_list_inplace(self):
        """Attempt to modify list inplace."""
        self._params.set_list('test', list=list_a, value=[1, 2])
        self._params['test'].list.append('X')
        # Check that the operation didn't actually mutate the parameter:
        self._assert_list([1, 2])

    def test_multiselect_modes(self):
        """Test all multiselect modes with existing value_names."""
        self._params.set_list('test', list=list_a, value_names=['A'])

        # selected:
        self._params['test']._multiselect_mode = (
            self._params['test']._mode_selected)
        self.assertEqual(
            self._params['test'].selected_names(list_a), ['A'])
        # selected_exists:
        self._params['test']._multiselect_mode = (
            self._params['test']._mode_selected_exists)
        self.assertEqual(
            self._params['test'].selected_names(list_a), ['A'])
        # unselected:
        self._params['test']._multiselect_mode = (
            self._params['test']._mode_unselected)
        self.assertEqual(
            self._params['test'].selected_names(list_a), list_a[1:])
        # passthrough:
        self._params['test']._multiselect_mode = (
            self._params['test']._mode_passthrough)
        self.assertEqual(
            self._params['test'].selected_names(list_a), list_a)

    def test_multiselect_modes_nonextistant(self):
        """Test all multiselect modes with non-existant value_names."""
        self._params.set_list('test', list=list_a, value_names=['A', 'X'])

        # selected:
        self._params['test']._multiselect_mode = (
            self._params['test']._mode_selected)
        with self.assertRaises(exceptions.SyDataError):
            self._params['test'].selected_names(list_a)
        # selected_exists:
        self._params['test']._multiselect_mode = (
            self._params['test']._mode_selected_exists)
        self.assertEqual(
            self._params['test'].selected_names(list_a), ['A'])
        # unselected:
        self._params['test']._multiselect_mode = (
            self._params['test']._mode_unselected)
        self.assertEqual(
            self._params['test'].selected_names(list_a), list_a[1:])
        # passthrough:
        self._params['test']._multiselect_mode = (
            self._params['test']._mode_passthrough)
        self.assertEqual(
            self._params['test'].selected_names(list_a), list_a)

    def test_noupdate_string_value(self):
        """Create list with a value argument of string type."""
        self._params._set_list_no_update('test', value=['A'])
        self._assert_no_update_list(
            value=['A'], names=[], plist=[], test_selected=False)

    def test_noupdate_non_existant_value_names(self):
        """Create list with a value_names arguments which isn't in the list."""
        self._params._set_list_no_update(
            'test', list=list_a, value_names=['X'])
        self._assert_no_update_list(names=['X'], test_selected=False)
        assert self._params['test'].selected == 'X'

    @unittest.skip('Expected failure')
    def test_noupdate_repeated_value_names(self):
        """Create list with a repeated value_names arguments."""
        self._params._set_list_no_update(
            'test', list=list_a, value_names=['A', 'A'])
        self._assert_no_update_list(names=['A'])

    def test_noupdate_conflicting_value_value_names(self):
        """Create list with conflicting value and value_names arguments."""
        self._params._set_list_no_update(
            'test', list=list_a, value=[0], value_names=['B'])
        self._assert_no_update_list(value=[0], names=['B'],
                                    test_selected=False)
        assert self._params['test'].selected == 'A'

    def test_noconflict_after_set_value(self):
        self._params._set_list_no_update(
            'test', list=list_a, value=[0], value_names=['B'])
        self._params['test'].value = [0]
        self._assert_list(value=[0])

    def test_noconflict_after_set_value_names(self):
        self._params._set_list_no_update(
            'test', list=list_a, value=[0], value_names=['B'])
        self._params['test'].value_names = ['B']
        self._assert_list(names=['B'])

    def test_noconflict_after_set_selected(self):
        self._params._set_list_no_update(
            'test', list=list_a, value=[0], value_names=['B'])
        self._params['test'].selected = 'C'
        self._assert_list(names=['C'])
