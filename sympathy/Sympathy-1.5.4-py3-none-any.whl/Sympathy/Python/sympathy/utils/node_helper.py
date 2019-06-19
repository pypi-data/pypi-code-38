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
import collections
import numpy as np
import sys
import six
from .. platform import gennode
from .. platform import exceptions
from . parameter_helper_visitors import WidgetBuildingVisitor
from . port import Port, Ports
from . import port as syport
from .. typeutils import table, adaf
from sympathy.types import types as sytypes
from sympathy.types import typefactory
from sympathy.api.exceptions import NoDataError
from .. api import qt as qt_compat
from sympathy.platform import version_support as vs
QtGui = qt_compat.import_module('QtGui')

CHILD_GROUP = 'Child'
ADAF_GROUP = 'ADAF Selection'


class TableOperation(object):
    """Base class for operations that can be wrapped into both ADAF and
    Table operations. To add parameters:
    class MyOperation(TableOperation)
        parameter_group = TableOperation.parameter_group
        parameter_group.set_boolean(...)
    """
    update_using = None  # Set to False if a new table should be created.
    has_custom_widget = False
    inputs = ['Input']
    outputs = ['Output']

    @staticmethod
    def get_parameter_group():
        parameters = gennode.parameters()
        return parameters

    def adjust_table_parameters(self, in_table, parameters):
        """Adjust parameters.
        :param in_table: (sample) input table
        :type in_table: table.File
        :type parameters: parameter_helper.ParameterRoot
        """
        pass

    def execute_table(self, in_table, out_table, parameters):
        raise NotImplementedError('Must supply execute_table!')

    def custom_widget(self, in_table, parameters):
        """
        Must return a QWidget that takes __init__(in_table, parameters).
        """
        raise NotImplementedError('Must supply custom_widget')


class TableCalculation(gennode.Node):
    """Calculation class that takes a table in and a table out."""

    def exec_parameter_view(self, node_context):
        if self.has_custom_widget:
            in_table = {
                port: node_context.input[port_idx]
                for port_idx, port in enumerate(self._input_ports)}
            return self.custom_widget(in_table, node_context.parameters)
        else:
            visitor = WidgetBuildingVisitor()
            node_context.parameters.accept(visitor)
            return visitor.gui()

    def adjust_parameters(self, node_context):
        self.adjust_table_parameters(
            {port: node_context.input[port_idx]
             for port_idx, port in enumerate(self._input_ports)},
            node_context.parameters)
        return node_context

    def execute(self, node_context):
        if self.update_using is not None:
            node_context.output[0].update(node_context.input[0])
        self.execute_table(
            {port: node_context.input[port_idx]
             for port_idx, port in enumerate(self._input_ports)},
            {port: node_context.output[port_idx]
             for port_idx, port in enumerate(self._output_ports)},
            node_context.parameters)


class TablesCalculation(gennode.Node):
    """Calculation class taking a list of tables in and a list of tables out.
    """

    def exec_parameter_view(self, node_context):
        if self.has_custom_widget:
            in_table = {}
            for port_idx, port in enumerate(self._input_ports):
                if (node_context.input[port_idx].is_valid() and
                        len(node_context.input[port_idx])):
                    # Only expose a single Table to the operation
                    in_table[port] = node_context.input[port_idx][0]
                else:
                    # If there is no Table available, feed an empty Table to
                    # the operation instead
                    in_table[port] = table.File()

            return self.custom_widget(in_table, node_context.parameters)
        else:
            visitor = WidgetBuildingVisitor()
            node_context.parameters.accept(visitor)
            return visitor.gui()

    def adjust_parameters(self, node_context):
        in_table = {}
        for port_idx, port in enumerate(self._input_ports):
            if (node_context.input[port_idx].is_valid() and
                    len(node_context.input[port_idx])):
                # Only expose a single Table to the operation
                in_table[port] = node_context.input[port_idx][0]
            else:
                # If there is no Table available, feed an empty Table to
                # the operation instead
                in_table[port] = table.File()
        self.adjust_table_parameters(in_table, node_context.parameters)
        return node_context

    def execute(self, node_context):
        number_of_tables = len(node_context.input[0])
        in_table = {}

        try:
            factor = 100.0 / number_of_tables
        except ArithmeticError:
            factor = 1

        for idx in range(number_of_tables):
            for port_idx, port in enumerate(self._input_ports):
                if len(node_context.input[port_idx]):
                    in_table[port] = node_context.input[port_idx][idx]
                else:
                    in_table[port] = table.File()

            if self.update_using is not None:
                out_table = table.File(source=in_table[self.update_using])
            else:
                out_table = table.File()

            out_table = {port: out_table for port in self._output_ports}

            self.execute_table(
                in_table, out_table, node_context.parameters)
            for port_idx, port in enumerate(self._output_ports):
                node_context.output[port_idx].append(out_table[port])
            self.set_progress(factor * idx)


