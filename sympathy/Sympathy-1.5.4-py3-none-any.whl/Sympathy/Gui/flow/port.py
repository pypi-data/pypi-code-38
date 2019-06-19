# This file is part of Sympathy for Data.
# Copyright (c) 2013 Combine Control Systems AB
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
import six
import PySide.QtCore as QtCore

from . types import ElementInterface, Type, Executors
from .. import datatypes
from . import flowlib


@six.python_2_unicode_compatible
class Port(ElementInterface):
    datatype_changed = QtCore.Signal()
    description_changed = QtCore.Signal()
    viewer_changed = QtCore.Signal(bool)
    executor = Executors.Port

    def __init__(self, node=None, definition=None,
                 generics_map=None, **kwargs):
        assert(node)
        assert(definition)
        super(Port, self).__init__(**kwargs)
        self._size = QtCore.QSizeF(10, 10)
        self._node = node
        self._scheme = None
        self._datatype = None
        self._description = None
        self._requires_input_data = None
        self._filename = ''
        self._definition = definition
        self._mirror_port = None
        self._port_viewer_open = False
        self._name = self._definition.name
        self._description = self._definition.description
        # Make a copy
        self._scheme = self._definition.scheme
        self._requires_input_data = self._definition.requires_input_data
        self._generics_map = {} if generics_map is None else generics_map

        self.datatype_base = datatypes.DataType.from_datatype(
            self._definition.datatype)

        if self._datatype is None:
            assert(False)

    def to_dict(self, execute=False):
        port_dict = {
            'uuid': self.full_uuid if execute else self.uuid,
            'name': self._name,
            'key': self._name,
            'description': self._description,
            'type': str(self.datatype),
            'type_base': str(self.datatype_base),
            'scheme': self.scheme,
            'requiresdata': self._requires_input_data,
            'file': self.filename}

        return port_dict

    def update(self, other):
        """Update the port definitions from another port's."""
        assert(False)
        # self._name = other.name
        # if self._description is None:
        #     self._description = other.description
        # self._datatype = other.datatype
        # self._scheme = other.scheme
        # self._requires_input_data = other.requires_input_data
        # self._filename = other.filename
        # self.datatype_changed.emit()

    def __str__(self):
        """String for printing."""
        return u'{}:{}>{}:{}'.format(
            self.type.name, self.node.name, self.name, self.uuid)

    @property
    def index(self):
        """Returns the index of this port on it's node."""
        return self._node.port_index(self)

    @property
    def datatype(self):
        """Returns the datatype (eg. table, ADAF, datasource, text, ...)."""
        return self._datatype

    @property
    def datatype_base(self):
        return self._datatype_base

    @datatype_base.setter
    def datatype_base(self, value):
        self._datatype_base = value
        self._datatype_generics = None

        if self._datatype_base.generics():
            self._datatype_base.identify(self._generics_map)
            self._datatype_generics = self._datatype_base.generics()

        self._datatype = datatypes.DataType.from_datatype(self._datatype_base)
        self.datatype_changed.emit()

    @property
    def datatype_generics(self):
        return self._datatype_generics

    def datatype_instantiate(self, mapping):

        if self._datatype_generics:
            before = str(self._datatype)

            datatype = datatypes.DataType.from_datatype(self._datatype_base)
            datatype.instantiate(mapping)
            if datatype is None:
                assert(False)
            after = str(datatype)

            self._datatype = datatype

            if before != after:
                self.datatype_changed.emit()

    @property
    def node(self):
        """Returns the node on which the port is attached."""
        return self._node

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def description(self):
        return self._description

    @description.setter
    def description(self, value):
        self._description = value
        self.description_changed.emit()

    @property
    def scheme(self):
        """The port's scheme describes the way the data is stored."""
        return self._scheme

    @scheme.setter
    def scheme(self, value):
        self._scheme = value

    @property
    def filename(self):
        if self.node.needs_filename(self):
            return self._filename
        else:
            port = self._flow.source_port(self)
            if port:
                return port._filename
        return ''

    @filename.setter
    def filename(self, value):
        if self.node.needs_filename(self):
            self._filename = value

    @property
    def requires_input_data(self):
        return self._requires_input_data

    @property
    def port_definition(self):
        return self._definition

    def add(self, flow=None):
        if flow is not None:
            self._flow = flow
        if self.type == Type.InputPort:
            self._flow.add_input_port(self)
        else:
            self._flow.add_output_port(self)

    def remove(self):
        if self.type == Type.InputPort:
            self._flow.remove_input_port(self)
        else:
            self._flow.remove_output_port(self)

    def matches(self, other):
        if self._datatype is None or other._datatype is None:
            return False
        else:
            if (self._datatype == datatypes.Any or
                    other._datatype == datatypes.Any):
                return True
            else:
                if self._datatype == other._datatype:
                    return True
                else:
                    return self._datatype.match(other._datatype)

    @property
    def mirror_port(self):
        """Ports on flows and FlowInput/Output have mirror ports on the
        inside/outside.
        """
        return self._mirror_port

    @mirror_port.setter
    def mirror_port(self, value):
        self._mirror_port = value

    def has_mirror(self):
        return self._mirror_port is not None

    @property
    def port_viewer_open(self):
        return self._port_viewer_open

    @port_viewer_open.setter
    def port_viewer_open(self, value):
        if value != self._port_viewer_open:

            self._port_viewer_open = value
            self.viewer_changed.emit(value)

            destination_ports = self.flow.destination_ports(self, both=True)
            for dest_port in destination_ports:
                if dest_port.type == Type.OutputPort and dest_port != self:
                    dest_port.port_viewer_open = value

    def _connection(self):
        """ Returns the Connection to which this port is connected, or None
        if it isn't """
        self._flow.input_connection_to_port(self)

    def is_connected(self):
        raise NotImplementedError('Port is abstract.')

    def disconnect(self):
        if self._datatype_generics:
            self._datatype = datatypes.DataType.from_datatype(
                self._datatype_base)
            self.datatype_changed.emit()


