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
"""Apply function(s) on Table(s)."""
from __future__ import (print_function, division, unicode_literals,
                        absolute_import)
import sys
import os.path
from collections import OrderedDict

from sympathy.api import fx_wrapper
from sympathy.utils.components import get_file_env, get_subclasses_env
from sympathy.types import types
from sympathy.platform import qt_compat
from sympathy.platform import os_support as oss
from sympathy.utils import filebase
from sylib.util import mock_wrap
from sympathy.api import exceptions


QtGui = qt_compat.import_module('QtGui')  # noqa
QtCore = qt_compat.QtCore  # noqa


def functions_filename(datasource):
    """Returns file datasource filename."""
    path = datasource.decode_path()
    if path:
        return os.path.abspath(path)


def _datatype(node_context):
    return node_context.definition['ports']['inputs'][1]['type']


def match_cls(cls, arg_type, multi):
    if multi:
        try:
            arg_type = arg_type[0]
        except Exception:
            return False

    return any([types.match(types.from_string(arg_type_, False), arg_type)
                for arg_type_ in cls.arg_types])


class PyfileWrapper(object):
    """Extract classes that extend a given base class (functions) from a
    python file. Used to extract function names for node_function_selector.
    """

    def __init__(self, fq_source_filename, arg_type, multi):
        arg_type = types.from_string(arg_type)
        if types.generics(arg_type):
            self._classes = {}
        elif fq_source_filename:
            sys_path = sys.path[:]
            if fq_source_filename.endswith('None'):
                raise IOError(fq_source_filename)
            sys.path.append(
                os.path.dirname(os.path.abspath(fq_source_filename)))

            self._classes = get_subclasses_env(
                get_file_env(fq_source_filename), fx_wrapper.FxWrapper)
            self._classes = OrderedDict(
                [(k, v) for k, v in self._classes.items()
                 if match_cls(v, arg_type, multi) and not (
                         multi and v.list_wrapper)])
            # Restore sys.path.
            sys.path[:] = sys_path
        else:
            self._classes = {}

    def get_class(self, class_name):
        """Retrieve a single class from the supplied python file.
        Raises NameError if the class doesn't exist.
        """
        try:
            return self._classes[class_name]
        except KeyError:
            raise NameError

    def function_names(self):
        """Extract the names of classes that extend the base class in the
        supplied python file.
        """
        # Only select classes that extend the base class
        return list(self._classes.keys())


@mock_wrap
class FxSelectorGui(QtGui.QWidget):
    def __init__(self, node_context, parent=None):
        super(FxSelectorGui, self).__init__(parent)
        self._node_context = node_context
        self._parameters = node_context.parameters
        self._init_gui()

    def _init_gui(self):
        self._copy_input = self._parameters['copy_input'].gui()
        self._functions = self._parameters['selected_functions'].gui()
        self._edit = QtGui.QPushButton('Edit source file')
        self._edit.setToolTip(
            'Brings up the source file in the system default editor')
        self._edit.setEnabled(self._node_context.input['port1'].is_valid())
        layout = QtGui.QVBoxLayout()
        layout.addWidget(self._copy_input)
        layout.addWidget(self._functions)
        layout.addWidget(self._edit)
        self.setLayout(layout)
        self._edit.clicked[bool].connect(self._edit_source)

    @qt_compat.Slot(bool)
    def _edit_source(self, checked):
        fq_functions_filename = functions_filename(
            self._node_context.input['port1'])
        oss.run_editor(fq_functions_filename)


class FxSelector(object):

    def __init__(self):
        self._multi = False

    def exec_parameter_view(self, node_context):
        return FxSelectorGui(node_context)

    def adjust_parameters(self, node_context):
        parameters = node_context.parameters
        function_names = self._available_function_names(node_context)
        parameters['selected_functions'].adjust(function_names)

    def execute(self, node_context, set_progress):
        in_datafile = node_context.input['port2']
        parameters = node_context.parameters
        copy_input = parameters['copy_input'].value
        out_datafile = node_context.output['port3']
        functions = self._selected_functions(node_context)
        calc_count = len(functions)
        if not functions:
            exceptions.sywarn('No calculations selected.')

        tmp_datafile = filebase.empty_from_type(
            in_datafile.container_type)

        if copy_input:
            tmp_datafile.source(in_datafile)

        for i, function in enumerate(functions):
            set_progress(100.0 * i / calc_count)
            _execute(function, in_datafile, tmp_datafile)

        out_datafile.source(tmp_datafile)

    def _available_function_names(self, node_context):
        datasource = node_context.input['port1']

        if datasource.is_valid():
            wrapper = self._get_wrapper(node_context)
            function_names = wrapper.function_names()
        else:
            function_names = []
        return function_names

    def _get_wrapper(self, node_context):
        datasource = node_context.input['port1']
        fq_functions_filename = functions_filename(datasource)
        wrapper = PyfileWrapper(
            fq_functions_filename,
            arg_type=_datatype(node_context), multi=self._multi)
        return wrapper

    def _selected_functions(self, node_context):
        parameters = node_context.parameters
        wrapper = self._get_wrapper(node_context)
        function_names = parameters['selected_functions'].selected_names(
            self._available_function_names(node_context))
        functions = [wrapper.get_class(f) for f in function_names]
        return functions


def _execute(function, in_data, out_data):
    instance = function(in_data, out_data)
    instance.execute()


class FxSelectorList(FxSelector):

    def __init__(self):
        super(FxSelectorList, self).__init__()
        self._multi = True

    def exec_parameter_view(self, node_context):
        return FxSelectorGui(node_context)

    def execute(self, node_context, set_progress):
        input_list = node_context.input['port2']
        parameters = node_context.parameters
        copy_input = parameters['copy_input'].value
        output_list = node_context.output['port3']
        functions = self._selected_functions(node_context)
        if not functions:
            exceptions.sywarn('No calculations selected.')

        n_inputs = len(input_list)
        n_functions = len(functions)

        for i, in_datafile in enumerate(input_list):
            try:
                input_factor = 100. / n_inputs
                set_progress(i * input_factor)

                out_datafile = input_list.create()
                if copy_input:
                    out_datafile.source(in_datafile)

                for j, function in enumerate(functions):
                    func_factor = input_factor / n_functions
                    _execute(function, in_datafile, out_datafile)
                    set_progress(i * input_factor + j * func_factor)

                output_list.append(out_datafile)
            except Exception:
                raise exceptions.SyListIndexError(i, sys.exc_info())