class ADAFSelection(QtGui.QWidget):
    def __init__(self, node_context, table_class, parent=None):
        super(ADAFSelection, self).__init__(parent)

        self._node_context = node_context
        self._parameters = self._node_context.parameters
        self._adaf_parameters = self._parameters[ADAF_GROUP]
        self._node_parameters = self._parameters[CHILD_GROUP]

        if (self._node_context.input[0].is_valid() and
                len(self._node_context.input[0])):
            self._adafdata = self._node_context.input[0][0]
        self._table_class = table_class
        self._generated_gui = None
        self._layout = QtGui.QVBoxLayout()
        # visitor = WidgetBuildingVisitor()
        self._system_gui = self._adaf_parameters['system'].gui()
        self._raster_gui = self._adaf_parameters['raster'].gui()
        if self._table_class.has_custom_widget:
            groupbox = QtGui.QGroupBox('ADAF Selection')
            self._group_layout = QtGui.QVBoxLayout()
            groupbox.setLayout(self._group_layout)
            self._group_layout.addWidget(self._system_gui)
            self._group_layout.addWidget(self._raster_gui)
            if 'output' in self._adaf_parameters:
                self._group_layout.addWidget(
                    self._adaf_parameters['output'].gui())
            self._layout.addWidget(groupbox)

        self._node_gui = self._get_node_gui()
        self._layout.addWidget(self._node_gui)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self._layout)

        self._system_gui.editor().currentIndexChanged.connect(
            self._update_system)
        self._raster_gui.editor().currentIndexChanged.connect(
            self._update_raster)

    def _get_node_gui(self):
        if self._table_class.has_custom_widget:
            node_gui = self._table_class.custom_widget(
                self._get_in_table(), self._node_parameters)
        else:
            if self._generated_gui is None:
                visitor = WidgetBuildingVisitor()
                self._parameters.accept(visitor)
                node_gui = visitor.gui()
                self._generated_gui = node_gui
            else:
                node_gui = self._generated_gui
        return node_gui

    def _get_in_table(self):
        selected_system = self._adaf_parameters['system'].selected
        selected_raster = self._adaf_parameters['raster'].selected
        in_table = {}
        for port_idx, input_port in enumerate(self._table_class._input_ports):
            if self._node_context.input[port_idx].is_valid():
                if (len(self._node_context.input[port_idx]) and
                        selected_system is not None and
                        selected_raster is not None):
                    in_adaf = self._node_context.input[port_idx][0]
                    in_table[input_port] = (
                        in_adaf.sys[selected_system][selected_raster].to_table(
                            selected_raster))
                else:
                    in_table[input_port] = table.File()  # Empty table
        self._table_class.adjust_table_parameters(
            in_table, self._node_parameters)
        return in_table

    def _update_system(self):
        selected = self._adaf_parameters['system'].selected
        rasters = self._adafdata.sys[selected].keys()
        self._raster_gui.editor().clear()
        self._raster_gui.editor().addItems(rasters)

        if selected in rasters:
            if selected in rasters:
                i = self._raster_gui.editor().combobox().find_text(selected)
                if i >= 0:
                    self._raster_gui.editor().combobox().setCurrentIndex(i)

        self._update_raster()

    def _update_raster(self):
        self._node_gui.hide()
        self._layout.removeWidget(self._node_gui)
        del self._node_gui
        self._node_gui = self._get_node_gui()
        self._layout.addWidget(self._node_gui)