class InputPort(Port):
    _type = Type.InputPort

    def __init__(self, node=None, *args, **kwargs):
        super(InputPort, self).__init__(node, *args, **kwargs)
        infertype_ctx = flowlib.infertype_ctx
        if infertype_ctx.delayed:
            infertype_ctx.edges.append((self, node))

    def to_dict(self, execute=False):
        port_dict = super(InputPort, self).to_dict(execute)
        if execute:
            source = self.flow.source_port(self, traverse_subflows=True)
            if source is None:
                inputs_w_same_source = 1
            else:
                inputs_w_same_source = len(source.node.flow.destination_ports(
                    source, traverse_subflows=True))
            port_dict['requires_deepcopy'] = inputs_w_same_source > 1
        return port_dict

    @property
    def scheme(self):
        port = self._flow.source_port(self, True, False)
        if not port:
            port = self._flow.source_port(self, True, True)
        if port:
            return port.scheme
        return self._scheme

    @property
    def port_viewer_open(self):
        return False

    def is_connected(self):
        source_port = self.flow.source_port(self, True, True)
        if source_port:
            if source_port.type == Type.OutputPort:
                if source_port.node.type == Type.Node:
                    return True
                elif (source_port.node.type == Type.FlowInput and
                      source_port.node.flow.is_atom()):
                    return True
                elif (source_port.node.type == Type.Flow and
                      source_port.node.is_atom()):
                    return True
        return False

    def connected_source_port(self):
        self._flow.source_port(self)

    def can_create(self):
        return self.node.can_create_input(self.name)

    def can_delete(self):
        return self.node.can_delete_input(self)


class OutputPort(Port):
    _type = Type.OutputPort

    def __init__(self, node, *args, **kwargs):
        super(OutputPort, self).__init__(node, *args, **kwargs)
        infertype_ctx = flowlib.infertype_ctx
        if infertype_ctx.delayed:
            infertype_ctx.edges.append((node, self))

    def is_connected(self):
        destinations = self.flow.destination_ports(self, both=True)
        return len(destinations) > 0

    def can_create(self):
        return self.node.can_create_output(self.name)

    def can_delete(self):
        return self.node.can_delete_output(self)

    @property
    def scheme(self):
        if self.node.type == Type.FlowInput and self.node.parent_port:
            return self.node.parent_port.scheme
        return self._scheme
