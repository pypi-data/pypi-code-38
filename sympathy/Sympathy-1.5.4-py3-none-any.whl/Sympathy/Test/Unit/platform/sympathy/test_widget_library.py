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

import six

from sympathy.platform import widget_library as sywidgets


class TestValidatedWidgetBase(unittest.TestCase):
    def setUp(self):
        self._start_value = 0
        self._slot_values = []
        self._w.valueChanged.connect(self._slot)

    def _slot(self, value):
        self._slot_values.append(value)

    def _set_value(self, value):
        self._w.setValue(value)

    def _value(self):
        return self._w.value()

    def _set_text(self, text):
        self._w.setText(text)

    def _text(self):
        return self._w.text()

    def try_set_invalid_text(self, new_text):
        self._set_value(self._start_value)
        self._slot_values = []

        self._set_text(new_text)
        self.assertEqual(self._text(), new_text)
        self.assertEqual(self._value(), self._start_value)
        self.assertEqual(self._slot_values, [])

    def try_set_value(self, new_value, expected_value=None):
        if expected_value is None:
            expected_value = new_value
        expected_text = six.text_type(expected_value)

        self._set_value(self._start_value)
        self._slot_values = []

        self._set_value(new_value)
        self.assertEqual(self._text(), expected_text)
        self.assertEqual(self._value(), expected_value)
        self.assertEqual(self._slot_values, [expected_value])


class TestValidatedLineEditBase(TestValidatedWidgetBase):
    def _set_value(self, text):
        self._w.setText(six.text_type(text))


class TestValidatedIntLineEdit(TestValidatedLineEditBase):
    def setUp(self):
        self._w = sywidgets.ValidatedIntLineEdit()
        super(TestValidatedIntLineEdit, self).setUp()

    def test_valid(self):
        self.try_set_value(new_value=1)
        self.try_set_value(new_value=-1)

    def test_invalid(self):
        self.try_set_invalid_text(new_text="abc")


class TestValidatedFloatLineEdit(TestValidatedLineEditBase):
    def setUp(self):
        self._w = sywidgets.ValidatedFloatLineEdit()
        super(TestValidatedFloatLineEdit, self).setUp()

    def test_valid(self):
        self.try_set_value(new_value=1)
        self.try_set_value(new_value=-1)
        self.try_set_value(new_value=1.0)
        self.try_set_value(new_value=0.1)

    def test_invalid(self):
        self.try_set_invalid_text(new_text="abc")


class TestValidatedTextLineEdit(TestValidatedLineEditBase):
    def setUp(self):
        self._w = sywidgets.ValidatedTextLineEdit()
        super(TestValidatedTextLineEdit, self).setUp()
        self._start_value = ''

    def test_valid(self):
        self.try_set_value(new_value="abc")


class TestValidatedSpinBoxBase(TestValidatedWidgetBase):
    def _set_text(self, text):
        self._w.lineEdit().setText(text)


class TestValidatedIntSpinBox(TestValidatedSpinBoxBase):
    def setUp(self):
        self._w = sywidgets.ValidatedIntSpinBox()
        self._w.setMinimum(-10)
        self._w.setMaximum(10)
        super(TestValidatedIntSpinBox, self).setUp()

    def test_valid(self):
        self.try_set_value(new_value=1)
        self.try_set_value(new_value=-1)
        self.try_set_value(new_value=15, expected_value=10)
        self.try_set_value(new_value=-15, expected_value=-10)

    def test_invalid(self):
        self.try_set_invalid_text(new_text="abc")


class TestValidatedFloatSpinBox(TestValidatedSpinBoxBase):
    def setUp(self):
        self._w = sywidgets.ValidatedFloatSpinBox()
        self._w.setMinimum(-10)
        self._w.setMaximum(10)
        self._w.setDecimals(1)
        super(TestValidatedFloatSpinBox, self).setUp()

    def test_valid(self):
        self.try_set_value(new_value=1.0)
        self.try_set_value(new_value=-1.0)
        self.try_set_value(new_value=1.2)
        self.try_set_value(new_value=1, expected_value=1.0)
        self.try_set_value(new_value=-15, expected_value=-10.0)
        self.try_set_value(new_value=-15, expected_value=-10.0)
        self.try_set_value(new_value=1.999, expected_value=2.0)

    def test_invalid(self):
        self.try_set_invalid_text(new_text="abc")


class TestValidatedComboBoxBase(TestValidatedWidgetBase):
    def _text(self):
        return self._w.currentText()

    def _set_text(self, text):
        self._w.lineEdit().setText(text)


class TestValidatedIntComboBox(TestValidatedComboBoxBase):
    def setUp(self):
        self._w = sywidgets.ValidatedIntComboBox()
        super(TestValidatedIntComboBox, self).setUp()

    def test_valid(self):
        self.try_set_value(new_value=1)
        self.try_set_value(new_value=-1)

    def test_invalid(self):
        self.try_set_invalid_text(new_text="abc")


class TestValidatedFloatComboBox(TestValidatedComboBoxBase):
    def setUp(self):
        self._w = sywidgets.ValidatedFloatComboBox()
        super(TestValidatedFloatComboBox, self).setUp()

    def test_valid(self):
        self.try_set_value(new_value=1)
        self.try_set_value(new_value=-1)

    def test_invalid(self):
        self.try_set_invalid_text(new_text="abc")


class TestValidatedTextComboBox(TestValidatedComboBoxBase):
    def setUp(self):
        self._w = sywidgets.ValidatedTextComboBox()
        super(TestValidatedTextComboBox, self).setUp()
        self._start_value = ''

    def test_valid(self):
        self.try_set_value(new_value="abc")


class TestValidatedComboBoxNonEditableBase(TestValidatedWidgetBase):
    def setUp(self):
        self._w = sywidgets.NonEditableComboBox()
        self._all_items = ['', 'a', 'b', 'c']
        for label in self._all_items:
            self._w.addItem(label)
        super(TestValidatedComboBoxNonEditableBase, self).setUp()
        self._start_value = ''

    def _set_value(self, value):
        index = self._all_items.index(str(value))
        self._w.setCurrentIndex(index)

    def _text(self):
        return self._w.currentText()

    def _set_text(self, text):
        assert False, "Can't set text on non-editable combobox."

    def test_valid(self):
        self.try_set_value(new_value='a')
