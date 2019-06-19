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
from __future__ import (print_function, division, unicode_literals,
                        absolute_import)

import json
import os.path
import logging
import itertools
import copy
import PySide.QtCore as QtCore
import PySide.QtGui as QtGui

from sympathy.utils import uuid_generator
from sympathy.platform import version_support as vs
from sympathy.utils.prim import uri_to_path

from . import library
import Gui.flow
import Gui.flow_serialization


__flow_factory = None


def _flow_factory(flowname):
    global __flow_factory
    if __flow_factory is None:
        __flow_factory = {flowtype.__name__: flowtype for flowtype in
                          [Gui.flow.Flow, Gui.flow.Lambda]}

    return __flow_factory[flowname]


core_logger = logging.getLogger('core')


def copy_element_list_to_clipboard(flow_, element_list):
    """Helper for copying nodes without using the undo buffer."""
    flow_dict = Gui.flow_serialization.partial_dict(flow_, element_list)
    data = json.dumps(flow_dict)

    mime_data = QtCore.QMimeData()
    mime_data.setData(flow_.app_core.mime_type_flow(), data)
    QtGui.QApplication.clipboard().setMimeData(mime_data)


class UndoCommandBase(QtGui.QUndoCommand):
    def __init__(self, parent=None, flow=None, flow_=None,
                 **kwargs):
        self._flow = flow or flow_
        self._valid = True
        super(UndoCommandBase, self).__init__(parent=None)

    def flow(self):
        return self._flow

    @property
    def valid(self):
        return self._valid


class CreateElementCommandInterface(object):
    def __init__(self):
        super(CreateElementCommandInterface, self).__init__()

    @property
    def element_uuid(self):
        raise NotImplementedError('Not implemented for interface')

    def created_element(self):
        raise NotImplementedError('Not implemented for interface')


class CreateNodeCommand(UndoCommandBase, CreateElementCommandInterface):
    def __init__(self, node_id=None, library_node=None,
                 **kwargs):
        super(CreateNodeCommand, self).__init__(**kwargs)
        self._node_id = node_id
        self._node = None
        self._kwargs = kwargs
        # Node instance doesn't exist yet so we use the name from the library.
        if library_node is None:
            library_node = self._flow.app_core.library_node(node_id)
        self._library_node = library_node
        name = library_node.name
        self.setText('Creating node {}'.format(name))

    def redo(self):
        # Think about create vs activate and release!
        if self._node is not None:
            self._node.add(self._flow)
        else:
            self._node = self._flow.create_node(
                node_id=self._node_id,
                library_node=self._library_node, **self._kwargs)

    def undo(self):
        self._node.remove()

    def element_uuid(self):
        return self._node.uuid

    def created_element(self):
        return self._node


class CreateLibraryElementCommand(UndoCommandBase,
                                  CreateElementCommandInterface):
    def __init__(self, node_id=None, library_node=None, **kwargs):
        super(CreateLibraryElementCommand, self).__init__(**kwargs)
        self.setText('Creating library element')

        if library_node is None:
            library_node = self._flow.app_core.library_node(node_id)

        if library_node.type == 'flow':
            self._cmd = InsertSubflowLinkCommand(
                node_id=node_id, library_node=library_node, **kwargs)
        else:
            self._cmd = CreateNodeCommand(
                node_id=node_id, library_node=library_node, **kwargs)

        self._valid = self._cmd.valid

    def redo(self):
        self._cmd.redo()

    def undo(self):
        self._cmd.undo()

    def created_element(self):
        return self._cmd.created_element()


class DuplicateInputPortCommand(UndoCommandBase,
                                CreateElementCommandInterface):
    def __init__(self, port, parent=None):
        super(DuplicateInputPortCommand, self).__init__(parent)
        self._port = port
        self._flow = port.flow
        self._new_port = None
        self._index = None
        self.setText('Creating node port')

    def redo(self):
        if self._new_port:
            self._flow.add_input_port(self._new_port)
            self._port.node.insert_named_input(self._index, self._new_port)
        else:
            self._new_port = self._port.node.create_named_input(
                self._port.name)
            self._index = self._new_port.index

    def undo(self):
        self._new_port.node.delete_input(self._new_port)

    def created_element(self):
        return self._new_port


class DuplicateOutputPortCommand(UndoCommandBase,
                                 CreateElementCommandInterface):
    def __init__(self, port, parent=None):
        super(DuplicateOutputPortCommand, self).__init__(parent)
        self._port = port
        self._flow = port.flow
        self._new_port = None
        self._index = None
        self.setText('Creating node port')

    def redo(self):
        if self._new_port:
            self._flow.add_output_port(self._new_port)
            self._port.node.insert_named_output(self._index, self._new_port)
        else:
            self._new_port = self._port.node.create_named_output(
                self._port.name)
            self._index = self._new_port.index

    def undo(self):
        self._new_port.node.delete_output(self._new_port)

    def created_element(self):
        return self._new_port


class CreateNamedInputPortCommand(UndoCommandBase,
                                  CreateElementCommandInterface):
    def __init__(self, node, name, parent=None):
        super(CreateNamedInputPortCommand, self).__init__(parent)
        self._node = node
        self._name = name
        self._flow = node.flow
        self._new_port = None
        self._index = None
        self.setText('Creating node port')

    def redo(self):
        if self._new_port:
            self._flow.add_input_port(self._new_port)
            self._new_port.node.insert_named_input(self._index, self._new_port)
        else:
            self._new_port = self._node.create_named_input(
                self._name)
            self._index = self._new_port.index

    def undo(self):
        self._node.delete_input(self._new_port)

    def created_element(self):
        return self._new_port


class CreateNamedOutputPortCommand(UndoCommandBase,
                                   CreateElementCommandInterface):
    def __init__(self, node, name, parent=None):
        super(CreateNamedOutputPortCommand, self).__init__(parent)
        self._node = node
        self._name = name
        self._flow = node.flow
        self._new_port = None
        self.setText('Creating node port')

    def redo(self):
        if self._new_port:
            self._flow.add_output_port(self._new_port)
            self._new_port.node.insert_named_output(
                self._index, self._new_port)
        else:
            self._new_port = self._node.create_named_output(
                self._name)
            self._index = self._new_port.index

    def undo(self):
        self._node.delete_output(self._new_port)

    def created_element(self):
        return self._new_port