class ADAFsCalculation(gennode.Node):
    def exec_parameter_view(self, node_context):
        return ADAFSelection(node_context, self)

    def adjust_parameters(self, node_context):
        parameters = node_context.parameters
        in_table = {}
        systems = []
        rasters = []

        for port_idx, port in enumerate(self._input_ports):
            try:
                if (node_context.input[port_idx].is_valid() and
                        len(node_context.input[port_idx])):
                    first_file = node_context.input[port_idx][0]
                    systems = sorted(first_file.sys.keys())
                    first_system = first_file.sys[systems[0]]
                    rasters = sorted(first_system.keys())
                    first_raster = first_system[rasters[0]]
                    in_table[port] = first_raster.to_table(rasters[0])
                else:
                    # Use empty table as fallback
                    in_table[port] = table.File()
            except (NoDataError, IndexError):
                # Use empty table as fallback
                in_table[port] = table.File()

        parameters[ADAF_GROUP]['system'].list = systems
        parameters[ADAF_GROUP]['raster'].list = rasters
        self.adjust_table_parameters(in_table, parameters[CHILD_GROUP])
        return node_context

    def execute(self, node_context):
        parameters = node_context.parameters
        parameter_group = parameters[CHILD_GROUP]
        system = parameters[ADAF_GROUP]['system'].selected
        raster = parameters[ADAF_GROUP]['raster'].selected
        if self.output_location == 'Time series':
            output = parameters[ADAF_GROUP]['output'].value
        number_of_tables = len(node_context.input[0])
        try:
            factor = 100.0 / number_of_tables
        except ArithmeticError:
            factor = 1
        in_table = {}

        for idx in range(number_of_tables):
            for port in self._input_ports:
                if (len(node_context.input[port]) and
                        raster is not None and system is not None):
                    in_table[port] = (
                        node_context.input[port][idx]
                        .sys[system][raster].to_table(raster))
                else:
                    in_table[port] = table.File()

            if self.output_location == 'Time series':
                if output == '':
                    out_table_ = table.File(source=in_table[self.update_using])
                else:
                    out_table_ = table.File()

            elif self.output_location == 'Meta':
                out_table_ = table.File(
                    source=node_context.input[
                        self.update_using][idx].meta.to_table())
            elif self.output_location == 'Result':
                out_table_ = table.File(
                    source=node_context.input[
                        self.update_using][idx].res.to_table())

            out_table = {port: out_table_ for port in self._output_ports}
            self.execute_table(in_table, out_table, parameter_group)

            if len(node_context.input[self.update_using]):
                out_adaf = adaf.File(
                    source=node_context.input[self.update_using][idx])

                if (self.output_location == 'Time series' and
                        raster is not None and system is not None):
                    if output == '':
                        out_adaf.sys[system][raster].from_table(
                            out_table[self._output_ports[0]], raster)
                    else:
                        out_raster = out_adaf.sys[system].create(output)
                        out_raster.from_table(out_table[self._output_ports[0]])
                        out_raster.create_basis(np.arange(
                            out_table[self._output_ports[0]].number_of_rows()))

                elif self.output_location == 'Meta':
                    out_adaf.meta.from_table(out_table[self._output_ports[0]])
                elif self.output_location == 'Result':
                    out_adaf.res.from_table(out_table[self._output_ports[0]])

            else:
                out_adaf = adaf.File(
                    source=node_context.input[self.update_using])

            node_context.output[0].append(out_adaf)
            self.set_progress(factor * idx)


