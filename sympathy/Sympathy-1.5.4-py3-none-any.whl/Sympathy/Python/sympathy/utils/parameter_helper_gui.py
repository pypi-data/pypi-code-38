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
from __future__ import (print_function, division, unicode_literals,
                        absolute_import)

import os.path
import six
import platform
from sympathy.platform import qt_compat
from sympathy.platform import widget_library as sywidgets
from sympathy.platform import settings
from sympathy.utils.mock import mock_wrap
from sympathy.utils import prim
from sympathy.utils import search

QtCore = qt_compat.QtCore
QtGui = qt_compat.import_module('QtGui')


def get_default_path(old_path, flow_dir):
    if old_path and os.path.exists(old_path):
        return old_path
    elif flow_dir:
        return flow_dir
    return settings.get_default_dir()


class _ParameterContext(object):
    """Mock NodeContext used for validation of generated GUIs."""

    def __init__(self, params):
        self._params = params
        self._objects = {}
        self._own_objects = {}

    @property
    def definition(self):
        return {'ports': {'inputs': [], 'outputs': []}}

    @property
    def typealiases(self):
        return {}

    @property
    def parameters(self):
        return self._params

    @property
    def input(self):
        return []

    @property
    def output(self):
        return []

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass


@mock_wrap
class ParameterView(QtGui.QWidget):
    """
    Base class for generated and custom GUIs.
    Custom GUIs signal status changed that can trigger an update
    of status and messages. This can prevent accepting invalid
    configurations and enables interactive feedback in a standardized way.
    """

    status_changed = qt_compat.Signal()

    def __init__(self, params=None, validator=None, parent=None):
        self._params = params
        self._validator = validator
        super(ParameterView, self).__init__(parent)

    @property
    def status(self):
        """
        For custom GUIs that have custom parameter handling:
        override this property to include the current status message.

        Return status message string.
        """
        return ''

    @property
    def valid(self):
        """
        For custom GUIs that have custom parameter handling:
        override this property to reflect if the configuration is valid.

        Return True if the view is valid and False otherwise.
        """
        if self._validator:
            return self._validator(_ParameterContext(self._params))
        # Returning True for compatiblility with old custom_parameters.
        return True

    def save_parameters(self):
        """
        For custom GUIs that have custom parameter handling:
        override this method to update parameters just before the widget is
        accepted.
        """

    def cleanup(self):
        """
        For custom GUIs that need custom cleanup:
        override this method to perform cleanup just before the widget is
        closed.
        """


@mock_wrap
class ClampedButton(QtGui.QPushButton):
    def __init__(self, text, parent=None):
        super(ClampedButton, self).__init__(text, parent)

        font = self.font()
        fm = QtGui.QFontMetrics(font)
        rect = fm.boundingRect(text)
        self.setMaximumWidth(rect.width() + 32)

        # For OSX this is the minimum size allowed for a button with rounded
        # corners.
        if platform.system() == 'Darwin':
            self.setMinimumWidth(50)
            self.setMinimumHeight(30)


@mock_wrap
class ParameterWidget(QtGui.QWidget):
    def __init__(self, parameter_value, editor=None,
                 parent=None):
        super(ParameterWidget, self).__init__(parent)
        self._parameter_value = parameter_value
        self._editor = editor

        # If the editor is Expanding, then the containing widget should be too.
        if editor is not None:
            editor_policy = editor.sizePolicy()
            policy = self.sizePolicy()
            policy.setVerticalPolicy(editor_policy.verticalPolicy())
            self.setSizePolicy(policy)

    @qt_compat.Slot(int)
    def set_visible(self, value):
        self.setVisible(value)
        self._editor.setVisible(value)

    @qt_compat.Slot(int)
    def set_enabled(self, value):
        self.setEnabled(value)
        self._editor.setEnabled(value)

    @qt_compat.Slot(int)
    def set_disabled(self, value):
        self.setDisabled(value)
        self._editor.setDisabled(value)

    def editor(self):
        return self._editor

    def set_value(self, value):
        self._editor.set_value(value)


@mock_wrap
class ParameterValueWidget(ParameterWidget):
    def __init__(self, parameter_value, editor,
                 parent=None):
        if editor is None:
            editor = ParameterEditorTextLineWidget(parameter_value, {})
        super(ParameterValueWidget, self).__init__(
            parameter_value, editor, parent)
        self._value_label = None
        self.__init_gui()
        assert(self.editor() is not None)

    def label_widget(self):
        return self._value_label

    def __init_gui(self):
        hlayout = QtGui.QHBoxLayout()
        hlayout.setContentsMargins(0, 0, 0, 0)
        if self._parameter_value.label:
            self._value_label = QtGui.QLabel(self._parameter_value.label)
            hlayout.addWidget(self._value_label)
            hlayout.addItem(QtGui.QSpacerItem(10, 1))
        if self._parameter_value.description:
            self.setToolTip(self._parameter_value.description)
        hlayout.addWidget(self._editor)
        self.setLayout(hlayout)

        self.__init_gui_from_parameters()
        self._editor.valueChanged[six.text_type].connect(self._text_changed)

    def __init_gui_from_parameters(self):
        self._editor.set_value(self._parameter_value.value)

    def _text_changed(self, text):
        raise NotImplementedError(
            "Override when extending!")

    @qt_compat.Slot(int)
    def set_visible(self, value):
        super(ParameterValueWidget, self).set_visible(value)
        self.label_widget().setVisible(value)

    @qt_compat.Slot(int)
    def set_enabled(self, value):
        super(ParameterValueWidget, self).set_enabled(value)
        self.label_widget().setEnabled(value)

    @qt_compat.Slot(int)
    def set_disabled(self, value):
        super(ParameterValueWidget, self).set_disabled(value)
        self.label_widget().setDisabled(value)


class ParameterNumericValueWidget(ParameterWidget):
    def __init__(self, parameter_value, editor=None,
                 parent=None):
        if editor is None:
            editor = ParameterEditorTextLineWidget(parameter_value, {})
        super(ParameterNumericValueWidget, self).__init__(
            parameter_value, editor, parent)
        self._value_label = None
        self._layout = None
        self.__init_gui()
        assert(self._layout is not None)

    def label_widget(self):
        return self._value_label

    def __init_gui(self):
        vlayout = QtGui.QVBoxLayout()
        vlayout.setContentsMargins(0, 0, 0, 0)
        self._layout = QtGui.QHBoxLayout()
        self._layout.setContentsMargins(0, 0, 0, 0)
        if self._parameter_value.label:
            self._value_label = QtGui.QLabel(self._parameter_value.label)
            self._layout.addWidget(self._value_label)
            self._layout.addItem(QtGui.QSpacerItem(10, 1))
        if self._parameter_value.description:
            self.setToolTip(self._parameter_value.description)

        self._layout.addWidget(self._editor)

        vlayout.addItem(self._layout)
        self.setLayout(vlayout)

        self.__init_gui_from_parameters()

    def __init_gui_from_parameters(self):
        self._editor.set_value(self._parameter_value.value)