class DeleteInputPortCommand(DuplicateInputPortCommand):
    def __init__(self, port, parent=None):
        super(DeleteInputPortCommand, self).__init__(port, parent)
        self._new_port = port
        self._node = port.node
        self._index = port.index
        self._element_list = self._flow.connected_port_connections(
            [self._port])
        self.setText('Deleting node port')

    def redo(self):
        for element in self._element_list:
            element.remove()
        super(DeleteInputPortCommand, self).undo()

    def undo(self):
        self._flow.add_input_port(self._port)
        self._node.insert_named_input(self._index,
                                      self._port)
        for element in reversed(self._element_list):
            element.add(self._flow)


class DeleteOutputPortCommand(DuplicateOutputPortCommand):
    def __init__(self, port, parent=None):
        super(DeleteOutputPortCommand, self).__init__(port, parent)
        self._new_port = port
        self._node = port.node
        self._index = port.index
        self._element_list = self._flow.connected_port_connections(
            [self._port])
        self.setText('Deleting node port')

    def redo(self):
        for element in self._element_list:
            element.remove()
        super(DeleteOutputPortCommand, self).undo()

    def undo(self):
        self._flow.add_output_port(self._port)
        self._node.insert_named_output(self._index,
                                       self._port)
        for element in reversed(self._element_list):
            element.add(self._flow)


class DeleteParentPortCommand(UndoCommandBase,
                              CreateElementCommandInterface):
    def __init__(self, flowio, port, parent=None):
        self._flowio = flowio
        super(DeleteParentPortCommand, self).__init__(
            flow=port.node, parent=parent)
        self._port = port
        self._index = self._port.index
        self._element_list = self._flow.flow.connected_port_connections(
            [self._port])

    def redo(self):
        for element in self._element_list:
            element.remove()
        self._flowio.delete_parent_port()
        self._flow.arm(self._port)

    def undo(self):
        self._add_port(self._port)
        self._flowio.add_parent_port(self._port)
        self._insert_port(self._index,
                          self._port)
        for element in reversed(self._element_list):
            element.add(self._flow.flow)
        self._flow.arm()


class DeleteParentInputPortCommand(DeleteParentPortCommand):
    def __init__(self, port, parent=None):
        flowio = port.mirror_port.node
        super(DeleteParentInputPortCommand, self).__init__(
            flowio, port, parent)
        self.setText('Deleting input port')
        self._add_port = self._flow.flow.add_input_port
        self._insert_port = self._flow.insert_input


class DeleteParentOutputPortCommand(DeleteParentPortCommand):
    def __init__(self, port, parent=None):
        flowio = port.mirror_port.node
        super(DeleteParentOutputPortCommand, self).__init__(
            flowio, port, parent)
        self.setText('Deleting output port')
        self._add_port = self._flow.flow.add_output_port
        self._insert_port = self._flow.insert_output


class CreateParentInputPortCommand(UndoCommandBase,
                                   CreateElementCommandInterface):
    def __init__(self, flowio, parent=None):
        super(CreateParentInputPortCommand, self).__init__(parent)
        self._flowio = flowio
        self._flow = flowio.flow
        self._port = None
        self._index = None
        self.setText('Creating input port')

    def redo(self):
        if self._port is None:
            inputs = [
                input_ for input_ in self._flow._flow_inputs
                if (input_.parent_port in self._flow.inputs or
                    input_ == self._flowio)]

            index = inputs.index(self._flowio)
            self._flowio.create_parent_port(pos=index)
            self._port = self._flowio.parent_port
            self._index = index
        else:
            self._flow.flow.add_input_port(self._port)
            self._flowio.add_parent_port(self._port)
            self._flow.insert_input(self._index,
                                    self._port)
        self._flow.disarm()

    def undo(self):
        self._flowio.delete_parent_port()
        self._flow.arm()


class CreateParentOutputPortCommand(UndoCommandBase,
                                    CreateElementCommandInterface):
    def __init__(self, flowio, parent=None):
        super(CreateParentOutputPortCommand, self).__init__(parent)
        self._flowio = flowio
        self._flow = flowio.flow
        self._port = None
        self._index = None
        self.setText('Creating output port')

    def redo(self):
        if self._port is None:
            outputs = [
                output_ for output_ in self._flow._flow_outputs
                if (output_.parent_port in self._flow.outputs or
                    output_ == self._flowio)]

            index = outputs.index(self._flowio)
            self._flowio.create_parent_port(pos=index)
            self._port = self._flowio.parent_port
            self._index = index
        else:
            self._flow.flow.add_output_port(self._port)
            self._flowio.add_parent_port(self._port)
            self._flow.insert_output(self._index,
                                     self._port)
        self._flow.disarm()

    def undo(self):
        self._flowio.delete_parent_port()
        self._flow.arm()


class CreateSubflowCommand(UndoCommandBase, CreateElementCommandInterface):
    def __init__(self, cls=None, **kwargs):
        super(CreateSubflowCommand, self).__init__(**kwargs)
        self._subflow = None
        self._factory = _flow_factory(cls) if cls else Gui.flow.Flow
        self.setText('Creating subflow')
        self._kwargs = kwargs

    def redo(self):
        # Think about create vs activate and release!
        if self._subflow is not None:
            self._subflow.add(self._flow)
        else:
            self._subflow = self._flow.create_function(
                self._factory, **self._kwargs)

    def undo(self):
        self._subflow.remove()

    def element_uuid(self):
        return self._subflow.uuid

    def created_element(self):
        return self._subflow


