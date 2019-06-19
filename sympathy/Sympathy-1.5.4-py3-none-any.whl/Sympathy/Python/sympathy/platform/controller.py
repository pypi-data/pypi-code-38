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
import collections

from sympathy.platform import qt_compat
from sympathy.utils.parameter_helper import ParameterRoot
from sympathy.utils.parameter_helper_visitors import WidgetBuildingVisitor

QtCore = qt_compat.QtCore
QtGui = qt_compat.import_module('QtGui')


class SignalFilter(QtCore.QObject):
    signal = qt_compat.Signal(bool)

    def __init__(self, raw_signal, target_value, editor_widget):
        super(SignalFilter, self).__init__(editor_widget)
        self._raw_signal = raw_signal
        self._target_value = target_value
        self._parameter = editor_widget._parameter_value
        self._raw_signal.connect(self.emit_)

    def emit_(self, *args):
        if self._parameter.value == self._target_value:
            self.signal.emit(True)
        else:
            self.signal.emit(False)

    def connect_(self, slot):
        self.signal.connect(slot)


class Field(object):
    def __init__(self, name, state, value=None):
        self._name = name
        self._state = state
        self._value = value

    def signal(self, widget_dict):
        signal_name_dict = {
            'checked': ('stateChanged', None, True),
            'value': ('valueChanged', None, self._value)}
        signal_name, signal_type, target_value = signal_name_dict[self._state]
        signal_no_type = getattr(widget_dict[self._name], signal_name)
        if signal_type is not None:
            raw_signal = signal_no_type[signal_type]
        else:
            raw_signal = signal_no_type
        return SignalFilter(
            raw_signal, target_value, widget_dict[self._name])

    def slot(self, widget_dict):
        slot_name_dict = {
            'enabled': 'set_enabled',
            'disabled': 'set_disabled',
            'visible': 'set_visible'
        }
        slot_name = slot_name_dict[self._state]
        slot = getattr(widget_dict[self._name], slot_name)
        return slot


class Controller(object):
    def __init__(self, when=None, action=None, function=None):
        # assert(when is not None and action is not None)
        self._when = when
        self._action = action
        self._function = function

    def connect(self, widget_dict):
        if self._when is not None and self._action is not None:
            self._connect_when_action(widget_dict)
        elif self._function is not None:
            self._connect_function(widget_dict)
        else:
            raise NotImplementedError('Not a valid controller choice.')

    def _connect_function(self, widget_dict):
        self._function(widget_dict)

    def _connect_when_action(self, widget_dict):
        signal = self._when.signal(widget_dict)
        if isinstance(self._action, collections.Iterable):
            for action in self._action:
                slot = action.slot(widget_dict)
                signal.connect_(slot)
        else:
            slot = self._action.slot(widget_dict)
            signal.connect_(slot)
        # Trigger checking value and emitting the result
        signal.emit_()