class ParameterStringWidget(ParameterValueWidget):
    valueChanged = qt_compat.Signal(six.text_type)

    def __init__(self, parameter_value, editor=None, parent=None):
        super(ParameterStringWidget, self).__init__(
            parameter_value, editor, parent)

    def _text_changed(self, text):
        self._parameter_value.value = six.text_type(text)
        self.valueChanged.emit(six.text_type(text))


class ParameterBooleanWidget(ParameterWidget):
    stateChanged = qt_compat.Signal(int)
    valueChanged = qt_compat.Signal(bool)

    def __init__(self, parameter_value, parent=None):
        super(ParameterBooleanWidget, self).__init__(
            parameter_value, None, parent)
        self.__init_gui()
        assert(self._editor is not None)

    def __init_gui(self):
        vlayout = QtGui.QVBoxLayout()
        vlayout.setContentsMargins(0, 0, 0, 0)
        self._editor = QtGui.QCheckBox()
        if self._parameter_value.label:
            self._editor.setText(self._parameter_value.label)
        if self._parameter_value.description:
            self._editor.setToolTip(
                self._parameter_value.description)
        vlayout.addWidget(self._editor)
        self.setLayout(vlayout)

        self.__init_gui_from_parameters()

        self._editor.stateChanged[int].connect(self._state_changed)

    def __init_gui_from_parameters(self):
        try:
            self._editor.setChecked(self._parameter_value.value)
        except Exception:
            self._editor.setChecked(QtCore.Qt.Unchecked)

    def _state_changed(self, state):
        self._parameter_value.value = state > 0
        self.stateChanged.emit(state)
        self.valueChanged.emit(state > 0)


@mock_wrap
class ParameterEditorWidget(QtGui.QWidget):
    valueChanged = qt_compat.Signal(six.text_type)

    def __init__(self, parameter_list, editor_dict, customization=None,
                 parent=None):
        super(ParameterEditorWidget, self).__init__(parent)
        self._customization = customization or {}
        self._parameter_list = parameter_list
        self._editor_dict = editor_dict
        self._init_customizations()

    def _init_customizations(self):
        for key in self._customization:
            try:
                self._customization[key] = self._editor_dict[key]
            except KeyError:
                pass

    @property
    def parameter_model(self):
        return self._parameter_list


@mock_wrap
class ParameterEditorTextLineWidget(ParameterEditorWidget):
    def __init__(self, parameter_value, editor_dict, parent=None):
        customization = {'placeholder': ''}

        super(ParameterEditorTextLineWidget, self).__init__(
            parameter_value, editor_dict, customization,
            parent=parent)
        self.__init_gui()

    def __init_gui(self):
        self._layout = QtGui.QHBoxLayout()
        self._layout.setContentsMargins(0, 0, 0, 0)

        if self._parameter_list.type == 'float':
            line_edit = sywidgets.ValidatedFloatLineEdit()
            line_edit.valueChanged[float].connect(
                self._value_changed)
        elif self._parameter_list.type == 'integer':
            line_edit = sywidgets.ValidatedIntLineEdit()
            line_edit.valueChanged[int].connect(
                self._value_changed)
        else:
            line_edit = sywidgets.ValidatedTextLineEdit()
            line_edit.valueChanged[six.text_type].connect(
                self._value_changed)

        self._value_lineedit = line_edit
        self._layout.addWidget(self._value_lineedit)
        self.setLayout(self._layout)

        self._init_gui_from_parameters()

    def _init_gui_from_parameters(self):
        self._value_lineedit.setPlaceholderText(
            self._customization['placeholder'])

    def set_value(self, value):
        self._value_lineedit.setText(six.text_type(value))

    def set_builder(self, builder):
        return self._value_lineedit.setBuilder(builder)

    def _value_changed(self, value):
        if self._parameter_list.type == 'float':
            try:
                self._parameter_list.value = float(value)
            except ValueError:
                self._parameter_list.value = 0.0
        elif self._parameter_list.type == 'integer':
            try:
                self._parameter_list.value = int(value)
            except ValueError:
                self._parameter_list.value = 0
        elif self._parameter_list.type == 'string':
            self._parameter_list.value = value
        else:
            raise Exception("Unknown parameter type")
        self.valueChanged.emit(self._parameter_list.value)


@mock_wrap
class ParameterEditorTextAreaWidget(ParameterEditorWidget):
    def __init__(self, parameter_value, editor_dict, parent=None):
        customization = {}

        super(ParameterEditorTextAreaWidget, self).__init__(
            parameter_value, editor_dict, customization,
            parent=parent)
        self.__init_gui()

    def __init_gui(self):
        self._layout = QtGui.QHBoxLayout()
        self._layout.setContentsMargins(0, 0, 0, 0)

        self._value_lineedit = QtGui.QTextEdit()
        self._layout.addWidget(self._value_lineedit)
        self.setLayout(self._layout)

        # This editor can make use of any extra space it gets.
        policy = self.sizePolicy()
        policy.setVerticalPolicy(QtGui.QSizePolicy.Expanding)
        self.setSizePolicy(policy)

        self._value_lineedit.textChanged.connect(self._value_changed)

    def set_value(self, value):
        self._value_lineedit.setText(six.text_type(value))

    def _value_changed(self):
        self._parameter_list.value = self._value_lineedit.toPlainText()
        self.valueChanged.emit(self._parameter_list.value)