class CreateFunction(UndoCommandBase, CreateElementCommandInterface):
    def __init__(self, factory, **kwargs):
        super(CreateFunction, self).__init__(**kwargs)
        self._factory = factory
        self._kwargs = kwargs
        self._subflow = None
        self.setText('Creating function')

    def redo(self):
        # Think about create vs activate and release!
        if self._subflow is not None:
            self._subflow.add(self._flow)
        else:
            self._subflow = self._flow.create_function(
                self._factory, **self._kwargs)

    def undo(self):
        self._subflow.remove()

    def element_uuid(self):
        return self._subflow.uuid

    def created_element(self):
        return self._subflow


class CreateLambdaCommand(CreateFunction):
    def __init__(self, **kwargs):
        super(CreateLambdaCommand, self).__init__(Gui.flow.Lambda, **kwargs)
        self.setText('Creating lambda')


class CreateSubflowFromSelectionCommand(UndoCommandBase,
                                        CreateElementCommandInterface):

    def __init__(self, position, elements, flow_, parent=None):
        super(CreateSubflowFromSelectionCommand, self).__init__(parent)
        self._flow = flow_
        self._position = position
        self._elements = elements
        self._subflow = None
        self._external_connections = None
        self.setText('Creating subflow from selection')

    def redo(self):
        if self._subflow is None:
            # Create stuff and store it as members
            self._subflow = self._flow.create_subflow(self._position)
            fixed_position = (self._position - QtCore.QPointF(
                self._subflow.size.width() / 2.0,
                self._subflow.size.height() / 2.0))
            self._subflow.position = fixed_position
            self._incoming, self._outgoing = (
                self._flow.external_connections_from_elements(self._elements))

            # Add/remove/move stuff storing subflow/parent connections
            for clist in itertools.chain(
                    self._incoming.values(), self._outgoing.values()):
                for c in clist:
                    c.remove(emit=False)
            self._flow.move_elements_to_flow(self._elements, self._subflow)
            self._subflow_connections, self._parent_connections = (
                self._flow.create_external_subflow_connections(
                    self._subflow, self._incoming, self._outgoing))
        else:
            # Add/remove/move stuff
            self._subflow.add(self._flow)
            for clist in itertools.chain(self._incoming.values(),
                                         self._outgoing.values()):
                for c in clist:
                    c.remove(emit=False)
            self._flow.move_elements_to_flow(
                self._elements, self._subflow)

            for c in self._subflow_connections:
                c.add(self._subflow, emit=False)
            for c in self._parent_connections:
                c.add(self._flow, emit=False)

    def undo(self):
        # Add/remove/move stuff in reverse order
        for c in itertools.chain(self._subflow_connections,
                                 self._parent_connections):
            c.remove(emit=False)
        self._subflow.move_elements_to_flow(self._elements, self._flow)
        for clist in itertools.chain(
                self._incoming.values(), self._outgoing.values()):
            for c in clist:
                c.add(self._flow, emit=False)
        self._subflow.remove()

    def element_uuid(self):
        return self._subflow.uuid

    def created_element(self):
        return self._subflow


class UnlinkSubflowCommand(UndoCommandBase,
                           CreateElementCommandInterface):
    """
    Unlink subflow.
    Implemented by trying to follow the same steps as you would when using the
    GUI:

    1. Create a new subflow.
    2. Edit the old subflow and copy everything.
    3. Paste into the new subflow.
    4. Redraw connections to the new subflow.
    5. Remove the old subflow.

    The clipboard is actually not used, instead the data is copied by
    serializing and deserializing which makes it pretty close.
    """
    def __init__(self, subflow, **kwargs):
        super(UnlinkSubflowCommand, self).__init__(flow=subflow.flow, **kwargs)
        self._linked_subflow = subflow
        self._unlinked_subflow = None
        self._linked_connections = []
        self._unlinked_connections = []

        self.setText('Unlinking subflow')

    def created_element(self):
        return self._unlinked_subflow

    def redo(self):
        if self._unlinked_subflow is None:
            create_subflow_cmd = CreateSubflowCommand(
                position=self._linked_subflow.position, flow=self._flow,
                uuid=uuid_generator.generate_uuid())
            create_subflow_cmd.redo()

            subflow = create_subflow_cmd.created_element()
            element_list = list(itertools.chain(
                (e for e in self._linked_subflow.elements()
                 if e.type not in Gui.flow.Type.port_types),
                self._linked_subflow.shallow_text_fields()))

            flow_dict = copy.deepcopy(Gui.flow_serialization.partial_dict(
                self._linked_subflow, element_list))
            deserializer = Gui.flow_serialization.FlowDeserializer.from_dict(
                flow_dict,
                self._flow.app_core)

            try:
                self._flow.app_core.set_validate_enabled(False)
                deserializer.build_paste_flow(subflow, center=False)
            finally:
                self._flow.app_core.set_validate_enabled(True)

            subflow.set_flow_info(self._linked_subflow.get_flow_info())
            subflow.name = self._linked_subflow.name

            if self._linked_subflow.aggregation_settings:
                aggregation_settings = {}
                conf_view = self._linked_subflow.aggregation_settings.get(
                    'conf_view')
                if conf_view is not None:
                    aggregation_settings['conf_view'] = conf_view
                old_nodes = self._linked_subflow.shallow_nodes()
                new_nodes = subflow.shallow_nodes()
                old_selected_uuids = set(
                    self._linked_subflow.aggregation_settings.get(
                        'selected_uuids', []))
                # Copying of selected uuids relies on the exact same ordering
                # of nodes and subflows.
                if len(old_nodes) != len(new_nodes):
                    core_logger.critical(
                        'Cannot set selected nodes for aggregation.')
                elif old_selected_uuids:
                    new_selected_uuids = aggregation_settings.setdefault(
                        'selected_uuids', [])
                    for old_node, new_node in zip(old_nodes, new_nodes):
                        old_uuid = old_node.uuid
                        if old_uuid in old_selected_uuids:
                            new_selected_uuids.append(new_node.uuid)
                subflow.aggregation_settings = aggregation_settings

            self._unlinked_subflow = subflow

            incoming, outgoing = self._flow.external_connections_from_elements(
                [self._linked_subflow])

            incoming = incoming.get(self._linked_subflow, [])
            outgoing = outgoing.get(self._linked_subflow, [])

            self._linked_connections = list(
                itertools.chain(incoming, outgoing))

            for connection in incoming:
                new_connection = self._flow.create_connection(
                    connection.source,
                    self._unlinked_subflow.input(connection.destination.index))
                self._unlinked_connections.append(new_connection)

            for connection in outgoing:
                new_connection = self._flow.create_connection(
                    self._unlinked_subflow.output(connection.source.index),
                    connection.destination)
                self._unlinked_connections.append(new_connection)

            for connection in self._linked_connections:
                connection.remove()

            self._linked_subflow.remove()
            subflow.validate()
        else:
            for connection in self._linked_connections:
                connection.remove()
            self._linked_subflow.remove()

            self._unlinked_subflow.add(self._flow)
            for connection in self._unlinked_connections:
                connection.add(self._flow)

    def undo(self):

        for connection in self._unlinked_connections:
            connection.remove()
        self._unlinked_subflow.remove()

        self._linked_subflow.add(self._flow)
        for connection in self._linked_connections:
            connection.add(self._flow)


