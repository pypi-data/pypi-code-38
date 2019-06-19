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
from __future__ import print_function

import json
import os.path
import logging

import six
import PySide.QtCore as QtCore

from sympathy.platform import workflow_converter, node_result
from sympathy.platform.exceptions import ReadSyxFileError
from sympathy.utils import uuid_generator
from sympathy.utils.prim import uri_to_path

from . import library
from . import version
from . flow.types import Type
from . flow.exceptions import SyInferTypeError
from . flow import flowlib
import Gui.user_commands

core_logger = logging.getLogger('core')


def partial_dict(flow, element_list):
    def in_port_uuid(port, uuids):
        return (
            uuid_generator.join_uuid(
                port['namespace_uuid'],
                port['uuid']) in uuids or
            uuid_generator.join_uuid(
                port['namespace_uuid'],
                port['source_uuid']) in uuids)

    positions = [(e.position.x(), e.position.y())
                 for e in element_list]
    x_max = max([p[0] for p in positions])
    x_min = min([p[0] for p in positions])
    y_max = max([p[1] for p in positions])
    y_min = min([p[1] for p in positions])

    # Create a serialization (suitable for copying) of the entire flow
    flow_dict = flow.to_copy_dict(base_node_params=False)
    element_uuids = []
    for e in element_list:
        if e.type == Type.Flow:
            element_uuids.append(e.full_link_uuid)
        else:
            if e.type in [Type.FlowInput, Type.FlowOutput]:
                element_uuids.append(e.port.full_uuid)
                if e.is_linked:
                    element_uuids.append(
                        uuid_generator.join_uuid(
                            e.namespace_uuid(), e.source_uuid))

            element_uuids.append(e.full_uuid)

    # Remove parts of the serialization that were not selected or can't be
    # copied (such as connections)
    flow_dict['nodes'] = [
        node for node in flow_dict['nodes']
        if node['full_uuid'] in element_uuids]
    flow_dict['flows'] = [
        node for node in flow_dict['flows']
        if node['full_uuid'] in element_uuids]
    flow_dict['textfields'] = [
        node for node in flow_dict['textfields']
        if node['full_uuid'] in element_uuids]
    flow_dict['connections'] = [
        connection for connection in flow_dict['connections']
        if (uuid_generator.join_uuid(
            connection['namespace_uuid'],
            connection['source']['node']) in element_uuids and
            uuid_generator.join_uuid(
                connection['namespace_uuid'],
                connection['destination']['node']) in element_uuids)]
    flow_dict['ports'] = {
        'inputs': [ip for ip in flow_dict['ports'].get('inputs', [])
                   if in_port_uuid(ip, element_uuids)],

        'outputs': [op for op in flow_dict['ports'].get('outputs', [])
                    if in_port_uuid(op, element_uuids)]}
    return {
        'flow': flow_dict,
        'center': {
            'x': x_min + (x_max - x_min) / 2.0,
            'y': y_min + (y_max - y_min) / 2.0}}


def update_uuids_in_group(group, uuid_to_new_uuid, new_uuids):
    """
    Recursively traverse the 'group_structure' part of an aggregation settings
    dictionary and update all uuids.

    :param group: Dictionary with the group_structure part of the aggregation
    settings for a subflow.
    :param uuid_to_new_uuid: Dictionary mapping old node uuids to new uuids.
    Group uuids will be added to this dictionary.
    :param new_uuids: If True, generate new uuids for groups.
    """
    if group['type'] == 'group':
        if group['uuid']:
            # Group uuids are not in uuid_to_new_uuid
            if new_uuids:
                uuid_to_new_uuid[group['uuid']] = (
                    uuid_generator.generate_uuid())
            else:
                uuid_to_new_uuid[group['uuid']] = group['uuid']
            group['uuid'] = uuid_to_new_uuid[group['uuid']]
        for g in group['children']:
            update_uuids_in_group(g, uuid_to_new_uuid, new_uuids)
    elif group['type'] == 'node':
        # All node uuids should be in uuid_to_new_uuid
        if group['uuid'] in uuid_to_new_uuid:
            group['uuid'] = uuid_to_new_uuid[group['uuid']]


