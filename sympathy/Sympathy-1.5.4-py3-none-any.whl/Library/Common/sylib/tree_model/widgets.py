# Copyright (c) 2016, Combine Control Systems AB
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

import re

import six

from sylib.icons import utils as icon_utils
from sympathy.api import qt
from sympathy.platform import widget_library as sywidgets

QtCore = qt.QtCore
QtGui = qt.QtGui


# all tree model editors should inherit this class to function with the
# tree_model.qt_model.ParameterTreeDelegate
class SyBaseEditMixin(object):
    def set_completer(self, completer):
        pass

    def completer(self):
        return None

    def set_value(self, value):
        pass

    def get_value(self):
        return None

    def set_drop_down_items(self, items):
        pass

    def set_options(self, options):
        pass

    def set_parent_view_widget(self, widget):
        pass


class SyBaseTextEdit(sywidgets.BaseLineTextEdit, SyBaseEditMixin):
    def __init__(self, *args, **kwargs):
        super(SyBaseTextEdit, self).__init__(*args, **kwargs)
        self.setTabChangesFocus(True)
        self.setWordWrapMode(QtGui.QTextOption.NoWrap)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setFixedHeight(self.sizeHint().height())
        self.setSizePolicy(QtGui.QSizePolicy.Expanding,
                           QtGui.QSizePolicy.Fixed)

        self._completer = None
        self.parent_view_widget = None
        self.keep_focus = False

    def keyPressEvent(self, event):
        # always ignore return and enter keys
        if event.key() in [QtCore.Qt.Key_Return, QtCore.Qt.Key_Enter]:
            if self._completer and self._completer.popup().isVisible():
                event.ignore()
                return
            else:
                if self.parent_view_widget is not None:
                    self.parent_view_widget.end_edit()
                return

        if (self._completer and self._completer.popup() and
                self._completer.popup().isVisible()):
            # The following keys are forwarded by the completer to the widget
            if event.key() in [QtCore.Qt.Key_Enter,
                               QtCore.Qt.Key_Return,
                               QtCore.Qt.Key_Escape,
                               QtCore.Qt.Key_Tab,
                               QtCore.Qt.Key_Backtab]:
                event.ignore()
                return

        # check the shortcut combination Ctrl+R
        is_shortcut = (event.modifiers() == QtCore.Qt.ControlModifier and
                       event.key() == QtCore.Qt.Key_R)

        if not self._completer or not is_shortcut:
            super(SyBaseTextEdit, self).keyPressEvent(event)

        no_text = event.text() == ''
        ctrl_or_shift = event.modifiers() in (QtCore.Qt.ControlModifier,
                                              QtCore.Qt.ShiftModifier)
        if ctrl_or_shift and no_text:
            # ctrl or shift key on it's own
            return

        if not is_shortcut:
            if (self._completer and self._completer.popup() and
                    self._completer.popup().isVisible()):
                self._completer.popup().hide()

        completion_prefix = self.text_under_cursor()

        # only start if at lest one letter is typed
        if self._completer is not None:
            if len(completion_prefix) > 0:
                self._completer.setCompletionPrefix(completion_prefix)
                popup = self._completer.popup()
                popup.setCurrentIndex(
                    self._completer.completionModel().index(0, 0))
                cr = self.cursorRect()
                cr.setWidth(popup.sizeHintForColumn(0) +
                            popup.verticalScrollBar().sizeHint().width())
                self._completer.complete(cr)  # popup it up!

    def focusInEvent(self, event):
        if self.completer():
            self.completer().setWidget(self)
        super(SyBaseTextEdit, self).focusInEvent(event)

    def insert_completion(self, completion):
        if self._completer.widget() is not self:
            return
        if (len(self.text_right_of_cursor()) and
                self.text_right_of_cursor()[0] != ' '):
            # Do not insert completion if there is anything but whitespace
            # after the cursor.
            return
        tc = self.textCursor()
        completion_prefix = self._completer.completionPrefix()
        tc.movePosition(QtGui.QTextCursor.Left,
                        QtGui.QTextCursor.KeepAnchor, len(completion_prefix))
        tc.removeSelectedText()
        tc.insertText(completion)

        self.setTextCursor(tc)

    def text_under_cursor(self):
        tc = self.textCursor()
        text = self.toPlainText()
        pos = tc.position()

        text_under_cursor = ''
        # TODO: white space in '' or () should not be considered
        rx = re.compile(r'''[\w\.\(\)'"]+''')
        # rx = re.compile(r'''\w*(\(['"])[\w\s]*(["']\))''')
        for m in rx.finditer(text):
            if m.start() <= pos <= m.end():
                text_under_cursor = m.group()[:pos - m.start()]
                break
        return text_under_cursor

    def text_right_of_cursor(self):
        tc = self.textCursor()
        text = self.toPlainText()
        pos = tc.position()
        return text[pos:]

    def set_completer(self, c):
        if self._completer:
            self._completer.disconnect(self)
        self._completer = c

        if not self._completer:
            return

        self._completer.setWidget(self)
        self._completer.setCompletionMode(QtGui.QCompleter.PopupCompletion)
        self._completer.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
        self._completer.insert_text.connect(self.insert_completion)

    def completer(self):
        return self._completer

    def set_value(self, value):
        self.setPlainText(six.text_type(value))

    def get_value(self):
        return self.toPlainText()

    def set_drop_down_items(self, items):
        # implement in subclasses if needed
        pass

    def set_options(self, options):
        # implement in subclasses if needed
        pass

    def set_parent_view_widget(self, widget):
        self.parent_view_widget = widget