def table_node_factory(class_name, table_operation, node_name, node_id):
    parameters = gennode.parameters()
    table_operation.get_parameters(parameters)
    new_dict = {
        'name': node_name,
        'parameters': parameters,
        'nodeid': node_id,
        'inputs': Ports([
            Port.Table(port_name, name=port_name)
            for port_name in table_operation.inputs]),
        'outputs': Ports([
            Port.Table(port_name, name=port_name)
            for port_name in table_operation.outputs]),
        'description': (
            table_operation.description
            if 'description' in table_operation.__dict__
            else table_operation.__doc__),
        '_input_ports': table_operation.inputs,
        '_output_ports': table_operation.outputs,
        '__doc__': table_operation.__doc__,
    }

    return type(vs.str_(class_name),
                (TableCalculation, table_operation), new_dict)


def tables_node_factory(class_name, table_operation, node_name, node_id):
    parameters = gennode.parameters()
    table_operation.get_parameters(parameters)
    new_dict = {
        'name': node_name,
        'nodeid': node_id,
        'parameters': parameters,
        'inputs': Ports([
            Port.Tables(port_name, name=port_name)
            for port_name in table_operation.inputs]),
        'outputs': Ports([
            Port.Tables(port_name, name=port_name)
            for port_name in table_operation.outputs]),
        'description': (
            table_operation.description
            if 'description' in table_operation.__dict__
            else table_operation.__doc__),
        '_input_ports': table_operation.inputs,
        '_output_ports': table_operation.outputs,
        '__doc__': table_operation.__doc__,
    }

    return type(vs.str_(class_name), (TablesCalculation, table_operation),
                new_dict)


def adafs_node_factory(class_name, table_operation, node_name, node_id,
                       output_location):
    """When creating ADAFs, a source port to update from must always be
    supplied as we only ever replace a single table in the ADAF structure.
    """
    assert output_location in ('Time series', 'Meta', 'Result')
    update_using_ = table_operation.update_using
    if update_using_ is None:
        update_using_ = table_operation.inputs[0]

    parameters = collections.OrderedDict()
    parameter_root = gennode.parameters(parameters)
    parameter_group = parameter_root.create_group(ADAF_GROUP, order=0)
    node_group = parameter_root.create_group(CHILD_GROUP, order=100)
    parameter_group.set_list(
        'system', label='System',
        description='System',
        editor=gennode.Util.combo_editor().value())
    parameter_group.set_list(
        'raster', label='Raster',
        description='Raster',
        editor=gennode.Util.combo_editor().value())
    if output_location == 'Time series':
        parameter_group.set_string(
            'output', label='Output Raster',
            description='Output Raster, leave empty to use input raster.',
            value='')
    table_operation.get_parameters(node_group)

    new_dict = {
        'parameters': parameters,
        'name': node_name,
        'nodeid': node_id,
        'update_using': update_using_,
        'inputs': Ports([
            Port.ADAFs(port_name, name=port_name)
            for port_name in table_operation.inputs]),
        'outputs': Ports([
            Port.ADAFs(port_name, name=port_name)
            for port_name in table_operation.outputs]),
        'description': (
            table_operation.description
            if 'description' in table_operation.__dict__
            else table_operation.__doc__),
        '_input_ports': table_operation.inputs,
        '_output_ports': table_operation.outputs,
        'output_location': output_location,
        '__doc__': table_operation.__doc__,
    }

    return type(vs.str_(class_name), (ADAFsCalculation, table_operation),
                new_dict)


