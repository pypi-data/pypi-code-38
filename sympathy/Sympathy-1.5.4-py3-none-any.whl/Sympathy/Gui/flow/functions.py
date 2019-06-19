# -*- coding: utf-8 -*-
# This file is part of Sympathy for Data.
# Copyright (c) 2015 Combine Control Systems AB
#
# Sympathy for Data is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Sympathy for Data is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Sympathy for Data.  If not, see <http://www.gnu.org/licenses/>.
from __future__ import (print_function, division, unicode_literals,
                        absolute_import)

import PySide.QtCore as QtCore
import json
import base64
import six
from . import flow, node
from .. import library
from .. import datatypes
from . types import Type, Executors
from .. import environment_variables
from .. import settings
from .. import util
from . exceptions import SyInferTypeError
from sympathy.utils.prim import localuri


_void = datatypes.DataType.from_str('()')


class PortAdapter(object):
    type = None

    def __init__(self, datatype_base):
        self.datatype_base = datatype_base


class Lambda(node.StatefulNode, flow.Flow):
    executor = Executors.Lambda
    class_name = 'Lambda'
    source_file = None

    def __init__(self, **kwargs):
        super(Lambda, self).__init__(**kwargs)
        self._init_state_machine_()
        self._new = kwargs.get('uuid') is None
        self._output_port = None
        self._flow_output = None
        self._done = False
        self._exclude_input = None
        self._extra_input = False

    def initialize(self):
        # Initial creation of port.
        pdef = library.PortDefinition(
            'Function', 'Lambda function', '<a>', 'hdf5', 0, False)

        mapping = {}
        port = self._flow.create_output_port(self, pdef, mapping)
        self._output_port = port
        # Setup initial type.

        port.datatype_instantiate(mapping)
        self.output_port_created.emit(port)

        if self._new:
            middle = QtCore.QPointF(2000, 2000)
            flow_output = self.create_flow_output()
            flow_input = self.create_flow_input()

            flow_output.position = QtCore.QPointF(
                middle.x() + flow_output.size.width() * 2.0,
                middle.y())

            flow_input.position = QtCore.QPointF(
                middle.x() - flow_output.size.width() * 2.0,
                middle.y())

            self._new = False
        self._infertypes()

        self.recursive_connection_created.connect(self._top_validate)
        self.recursive_connection_removed.connect(self._top_validate)

    _base_name = 'New Lambda'

    def to_node_dict(self, data):
        """For builtins that want to execute as a specific flow."""
        # Could be done with parameter_helper but that could add some
        # dependencies.
        return {
            'parameters': {'data': {'type': 'group', 'flow':
                                    {'type': 'string', 'value':
                                     json.dumps(data)}},
                           'type': 'json'},
            'ports': {
                'inputs': [],
                'outputs': [self._output_port.to_dict(execute=True)]
            }
        }

    def to_copy_dict(self, base_node_params=True):
        result = flow.Flow.to_copy_dict(
            self, base_node_params=base_node_params)
        result['basic_ports'] = {
            'inputs': [], 'outputs': [self._output_port.to_dict()]}
        return result

    def to_dict(self, execute=False, stub=False):
        result = flow.Flow.to_dict(self, execute=execute, stub=stub)
        result['basic_ports'] = {
            'inputs': [], 'outputs': [self._output_port.to_dict(execute)]}
        return result

    def port_viewer(self, port):
        port = self.flow.source_port(port)

        if port is self._output_port:
            self._flow.app_core.port_viewer(port)

    def input_nodes(self):
        return [input_port.node for input_port in
                self.ports_connected_to_input_ports()]

    def output_nodes(self):
        return [output_port.node for output_port in
                self.ports_connected_to__output_ports()]

    def needs_filename(self, port):
        return port.node is self and port in self._outputs

    def _function_type(self, input_types=None):
        if input_types is None:
            input_types = [input_.port.datatype
                           for input_ in self._flow_inputs]

        output_port = self._output_port
        types = list(input_types)
        types.append(output_port.datatype)
        datatype = datatypes.DataType.from_datatypes_function(types)
        return datatype

    def infertype_constraints(self):
        type_mapping = {}
        constraints = []
        input_ports = [flow_input.port for flow_input in self._flow_inputs
                       if flow_input is not self._exclude_input]

        constraints.extend([(flow_input.port, flow_input.parent_port)
                            for flow_input in self._flow_inputs
                            if flow_input.parent_port])

        functype = datatypes.DataType.from_length_function(
            len(input_ports) + (2 if self._extra_input else 1))
        functype.identify(type_mapping)

        res_type = functype.datatype
        for input_port in input_ports:
            constraints.append((input_port, PortAdapter(
                datatypes.DataType(res_type.arg))))
            res_type = res_type.result

        if self._extra_input:
            res_type = res_type.result

        if self._flow_output:
            constraints.append((self._flow_output.port, PortAdapter(
                datatypes.DataType(res_type))))

        constraints.append((self._output_port, PortAdapter(functype)))
        return constraints

    def datatype(self):
        if self._output_port:
            return self._output_port.datatype

    def create_flow_input(self, create_parent_port=False, **kwargs):

        if create_parent_port is None:
            create_parent_port = False

        result = super(Lambda, self).create_flow_input(
            create_parent_port=create_parent_port,
            **kwargs)

        if self.is_initialized():
            self._infertypes()
        return result

    def create_flow_output(self, create_parent_port=False, **kwargs):

        if create_parent_port is None:
            create_parent_port = False

        result = super(Lambda, self).create_flow_output(
            create_parent_port=create_parent_port, **kwargs)
        self._flow_output = result

        if self.is_initialized():
            self._infertypes()
        return result

    def can_lock(self):
        return False

    def can_create_flow_input(self):
        try:
            self._extra_input = True
            self._infertypes(check=True)
            return True
        except SyInferTypeError:
            return False
        finally:
            self._extra_input = False

    def can_create_flow_output(self):
        return False

    def can_remove_flow_input(self, flowinput):
        if len(self._flow_inputs) <= 1:
            return False

        try:
            self._exclude_input = flowinput
            self._infertypes(check=True)
            return True
        except SyInferTypeError:
            return False
        finally:
            self._exclude_input = None

    def can_remove_flow_output(self, flowoutput):
        return False

    def can_reorder_flow_input(self, flowinfo):
        return False

    def can_delete_input(self, port):
        return True

    def creatable_parent_flow_inputs(self):
        return [input_ for input_ in self._flow_inputs
                if input_.parent_port is None]

    def creatable_parent_flow_outputs(self):
        return []

    def remove_flow_input(self, input):
        super(Lambda, self).remove_flow_input(input)
        if self.is_initialized():
            self._infertypes()

    def remove(self):
        self.before_remove.emit()
        try:
            self._flow.remove_subflow(self)
        except AttributeError:
            pass
        for output in self.outputs:
            self.remove_output_port(output)

    def port_index(self, port):
        if port.type in [Type.InputPort, Type.OutputPort]:
            return super(Lambda, self).port_index(port)
        elif port.type == Type.FlowInput:
            try:
                return self._flow_inputs.index(port)
            except ValueError:
                return None

    def reorder_inputs(self, new_order):
        self._flow_inputs = [self._flow_inputs[i] for i in new_order]

    def reorder_outputs(self, new_order):
        self._flow_outputs = [self._flow_outputs[i] for i in new_order]

    def remove_input(self, port):
        super(Lambda, self).remove_input(port)
        self._top_validate()

    def add_connection(self, connection, emit=True):
        result = super(Lambda, self).add_connection(connection, emit=emit)
        self._top_validate()
        return result

    def create_connection(self, src, dst, **kwargs):
        result = super(Lambda, self).create_connection(
            src, dst, **kwargs)
        self._top_validate()
        return result

    def remove_connection(self, connection, emit=True):
        result = super(Lambda, self).remove_connection(connection, emit=emit)
        self._top_validate()
        return result

    def add_node(self, node, emit=True):
        result = super(Lambda, self).add_node(node, emit)
        self._signals.connect(node, node.initialized, self._top_validate)
        self._top_validate()
        return result

    def remove_node(self, node):
        result = super(Lambda, self).remove_node(node)
        self._top_validate()
        return result

    def add_subflow(self, subflow, emit=True):
        result = super(Lambda, self).add_subflow(subflow, emit)
        self._top_validate()
        return result

    def remove_subflow(self, subflow):
        result = super(Lambda, self).remove_subflow(subflow)
        self._top_validate()
        return result

    def execute(self):
        self.execute_node(self)

    def validate(self):
        flow.Flow.validate(self)
        self._top_validate()

    def _top_validate(self):
        self._state_machine.validate()

    def _internal_validate(self):
        if not self._flow_output:
            return False

        res = False
        port = self.source_port(self._flow_output.port)
        output_connected = port and port is not self._flow_output.port
        if output_connected:
            all_nodes = self.all_nodes()
            connected = all(node_.inputs_are_connected()
                            for node_ in all_nodes)
            valid = all(node_.is_configuration_valid()
                        for node_ in all_nodes)
            armable = all(self._is_source_port_dependent_armable(
                input_.parent_port)
                          for input_ in self._flow_inputs
                          if input_.parent_port is not None)
            res = valid and connected and armable
        return res

    def has_pending_request(self):
        for node_ in self._nodes_and_subflows():
            if node_.has_pending_request():
                return True
        return False

    def internal_validate(self):
        internal = self._internal_validate()
        return self.validate_done(internal)

    def is_atom(self):
        return True

    def input_connection_added(self, port):
        for port_ in self.destination_ports(
                port.mirror_port, atom=True):
            port_.node.arm()

    def input_connection_removed(self, port):
        for port_ in self.destination_ports(
                port.mirror_port, atom=True):
            port_.node.disarm()

    def _arm_top(self):
        super(Lambda, self).arm()

    def arm(self, port=None):
        if port:
            if port.node is self:
                mirror_port = port.mirror_port
                for dst in self.destination_ports(mirror_port, atom=True):
                    if dst is not None:
                        dst.node.arm(dst)
        else:
            if self.is_armed():
                return
            flow.Flow.arm(self)

        if self._internal_validate():
            super(Lambda, self).arm()
        else:
            self._top_validate()

    def disarm(self, port=None):
        if port:
            if port.node is self:
                mirror_port = port.mirror_port
                for dst in self.destination_ports(mirror_port, atom=True):
                    if dst is not None:
                        dst.node.disarm(dst)
        else:
            flow.Flow.disarm(self)

        if self._internal_validate():
            super(Lambda, self).disarm()
        else:
            self._top_validate()

    @property
    def needs_validate(self):
        return False

    def is_executable(self):
        return super(Lambda, self).is_executable()

    def is_done(self):
        return self._state_machine.is_done()

    def set_queued(self):
        super(Lambda, self).set_queued()
        self.state_changed.emit()

    def set_started(self):
        super(Lambda, self).set_started()
        self.state_changed.emit()

    def set_done(self, result, locked=None):
        if locked is None:
            locked = False
        super(Lambda, self).set_done(result, locked=locked)
        self.state_changed.emit()

    def configure(self):
        self.app_core.execute_subflow_parameter_view(self, 'configure')

    def on_node_state_changed(self, node):
        self._add_node_state(node)
        # Only validate when changing non execution states.
        if any([self.is_armed(), self.is_done()]):
            if not node.is_configuration_valid():
                self._top_validate()
        else:
            if node.is_configuration_valid():
                self._top_validate()

    @QtCore.Slot()
    def on_state_valid(self):
        self._disarm_all_dependent_nodes()
        self._arm_top()

    @property
    def has_svg_icon(self):
        return True

    @property
    def icon(self):
        return localuri(util.icon_path('lambda.svg'))

    @property
    def background(self):
        return localuri(util.icon_path('lambda.svg'))

    def _infertypes(self, check=False):
        if self._flow:
            self._flow._infertype(
                self._output_port, None,
                check=check)