class SyDropDownToolButtonEdit(SyBaseTextEdit):
    def __init__(self, *args, **kwargs):
        super(SyDropDownToolButtonEdit, self).__init__(*args, **kwargs)

        icon = icon_utils.create_icon(icon_utils.SvgIcon.plus)
        self.toolbutton = sywidgets.LineEditDropDownMenuButton(
            icon, parent=self)
        self.toolbutton.setToolTip('<p>Inserts the selected expression.</p>')
        self.toolbutton.setEnabled(False)
        self.add_widget(self.toolbutton)
        self.drop_down_menu = QtGui.QMenu(parent=self)
        self.drop_down_menu.setStyleSheet("QMenu {menu-scrollable: 1;}")
        self.toolbutton.setMenu(self.drop_down_menu)

    def insert_action_text(self, action):
        tc = self.textCursor()
        tc.insertText(action.text())
        self.setTextCursor(tc)

    def set_drop_down_items(self, items):
        self.toolbutton.setEnabled(len(items) > 0)
        for item in items:
            action = QtGui.QAction(item, self.drop_down_menu)
            self.drop_down_menu.addAction(action)
        self.drop_down_menu.triggered.connect(self.insert_action_text)


class SyDataEdit(SyDropDownToolButtonEdit):
    def __init__(self, *args, **kwargs):
        super(SyDataEdit, self).__init__(*args, **kwargs)
        self.toolbutton.setToolTip('<p>Inserts a python expression returning '
                                   'the selected column data at the current '
                                   'cursor position.</p>')

    def insert_action_text(self, action):
        tc = self.textCursor()
        tc.insertText("arg['{}']".format(action.text()))
        self.setTextCursor(tc)


class SyLabelEdit(SyDropDownToolButtonEdit):
    def __init__(self, *args, **kwargs):
        super(SyLabelEdit, self).__init__(*args, **kwargs)
        self.toolbutton.setToolTip('<p>Inserts a python expression returning '
                                   'the selected column name at the current '
                                   'cursor position.</p>')

    def insert_action_text(self, action):
        tc = self.textCursor()
        tc.insertText("arg['{}']".format(action.text()))
        self.setTextCursor(tc)


class _SyIterableTextEdit(SyBaseTextEdit):
    def focusOutEvent(self, event):
        if event.lostFocus() and not self.parent().underMouse():
            self.parent_view_widget.end_edit()
        super(_SyIterableTextEdit, self).focusOutEvent(event)


class _SyIterableDataEdit(SyDataEdit):
    def focusOutEvent(self, event):
        if event.lostFocus() and not self.parent().underMouse():
            self.parent_view_widget.end_edit()
        super(_SyIterableDataEdit, self).focusOutEvent(event)