@mock_wrap
class ParameterEditorCodeEditWidget(ParameterEditorWidget):
    def __init__(self, parameter_value, editor_dict, parent=None):
        customization = {'language': 'python'}

        super(ParameterEditorCodeEditWidget, self).__init__(
            parameter_value, editor_dict, customization,
            parent=parent)
        self.__init_gui()

    def __init_gui(self):
        self._layout = QtGui.QHBoxLayout()
        self._layout.setContentsMargins(0, 0, 0, 0)

        self._value_lineedit = sywidgets.CodeEdit(
            self._customization['language'])
        self._layout.addWidget(self._value_lineedit)
        self.setLayout(self._layout)

        # This editor can make use of any extra space it gets.
        policy = self.sizePolicy()
        policy.setVerticalPolicy(QtGui.QSizePolicy.Expanding)
        self.setSizePolicy(policy)

        self._value_lineedit.textChanged.connect(self._value_changed)

    def set_value(self, value):
        self._value_lineedit.setPlainText(six.text_type(value))

    def _value_changed(self):
        self._parameter_list.value = self._value_lineedit.toPlainText()
        self.valueChanged.emit(self._parameter_list.value)


@mock_wrap
class ParameterEditorSpinBoxWidget(ParameterEditorWidget):
    def __init__(self, parameter_value, editor_dict, customization,
                 value_spinbox, parent=None):
        self._value_spinbox = value_spinbox
        super(ParameterEditorSpinBoxWidget, self).__init__(
            parameter_value, editor_dict, customization, parent)
        self.__init_gui()

    def __init_gui(self):
        # The following must be true in order to execute.
        assert(hasattr(self, '_value_spinbox'))
        assert(self._value_spinbox is not None)

        vlayout = QtGui.QVBoxLayout()
        vlayout.setContentsMargins(0, 0, 0, 0)

        vlayout.addWidget(self._value_spinbox)
        self.setLayout(vlayout)

        self._init_gui_from_parameters()

    def set_value(self, value):
        """Give the spinbox a new value."""
        self._value_spinbox.setValue(value)

    def set_range(self, minimum, maximum):
        """Set the minimum and maximum values."""
        self._value_spinbox.setRange(minimum, maximum)

    def _init_gui_from_parameters(self):
        self._value_spinbox.setMaximum(self._customization['max'])
        self._value_spinbox.setMinimum(self._customization['min'])
        self._value_spinbox.setSingleStep(self._customization['step'])


class ParameterEditorIntegerWidget(ParameterEditorSpinBoxWidget):
    valueChanged = qt_compat.Signal(int)

    def __init__(self, parameter_value, editor_dict, spin_buttons=False,
                 parent=None):
        customization = {
            'max': 100,
            'min': 0,
            'step': 1} if spin_buttons else {
                'max': None,
                'min': None,
                'step': 1}
        value_spinbox = sywidgets.ValidatedIntSpinBox()
        if not spin_buttons:
            value_spinbox.setButtonSymbols(QtGui.QAbstractSpinBox.NoButtons)

        super(ParameterEditorIntegerWidget, self).__init__(
            parameter_value, editor_dict, customization, value_spinbox, parent)
        self._value_spinbox.valueChanged[int].connect(
            self._value_changed)

    @qt_compat.Slot(int)
    def _value_changed(self, value):
        self._parameter_list.value = value
        self.valueChanged.emit(value)


class ParameterEditorFloatWidget(ParameterEditorSpinBoxWidget):
    valueChanged = qt_compat.Signal(float)

    def __init__(self, parameter_value, editor_dict, spin_buttons=False,
                 parent=None):
        customization = {
            'max': 100.0,
            'min': 0.0,
            'step': 1.0} if spin_buttons else {
                'max': None,
                'min': None,
                'step': 1.0}
        customization['decimals'] = 2
        value_spinbox = sywidgets.ValidatedFloatSpinBox()
        if not spin_buttons:
            value_spinbox.setButtonSymbols(QtGui.QAbstractSpinBox.NoButtons)

        super(ParameterEditorFloatWidget, self).__init__(
            parameter_value, editor_dict, customization, value_spinbox, parent)
        self._value_spinbox.valueChanged[float].connect(
            self._value_changed)
        self.__init_gui_from_parameters()

    def __init_gui_from_parameters(self):
        self._value_spinbox.setDecimals(self._customization['decimals'])
        super(ParameterEditorFloatWidget,
              self)._init_gui_from_parameters()

    @qt_compat.Slot(float)
    def _value_changed(self, value):
        self._parameter_list.value = value
        self.valueChanged.emit(value)


class FileSystemModel(QtGui.QFileSystemModel):

    def __init__(self, parent):
        super(FileSystemModel, self).__init__(parent)


class ParameterPath(object):
    def __init__(self, parameter_string):
        self._parameter = parameter_string

        # All paths should be stored in unipath_separators format. If it isn't,
        # we update it:
        self._parameter.value = prim.unipath_separators(self._parameter.value)

    @property
    def value(self):
        return prim.nativepath_separators(self._parameter.value)

    @value.setter
    def value(self, value):
        self._parameter.value = prim.unipath_separators(value)