class Map(node.BuiltinNode):
    def __init__(self, identifier=None, **kwargs):
        super(Map, self).__init__(identifier, **kwargs)


class Apply(node.BuiltinNode):
    def __init__(self, identifier=None, **kwargs):
        super(Apply, self).__init__(identifier, **kwargs)


class ExtractLambdas(node.BuiltinNode):
    _template_datatype = datatypes.DataType.from_str('[<a> -> <b>]')

    def __init__(self, identifier=None, **kwargs):
        super(ExtractLambdas, self).__init__(identifier, **kwargs)
        self._output_port = None

    def initialize(self):
        super(ExtractLambdas, self).initialize()
        self._output_port = self.outputs[0]
        self._update_datatype_base()

    def _update_datatype_base(self, datatype=None):
        if datatype is None:
            datatype = self._params_datatype(
                self.parameter_model.to_dict())
        self._output_port.datatype_base = datatype

    def configure(self):
        self._flow.app_core.execute_node_parameter_view(self)

    def _params_datatype(self, params):
        dt = datatypes.DataType.from_str(
            '[{}]'.format(
                params['datatype']['value']))
        dt.identify({})
        return dt

    def _valid_datatype(self, datatype):
        if (datatype and not datatype.generics() and
                datatype.match(self._template_datatype)):
            return True
        return False

    def _infertypes(self, check=False):
        self._flow._infertype(
            self.outputs[0], None, check=check)

    @property
    def parameter_model(self):
        return self._get_parameter_model()

    @parameter_model.setter
    def parameter_model(self, new_parameters):
        try:
            new_datatype = self._params_datatype(new_parameters.to_dict())
        except Exception:
            # Ignore invalid function.
            pass
        else:
            # Non-generic function.
            if self._valid_datatype(new_datatype):
                self._update_datatype_base(new_datatype)
                try:
                    self._infertypes(check=True)
                except SyInferTypeError:
                    # Restore old datatype.
                    datatype = self._params_datatype(
                        self.parameter_model.to_dict())
                    self._update_datatype_base(datatype)
                else:
                    self._set_parameter_model(new_parameters)

    def _get_parameter_model(self):
        return super(node.BuiltinNode, self)._get_parameter_model()

    def _set_parameter_model(self, new_model):
        super(node.BuiltinNode, self)._set_parameter_model(new_model)
        self._update_datatype_base()
        self._infertypes()

    def to_dict(self, execute=False):
        result = super(ExtractLambdas, self).to_dict(execute=execute)
        if execute:
            result['parameters']['data']['json-data'] = {
                'description': '',
                'editor': None,
                'label': '',
                'type': 'string',
                'value': base64.b64encode(json.dumps({
                    'identifier': self.full_uuid,
                    'env': environment_variables.instance().variables(),
                    'folders': {
                        'temp': settings.instance()['temp_folder'],
                        'storage': settings.instance()['storage_folder'],
                        'session': settings.instance()['session_folder'],
                        'resource': settings.instance()['resource_folder'],
                        'install': settings.instance()['install_folder']},
                    'lib': self.flow.app_core.get_library_dict(update=False)
                }).encode('ascii')).decode('ascii')}
        else:
            result['parameters']['data'].pop('json-data', None)
        return result


