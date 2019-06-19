# Copyright (c) 2018, Combine Control Systems AB
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

from sympathy.platform import gennode as synode


class TestParameterWidgets(unittest.TestCase):
    def setUp(self):
        self._params = synode.parameters()

    def test_int_lineedit_widget(self):
        self._params.set_integer(
            'test', value=0,
            editor=synode.editors.lineedit_editor())

        param = self._params['test']
        widget = param.gui()
        editor = widget.editor()

        editor.set_value(1)
        self.assertEqual(param.value, 1)

        # _value_spinbox is a widget_library.ValidatedIntSpinBox.
        # If this ever changes, this part of the test might become obosolete.
        spinbox = editor._value_spinbox
        self.assertEqual(spinbox.value(), 1)
        self.assertEqual(spinbox.text(), "1")

    def test_float_lineedit_widget(self):
        self._params.set_float(
            'test', value=0.0,
            editor=synode.editors.lineedit_editor())

        param = self._params['test']
        widget = param.gui()
        editor = widget.editor()

        editor.set_value(1.0)
        self.assertEqual(param.value, 1.0)

        # _value_spinbox is a widget_library.ValidatedFloatSpinBox.
        # If this ever changes, this part of the test might become obosolete.
        spinbox = editor._value_spinbox
        self.assertEqual(spinbox.value(), 1.0)
        self.assertEqual(spinbox.text(), "1.0")

    def test_text_lineedit_widget(self):
        self._params.set_string(
            'test', value='',
            editor=synode.editors.lineedit_editor())

        param = self._params['test']
        widget = param.gui()
        editor = widget.editor()

        editor.set_value('abc')
        self.assertEqual(param.value, 'abc')

        # _value_lineedit is a widget_library.ValidatedTextLineEdit.
        # If this ever changes, this part of the test might become obosolete.
        lineedit = editor._value_lineedit
        self.assertEqual(lineedit.value(), 'abc')
        self.assertEqual(lineedit.text(), 'abc')

    def test_int_combobox_widget(self):
        self._params.set_integer(
            'test', value=1,
            editor=synode.editors.combo_editor(options=[1, 2, 3]))

        param = self._params['test']
        widget = param.gui()
        editor = widget.editor()

        editor.set_value(2)
        self.assertEqual(param.value, 2)

        # combobox is a widget_library.NonEditableComboBox.
        # If this ever changes, this part of the test might become obosolete.
        combobox = editor.combobox()
        self.assertEqual(combobox.value(), '2')
        self.assertEqual(combobox.currentText(), '2')

    def test_float_combobox_widget(self):
        self._params.set_integer(
            'test', value=1.0,
            editor=synode.editors.combo_editor(options=[1.0, 2.0, 3.0]))

        param = self._params['test']
        widget = param.gui()
        editor = widget.editor()

        editor.set_value(2.0)
        self.assertEqual(param.value, 2.0)

        # combobox is a widget_library.NonEditableComboBox.
        # If this ever changes, this part of the test might become obosolete.
        combobox = editor.combobox()
        self.assertEqual(combobox.value(), '2.0')
        self.assertEqual(combobox.currentText(), '2.0')

    def test_text_combobox_widget(self):
        self._params.set_string(
            'test', value='a',
            editor=synode.editors.combo_editor(options=['a', 'b', 'c']))

        param = self._params['test']
        widget = param.gui()
        editor = widget.editor()

        editor.set_value('b')
        self.assertEqual(param.value, 'b')

        # combobox is a widget_library.NonEditableComboBox.
        # If this ever changes, this part of the test might become obosolete.
        combobox = editor.combobox()
        self.assertEqual(combobox.value(), 'b')
        self.assertEqual(combobox.currentText(), 'b')

    def test_int_editable_combobox_widget(self):
        self._params.set_integer(
            'test', value=1,
            editor=synode.editors.combo_editor(
                options=[1, 2, 3], edit=True))

        param = self._params['test']
        widget = param.gui()
        editor = widget.editor()

        editor.set_value(2)
        self.assertEqual(param.value, 2)

        # combobox is a widget_library.ValidatedIntComboBox.
        # If this ever changes, this part of the test might become obosolete.
        combobox = editor.combobox()
        self.assertEqual(combobox.value(), 2)
        self.assertEqual(combobox.currentText(), '2')

    def test_float_editable_combobox_widget(self):
        self._params.set_float(
            'test', value=1.0,
            editor=synode.editors.combo_editor(
                options=[1.0, 2.0, 3.0], edit=True))

        param = self._params['test']
        widget = param.gui()
        editor = widget.editor()

        editor.set_value(2.0)
        self.assertEqual(param.value, 2.0)

        # combobox is a widget_library.ValidatedFloatComboBox.
        # If this ever changes, this part of the test might become obosolete.
        combobox = editor.combobox()
        self.assertEqual(combobox.value(), 2.0)
        self.assertEqual(combobox.currentText(), '2.0')

    def test_text_editable_combobox_widget(self):
        self._params.set_string(
            'test', value='a',
            editor=synode.editors.combo_editor(
                options=['a', 'b', 'c'], edit=True))

        param = self._params['test']
        widget = param.gui()
        editor = widget.editor()

        editor.set_value('b')
        self.assertEqual(param.value, 'b')

        # combobox is a widget_library.ValidatedTextComboBox.
        # If this ever changes, this part of the test might become obosolete.
        combobox = editor.combobox()
        self.assertEqual(combobox.value(), 'b')
        self.assertEqual(combobox.currentText(), 'b')