class FlowDeserializer(object):

    def __init__(self, app_core):
        super(FlowDeserializer, self).__init__()
        self._app_core = app_core
        self._dictionary = {}
        self._xml_file = ''
        self._valid_file = True
        self._created_nodes = []
        self._created_connections = []
        self._init()

    def load_xml_file(self, xml_file):
        if not os.path.isfile(xml_file):
            raise ReadSyxFileError(
                u"File doesn't exist.",
                u"File {} doesn't exist.".format(xml_file))
        with open(xml_file, 'r') as source:
            converter = workflow_converter.XMLToJson(source)
            self._dictionary = converter.dict()

    def load_xml_data(self, xml_data):
        pass

    def load_json_data(self, json_data):
        self._dictionary = json.loads(json_data)

    @classmethod
    def from_dict(cls, dictionary, app_core):
        instance = cls(app_core)
        instance._dictionary = dictionary
        return instance

    @classmethod
    def from_json(cls, json_data, app_core):
        instance = cls(app_core)
        instance.load_json_data(json_data)
        return instance

    def is_valid(self):
        return self._valid_file

    def to_dict(self):
        return self._dictionary

    def created_nodes(self):
        return self._created_nodes

    def created_connections(self):
        return self._created_connections

    def build_flow(self, flow, is_linked=False):

        def inform_duplicate_identifiers(dup_probs):
            nr = node_result.NodeResult()
            nr.stderr = (
                'Duplicate element identifiers in flow:'
                '\n'
                'The flow contains duplicate elements identifiers and may '
                'not be fully recovered. '
                '\n\n'
                'BASIC:'
                '\n'
                'Remove nodes that have lost their connections '
                'or in other ways behave strangely '
                'and add them again redrawing the intended connections. '
                'Afterwards, save the flow.'
                '\n\n'
                'ADVANCED:'
                '\n'
                'Check the duplicate identifiers in the flow file.'
                '\n\n'
                'Duplicate identifiers of type(s): {}.'
                '\n\n'
                'Duplicate identifier(s): {}.'
            ).format(', '.join(dup_probs),
                     ', '.join(ident for v in dup_probs.values()
                               for ident in v))
            self._app_core.node_output(flow.full_uuid, nr)

        def inform_lost_connections(conn_probs):
            nr = node_result.NodeResult()
            nr.stderr = (
                'Unable to create some flow connections: '
                'This could be the result of removed ports '
                'or changed port types.\n'
                '\n'
                'Be careful when changing types of ports that are '
                'in use on nodes or flows that are linked.'
                '\n\n'
                'Update affected workflows where connections are missing, '
                'and redraw the lost connections.'
                '\n\n'
                'Lost Connections: {}.'.format(', '.join(
                    "{} -> {}".format(*conn_prob)
                    for conn_prob in conn_probs)))

            self._app_core.node_output(flow.full_uuid, nr)

        def inform_infer_lost_connections(conn_probs):
            nr = node_result.NodeResult()
            nr.stderr = (
                'Unable to infer type for some flow connections: '
                'This could be the result of removed ports '
                'or changed port types. '
                'The ports that lost connections may not be the ones '
                'that introduced the problem. This should not happen '
                'For flows saved in Sympathy version >= 1.3.1.'
                '\n'
                'Be careful when changing types of ports that are '
                'in use on nodes or flows that are linked.'
                '\n\n'
                'Update affected workflows and save them again.'
                '\n\n'
                'Lost Connections: {}.'.format(', '.join(
                    "{} -> {}".format(*conn_prob)
                    for conn_prob in conn_probs)))

            self._app_core.node_output(flow.full_uuid, nr)

        def inform_lost_overrides(override_probs):
            nr = node_result.NodeResult()
            nr.stderr = (
                'Unable to restore some overrides: '
                'This could be the result of a bug. '
                'Please make a bug report to support@sympathyfordata.com. '
                '\n\n'
                'Lost overrides for node uuid: {}.'.format(', '.join(
                    override_probs)))

            self._app_core.node_output(flow.full_uuid, nr)

        probs = {}
        with flowlib.delayed_infertype_ctx() as ctx:
            result = self._build_flow(
                flow, self._dictionary, is_linked=is_linked, probs=probs)

            flowlib.infertype_flow(flow)
            if ctx.errors:
                for src, dst in ctx.removed:
                    core_logger.warn(
                        "Couldn't infer type for connection between "
                        "nodes %s and %s", src, dst)

                    probs.setdefault('connection_infer_type', []).append((
                        src, dst))

        if probs:
            override_probs = probs.pop('overrides_exception', None)
            conn_probs = probs.pop('connection_type', None)
            infer_conn_probs = probs.pop(
                'connection_infer_type', None)

            if override_probs:
                inform_lost_overrides(override_probs)

            if conn_probs:
                inform_lost_connections(conn_probs)

            if infer_conn_probs:
                inform_infer_lost_connections(infer_conn_probs)

            if probs:
                inform_duplicate_identifiers(probs)

        return result

    def build_paste_flow(self, flow, anchor=QtCore.QPointF(0, 0), center=True):
        if center:
            center = QtCore.QPointF(self._dictionary['center']['x'],
                                    self._dictionary['center']['y'])
        else:
            center = QtCore.QPointF(0, 0)

        with flowlib.delayed_infertype_ctx():
            result = self._build_flow(
                flow, self._dictionary['flow'], anchor - center,
                update_flow=False, create_copy=True)

            flowlib.infertype_flow(flow)
        return result

    def check_min_version(self, flow):
        """"""
        min_version = flow.get_flow_info().get('min_version', '')
        if not min_version:
            return

        min_parts = [p or 0 for p in min_version.split('.')]
        while len(min_parts) < 3:
            min_parts.append(0)
        min_tuple = tuple(map(int, min_parts))
        if min_tuple > version.version_tuple[:3]:
            min_version = '.'.join(map(six.text_type, min_tuple))
            result = node_result.NodeResult()
            result.stderr = (
                "Flow '{}' requires Sympathy version {}".format(
                    flow.display_name, min_version))
            self._app_core.node_output(flow.full_uuid, result)

    def _init(self):
        pass

    def _build_flow(self, flow, dictionary, anchor=QtCore.QPointF(0, 0),
                    update_flow=True, create_copy=False, is_linked=False,
                    parent_is_linked=False, unique_uuids=None, probs=None):
        """
        Add elements to a flow object from a dictionary representation.

        Parameters
        ----------
        flow : sympathy flow
            Parent flow.
        dictionary : dict
            Dictionary describing the flow elements to be added.
        anchor : QtCore.QPointF
            Origin position where the elements will be added. In scene
            coordinates.
        update_flow : bool
            If True, also modify the parent flow using the flow meta
            data in the dictionary.
        create_copy : bool
            If True, give most elements new uuids. Defaults to False.
        is_linked : bool
            Should be True when flow is linked. If True, don't elements new
            uuids. External ports in linked subflows will still get new uuids
            depending on the value of parent_is_linked. Defaults to False.
        parent_is_linked : bool
            If False, give external ports in linked subflows new
            uuids. Defaults to False.

        Returns
        -------
        tuple of two dictionaries
            The first dictionary contains a map from old uuids to new ones, the
            second dictionary is a map from new uuids to actual objects.
        """
        class StringKeyDict(dict):
            def __setitem__(self, key, value):
                if not isinstance(key, six.string_types):
                    core_logger.warn(
                        "Trying to add key with type %s: (%s, %s)", type(key),
                        key, value)
                super(StringKeyDict, self).__setitem__(key, value)

        def update_port_uuids(dict_, instance, uuid_to_class,
                              uuid_to_new_uuid, kind):
            if kind == 'input':
                port_from_index = instance.input
                maxlen = len(instance.inputs)
                ports = 'inputs'
            elif kind == 'output':
                port_from_index = instance.output
                maxlen = len(instance.outputs)
                ports = 'outputs'

            for index, port in enumerate(dict_.get(ports, [])):
                if index >= maxlen:
                    break
                p = port_from_index(index)

                if create_copy and not is_linked and not parent_is_linked:
                    uuid = uuid_generator.generate_uuid()
                else:
                    uuid = port['uuid']
                    if uuid in unique_uuids:
                        core_logger.warn(
                            'Duplicate %s port: %s', kind, uuid)
                        probs.setdefault('port', []).append(uuid)
                unique_uuids.add(uuid)

                p.uuid = uuid
                uuid_to_class[p.uuid] = p
                uuid_to_new_uuid[port['uuid']] = p.uuid

        def valid_connection_ports(source, dest, conntype):
            if source and dest:
                if conntype is None:
                    return True
                else:
                    conntype = dest.datatype.from_str(conntype)
                    return (conntype.match(source.datatype) and
                            conntype.match(dest.datatype))
            return False

        if probs is None:
            probs = {}

        if is_linked:
            unique_uuids = set()
        else:
            unique_uuids = set() if unique_uuids is None else unique_uuids

        tag = dictionary.get('tag')
        flow.identifier = dictionary.get('id')
        flow.tag = tag

        update_uuids = create_copy and not is_linked and not parent_is_linked

        uuid_to_class = StringKeyDict()
        uuid_to_new_uuid = StringKeyDict()
        broken = dictionary.get('broken_link', False)
        if update_flow:
            label = dictionary.get('label', '')
            if label:
                flow.name = label

            # flow.set_flow_info ignores any keys that it isn't interested in.
            flow.set_flow_info(dictionary)
            self.check_min_version(flow)

            if 'source' in dictionary:
                flow.source_uri = dictionary['source']
            if 'filename' in dictionary:
                flow.filename = dictionary['filename']
            flow.set_linked(dictionary.get('is_linked', False))
            flow.set_locked(dictionary.get('is_locked', False))
            flow.icon_filename = dictionary.get('icon')

            flow.set_broken_link(broken)
            if broken:
                if not dictionary.get('id'):
                    self._app_core.create_node_result(
                        flow.full_uuid,
                        error="Can't open subflow file '{}'".format(
                            dictionary.get('source', '')))

            # We expect the flow parameters to be a dict such as
            # {'data': {...}, 'type': 'json'}, but let's not be too picky.
            parameters = dictionary.get('parameters', {})
            if 'data' in parameters:
                parameters = parameters['data']
                # Earlier versions of sympathy would create "recursive"
                # parameter dictionaries (i.e.
                # {type: json, environment: {}, data: {
                #     type: json, environment: {}, data: {...}}}).
                # Let's try to fix that by dropping any "data" and "type" keys.
                for bad_key in ["data", "type"]:
                    parameters.pop(bad_key, None)
            environment = dictionary.get('environment', {})
            if environment:
                parameters['environment'] = environment
            flow.parameters = parameters

            flow.set_libraries_and_pythonpaths(
                libraries=dictionary.get('libraries', []),
                pythonpaths=dictionary.get('pythonpaths', []))
            flow.aggregation_settings = dictionary.get(
                'aggregation_settings', {})
            flow.source_uuid = dictionary.get('source_uuid')
            flow.source_label = dictionary.get('source_label')

        if ('source_uuid' in dictionary and
                dictionary['source_uuid'] is not None):
            uuid_to_new_uuid[dictionary['source_uuid']] = flow.uuid
            uuid_to_class[dictionary['source_uuid']] = flow
        uuid_to_new_uuid[dictionary['uuid']] = flow.uuid
        uuid_to_class[flow.uuid] = flow

        for node in dictionary['nodes']:
            pos = QtCore.QPointF(node['x'], node['y']) + anchor
            parameters = library.ParameterModel.from_dict(node['parameters'])

            if update_uuids:
                uuid = uuid_generator.generate_uuid()
            else:
                uuid = node['uuid']
                if uuid in unique_uuids:
                    new_uuid = uuid_generator.generate_uuid()
                    core_logger.warn(
                        'Duplicate node: {}, replaced with: {}'.format(
                            uuid, new_uuid))
                    probs.setdefault('node', []).append(uuid)
                    uuid = new_uuid
            unique_uuids.add(uuid)

            library_node = None
            root = flow.root_or_linked_flow()
            libraries = [os.path.normcase(l)
                         for l in Gui.util.library_paths(root)]

            if not self._app_core.is_node_in_library(node['id'], libraries):
                node['type'] = 'node'
                library_node = self._app_core.library_node_from_definition(
                    node['id'], node)

            cmd = Gui.user_commands.CreateNodeCommand(
                node_id=node['id'], position=pos,
                uuid=uuid, flow=flow, ports=node.get('ports', {}),
                port_format=node.get('port_format'), library_node=library_node,
                only_conf=node.get('only_conf'), version=node.get('version'),
                name=node.get('label'))
            cmd.redo()
            uuid_to_new_uuid[node['uuid']] = cmd.element_uuid()
            node_instance = cmd.created_element()
            uuid_to_class[cmd.element_uuid()] = node_instance
            if not parameters.is_empty():
                node_instance.parameter_model = parameters
            self._created_nodes.append(cmd)

            update_port_uuids(node.get('ports', {}), node_instance,
                              uuid_to_class, uuid_to_new_uuid, 'input')

            update_port_uuids(node.get('ports', {}), node_instance,
                              uuid_to_class, uuid_to_new_uuid, 'output')

        for subflow in dictionary['flows']:
            pos = QtCore.QPointF(subflow['x'], subflow['y']) + anchor
            if update_uuids:
                uuid = uuid_generator.generate_uuid()
            else:
                uuid = subflow['uuid']
                if uuid in unique_uuids:
                    core_logger.warn('Duplicate flows: {}'.format(uuid))
                    probs.setdefault('flow', []).append(uuid)
            unique_uuids.add(uuid)
            cls = subflow.get('cls', 'Flow')

            subflow_is_linked = subflow.get('is_linked', False)

            root = flow.root_or_linked_flow()
            libraries = [os.path.normcase(l)
                         for l in Gui.util.library_paths(root)]

            content_dict = subflow
            library_node_id = subflow.get('node_id')
            node_id = subflow.get('id')
            library_node = None

            if library_node_id or (node_id and not subflow.get('source')):
                subflow_is_linked = True
                node_id = library_node_id or node_id
                if self._app_core.is_node_in_library(
                        node_id, libraries):
                    library_node = self._app_core.library_node(node_id)
                    deserializer = FlowDeserializer(self._app_core)
                    subflow_filename = uri_to_path(library_node.source_uri)
                    deserializer.load_xml_file(subflow_filename)
                    content_dict = deserializer.to_dict()
                    content_dict['source_label'] = content_dict['label']
                    content_dict['label'] = subflow['label']

                    workflow_converter.update_link_uuids(
                        subflow, content_dict)

                    content_dict['filename'] = subflow_filename
                    content_dict['source'] = subflow_filename
                    content_dict['overrides'] = subflow.get('overrides', {})
                else:
                    content_dict['broken_link'] = True
                content_dict['is_linked'] = True

            cmd = Gui.user_commands.CreateSubflowCommand(
                position=pos, flow=flow, uuid=uuid, library_node=library_node,
                cls=cls)
            cmd.redo()
            self._created_nodes.append(cmd)
            uuid_to_new_uuid[subflow['uuid']] = cmd.element_uuid()
            uuid_to_class[cmd.element_uuid()] = cmd.created_element()

            uuid_to_new_uuid_, uuid_to_class_ = self._build_flow(
                cmd.created_element(), content_dict,
                create_copy=create_copy,
                parent_is_linked=(parent_is_linked or is_linked),
                is_linked=subflow_is_linked, unique_uuids=unique_uuids,
                probs=probs)

            uuid_to_new_uuid.update(uuid_to_new_uuid_)
            uuid_to_class.update(uuid_to_class_)

        # Subflow basic inputs and outputs
        inputs = dictionary.get('basic_ports', {'inputs': []})
        outputs = dictionary.get('basic_ports', {'outputs': []})
        update_port_uuids(inputs, flow, uuid_to_class,
                          uuid_to_new_uuid, 'input')
        update_port_uuids(outputs, flow, uuid_to_class,
                          uuid_to_new_uuid, 'output')

        # Subflow inputs and outputs
        inputs = dictionary.get('ports', {}).get('inputs', [])
        outputs = dictionary.get('ports', {}).get('outputs', [])

        new_input_order = []
        new_output_order = []
        for port in inputs + outputs:
            pos = QtCore.QPointF(port['x'], port['y']) + anchor

            old_parent_port_uuid = port['uuid']
            old_uuid = port.get('source_uuid', old_parent_port_uuid)
            if update_uuids:
                uuid = uuid_generator.generate_uuid()
            else:
                uuid = old_uuid
                if uuid in unique_uuids:
                    core_logger.warn('Duplicate flow port: {}'.format(uuid))
                    probs.setdefault('flow port', []).append(uuid)
            unique_uuids.add(uuid)

            if old_uuid == old_parent_port_uuid:
                parent_port_uuid = uuid
            elif update_uuids or (create_copy and is_linked and
                                  not parent_is_linked):
                # Also update uuids for parent port if we are copying stuff and
                # this is a link and no parent or ancestor flow is linked.
                parent_port_uuid = uuid_generator.generate_uuid()
            else:
                parent_port_uuid = old_parent_port_uuid
                if (parent_port_uuid in unique_uuids and
                        parent_port_uuid != uuid):
                    core_logger.warn(
                        'Duplicate flow port: {}'.format(parent_port_uuid))
                    probs.setdefault('node', []).append(parent_port_uuid)
            unique_uuids.add(parent_port_uuid)

            if port in inputs:
                cmdclass = Gui.user_commands.CreateFlowInputCommand
            else:
                cmdclass = Gui.user_commands.CreateFlowOutputCommand
            if broken:
                port_definition_tuple = (
                    port['name'], port['description'], port['type'],
                    port['scheme'], port['index'])
            else:
                port_definition_tuple = None

            create_parent_port = port.get('parent')

            cmd = cmdclass(position=pos, flow=flow, uuid=uuid,
                           port_definition_tuple=port_definition_tuple,
                           create_parent_port=create_parent_port,
                           parent_port_uuid=parent_port_uuid)
            cmd.redo()
            self._created_nodes.append(cmd)
            uuid_to_new_uuid[old_uuid] = uuid
            uuid_to_class[uuid] = cmd.created_element()

            # If parent port and port had different uuids, we need to add both
            # to uuid_to_new_uuid and uuid_to_class to be able to recreate
            # connections.
            if old_parent_port_uuid != old_uuid:
                uuid_to_new_uuid[old_parent_port_uuid] = parent_port_uuid
                uuid_to_class[parent_port_uuid] = (
                    cmd.created_element().parent_port)

            if 'description' in port:
                cmd.created_element().name = port['description']
            if port in inputs:
                new_input_order.append(port.get('index', len(new_input_order)))
            if port in outputs:
                new_output_order.append(
                    port.get('index', len(new_output_order)))

        if (new_input_order != sorted(new_input_order) or
                new_output_order != sorted(new_output_order)):
            core_logger.warn("Incorrect port order for flow %s", flow)

        for text_field in dictionary.get('textfields', []):
            rectangle = QtCore.QRectF(
                text_field['x'] + anchor.x(), text_field['y'] + anchor.y(),
                text_field['width'], text_field['height'])
            if update_uuids:
                uuid = uuid_generator.generate_uuid()
            else:
                uuid = text_field['uuid']
                if uuid in unique_uuids:
                    core_logger.warn(
                        'Duplicate text field: {}'.format(uuid))
                    probs.setdefault('text field', []).append(uuid)
                unique_uuids.add(uuid)

            cmd = Gui.user_commands.CreateTextFieldCommand(
                rectangle, flow, uuid)
            cmd.redo()
            self._created_nodes.append(cmd)
            cmd.created_element().set_text(text_field['text'])
            if 'color' in text_field:
                cmd.created_element().set_color(text_field['color'])

        # And finally connections
        for connection in dictionary['connections']:

            core_logger.debug('Connection from {} {}'.format(
                connection['source']['node'],
                connection['source']['port']))
            core_logger.debug('Connection to {} {}'.format(
                connection['destination']['node'],
                connection['destination']['port']))
            if not connection['source']['node'] in uuid_to_new_uuid:
                core_logger.warn("Unknown source node")
                continue
            if not connection['destination']['node'] in uuid_to_new_uuid:
                core_logger.warn("Unknown destination node")
                continue

            if update_uuids:
                uuid = uuid_generator.generate_uuid()
            else:
                uuid = connection['uuid']
                if uuid in unique_uuids:
                    core_logger.warn(
                        'Duplicate connection uuid: {}'.format(uuid))
                    probs.setdefault('connection', []).append(uuid)
            unique_uuids.add(uuid)

            source_node_uuid = uuid_to_new_uuid.get(
                connection['source']['node'], None)
            source_port_uuid = uuid_to_new_uuid.get(
                connection['source']['port'], None)
            destination_node_uuid = uuid_to_new_uuid.get(
                connection['destination']['node'], None)
            destination_port_uuid = uuid_to_new_uuid.get(
                connection['destination']['port'], None)
            source_port = destination_port = None

            if (source_node_uuid in uuid_to_class and
                    destination_node_uuid in uuid_to_class):
                if source_node_uuid == flow.uuid:
                    flow_input = flow.flow_input(source_port_uuid)
                    if flow_input:
                        source_port = flow_input.output
                else:
                    source_port = uuid_to_class[source_node_uuid].output(
                        source_port_uuid)

                if destination_node_uuid == flow.uuid:
                    flow_output = flow.flow_output(destination_port_uuid)
                    if flow_output:
                        destination_port = flow_output.input
                else:
                    destination_port = (
                        uuid_to_class[destination_node_uuid].input(
                            destination_port_uuid))

                if valid_connection_ports(source_port, destination_port,
                                          connection['type']):
                    route_points = [
                        QtCore.QPointF(r['x'], r['y']) + anchor
                        for r in connection.get('route', [])]

                    core_logger.debug(
                        "Creating connection between nodes %s (%s) "
                        "and %s (%s)", source_node_uuid, source_port,
                        destination_node_uuid, destination_port)
                    cmd = Gui.user_commands.CreateConnectionCommand(
                        source_port, destination_port, flow, uuid,
                        route_points=route_points)
                    try:
                        cmd.redo()
                        self._created_connections.append(cmd)
                    except SyInferTypeError:
                        core_logger.warn(
                            "Couldn't infer type for connection between "
                            "ports %s and %s.",
                            source_port,
                            destination_port)
                        probs.setdefault('connection_infer_type', []).append((
                            source_port,
                            destination_port))
                    except Exception:
                        core_logger.warn(
                            "Failed to build connection between %s -> %s",
                            source_node_uuid, destination_node_uuid)

                else:
                    probs.setdefault('connection_type', []).append((
                        source_port,
                        destination_port))

                    core_logger.warn("Couldn't create a connection between "
                                     "ports %s and %s",
                                     source_port,
                                     destination_port)
            else:
                core_logger.warn(
                    "Failed to build connection between %s -> %s",
                    source_node_uuid, destination_node_uuid)

        if update_flow:
            # Update uuids in aggregation settings skipping settings
            # for any nodes that are no longer in the workflow.
            if flow.aggregation_settings:
                settings = flow.aggregation_settings
                for key in ('uuid_selected', 'selected_uuids'):
                    if key in settings:
                        settings[key] = [
                            uuid_to_new_uuid[uuid_]
                            for uuid_ in settings[key]
                            if uuid_ in uuid_to_new_uuid]
                if 'group_structure' in settings:
                    update_uuids_in_group(
                        settings['group_structure'], uuid_to_new_uuid,
                        update_uuids)

            # Set override parameters now that all nodes have been created.
            overrides_dict = dictionary.get('overrides', {})
            for tree_uuid, overrides in overrides_dict.items():
                try:
                    uuid_parts = uuid_generator.split_uuid(tree_uuid)
                    flow_ = flow
                    for i, uuid_part in enumerate(uuid_parts):
                        shallow_flodes = {
                            n.uuid: n for n in flow_.shallow_nodes()}

                        if uuid_part in shallow_flodes:
                            flow_ = shallow_flodes[uuid_part]
                            last_part = i == len(uuid_parts) - 1
                            is_node = flow_.type == Type.Node

                            if last_part and is_node:
                                node = flow_  # This part is actually a node.
                                parameter_model = (
                                    library.ParameterModel.from_dict(
                                        {'data': overrides, 'type': 'json'}))
                                flow.set_node_override_parameters(
                                    node, parameter_model)
                            elif last_part or is_node:
                                # The last uuid part should always be a node,
                                # and all other parts should be
                                # flows. Otherwise, we discard these overrides.
                                break
                        else:
                            # This uuid_part doesn't exist in flow_. Discard
                            # these overrides.
                            break
                except Exception:
                    probs.setdefault('overrides_exception', []).append(
                        tree_uuid)

        return uuid_to_new_uuid, uuid_to_class

    def _debug_uuid_dicts(self, uuid_to_new_uuid, uuid_to_class):
        """
        Print uuid dictionaries to stdout in a readable format.

        This function is very useful for debugging the uuid substitutions.
        """
        from .common import RED

        def shorten(uuid):
            return uuid[:9] + uuid[-1]

        def no_color(s):
            return '  {}  '.format(s)

        def diff_colors_factory(*args):
            colors = [no_color]*len(args)
            for i, (a1, a2) in enumerate(zip(args[1:], args[:-1])):
                if a1 != a2:
                    colors[i:i+2] = [RED, RED]
            return colors

        for utnu_key, utnu_value in sorted(uuid_to_new_uuid.items()):
            if utnu_value in uuid_to_class:
                utc_value_uuid = uuid_to_class[utnu_value].uuid
                utc_value_name = uuid_to_class[utnu_value]
            else:
                utc_value_uuid = "N/A".ljust(10)
                utc_value_name = "N/A"
            c1, c2, c3 = diff_colors_factory(
                utnu_key, utnu_value, utc_value_uuid)
            print("{} -> {} -> {} ({})".format(
                c1(shorten(utnu_key)),
                c2(shorten(utnu_value)),
                c3(shorten(utc_value_uuid)),
                utc_value_name))
        print()

        utc_keys = set(uuid_to_class.keys()) - set(uuid_to_new_uuid.values())
        utnu_key = "N/A".ljust(10)
        for utc_key in utc_keys:
            utc_value = uuid_to_class[utc_key]
            c1, c2 = diff_colors_factory(
                utc_key, utc_value_uuid)
            print("{} -> {} -> {} ({})".format(
                no_color(shorten(utnu_key)),
                c1(shorten(utc_key)),
                c2(shorten(utc_value.uuid)),
                utc_value))
        print()