class ExtractFlowsLambdas(ExtractLambdas):
    pass


def top_lambdas_from_flow(flow_):
    return [node_ for node_ in flow_.shallow_nodes()
            if isinstance(node_, Lambda)]


def filter_lambdas_datatype(lambdas, datatype):
    return [lambda_ for lambda_ in lambdas
            if datatype.match(lambda_.datatype())]


def flow_to_lambda(flow_):
    flow_.app_core.set_validate_enabled(False)
    try:
        top = flow.Flow(app_core=flow_.app_core)
        top.filename = flow_.filename
        top.set_flow_info(flow_.get_flow_info())
        res = top.create_function(Lambda)
        flow_.add(res)
        res.initialize()
        res.name = flow_.filename

        # Connect first input port
        iter_flow_input = iter(flow_._flow_inputs)
        flow_input = six.next(iter_flow_input)
        lambda_flow_input = res._flow_inputs[0]
        flow_input.create_parent_port()
        res.create_connection(lambda_flow_input.port, flow_input.parent_port)

        # Connect remaining input ports
        for flow_input in iter_flow_input:
            lambda_flow_input = res.create_flow_input()
            flow_input.create_parent_port()
            res.create_connection(
                lambda_flow_input.port, flow_input.parent_port)

        flow_._flow_outputs[0].create_parent_port()
        res.create_connection(
            flow_._flow_outputs[0].parent_port, res._flow_outputs[0].port)
        return [res]
    finally:
        flow_.app_core.set_validate_enabled(True)