class InsertSubflowLinkCommand(UndoCommandBase,
                               CreateElementCommandInterface):
    def __init__(self, position=None, library_node=None,
                 filename=None, uuid=None, **kwargs):
        super(InsertSubflowLinkCommand, self).__init__(**kwargs)
        self.setText('Inserting subflow as link')
        self._library_node = library_node

        def flow_filenames(flow_):
            """Filename of flow and its parent flows."""

            while flow_:
                filename = flow_.filename
                if filename:
                    yield filename
                flow_ = flow_.flow

        def contains_same_filename(filename, filenames):
            """
            Returns True if any element of filenames refers to the
            same file as filename and False otherwise.
            """
            for flow_filename in filenames:
                if vs.samefile(filename, flow_filename):
                    return True
            return False

        def flow_dict_filenames(flow_dict):
            """
            Return all flow filenames from flow dictionary.
            """
            def inner(flow_dict):
                filename = flow_dict.get('filename')
                if filename:
                    yield filename
                for child_flow_dict in flow_dict.get('flows', []):
                    for filename in inner(child_flow_dict):
                        yield filename

            res = list(inner(flow_dict))
            return res

        self._valid = False
        source_uri = None
        flow_filename = self._flow.root_or_linked_flow_filename

        if library_node:
            source_uri = uri_to_path(library_node.source_uri)
            filename = source_uri
        else:
            source_uri = filename

        if source_uri:
            if flow_filename:
                try:
                    source_uri = os.path.relpath(
                        filename, os.path.dirname(flow_filename))
                except ValueError:
                    # Path can't be made relative. Perhaps this flow and
                    # subflow are on different drives. Fall back to absolute
                    # path.
                    pass

            deserializer = Gui.flow_serialization.FlowDeserializer(
                self._flow.app_core)
            deserializer.load_xml_file(filename)
            if not deserializer.is_valid():
                core_logger.critical('Failed to load {}'.format(filename))

            loaded_flow_filenames = [filename] + flow_dict_filenames(
                deserializer.to_dict())
            flow_parent_filenames = flow_filenames(self._flow)

            # Ensure that insertion does not cause self referencing loops.
            # Exit early, without inserting, in such cases.
            for filename_ in loaded_flow_filenames:
                if contains_same_filename(
                        filename_, flow_parent_filenames):
                    core_logger.critical(
                        'Failed to insert "{}", because it would link to '
                        '"{}", its own parent.'
                        .format(filename, filename_))
                    return

            loaded_flow_filenames = [filename] + flow_dict_filenames(
                deserializer.to_dict())
            flow_parent_filenames = flow_filenames(self._flow)

            # Ensure that insertion does not cause self referencing loops.
            # Exit early, without inserting, in such cases.
            for filename_ in loaded_flow_filenames:
                if contains_same_filename(
                        filename_, flow_parent_filenames):
                    core_logger.critical(
                        'Failed to insert "{}", because it would link to '
                        '"{}", its own parent.'
                        .format(filename, filename_))
                    return

            self.create_subflow_cmd = CreateSubflowCommand(
                position=position, flow=self._flow,
                uuid=uuid_generator.generate_uuid(),
                library_node=library_node)

            self._deserializer = deserializer
            self._filename = source_uri
            flow_dict = deserializer.to_dict()
            self._source_uuid = flow_dict['uuid']
            self._source_label = flow_dict['label']
            self._valid = True
            self.flow_dict = flow_dict

    def redo(self):
        first_time = self.created_element() is None
        self.create_subflow_cmd.redo()
        if first_time:
            new_flow = self.created_element()
            new_flow.filename = os.path.normpath(os.path.join(
                os.path.dirname(new_flow.flow.root_or_linked_flow_filename),
                self._filename))
            self._flow.app_core.set_validate_enabled(False)
            try:
                self._deserializer.build_flow(new_flow, is_linked=True)
            finally:
                self._flow.app_core.set_validate_enabled(True)

            new_flow.source_uuid = self._source_uuid
            for port in itertools.chain(new_flow.inputs, new_flow.outputs):
                port.uuid = uuid_generator.generate_uuid()
            new_flow.set_linked(True)
            new_flow.source_uri = self._filename
            new_flow.source_label = self._source_label
            new_flow.library_node = self._library_node
            new_flow.name = ''
            new_flow.validate()

    def undo(self):
        self.create_subflow_cmd.undo()

    def element_uuid(self):
        return self.created_element().uuid

    def created_element(self):
        return self.create_subflow_cmd.created_element()

    def flow(self):
        return self.create_subflow_cmd.flow()