@mock_wrap
class ParameterEditorFileDialogWidget(ParameterEditorTextLineWidget):
    dialogChanged = qt_compat.Signal(six.text_type)
    state_changed = qt_compat.Signal(bool)
    text_changed = qt_compat.Signal()

    _abs = ('abs', 'Absolute path')
    _rel = ('rel', 'Relative to top flow')
    _flo = ('flow', 'Relative to subflow')

    _flow_dir = '$(SY_FLOW_DIR)'

    def __init__(self, parameter_string, editor_dict, parent=None):
        customization = {
            'placeholder': '',
            'states': None,
        }
        # specifically don't call the direct super class to be able to
        # override the __init_gui() call
        self._parameter_path = ParameterPath(parameter_string)
        ParameterEditorWidget.__init__(self, self._parameter_path, editor_dict,
                                       customization, parent)

        self._flow_dir_value = prim.unipath(os.path.dirname(
            parameter_string._state_settings['node/flow_filename']))
        self.__init_gui()

    def filename(self):
        return self._abs_path(self._get_text())

    def __init_gui(self):
        self._layout = QtGui.QHBoxLayout()
        self._layout.setContentsMargins(0, 0, 0, 0)

        value = self._parameter_path.value

        # Customization
        self._rel_dir_value = six.moves.getcwd()
        self._states = []
        if self._customization['states'] is None:
            self._states = [self._abs, self._rel, self._flo]
        else:
            has_rel_state = False
            for state in self._customization['states']:
                if state == 'abs':
                    self._states.append(self._abs)
                elif state == 'rel':
                    if has_rel_state:
                        raise ValueError("Only one relative state is allowed.")
                    has_rel_state = True
                    self._states.append(self._rel)
                elif state == 'flow':
                    self._states.append(self._flo)
                else:
                    if has_rel_state:
                        raise ValueError("Only one relative state is allowed.")
                    if not os.path.isabs(state[2]):
                        raise ValueError(
                            "Need an absolute path as root for "
                            "relative state '{}'.".format(state[0]))
                    has_rel_state = True
                    self._states.append(state[:2])
                    self._rel = state[:2]
                    self._rel_dir_value = state[2]

        # Initial state and value
        text = value
        if value.startswith(self._flow_dir):
            self._state = self._flo
            text = value[len(self._flow_dir) + 1:]
        elif os.path.isabs(value):
            self._state = self._abs
        else:
            self._state = self._rel
        # At this point self._state can possibly be a state not included in
        # states. We fix this as soon as the lineedit widget and completer have
        # been set up.

        self._value_lineedit = sywidgets.MenuLineEdit(
            options=self._states, value=self._state, parent=self)
        self._text = text
        self._value_lineedit.setText(text)

        self._layout.addWidget(self._value_lineedit)
        self.setLayout(self._layout)

        self._value_lineedit.prefix_button.setToolTip(
            'Toggle between relative and absolute path.')

        self._dialog_button = ClampedButton('\u2026')
        self._layout.addWidget(self._dialog_button)

        completer = QtGui.QCompleter(self)
        self._completer_model = FileSystemModel(completer)
        completer.setModel(self._completer_model)
        self._value_lineedit.setCompleter(completer)
        self._completer_model.setRootPath(
            os.path.abspath(self._abs_path(self._get_text())))

        # Now we can fix the possible problem of self._state not being one of
        # the available states.
        if self._state not in self._states:
            if self._abs in self._states:
                # Defaulting to absolute path feels natural if it is available
                self._state_edited(self._abs)
            else:
                # otherwise default to whatever is available
                self._state_edited(self._states[0])

        self._dialog_button.clicked.connect(self._dialog_click)
        self.dialogChanged.connect(self._filename_changed_from_dialog)

        self._value_lineedit.state_edited.connect(self._state_edited)
        self._value_lineedit.textEdited.connect(self._text_edited)
        completer.activated.connect(self._text_edited)

    def _abs_path(self, text):
        if self._state == self._flo:
            return os.path.normpath(os.path.join(self._flow_dir_value, text))
        elif self._state == self._rel:
            return os.path.normpath(os.path.join(self._rel_dir_value, text))
        return text

    def _rel_cwd_path(self, text):
        abs_path = self._abs_path(text)
        try:
            return os.path.relpath(abs_path, self._rel_dir_value), self._rel
        except Exception:
            return abs_path, self._abs

    def _rel_flow_path(self, text):
        abs_path = self._abs_path(text)
        try:
            return os.path.relpath(abs_path, self._flow_dir_value), self._flo
        except Exception:
            return abs_path, self._abs

    def _get_text(self):
        """Return the current text from the gui."""
        return self._value_lineedit.text()

    def _get_state(self):
        """Return the current state from the gui."""
        return self._value_lineedit.current_value

    def _set_text(self, value):
        """Set the text in the gui."""
        self._value_lineedit.setText(value)

    def _set_state(self, value):
        """Set the state in the gui."""
        self._value_lineedit.current_value = value

    def set_value(self, value):
        value = prim.nativepath_separators(value)
        if value.startswith(self._flow_dir):
            text = value[len(self._flow_dir) + 1:]
        else:
            text = value
        self._set_text(text)

    def _can_change_state(self, state):
        """
        Return True if it is possible to modify the current path to state.
        This will return False on Windows when going to rel or flow states if
        the path is on a different drive than the flow.
        """
        abs_path = self._abs_path(self._get_text())

        if state == self._rel:
            try:
                os.path.relpath(abs_path, self._rel_dir_value)
                return True
            except Exception:
                return False

        elif state == self._flo:
            try:
                os.path.relpath(abs_path, self._flow_dir_value)
                return True
            except Exception:
                return False

        return True

    def _change(self, state, text):
        """
        Set state and text in local model, parameter model and (if needed) in
        the gui. Also update the completer model to the current directory.
        """
        if self._get_state() != state:
            self._set_state(state)
        if self._get_text() != text:
            self._set_text(text)

        self._state = state
        self._text = text

        if state == self._flo:
            self._parameter_path.value = os.path.join(self._flow_dir, text)
        else:
            self._parameter_path.value = text

        self._completer_model.setRootPath(
            os.path.abspath(self._abs_path(self._get_text())))

    def _text_edited(self, text):
        """
        Triggered when the path is edited by hand, not when programmatically
        changed.
        """
        if self._text == text:
            return

        if os.path.isabs(text):
            self._change(self._abs, text)
        elif self._state == self._abs:
            self._change(self._rel, text)
        else:
            self._change(self._state, text)
        self.text_changed.emit()

    def _state_edited(self, state):
        """
        Triggered when the state is edited by hand, not when programmatically
        changed.
        """
        if state == self._state:
            return

        text = self._abs_path(self._get_text())

        # TODO(erik): Ideally we should re-implement handling for relative
        # paths so that it does not force the path to be normalized.

        if self._can_change_state(state):
            if state == self._abs:
                text = os.path.abspath(self._abs_path(text))
            elif state == self._rel:
                text, state = self._rel_cwd_path(text)
            elif state == self._flo:
                text, state = self._rel_flow_path(text)
        else:
            state = self._state

        self._change(state, text)

    def _dialog_click(self):
        default_path = get_default_path(
            self._abs_path(self._get_text()),
            self._flow_dir_value)

        if not qt_compat.USES_PYSIDE:
            fq_filename = QtGui.QFileDialog.getOpenFileName(
                self, "Select file", default_path,
                ";;".join(self._editor_dict['filter']))
        else:
            fq_filename, _ = QtGui.QFileDialog.getOpenFileName(
                self, "Select file", default_path,
                ";;".join(self._editor_dict['filter']))

        if fq_filename:
            self.dialogChanged.emit(fq_filename)

    def _filename_changed_from_dialog(self, text):
        state = self._state
        if state == self._abs:
            text = self._abs_path(text)
        elif state == self._rel:
            text, state = self._rel_cwd_path(text)
            if state not in self._states:
                # TODO: Should probably try changing to any other state that
                # works (not only try abs) and if no ok state is found, give
                # the user a warning. This is only ever a problem if 'abs'
                # state has been disabled.
                return
        elif state == self._flo:
            text, state = self._rel_flow_path(text)
            if state not in self._states:
                # TODO: Should probably try changing to any other state that
                # works (not only try abs) and if no ok state is found, give
                # the user a warning. This is only ever a problem if 'abs'
                # state has been disabled.
                return
        self._change(state, text)