class Empty(node.BuiltinNode):
    _template_datatype = datatypes.DataType.from_str('<a>')

    def __init__(self, identifier=None, **kwargs):
        super(Empty, self).__init__(identifier, **kwargs)
        self._output_port = None

    def initialize(self):
        super(Empty, self).initialize()
        self._output_port = self.outputs[0]
        self._update_datatype_base()
        self._output_port.datatype_changed.connect(self._reload)

    def _reload(self):
        if self.is_done():
            self.validate()

    def _update_datatype_base(self, datatype=None):
        if datatype is None:
            datatype = self._params_datatype(
                self.parameter_model.to_dict())
        self._output_port.datatype_base = datatype

    def configure(self):
        self._flow.app_core.execute_node_parameter_view(self)

    def _params_datatype(self, params):
        dt = datatypes.DataType.from_str(
            '{}'.format(params.get('datatype', {}).get('value', '<a>')))
        dt.identify({})
        return dt

    def _valid_datatype(self, datatype):
        if datatype and datatype.match(self._template_datatype):
            return True
        return False

    def _infertypes(self, input_port=None, check=False):
        self._flow._infertype(
            self.outputs[0], input_port, check=check)

    @property
    def parameter_model(self):
        return self._get_parameter_model()

    @parameter_model.setter
    def parameter_model(self, new_parameters):
        try:
            new_datatype = self._params_datatype(new_parameters.to_dict())
        except Exception:
            # Ignore invalid function.
            pass
        else:
            # Non-generic type.
            if self._valid_datatype(new_datatype):
                self._update_datatype_base(new_datatype)
                try:
                    self._infertypes(check=True)
                except SyInferTypeError:
                    # Restore old datatype.
                    datatype = self._params_datatype(
                        self.parameter_model.to_dict())
                    self._update_datatype_base(datatype)
                else:
                    self._set_parameter_model(new_parameters)

    def _get_parameter_model(self):
        return super(node.BuiltinNode, self)._get_parameter_model()

    def _set_parameter_model(self, new_model):
        super(node.BuiltinNode, self)._set_parameter_model(new_model)
        self._update_datatype_base()
        self._infertypes()


node.factories['org.sysess.builtin.apply'] = Apply
node.factories['org.sysess.builtin.map'] = Map
node.factories['org.sysess.builtin.extractlambdas'] = ExtractLambdas
node.factories['org.sysess.builtin.extractflowslambdas'] = ExtractFlowsLambdas
node.factories['org.sysess.builtin.empty'] = Empty