class CreateFlowInputCommand(UndoCommandBase,
                             CreateElementCommandInterface):
    def __init__(self, flow=None, port_definition_tuple=None,
                 parent=None, **kwargs):
        super(CreateFlowInputCommand, self).__init__(parent)
        self._kwargs = kwargs
        if port_definition_tuple is not None:
            self._port_definition = library.PortDefinition(
                *port_definition_tuple)
        else:
            self._port_definition = None
        self._flow = flow
        self._flow_input = None
        self.setText('Creating flow input')

    def redo(self):
        # Think about create vs activate and release!
        if self._flow_input is not None:
            self._flow_input.add(self._flow)
        else:
            self._flow_input = self._flow.create_flow_input(
                port_definition=self._port_definition, **self._kwargs)

    def undo(self):
        self._flow_input.remove()

    def element_uuid(self):
        return self._flow_input.uuid

    def created_element(self):
        return self._flow_input


class CreateFlowOutputCommand(UndoCommandBase,
                              CreateElementCommandInterface):

    def __init__(self, flow=None, port_definition_tuple=None,
                 parent=None, **kwargs):
        super(CreateFlowOutputCommand, self).__init__(parent)
        self._kwargs = kwargs
        if port_definition_tuple is not None:
            self._port_definition = library.PortDefinition(
                *port_definition_tuple)
        else:
            self._port_definition = None
        self._flow = flow
        self._flow_output = None
        self.setText('Creating flow output')

    def redo(self):
        # Think about create vs activate and release!
        if self._flow_output is not None:
            self._flow_output.add(self._flow)
        else:
            self._flow_output = self._flow.create_flow_output(
                port_definition=self._port_definition,
                **self._kwargs)

    def undo(self):
        if self._flow_output:
            self._flow_output.remove()

    def element_uuid(self):
        return self._flow_output.uuid

    def created_element(self):
        return self._flow_output


class ChangeFlowIOOrderInterface(UndoCommandBase):
    def __init__(self, flow_, new_order, parent=None):
        super(ChangeFlowIOOrderInterface, self).__init__(parent)
        self.setText("Changing port order")
        self._flow = flow_
        self._to_new_order = tuple(new_order)
        # Calculate the order for the reverse port ordering operation:
        # E.g. if new_order = [2,0,1,3,4], the order for the reverse operation
        # is [1,2,0,3,4]. In other words, when moving index 2 to position 0 the
        # reverse is to move index 0 to position 2.
        self._to_old_order = list(zip(*sorted(
            zip(new_order, range(len(new_order))))))[1]

    def redo(self):
        raise NotImplementedError('Not implemented for interface')

    def undo(self):
        raise NotImplementedError('Not implemented for interface')


class ChangeFlowInputOrderCommand(ChangeFlowIOOrderInterface):
    def redo(self):
        self._flow.reorder_inputs(self._to_new_order)

    def undo(self):
        self._flow.reorder_inputs(self._to_old_order)


class ChangeFlowOutputOrderCommand(ChangeFlowIOOrderInterface):
    def redo(self):
        self._flow.reorder_outputs(self._to_new_order)

    def undo(self):
        self._flow.reorder_outputs(self._to_old_order)


class CreateConnectionCommand(UndoCommandBase,
                              CreateElementCommandInterface):

    def __init__(self, source_port, destination_port, flow_, uuid=None,
                 parent=None, route_points=None):
        super(CreateConnectionCommand, self).__init__(parent)
        self._flow = flow_
        self._uuid = uuid
        self._source_port = source_port
        self._destination_port = destination_port
        self._connection = None
        self._route_points = route_points
        self.setText('Creating connection')

    def redo(self):
        # Think about create vs activate and release!
        if self._connection is not None:
            self._connection.add(self._flow)
        else:
            self._connection = self._flow.create_connection(
                self._source_port, self._destination_port,
                uuid=self._uuid,
                route_points=self._route_points)

    def undo(self):
        self._connection.remove()

    def element_uuid(self):
        return self._connection.uuid

    def created_element(self):
        return self._connection


class CreateTextFieldCommand(UndoCommandBase,
                             CreateElementCommandInterface):

    def __init__(self, rectangle, flow_, uuid=None, parent=None):
        super(CreateTextFieldCommand, self).__init__(parent)
        self._rectangle = rectangle
        self._flow = flow_
        self._uuid = uuid
        self._text_field = None
        self.setText('Creating text field')

    def redo(self):
        # Think about create vs activate and release!
        if self._text_field is not None:
            self._text_field.add(self._flow)
        else:
            self._text_field = self._flow.create_text_field(
                self._rectangle, self._uuid)

    def undo(self):
        self._text_field.remove()

    def element_uuid(self):
        return self._text_field.uuid

    def created_element(self):
        return self._text_field


class PasteElementListCommand(UndoCommandBase):
    """docstring for PasteElementListCommand"""

    def __init__(self, flow_, encoded_mime_data, mouse_anchor, app_core,
                 parent=None):
        super(PasteElementListCommand, self).__init__(parent)
        flow_dict = json.loads(encoded_mime_data)
        ports = flow_dict.get('flow', []).get('ports', {})

        if not flow_.can_create_flow_input():
            ports.pop('inputs')

        if not flow_.can_create_flow_output():
            ports.pop('outputs')

        self._deserializer = Gui.flow_serialization.FlowDeserializer.from_dict(
            flow_dict,
            app_core)

        self._flow = flow_
        self._mouse_anchor = mouse_anchor
        self.setText('Pasting')
        self._top_level_created_elements = []
        self._top_level_created_connections = []
        self._element_list = []
        self._first_run = True

    def created_top_level_elements(self):
        return self._top_level_created_elements

    def redo(self):
        if self._first_run:
            try:
                self._flow.app_core.set_validate_enabled(False)
                self._deserializer.build_paste_flow(
                    self._flow, self._mouse_anchor)
            finally:
                self._flow.app_core.set_validate_enabled(True)

            self._top_level_created_elements = [
                cmd.created_element()
                for cmd in self._deserializer.created_nodes()
                if cmd.created_element().flow is self._flow]

            for node in self._top_level_created_elements:
                if node.type in {Gui.flow.Type.Node, Gui.flow.Type.Flow}:
                    node.validate()

            top_level_connections = [
                cmd.created_element()
                for cmd in itertools.chain(
                        self._deserializer.created_connections())
                if cmd.created_element().flow is self._flow]

            self._element_list = (self._top_level_created_elements +
                                  top_level_connections)
            self._top_level_created_elements.extend(
                [r for c in top_level_connections for r in c.route_points])
            self._first_run = False
        else:
            for element in self._element_list:
                element.add(self._flow)

    def undo(self):
        for element in reversed(self._element_list):
            element.remove()