class SyIterableEdit(QtGui.QWidget, SyBaseEditMixin):
    def __init__(self, *args, **kwargs):
        super(SyIterableEdit, self).__init__(*args, **kwargs)
        kwargs['parent'] = self
        self._varedit = _SyIterableTextEdit(*args, **kwargs)
        self._varedit.setSizePolicy(QtGui.QSizePolicy.Minimum,
                                    QtGui.QSizePolicy.Fixed)
        self._varedit.setMinimumWidth(20)
        self._varedit.setToolTip('Specify the iterables name.')
        self._textedit = _SyIterableDataEdit(*args, **kwargs)
        self._textedit.setToolTip('Define the iterable.')

        eq_label = QtGui.QLabel(' = ')
        # override background color to hide underlying display widget during
        # editing mode
        eq_label.setStyleSheet("""QLabel {background-color: white;}""")

        self.setContentsMargins(0, 0, 0, 0)
        layout = QtGui.QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self._varedit)
        layout.addWidget(eq_label)
        layout.addWidget(self._textedit)
        self.setLayout(layout)

        self._completer = None
        self.parent_view_widget = None

    def set_completer(self, c):
        self._textedit.set_completer(c)

    def set_drop_down_items(self, items):
        self._textedit.set_drop_down_items(items)

    def set_value(self, value):
        if '=' in value:
            name, exp = value.split('=', 1)
        else:
            name = 'e'
            exp = ''
        self._varedit.set_value(six.text_type(name.strip()))
        self._textedit.set_value(six.text_type(exp.strip()))

    def get_value(self):
        name = self._varedit.get_value()
        exp = self._textedit.get_value()
        return six.text_type('{} = {}'.format(name, exp))

    def set_parent_view_widget(self, widget):
        self.parent_view_widget = widget
        self._varedit.set_parent_view_widget(self.parent_view_widget)
        self._textedit.set_parent_view_widget(self.parent_view_widget)


class SyComboBox(QtGui.QComboBox, SyBaseEditMixin):
    def set_value(self, value):
        idx = self.findText(value)
        if idx != -1:
            self.setCurrentIndex(idx)
        else:
            self.setCurrentIndex(0)

    def get_value(self):
        return six.text_type(self.currentText())

    def set_options(self, options):
        self.clear()
        self.addItems(options)

class SyComboBoxEditable(SyComboBox):
    def __init__(self, *args, **kwargs):
        super(SyComboBoxEditable, self).__init__(*args, **kwargs)
        self.setEditable(True)

    def set_value(self, value):
        value = six.text_type(value)
        idx = self.findText(value)
        if idx != -1:
            self.setCurrentIndex(idx)
        else:
            self.addItem(value)
            idx = self.findText(value)
            self.setCurrentIndex(idx)

class SySpinBox(QtGui.QSpinBox, SyBaseEditMixin):
    def set_value(self, value):
        self.setValue(float(value))

    def get_value(self):
        return six.text_type(self.value())

    def set_options(self, options):
        if len(options) > 0 and options[0] is not None:
            self.setMinimum(int(options[0]))
        if len(options) > 1 and options[1] is not None:
            self.setMaximum(int(options[1]))
        if len(options) > 2 and options[2] is not None:
            self.setSingleStep(int(options[2]))


class SyDoubleSpinBox(QtGui.QDoubleSpinBox, SyBaseEditMixin):
    def set_value(self, value):
        self.setValue(float(value))

    def get_value(self):
        return six.text_type(self.value())

    def set_options(self, options):
        if len(options) > 0 and options[0] is not None:
            self.setMinimum(float(options[0]))
        if len(options) > 1 and options[1] is not None:
            self.setMaximum(float(options[1]))
        if len(options) > 2 and options[2] is not None:
            self.setSingleStep(float(options[2]))


class SyCheckBox(QtGui.QCheckBox, SyBaseEditMixin):
    def set_value(self, value):
        self.setChecked(bool(value))

    def get_value(self):
        return six.text_type(self.isChecked())