class ParameterEditorFileSaveDialogWidget(ParameterEditorFileDialogWidget):

    def __init__(self, parameter_string, editor_dict, parent=None):
        super(ParameterEditorFileSaveDialogWidget, self).__init__(
            parameter_string, editor_dict, parent)

    def _dialog_click(self):

        default_path = get_default_path(
            self._abs_path(self._get_text()),
            self._flow_dir_value)

        if not qt_compat.USES_PYSIDE:
            fq_filename = QtGui.QFileDialog.getSaveFileName(
                self, "Select file", default_path,
                ";;".join(self._editor_dict['filter']))
        else:
            fq_filename, _ = QtGui.QFileDialog.getSaveFileName(
                self, "Select file", default_path,
                ";;".join(self._editor_dict['filter']))
        if fq_filename:
            self.dialogChanged.emit(fq_filename)


class ParameterEditorDirectoryDialogWidget(ParameterEditorFileDialogWidget):
    def __init__(self, parameter_string, editor_dict, parent=None):
        super(ParameterEditorDirectoryDialogWidget, self).__init__(
            parameter_string, editor_dict, parent)

    def _dialog_click(self):
        default_path = get_default_path(
            self._abs_path(self._get_text()), self._flow_dir_value)

        selected_dir = QtGui.QFileDialog.getExistingDirectory(
            self, "Select directory", default_path)

        if selected_dir:
            self.dialogChanged.emit(selected_dir)


class ParameterScalarEditorComboboxWidget(ParameterEditorWidget):
    currentIndexChanged = qt_compat.Signal(int)

    def __init__(self, parameter_list, editor_dict, parent=None):
        super(ParameterScalarEditorComboboxWidget, self).__init__(
            parameter_list, editor_dict, parent=parent)
        self._keys = None
        vlayout = QtGui.QVBoxLayout()
        vlayout.setContentsMargins(0, 0, 0, 0)
        vlayout.setSpacing(0)

        hlayout = QtGui.QHBoxLayout()
        hlayout.setContentsMargins(0, 0, 0, 0)
        hlayout.setSpacing(0)

        if not self._editor_dict.get('edit', False):
            self._list_combobox = sywidgets.NonEditableComboBox()
        elif parameter_list.type == 'integer':
            self._list_combobox = sywidgets.ValidatedIntComboBox()
        elif parameter_list.type == 'float':
            self._list_combobox = sywidgets.ValidatedFloatComboBox()
        else:
            self._list_combobox = sywidgets.ValidatedTextComboBox()

        self._search_model = OrderedComboboxSearchFilterModel(
            self._list_combobox)
        self._list_combobox.setModel(self._search_model)
        self._filter_widget = sywidgets.ClearButtonLineEdit(
            placeholder='Filter')

        hlayout.addWidget(self._list_combobox)
        self._filter_button = sywidgets.ToggleFilterButton(
            filter_widget=self._filter_widget,
            next_to_widget=self._list_combobox)

        if self._editor_dict.get('filter', False):
            hlayout.addWidget(self._filter_button)

        vlayout.addLayout(hlayout)
        vlayout.addWidget(self._filter_widget)
        self.setLayout(vlayout)
        # GUI must be initialized from parameters before signals are
        # connected to ensure correct behavior.
        self.__init_gui_from_parameters()

        self._list_combobox.valueChanged.connect(self._value_changed)
        self._list_combobox.currentIndexChanged[int].connect(
            self.currentIndexChanged)
        self._search_model.setFilterRole(QtCore.Qt.DisplayRole)
        self._search_model.set_filter('')
        self._filter_widget.textChanged.connect(self._search_model.set_filter)

    def __init_gui_from_parameters(self):
        include_empty = self._editor_dict.get('include_empty', False)
        self._options = list(self._editor_dict['options'])
        display = self._editor_dict.get('display')
        if display is None:
            display = list(self._options)
        else:
            # Forwards compatibility if we ever want to add e.g. tooltips for
            # each option.
            display = [d.get('text', o) if isinstance(d, dict) else d
                       for d, o in zip(display, self._options)]

        if include_empty and '' not in self._options:
            display.insert(0, '')
            self._options.insert(0, '')

        self._display = [six.text_type(d) for d in display]
        self._list_combobox.addItems(self._display)

    def combobox(self):
        return self._list_combobox

    def set_value(self, value):
        text_value = six.text_type(value)
        if value in self._options:
            index = self._options.index(value)
        else:
            index = 0
            self._options.insert(index, value)
            self._display.insert(index, text_value)
            self._list_combobox.insertItem(index, text_value)
            self._list_combobox.setItemData(
                index, QtGui.QBrush(QtCore.Qt.gray), QtCore.Qt.ForegroundRole)
            self._list_combobox.setItemData(
                index, "This item is currently not available.",
                QtCore.Qt.ToolTipRole)

        self._list_combobox.setCurrentIndex(index)

    def _value_changed(self, value):
        text_value = six.text_type(value)
        if not self._editor_dict.get('edit', False):
            try:
                value = self._options[self._display.index(text_value)]
            except ValueError:
                pass
        self._parameter_list.value = value
        self.valueChanged.emit(self._parameter_list.value)


class SortedSearchFilterModel(QtGui.QSortFilterProxyModel):
    """
    Search filter model which sorts the data in ascending order.
    """
    def __init__(self, parent=None):
        self._filter = None
        super(SortedSearchFilterModel, self).__init__(parent)

    def set_filter(self, filter):
        if filter is not None:
            self._filter = search.fuzzy_pattern(filter)
            self.invalidateFilter()
            self.sort(0, QtCore.Qt.AscendingOrder)

    def filterAcceptsRow(self, source_row, source_parent):
        model = self.sourceModel()
        if self._filter is None or model is None:
            return True
        index = model.index(
            source_row, model.columnCount() - 1, source_parent)
        data = model.data(index, self.filterRole())
        if data is None:
            return True
        return search.matches(self._filter, data)


class OrderedSearchFilterModel(SortedSearchFilterModel):
    """
    Search Filter model which keeps the ordering from the source
    model.
    """
    def __init__(self, parent=None):
        super(OrderedSearchFilterModel, self).__init__(parent)

    def lessThan(self, left, right):
        return self.mapFromSource(left).row() < self.mapFromSource(right).row()