class RemoveElementCommand(UndoCommandBase):
    def __init__(self, element, flow_, parent=None):
        super(RemoveElementCommand, self).__init__(parent)
        self._element = element
        self._flow = flow_
        self.setText('Removing item')
        self._remove = False

    def redo(self):
        self._remove = self._element.is_deletable()
        if self._remove:
            self._element.remove()

    def undo(self):
        if self._remove:
            self._element.add(self._flow)


class RemoveElementListCommand(UndoCommandBase):
    def __init__(self, element_list, flow_, parent=None):
        super(RemoveElementListCommand, self).__init__(parent)
        self._flow = flow_
        self._connections = Gui.flow.Type.filter_connections(element_list)
        self._element_list = [
            e for e in element_list if e not in self._connections]
        # First connections, then everything else
        self.setText('Removing {} elements'.format(len(element_list)))

        self._remove_command_list = []
        self._first_run = True

    def redo(self):
        if self._first_run:
            element_set = set()
            for element in (
                    self._connections +
                    self._flow.connected_connections(self._element_list,
                                                     search_parent_flow=True) +
                    self._element_list):

                if element not in element_set:
                    element_set.add(element)
                    cmd = RemoveElementCommand(element, self._flow, self)
                    self._remove_command_list.append(cmd)

            self._first_run = False

        for cmd in self._remove_command_list:
            cmd.redo()

    def undo(self):
        for cmd in reversed(self._remove_command_list):
            cmd.undo()


class CutElementListCommand(UndoCommandBase):
    def __init__(self, flow_, element_list, mouse_anchor, parent=None):
        super(CutElementListCommand, self).__init__(parent)
        self._flow = flow_
        self._connections = Gui.flow.Type.filter_connections(element_list)
        self._element_list = element_list
        self._data = None
        self._remove_command_list = []
        copy_element_list_to_clipboard(flow_, element_list)
        self.setText('Cutting {} items'.format(len(element_list)))
        self._first_run = True
        self._remove_command_list = []

    def redo(self):

        if self._first_run:
            element_set = set()
            for element in (
                    self._connections +
                    self._flow.connected_connections(self._element_list,
                                                     search_parent_flow=True) +
                    self._element_list):
                if element not in element_set:
                    element_set.add(element)
                    cmd = RemoveElementCommand(element, self._flow, self)
                    self._remove_command_list.append(cmd)
            self._first_run = False

        for cmd in self._remove_command_list:
            cmd.redo()

    def undo(self):
        for cmd in reversed(self._remove_command_list):
            cmd.undo()


class MoveElementCommand(UndoCommandBase):
    def __init__(self, element, old_position, new_position, parent=None):
        super(MoveElementCommand, self).__init__(parent)
        self._flow = element.flow
        self._element = element
        self._old_position = old_position
        self._new_position = new_position
        self.setText('Moving element')

    def redo(self):
        self._element.position = self._new_position

    def undo(self):
        self._element.position = self._old_position


class ResizeElementCommand(UndoCommandBase):
    def __init__(self, element, old_rect, new_rect, parent=None):
        super(ResizeElementCommand, self).__init__(parent)
        self._flow = element.flow
        self._element = element
        self._old_rect = old_rect
        self._new_rect = new_rect
        self.setText('Resizing element')

    def redo(self):
        self._element.position = self._new_rect.topLeft()
        self._element.size = self._new_rect.size()

    def undo(self):
        self._element.position = self._old_rect.topLeft()
        self._element.size = self._old_rect.size()


class EditNodeLabelCommand(UndoCommandBase):
    def __init__(self, element, old_label, new_label, parent=None):
        super(EditNodeLabelCommand, self).__init__(parent)
        self._flow = element.flow
        self._element = element
        self._old_label = old_label
        self._new_label = new_label
        if not new_label:
            self.setText('Clearing node label')
        else:
            self.setText('Changing node label to {}'.format(new_label))

    def redo(self):
        self._element.name = self._new_label

    def undo(self):
        self._element.name = self._old_label


class EditTextFieldCommand(UndoCommandBase):
    def __init__(self, element, old_text, new_text, parent=None):
        super(EditTextFieldCommand, self).__init__(parent)
        self._flow = element.flow
        self._element = element
        self._old_text = old_text
        self._new_text = new_text
        self.setText('Editing text field')

    def redo(self):
        self._element.set_text(self._new_text)

    def undo(self):
        self._element.set_text(self._old_text)


class EditTextFieldColorCommand(UndoCommandBase):
    def __init__(self, element, old_color, new_color, parent=None):
        super(EditTextFieldColorCommand, self).__init__(parent)
        self._flow = element.flow
        self._element = element
        self._old_color = old_color
        self._new_color = new_color
        self.setText('Changing text field color')

    def redo(self):
        self._element.set_color(self._new_color)

    def undo(self):
        self._element.set_color(self._old_color)


class TextFieldOrderCommand(UndoCommandBase):
    def __init__(self, flow, current_model, direction, parent=None):
        super(TextFieldOrderCommand, self).__init__(parent)
        self._flow = flow
        self._current_model = current_model
        self._direction = direction
        self._old_models = self._flow._text_fields[:]
        self.setText('Changing text field order')

    def redo(self):
        self._flow.change_text_field_order(
            self._current_model, self._direction)

    def undo(self):
        self._flow.set_text_field_order(self._old_models)