class ListExecuteMixin(object):

    def _set_child_progress(self, set_parent_progress, parent_value, factor):
        def inner(child_value):
            return set_parent_progress(
                parent_value + (child_value * factor / 100.))
        return inner

    def _key_names(self, keys):
        if isinstance(keys, dict):
            return [value['name'] if 'name' else key in value
                    for key, value in keys.items()]
        return keys

    def exec_parameter_view(self, node_context):

        inputs = list(node_context.input)
        outputs = list(node_context.output)

        list_inputs = [node_context.input[key]
                       for key in self._key_names(
                               self._input_list_keys)]
        child_inputs = []

        for i, p in enumerate(inputs):
            if p in list_inputs:
                if p.is_valid() and len(p):
                    child_port = p[0]
                else:
                    sytype = sytypes.from_string(
                        node_context.definition['ports'][
                            'inputs'][i]['type'])[0]
                    child_port = typefactory.from_type(sytype)
            else:
                child_port = p
            child_inputs.append(child_port)

        updated_node_context = self.update_node_context(
            node_context, child_inputs, outputs)

        return super(ListExecuteMixin, self).exec_parameter_view(
            updated_node_context)

    def execute(self, node_context):
        inputs = list(node_context.input)
        outputs = list(node_context.output)

        list_inputs = [node_context.input[key]
                       for key in self._key_names(self._input_list_keys)]
        list_outputs = [node_context.output[key]
                        for key in self._key_names(self._output_list_keys)]

        len_list_inputs = len(list_inputs)

        input_indices = {inputs.index(p): i
                         for i, p in enumerate(list_inputs)}
        output_indices = {outputs.index(p): i
                          for i, p in enumerate(list_outputs)}

        n_items = min(len(input) for input in list_inputs)
        res = None
        org_set_progress = self.set_progress

        for i, ports in enumerate(six.moves.zip(*list_inputs)):
            factor = 100. / n_items
            parent_progress = i * factor
            self.set_progress(parent_progress)
            self.set_progress = self._set_child_progress(
                org_set_progress, parent_progress, factor)
            try:
                output_ports = [o.create() for o in list_outputs]

                input_ports = ports[:len_list_inputs]

                child_inputs = [input_ports[input_indices[j]]
                                if j in input_indices else p
                                for j, p in enumerate(inputs)]

                child_outputs = [output_ports[output_indices[j]]
                                 if j in output_indices else p
                                 for j, p in enumerate(outputs)]

                updated_node_context = self.update_node_context(
                    node_context, child_inputs, child_outputs)

                res = super(ListExecuteMixin, self).execute(
                    updated_node_context)

                for output_port, list_output in zip(output_ports,
                                                    list_outputs):
                    list_output.append(output_port)

            except Exception:
                raise exceptions.SyListIndexError(i, sys.exc_info())
            finally:
                self.set_progress = org_set_progress

        self.set_progress(100)
        return res


def list_node_factory(cls, input_keys, output_keys, name=None, nodeid=None,
                      cls_name=None):

    def gen_list_string(name):
        assert name
        return '{}s'.format(name)

    def gen_list_ports(ports, keys):
        list_ports = [ports[key] for key in keys]
        changes = dict.fromkeys(list_ports)
        if isinstance(keys, dict):
            for key, port in zip(keys, list_ports):
                changes[port] = keys[key]

        return syport.Ports([
            syport.make_list_port(p, changes[p]) if p in list_ports else p
            for p in ports])

    def format_key(key):
        if isinstance(key, six.string_types):
            return '{}'.format(key)
        else:
            return 'port-index:{}'.format(key)

    if not name:
        name = gen_list_string(cls.name)

    if not nodeid:
        nodeid = gen_list_string(cls.nodeid)

    if not cls_name:
        cls_name = gen_list_string(cls.__name__)

    inputs = gen_list_ports(cls.inputs, input_keys)
    outputs = gen_list_ports(cls.outputs, output_keys)

    doc = """
    Auto generated list version of :ref:`{node}`.

    In this version, the following ports from the original nodes have been
    changed to lists which the node loops over:

        :Looped Inputs: {inputs}.
        :Looped Outputs: {outputs}.

    For more details see :ref:`{node}`.

    """.format(node=cls.name,
               inputs=', '.join([format_key(key) for key in input_keys]),
               outputs=', '.join([format_key(key) for key in output_keys]))

    cls_dict = {
        '__doc__': doc,
        'name': name,
        'nodeid': nodeid,
        'inputs': inputs,
        'outputs': outputs,
        '_input_list_keys': input_keys,
        '_output_list_keys': output_keys,
    }

    return type(vs.str_(cls_name), (ListExecuteMixin, cls), cls_dict)