class OrderedComboboxSearchFilterModel(OrderedSearchFilterModel):
    """
    Search Filter model which keeps the ordering from the source
    model.

    For convenience also creates a new combobox model which is set as
    source model.
    """

    def __init__(self, parent=None):
        super(OrderedComboboxSearchFilterModel, self).__init__(parent)
        # Using existing model for standard combobox model behavior.
        self._dummy_combobox = QtGui.QComboBox()
        self.setSourceModel(self._dummy_combobox.model())


class ParameterListEditorComboboxWidget(ParameterEditorWidget):
    currentIndexChanged = qt_compat.Signal(int)
    valueChanged = qt_compat.Signal(six.text_type)

    def __init__(self, parameter_list, editor_dict, parent=None):
        super(ParameterListEditorComboboxWidget, self).__init__(
            parameter_list, editor_dict, parent=parent)
        self.__init_gui()

    def __init_gui(self):
        vlayout = QtGui.QVBoxLayout()
        vlayout.setContentsMargins(0, 0, 0, 0)
        vlayout.setSpacing(0)

        hlayout = QtGui.QHBoxLayout()
        hlayout.setContentsMargins(0, 0, 0, 0)
        hlayout.setSpacing(0)

        self._list_combobox = QtGui.QComboBox()
        self._search_model = OrderedComboboxSearchFilterModel(
            self._list_combobox)
        self._list_combobox.setEditable(self._editor_dict.get('edit', False))
        self._list_combobox.setModel(self._search_model)
        self._filter_widget = sywidgets.ClearButtonLineEdit(
            placeholder='Filter')

        hlayout.addWidget(self._list_combobox)
        self._filter_button = sywidgets.ToggleFilterButton(
            filter_widget=self._filter_widget,
            next_to_widget=self._list_combobox)

        if self._editor_dict.get('filter', False):
            hlayout.addWidget(self._filter_button)

        vlayout.addLayout(hlayout)
        vlayout.addWidget(self._filter_widget)
        self.setLayout(vlayout)
        # GUI must be initialized from parameters before signals are
        # connected to ensure correct behavior.
        self.__init_gui_from_parameters()

        self._list_combobox.currentIndexChanged[int].connect(
            self._index_changed)
        line_edit = self._list_combobox.lineEdit()
        if line_edit is not None:
            line_edit.textEdited.connect(self._value_changed)

        self._search_model.setFilterRole(QtCore.Qt.DisplayRole)
        self._search_model.set_filter('')
        self._filter_widget.textChanged.connect(self._search_model.set_filter)

    def __init_gui_from_parameters(self):
        # Treat None in parameter.list as equivalent to empty string, i.e. no
        # selection:
        self._available_items = [
            i if i is not None else '' for i in self._parameter_list.list]
        self._all_items = list(self._available_items)
        names = self._parameter_list.value_names
        if names:
            selected = names[0]
        else:
            # Sometimes the list parameter has no value_names, but still has an
            # index. This can be seen as a bug in the list parameter, but we
            # must still deal with it here.
            indexes = self._parameter_list.value
            try:
                selected = self._available_items[indexes[0]]
            except IndexError:
                selected = ''

        if selected not in self._all_items:
            self._all_items.insert(0, selected or '')
        include_empty = self._editor_dict.get('include_empty', False)
        if include_empty and '' not in self._all_items:
            self._all_items.insert(0, '')

        for i, label in enumerate(self._all_items):
            self._list_combobox.addItem(label)
            if label not in self._available_items:
                self._list_combobox.setItemData(
                    i, QtGui.QBrush(QtCore.Qt.gray), QtCore.Qt.ForegroundRole)
                self._list_combobox.setItemData(
                    i, "This item is currently not available.",
                    QtCore.Qt.ToolTipRole)

        index = self._all_items.index(selected)
        self._list_combobox.setCurrentIndex(index)

    def _index_changed(self, index):
        selected = self._list_combobox.itemText(index)
        self._value_changed(selected)
        self.currentIndexChanged.emit(index)

    def _value_changed(self, value):
        text_value = six.text_type(value)

        if text_value == '' or text_value is None:
            self._parameter_list.list = self._available_items
            self._parameter_list.value_names = []
        else:
            if text_value not in self._available_items:
                self._parameter_list.list = self._available_items
            self._parameter_list.value_names = [text_value]

        self.valueChanged.emit(self._parameter_list.selected)

    def setCurrentIndex(self, index):
        self._list_combobox.setCurrentIndex(index)

    def combobox(self):
        return self._list_combobox

    def clear(self):
        self._list_combobox.clear()
        self._parameter_list.value_names = []
        self._parameter_list.list = []

    def addItems(self, items):
        self._parameter_list.list = self._parameter_list.list + items
        self._list_combobox.addItems(items)