class ExpandSubflowCommand(UndoCommandBase):
    def __init__(self, subflow, parent=None):
        super(ExpandSubflowCommand, self).__init__(parent)
        self._subflow = subflow
        self._flow = subflow.flow
        self.setText('Expanding subflow {}'.format(subflow.display_name))

        self._first_run = True
        self._elements = None
        self._subflow_connections = None
        self._parent_connections = None
        self._flat_connections = None

        self._unlink_cmd = None

    def redo(self):
        subflow = self._subflow
        if self._first_run:
            if self._subflow.is_linked:
                self._unlink_cmd = UnlinkSubflowCommand(self._subflow)
                self._unlink_cmd.redo()

                subflow = self._unlink_cmd.created_element()

            self._elements = [
                e for e in subflow.elements()
                if e.type in Gui.flow.Type.main_types - {
                        Gui.flow.Type.FlowInput,
                        Gui.flow.Type.FlowOutput}]

            for e in self._elements:
                e.was_in_subflow = True

            for c in subflow.connections():
                for p in c.route_points:
                    p.was_in_subflow = True
            self._first_run = False
        else:
            if self._subflow.is_linked:
                self._unlink_cmd.redo()
                subflow = self._unlink_cmd.created_element()

        if self._subflow_connections is None:
            self._subflow_connections, self._parent_connections = (
                self._flow.external_connections_from_subflow(subflow))
            self._flat_connections = (
                self._flow.external_connections_convert_to_flat(
                    subflow, self._subflow_connections,
                    self._parent_connections))

        emit = self._subflow.is_linked

        # Add/remove/move stuff in reverse order
        for c in self._subflow_connections + self._parent_connections:
            c.remove(emit=emit)
        subflow.move_elements_to_flow(self._elements, self._flow)
        for c in self._flat_connections:
            c.add(self._flow, emit=emit)
        subflow.remove()

    def undo(self):
        # Add/remove/move stuff
        subflow = self._subflow
        if self._subflow.is_linked:
            subflow = self._unlink_cmd.created_element()

        subflow.add(self._flow)
        for c in self._flat_connections:
            c.remove(emit=False)
        self._flow.move_elements_to_flow(self._elements, subflow)

        for c in self._subflow_connections:
            c.add(subflow, emit=False)
        for c in self._parent_connections:
            c.add(self._flow, emit=False)

        if self._subflow.is_linked:
            self._unlink_cmd.undo()


class EditNodeParameters(UndoCommandBase):
    def __init__(self, node, new_params_model, parent=None):
        super(EditNodeParameters, self).__init__(parent)
        self._flow = node.flow
        self._old_params = node.parameter_model
        self._new_params = new_params_model
        self._node = node
        self._version = self._node.version
        self.setText('Editing parameters for node {}'.format(node.name))

    def redo(self):
        self._node.parameter_model = self._new_params
        self._node.version = self._node.library_node.version
        self._node.validate()

    def undo(self):
        self._node.parameter_model = self._old_params
        self._node.version = self._version
        self._node.validate()


class EditWorkflowEnvironment(UndoCommandBase):
    def __init__(self, flow_, new_env, old_env, parent=None):
        super(EditWorkflowEnvironment, self).__init__(parent)
        self.setText("Edit environment variables for workflow {}".format(
            flow_.display_name))
        self._flow = flow_
        self._new_env = new_env
        self._old_env = old_env

    def redo(self):
        self._flow.environment = self._new_env

    def undo(self):
        self._flow.environment = self._old_env


class EditNodeExecutionConfig(UndoCommandBase):
    def __init__(self, node, value, parent=None):
        super(EditNodeExecutionConfig, self).__init__(parent)
        self.setText(
            'Editing execution config for node {}'.format(node.name))
        self._node = node
        self._flow = node.flow
        self._old_value = self._node.exec_conf_only
        self._new_value = value

    def redo(self):
        self._node.exec_conf_only = self._new_value

    def undo(self):
        self._node.exec_conf_only = self._new_value


class DeleteOverrideParametersForUUID(UndoCommandBase):
    """
    Intended to be used when the node associated with a certain uuid can't be
    found.
    """

    def __init__(self, subflow, uuid, parent=None):
        super(DeleteOverrideParametersForUUID, self).__init__(parent)
        self._subflow = subflow
        self._flow = subflow.flow
        self._old_overrides = subflow.override_parameters[uuid]
        self._uuid = uuid
        self.setText(
            'Removing override parameters for uuid {}'.format(uuid))

    def redo(self):
        # Node doesn't exist so it should be enough to modify the subflows
        # override parameters directly.
        self._subflow.override_parameters.pop(self._uuid, None)

    def undo(self):
        # Node doesn't exist so it should be enough to modify the subflows
        # override parameters directly.
        self._subflow.override_parameters[self._uuid] = self._old_overrides


class EditNodeOverrideParameters(UndoCommandBase):
    def __init__(self, subflow, node, new_params_model, parent=None):
        super(EditNodeOverrideParameters, self).__init__(parent)
        self._subflow = subflow
        self._flow = subflow.flow
        self._old_overrides = node.get_override_parameter_model(subflow)
        self._new_overrides = new_params_model
        self._node = node
        self.setText(
            'Editing override parameters for node {}'.format(node.name))

    def redo(self):
        self._subflow.set_node_override_parameters(
            self._node, self._new_overrides)
        self._node.validate()

    def undo(self):
        self._subflow.set_node_override_parameters(
            self._node, self._old_overrides)
        self._node.validate()


class CreateRoutePoint(UndoCommandBase):
    def __init__(self, flow_, conn, pos, src_pos, dst_pos, parent=None):
        super(CreateRoutePoint, self).__init__(parent)
        self._flow = flow_
        self._conn = conn
        self._pos = pos
        self._src_pos = src_pos
        self._dst_pos = dst_pos

        self._first_run = True
        self._route_point = None
        self.setText('Adding connection route point')

    def redo(self):
        if self._first_run:
            self._route_point = self._conn.create_route_point(
                self._pos, self._src_pos, self._dst_pos)
            self._first_run = False
        else:
            self._route_point.add()

    def undo(self):
        self._route_point.remove()


