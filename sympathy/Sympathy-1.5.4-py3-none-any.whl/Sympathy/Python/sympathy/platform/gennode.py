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
import six
import sys
from . import basicnode as synode
from .. utils.parameter_helper import Editors
from .. utils.prim import combined_key
from . controller import Controller, Field
from .. platform import exceptions


managed_context = synode.managed_context
parameters = synode.sy_parameters
ParameterRoot = synode.ParameterRoot


class BasicNode(synode.BasicNode):
    def __init__(self):
        super(BasicNode, self).__init__()


class Node(BasicNode):
    def __init__(self):
        super(Node, self).__init__()
        self._managed = True
        self._expanded = False

    def _manual_context(self, node_context):
        # Rebuild input and output.
        close_handles = {
            'input': [
                value.close
                for value in node_context.input],
            'output': [
                value.close
                for value in node_context.output]}

        return (node_context, close_handles)

    # Methods to be overidden by user for manual node context management.
    @synode.original
    @managed_context
    def verify_parameters_basic(self, node_context):
        return self.verify_parameters(node_context)

    @managed_context
    def adjust_parameters_basic(self, node_context):
        return self.adjust_parameters(node_context)

    def custom_parameters_basic(self, node_context):
        return self.custom_parameters(node_context)

    def update_parameters_basic(self, old_params):
        params = parameters(old_params, update_lists=False)
        self.update_parameters(params)
        return params.parameter_dict

    @managed_context
    def execute_basic(self, node_context):
        try:
            self._beg_capture_text_streams(node_context)
            return self.execute(node_context)
        finally:
            self._end_capture_text_streams(node_context)

    def exec_parameter_view_basic(self, node_context):
        return self.exec_parameter_view(node_context)

    @managed_context
    def _execute_parameter_view(self, node_context, return_widget=False):
        return super(Node, self)._execute_parameter_view(
            node_context, return_widget)

    #   Methods to be overidden by user
    @synode.original
    def verify_parameters(self, node_context):
        return super(Node, self).verify_parameters_basic(node_context)

    def adjust_parameters(self, node_context):
        return super(Node, self).adjust_parameters_basic(node_context)

    def custom_parameters(self, node_context):
        return super(Node, self).custom_parameters_basic(node_context)

    def update_parameters(self, old_params):
        return super(Node, self).update_parameters_basic(old_params)

    def execute(self, node_context):
        return super(Node, self).execute_basic(node_context)

    def exec_parameter_view(self, node_context):
        return super(Node, self).exec_parameter_view_basic(node_context)


class ManagedNode(Node):
    """
    This class is still around as an option for writing nodes that are
    backwards compatible with 1.2.
    """

    def __init__(self, *args, **kwargs):
        super(ManagedNode, self).__init__(*args, **kwargs)

    @synode.original
    @managed_context
    def verify_parameters_basic(self, node_context):
        return self.verify_parameters_managed(node_context)

    @managed_context
    def adjust_parameters_basic(self, node_context):
        return self.adjust_parameters_managed(node_context)

    def custom_parameters_basic(self, node_context):
        return self.custom_parameters_managed(node_context)

    def update_parameters_basic(self, old_params):
        params = parameters(old_params, update_lists=False)
        self.update_parameters_managed(params)
        return params.parameter_dict

    @managed_context
    def execute_basic(self, node_context):
        try:
            self._beg_capture_text_streams(node_context)
            return self.execute_managed(node_context)
        finally:
            self._end_capture_text_streams(node_context)

    def exec_parameter_view_basic(self, node_context):
        return self.exec_parameter_view_managed(node_context)

    @managed_context
    def _execute_parameter_view(self, node_context, return_widget=False):
        return super(Node, self)._execute_parameter_view(
            node_context, return_widget)

    #   Methods to be overidden by user
    @synode.original
    def verify_parameters_managed(self, node_context):
        return super(Node, self).verify_parameters_basic(node_context)

    def adjust_parameters_managed(self, node_context):
        return super(Node, self).adjust_parameters_basic(node_context)

    def update_parameters_managed(self, old_params):
        return super(Node, self).update_parameters_basic(old_params)

    def custom_parameters_managed(self, node_context):
        return super(Node, self).custom_parameters_basic(node_context)

    def execute_managed(self, node_context):
        return super(Node, self).execute_basic(node_context)

    def exec_parameter_view_managed(self, node_context):
        return super(Node, self).exec_parameter_view_basic(node_context)


def adjust(parameter, sydata, kind=None, lists='all', **kwargs):
    """
    Helper function to standardize implementation of adjust_parameters.
    Possible kwargs depends on the actual sydata type.
    """
    def _names(sydata):
        try:
            names = sydata.names(kind, **kwargs)
        except (AttributeError, NotImplementedError):
            names = []
        return names

    names = []

    if sydata is not None and sydata.is_valid():
        # Primitive check for list types without isinstance.
        is_list = str(sydata.container_type).startswith('[')

        if is_list:
            # Special case handling for single list.
            if lists == 'all':
                names_set = set()
                for item in sydata:
                    names_set.update(_names(item))
                names = list(sorted(names_set, key=combined_key))
            elif lists == 'first':
                if len(sydata):
                    names = _names(sydata[0])
            elif lists == 'index':
                names = [six.text_type(i) for i in range(len(sydata))]
            else:
                assert False, (
                    'Unknown list handling: "{}" in adjust.'.format(
                        lists))
        else:
            names = _names(sydata)

    parameter.adjust(names)


controller = Controller
field = Field
editors = Editors

# For backwards compatibility:
Util = Editors


def _set_child_progress_func(set_parent_progress, parent_value, factor):
    def inner(child_value):
        return set_parent_progress(
            parent_value + (child_value * factor / 100.))
    return inner


def map_list_node(func, input_list, output_list, set_progress):
    n_items = len(input_list)

    for i, input_item in enumerate(input_list):
        factor = 100. / n_items
        parent_progress = i * factor
        set_progress(parent_progress)
        set_child_progress = _set_child_progress_func(
            set_progress, parent_progress, factor)
        output_item = output_list.create()
        try:
            func(input_item, output_item, set_child_progress)
            output_list.append(output_item)
        except Exception:
            raise exceptions.SyListIndexError(i, sys.exc_info())

    set_progress(100)