class ParameterEditorListWidget(ParameterEditorWidget):
    itemChanged = qt_compat.Signal(QtGui.QListWidgetItem)
    _all_buttons = ['All', 'Clear', 'Invert']
    _all_button, _clear_button, _invert_button = _all_buttons
    _all_item_buttons = ['Delete', 'Insert']
    _delete_button, _insert_button = _all_item_buttons
    _standard_item_foreground = QtGui.QStandardItem().foreground()

    def __init__(self, parameter_list, editor_dict, parent=None):
        customization = {
            'selection': '',
            'alternatingrowcolors': True,
            'filter': False,
            'buttons': False,
            'invertbutton': False,
            'mode': False,
            'edit': False}

        passthrough = editor_dict.get('passthrough', False)
        if passthrough:
            editor_dict['mode'] = True

        super(ParameterEditorListWidget, self).__init__(
            parameter_list, editor_dict, customization, parent)
        self.__init_gui()

    def __init_gui(self):
        # This editor can make use of any extra space it gets.
        policy = self.sizePolicy()
        policy.setVerticalPolicy(QtGui.QSizePolicy.Expanding)
        self.setSizePolicy(policy)

        vlayout = QtGui.QVBoxLayout()
        vlayout.setContentsMargins(0, 0, 0, 0)
        vlayout.setSpacing(0)

        hlayout = QtGui.QHBoxLayout()
        hlayout.setContentsMargins(0, 0, 0, 0)
        hlayout.setSpacing(0)

        # Ignored customizations.
        # self._customization['buttons']
        # self._customization['invertbutton']
        # TODO: issue a warning.
        use_filter = self._customization['filter']
        self._editable = self._customization['edit']
        self._use_mode = False
        self._use_multi = self._customization['selection'] == 'multi'

        mode_selected = (self._parameter_list._mode_selected,
                         'Use and require selected')
        mode_selected_exists = (self._parameter_list._mode_selected_exists,
                                'Use selected')
        mode_unselected = (self._parameter_list._mode_unselected,
                           'Use unselected')
        mode_passthrough = (self._parameter_list._mode_passthrough,
                            'Use all')
        current_modes = []

        if self._use_multi:
            self._use_mode = self._customization['mode']
            if self._use_mode:
                current_modes = [
                    mode_selected, mode_selected_exists, mode_unselected,
                    mode_passthrough]
            else:
                current_modes = [mode_selected]
            self._mode_widget = sywidgets.ModeComboBox(current_modes)
            if self._use_mode:
                hlayout.addWidget(self._mode_widget)
        else:
            self._mode_widget = sywidgets.ModeComboBox([])

        buttons = []
        if self._use_multi:
            buttons.append(self._all_buttons)
        if self._editable:
            buttons.append(self._all_item_buttons)

        # Widgets
        self._list_widget = sywidgets.SpaceHandlingContextMenuListWidget(
            buttons, self)

        self._filter_widget = sywidgets.ClearButtonLineEdit(
            placeholder='Filter')

        if use_filter:
            if self._use_mode:
                self._filter_button = sywidgets.ToggleFilterButton(
                    filter_widget=self._filter_widget,
                    next_to_widget=self._mode_widget)
                hlayout.addWidget(self._filter_button)
                vlayout.addLayout(hlayout)
            vlayout.addWidget(self._filter_widget)

        vlayout.addWidget(self._list_widget)
        self.setLayout(vlayout)

        # GUI must be initialized from parameters before signals are
        # connected to ensure correct behavior.
        self._init_editor()
        self._init_gui_from_parameters()

        self._list_widget.itemChanged.connect(self._item_changed)
        self._filter_widget.textChanged.connect(self._filter_changed)
        self._list_widget.actionTriggered.connect(self._action_triggered)
        self._mode_widget.itemChanged.connect(self._mode_changed)

    def _init_editor(self):
        if self._use_multi:
            self._list_widget.setSelectionMode(
                QtGui.QAbstractItemView.ExtendedSelection)

        self._list_widget.setAlternatingRowColors(
            bool(self._customization['alternatingrowcolors']))

    def _init_gui_from_parameters(self):
        # Sort the list and put the selected items first.
        selected_items = self._get_and_sort_selected_items()
        if not self._use_multi:
            if len(selected_items) > 0:
                selected_items = [selected_items[0]]
            else:
                selected_items = []

        self._list_widget.blockSignals(True)
        self._check_items(selected_items)
        self._list_widget.blockSignals(False)

    def _mark_item(self, item):
        item.setEditable(self._editable)
        all_items = self._parameter_list.list
        item_text = six.text_type(item.text())
        item.setFlags(item.flags() | QtCore.Qt.ItemIsUserCheckable)
        if item_text not in all_items:
            item.setForeground(QtCore.Qt.gray)
            item.setToolTip("This item is currently not available.")
        else:
            item.setForeground(self._standard_item_foreground)
            item.setToolTip(None)

    def _get_and_sort_selected_items(self):
        """Get and sort selected and non-selected items."""
        all_items = list(self._parameter_list.list)
        value_names = list(self._parameter_list.value_names)
        if (len(value_names) == 0 and
                len(self._parameter_list.value) > 0) and len(all_items) > 0:
            value_names = [self._parameter_list.list[v]
                           for v in self._parameter_list.value]
        selected_items = sorted(self._parameter_list.value_names,
                                key=prim.combined_key)
        not_selected_items = sorted(list(
            set(all_items).difference(set(selected_items))),
                                    key=prim.combined_key)

        self._list_widget.clear()

        for label in selected_items + not_selected_items:
            item = QtGui.QStandardItem(label)
            self._mark_item(item)
            self._list_widget.addItem(item)

        return selected_items

    def _check_items(self, selected_items):
        for row in range(self._list_widget.count()):
            item = self._list_widget.item(row)
            if six.text_type(item.text()) in selected_items:
                item.setCheckState(QtCore.Qt.Checked)
            else:
                item.setCheckState(QtCore.Qt.Unchecked)

        passthrough = False
        if self._use_multi:
            self._mode_widget.set_selected(
                self._parameter_list._multiselect_mode)
            passthrough = self._parameter_list._passthrough
        self._list_widget.setEnabled(not passthrough)
        self._filter_widget.setEnabled(not passthrough)

    def _item_changed(self, item):
        self._item_state_changed(item)
        self._mark_item(item)

    def _checked_items(self):
        return [item_ for item_ in self._list_widget.items()
                if item_.checkState() == QtCore.Qt.Checked]

    def _set_value_names_from_checked(self):
        self._parameter_list.value_names = [
            six.text_type(item_.text()) for item_ in self._checked_items()]

    def _item_state_changed(self, item):
        if not self._use_multi:
            if item.checkState() == QtCore.Qt.Checked:
                # Uncheck all other items
                for item_ in self._checked_items():
                    if item_ is not item:
                        self._list_widget.blockSignals(True)
                        item_.setCheckState(QtCore.Qt.Unchecked)
                        self._list_widget.blockSignals(False)
            elif not self._checked_items():
                # Unchecking items is not possible with single selection
                self._list_widget.blockSignals(True)
                item.setCheckState(QtCore.Qt.Checked)
                self._list_widget.blockSignals(False)

        self._set_value_names_from_checked()
        self.itemChanged.emit(item)

    def _filter_changed(self, text):
        if six.text_type(text):
            filter_ = search.fuzzy_pattern(text)
            display = [row for row in range(self._list_widget.count())
                       if search.matches(filter_,
                                         self._list_widget.item(row).text())]
        else:
            display = range(self._list_widget.count())

        for row in range(self._list_widget.count()):
            self._list_widget.setRowHidden(row, row not in display)

    def _action_triggered(self, action, item):
        text = action.text()
        if text in self._all_buttons:
            return self._selection_action_triggered(action)
        elif text in self._all_item_buttons:
            return self._item_action_triggered(action, item)
        else:
            assert False, 'Unknown action'

    def _item_action_triggered(self, action, item):
        text = action.text()

        if text == self._delete_button:
            for item_ in self._list_widget.selectedItems():
                if (self._use_multi or
                        item_.checkState() == QtCore.Qt.Unchecked):
                    self._list_widget.removeItem(item_)
            self._set_value_names_from_checked()

        elif text == self._insert_button:
            item = QtGui.QStandardItem('')
            item.setCheckState(QtCore.Qt.Unchecked)
            self._mark_item(item)
            self._list_widget.addItem(item)
        else:
            assert False, 'Unknown action'

    def _selection_action_triggered(self, action):
        text = action.text()
        if text == self._all_button:
            self._all_triggered()
        elif text == self._clear_button:
            self._clear_triggered()
        elif text == self._invert_button:
            self._invert_triggered()
        else:
            assert False, 'Unknown action'

    def _clear_triggered(self):
        for row in range(self._list_widget.count()):
            item = self._list_widget.item(row)
            if not self._list_widget.isRowHidden(row):
                item.setCheckState(QtCore.Qt.Unchecked)

    def _all_triggered(self):
        for row in range(self._list_widget.count()):
            item = self._list_widget.item(row)
            if not self._list_widget.isRowHidden(row):
                item.setCheckState(QtCore.Qt.Checked)

    def _invert_triggered(self):
        for row in range(self._list_widget.count()):
            item = self._list_widget.item(row)
            if not self._list_widget.isRowHidden(row):
                if item.checkState() == QtCore.Qt.Checked:
                    item.setCheckState(QtCore.Qt.Unchecked)
                else:
                    item.setCheckState(QtCore.Qt.Checked)

    def _mode_changed(self, mode):
        self._parameter_list._multiselect_mode = mode
        passthrough = self._parameter_list._passthrough
        self._list_widget.setEnabled(not passthrough)
        self._filter_widget.setEnabled(not passthrough)

    def clear(self):
        self._list_widget.blockSignals(True)
        self._list_widget.clear()
        self._parameter_list.list = []
        self._parameter_list.value_names = []
        self._list_widget.blockSignals(False)

    def addItems(self, items):
        self._list_widget.blockSignals(True)
        self._parameter_list.list = self._parameter_list.list + items
        selected_items = self._get_and_sort_selected_items()
        self._check_items(selected_items)
        self._list_widget.blockSignals(False)
        self._filter_changed(self._filter_widget.text())