class EditSubflowLockStateCommand(UndoCommandBase):
    def __init__(self, subflow, new_locked_state, parent=None):
        super(EditSubflowLockStateCommand, self).__init__(parent)
        self._flow = subflow
        self._new_state = new_locked_state
        self._old_state = subflow.is_locked()
        if new_locked_state:
            self.setText('Locking subflow {}'.format(subflow.display_name))
        else:
            self.setText('Unlocking subflow {}'.format(subflow.display_name))

    def redo(self):
        self._flow.set_locked(self._new_state)

    def undo(self):
        self._flow.set_locked(self._old_state)


class EditSubflowSettingsCommand(UndoCommandBase):
    def __init__(self, top_flow, flow_info_dict, parent=None):
        """
        Constructor is called from appcore::execute_subflow_parameter_view_done
        """
        super(EditSubflowSettingsCommand, self).__init__(parent)
        self._flow_info_dict = flow_info_dict
        self._top_flow = top_flow
        self._new_aggregation_settings = json.loads(flow_info_dict[
            'json_aggregation_settings'])
        self._subflow = self._find_subflow(self._flow_info_dict['uuid'])
        self._old_aggregation_settings = self._subflow.aggregation_settings
        self.setText('Editing settings for flow {}'.format(
            self._subflow.display_name))

    def _find_subflow(self, full_uuid):
        _, flow_uuid = uuid_generator.split_uuid(full_uuid)
        all_flows = self._top_flow.all_subflows() + [self._top_flow]
        for flw in all_flows:
            if flw.uuid == flow_uuid:
                return flw
        return None

    def _set_aggregation_settings(self, settings):
        full_uuid = self._flow_info_dict['uuid']
        subflow = self._find_subflow(full_uuid)
        if subflow is not None:
            core_logger.info('Setting aggregation settings for {}'.format(
                full_uuid))
            subflow.aggregation_settings = settings

    def aggregation_settings_are_equal(self):
        return self._new_aggregation_settings == self._old_aggregation_settings

    def redo(self):
        self._set_aggregation_settings(self._new_aggregation_settings)

    def undo(self):
        self._set_aggregation_settings(self._old_aggregation_settings)

    def flow(self):
        return self._top_flow


class LinkSubflowCommand(UndoCommandBase):
    def __init__(self, subflow, filename, parent=None):
        super(LinkSubflowCommand, self).__init__(parent)
        self.setText('Linking subflow to file {}'.format(filename))
        self._flow = subflow.flow
        self._subflow = subflow
        self._old_is_linked = subflow.is_linked
        self._old_file_undo_stack = subflow.file_undo_stack()
        self._new_file_undo_stack = QtGui.QUndoStack(parent=subflow)
        self._library_node = self._subflow.library_node

        parent_flow_path = os.path.dirname(
            subflow.flow.root_or_linked_flow_filename)
        try:
            subflow_relative_path = os.path.relpath(filename,
                                                    parent_flow_path)
        except ValueError:
            # Path can't be made relative. Perhaps this flow and parent are on
            # different drives. Fall back to absolute path.
            subflow_relative_path = filename

        self._old_source = subflow.source_uri
        self._new_source = subflow_relative_path
        self._old_source_uuid = subflow.source_uuid
        self._new_source_uuid = uuid_generator.generate_uuid()
        self._old_in, self._new_in = self._make_uuids(
            subflow.inputs)
        self._old_out, self._new_out = self._make_uuids(
            subflow.outputs)
        self._old_filename = subflow.filename
        self._new_filename = filename

    def _make_uuids(self, ports):
        old = []
        new = []
        for port in ports:
            old.append(port.uuid)
            new.append(uuid_generator.generate_uuid())
        return old, new

    def _set_uuids(self, ports, uuids):
        for port, uuid in zip(ports, uuids):
            port.uuid = uuid

    def redo(self):
        self._subflow.set_file_undo_stack(self._new_file_undo_stack)
        self._subflow.set_linked(True)
        self._subflow.source_uri = self._new_source
        self._subflow.source_uuid = self._new_source_uuid
        self._subflow.filename = self._new_filename
        self._set_uuids(self._subflow.inputs, self._new_in)
        self._set_uuids(self._subflow.outputs, self._new_out)
        self._subflow.library_node = None

    def undo(self):
        self._subflow.set_file_undo_stack(self._old_file_undo_stack)
        self._subflow.set_linked(self._old_is_linked)
        self._subflow.filename = self._old_filename
        self._subflow.source_uri = self._old_source
        self._subflow.source_uuid = self._old_source_uuid
        self._set_uuids(self._subflow.inputs, self._old_in)
        self._set_uuids(self._subflow.outputs, self._old_out)
        self._subflow.library_node = self._library_node


class SetFlowInfo(UndoCommandBase):
    def __init__(self, flow, new_flow_info, parent=None):
        super(SetFlowInfo, self).__init__(parent)
        self.setText('Changing flow info')
        self._flow = flow
        self._new_flow_info = new_flow_info
        self._old_flow_info = flow.get_flow_info()

    def redo(self):
        self._flow.set_flow_info(self._new_flow_info)

    def undo(self):
        self._flow.set_flow_info(self._old_flow_info)


class SetFlowLibraries(UndoCommandBase):
    def __init__(self, flow, new_libraries, new_pythonpaths, parent=None):
        super(SetFlowLibraries, self).__init__(parent)
        self.setText('Changing flow libraries')
        self._flow = flow
        self._new_libraries = new_libraries
        self._old_libraries = flow.library_paths()
        self._new_pythonpaths = new_pythonpaths
        self._old_pythonpaths = flow.python_paths()

    def redo(self):
        self._flow.set_libraries_and_pythonpaths(
            libraries=self._new_libraries, pythonpaths=self._new_pythonpaths)

    def undo(self):
        self._flow.set_libraries_and_pythonpaths(
            libraries=self._old_libraries, pythonpaths=self._old_pythonpaths)