def editor_factory(editor_type, editor_dict, parameter_model):
    if editor_type == "combobox":
        if parameter_model.type == 'list':
            return ParameterListEditorComboboxWidget(
                parameter_model, editor_dict)
        else:
            return ParameterScalarEditorComboboxWidget(
                parameter_model, editor_dict)
    elif editor_type == "listview" or editor_type == "basiclist":
        # basiclist is a legacy editor. It has been superseeded by listview
        return ParameterEditorListWidget(
            parameter_model, editor_dict)
    elif editor_type == "filename":
        return ParameterEditorFileDialogWidget(
            parameter_model, editor_dict)
    elif editor_type == "savename":
        return ParameterEditorFileSaveDialogWidget(
            parameter_model, editor_dict)
    elif editor_type == "dirname":
        return ParameterEditorDirectoryDialogWidget(
            parameter_model, editor_dict)
    elif editor_type == "spinbox":
        if parameter_model.type == 'integer':
            return ParameterEditorIntegerWidget(
                parameter_model, editor_dict, spin_buttons=True)
        elif parameter_model.type == 'float':
            return ParameterEditorFloatWidget(
                parameter_model, editor_dict, spin_buttons=True)
        else:
            return None
    elif editor_type == "lineedit":
        if parameter_model.type == 'integer':
            return ParameterEditorIntegerWidget(
                parameter_model, editor_dict)
        elif parameter_model.type == 'float':
            return ParameterEditorFloatWidget(
                parameter_model, editor_dict)
        else:
            return ParameterEditorTextLineWidget(
                parameter_model, editor_dict)
    elif editor_type == 'textedit':
        return ParameterEditorTextAreaWidget(
            parameter_model, editor_dict)
    elif editor_type == 'code':
        return ParameterEditorCodeEditWidget(
            parameter_model, editor_dict)
    else:
        return None


class ParameterListWidget(ParameterWidget):
    def __init__(self, parameter_list, editor=None, parent=None):
        self._parameter_list = parameter_list
        self._list_label = None
        if editor is None:
            editor = ParameterListEditorComboboxWidget(parameter_list, {})
        super(ParameterListWidget, self).__init__(
            parameter_list, editor, parent)
        self.__init_gui()

    def label_widget(self):
        return self._list_label

    def __init_gui(self):
        horizontal = isinstance(self._editor,
                                ParameterListEditorComboboxWidget)
        if horizontal:
            layout = QtGui.QHBoxLayout()
        else:
            layout = QtGui.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        if self._parameter_list.label:
            self._list_label = QtGui.QLabel(self._parameter_list.label)
            layout.addWidget(self._list_label)
            layout.addItem(QtGui.QSpacerItem(10, 1))
        if self._parameter_list.description:
            self.setToolTip(self._parameter_list.description)
        layout.addWidget(self._editor)
        self.setLayout(layout)


@mock_wrap
class ParameterGroupWidget(ParameterView):
    def __init__(self, parameter_group, parent=None, validator=None):
        super(ParameterGroupWidget, self).__init__(parameter_group, validator,
                                                   parent)
        self._parameter_group = parameter_group
        self._group_vlayout = None
        self._groupbox = None
        self._tab_widget = None
        self._init_gui()

    def _init_gui(self):
        vlayout = QtGui.QVBoxLayout()
        self._group_vlayout = QtGui.QVBoxLayout()
        self._groupbox = QtGui.QGroupBox(self._parameter_group.label)
        self._groupbox.setLayout(self._group_vlayout)
        vlayout.addWidget(self._groupbox)
        self.setLayout(vlayout)

    def group_layout(self):
        return self._group_vlayout

    def add_page(self, page_widget, name):
        if self._tab_widget is None:
            self._tab_widget = QtGui.QTabWidget()
            self._group_vlayout.addWidget(self._tab_widget)
        self._tab_widget.addTab(page_widget, name)

    def add_group(self, group_widget):
        self._group_vlayout.addWidget(group_widget)

    def add_widget(self, widget):
        self._group_vlayout.addWidget(widget)

    @qt_compat.Slot(int)
    def set_enabled(self, value):
        self._groupbox.setEnabled(value)

    @qt_compat.Slot(int)
    def set_disabled(self, value):
        self._groupbox.setDisabled(value)

    def needs_stretch(self):
        """
        Returns True if this group contains no vertically expanding widgets.
        """
        layout = self.group_layout()
        for i in range(layout.count()):
            widget = layout.itemAt(i).widget()
            policy = widget.sizePolicy().verticalPolicy()
            if policy == QtGui.QSizePolicy.Expanding:
                return False
        return True
