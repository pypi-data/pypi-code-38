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

import json
import imp
import os
import sys
import collections
import functools
import uuid as uuidgen
import six

from sympathy.utils.prim import uri_to_path
from sympathy.types import (sylambda, sylist_set_read_through,
                            sylist_set_write_through)

from sympathy.platform.gennode import Node, BasicNode
from sympathy.platform.basicnode import ManualContextBuilder
from sympathy.platform import version_support as vs
from sympathy.platform import state
from sympathy.platform import message
from sympathy.platform import node_result
from sympathy.platform import exceptions


capture_output = vs.OS.environ.get('SY_NOCAPTURE') != '1'
SocketBundle = collections.namedtuple(
    'SocketBundle', ['socket', 'input_func', 'output_func'])


def _progress_output_func(org_func, n, ntot, child_full_uuid, locked_top_level,
                          msg):
    if isinstance(msg, message.ProgressMessage):
        if locked_top_level:
            msg = message.ChildNodeProgressMessage([child_full_uuid, msg.data])
        else:
            ntot_max = max(ntot, 1)
            msg = message.ProgressMessage((msg.data + 100.0 * n) / ntot_max)

    return org_func(msg)


def sub_progress_socket_bundle(socket_bundle, n, ntot, child_full_uuid=None,
                               locked_top_level=False):
    if socket_bundle is not None:
        return SocketBundle(
            socket_bundle.socket,
            None,
            functools.partial(
                _progress_output_func, socket_bundle.output_func, n, ntot,
                child_full_uuid, locked_top_level))


def set_write_through(data):
    try:
        # For sylists.
        sylist_set_write_through(data)
        return True
    except AssertionError:
        try:
            # For filelists.
            data.set_write_through()
            return True
        except Exception:
            pass
    return False


def set_read_through(data):
    try:
        sylist_set_read_through(data)
        return True
    except AssertionError:
        try:
            # For filelists.
            data.set_read_through()
            return True
        except Exception:
            pass
    return False


builtin = sys.modules[__name__]


class Lambda(Node):

    name = 'lambda'

    @staticmethod
    def set_from_flowdata(output, flow):
        full_uuid = flow['full_uuid']
        name = flow['name']
        nodes = flow['nodes']
        input_nodes = flow['input_nodes']
        output_nodes = flow['output_nodes']
        node_deps = flow['node_deps']
        input_ports = flow['input_ports']
        output_ports = flow['output_ports']
        bypass_ports = flow['bypass_ports']
        node_settings = flow['node_settings']

        output.set((sylambda.FlowDesc(
            full_uuid,
            name,
            nodes,
            input_nodes,
            output_nodes,
            node_deps,
            input_ports, output_ports, bypass_ports,
            node_settings), []))

    def execute(self, node_context):
        flow = json.loads(node_context.parameters['flow'].value)
        self.set_from_flowdata(node_context.output[0], flow)


def source_module(source_file):
    if source_file is None:
        return builtin
    else:
        return compile_file(source_file)


def compile_file(source_file):
    """Setup up stdout/stderr, compile a source_file."""
    local_file = uri_to_path(source_file)
    source_dir = vs.str_(os.path.dirname(local_file), vs.fs_encoding)
    modname = vs.str_(
        os.path.splitext(os.path.basename(local_file))[0], vs.fs_encoding)
    fo, filename, data = imp.find_module(modname, [source_dir])
    return imp.load_module(modname, fo, filename, data)


def capture_stdouterr(context, capture_output=True):
    """Capture stdout/stderr into string buffers."""
    if capture_output:
        stdout_file = six.StringIO()
        stderr_file = six.StringIO()
        context['stdout'] = sys.stdout
        context['stderr'] = sys.stderr
        sys.stdout = stdout_file
        sys.stderr = stderr_file
        # For logging to be captured.
        # stream_handler = logging.StreamHandler(stderr_file)
        # stream_handler.setLevel(logging.DEBUG)
        # root_logger.addHandler(stream_handler)

    vs.wrap_encode_std()


def restore_stdouterr(context, capture_output=True):
    """Restore stdout/stderr from the string buffer."""
    if capture_output:
        sys.stdout = context['stdout']
        sys.stderr = context['stderr']


def store_stdouterr(result, context, capture_output=True):
    def decode_if_str(text):
        if isinstance(text, six.binary_type):
            return text.decode(
                sys.getfilesystemencoding(), errors='replace')
        return text

    if capture_output:
        try:
            stdout_value = sys.stdout.getvalue()
        except UnicodeError:
            stdout_value = "Output lost due to encoding issues"
        result.stdout = decode_if_str(stdout_value)
        try:
            stderr_value = sys.stderr.getvalue()
        except UnicodeError:
            stderr_value = "Error messages lost due to encoding issues"
        result.stderr = decode_if_str(stderr_value)
    else:
        result.stdout = ''
        result.stderr = ''


class Flow(BasicNode):
    """
    Worker side node implementation for locked subflow.
    """
    name = 'Flow'

    def execute_basic(self, node_context):

        def writeback(outputs):
            def inner():
                for output in outputs:
                    output.close()

            return inner

        flowinfo = json.loads(
            node_context.definition['parameters']['data']['flow']['value'])

        outputs = []

        input_nodes = flowinfo['input_nodes']
        output_nodes = flowinfo['output_nodes']
        node_deps = flowinfo['node_deps']
        input_ports = flowinfo['input_ports']
        output_ports = flowinfo['output_ports']
        nodes = flowinfo['nodes']
        node_settings = flowinfo['node_settings']

        # Could be useful to provide better feedback on exception.
        # name = flowinfo['name']

        objects = node_context._objects
        own_objects = node_context._own_objects

        input_assign = []
        output_assign = []

        for port_fileobj, port_def in zip(
                node_context.input,
                node_context.definition['ports'].get('inputs', [])):

            if port_fileobj in own_objects:
                set_read_through(port_fileobj)

            input_assign.append(port_fileobj)
            objects[port_def['file']] = port_fileobj

        for port_fileobj, port_def in zip(
                node_context.output,
                node_context.definition['ports'].get('outputs', [])):

            if port_fileobj in own_objects:
                outputs.append(port_fileobj)

            output_assign.append(port_fileobj)
            objects[port_def['file']] = port_fileobj

        child_results = flow_execute(
            nodes, input_nodes, output_nodes, node_deps,
            input_ports,
            output_ports, [], {}, [], [], objects,
            writeback(outputs),
            node_settings, self.socket_bundle, locked_top_level=True)

        if child_results:
            state.node_state().result.child_results = child_results

            for _, child_result in child_results:
                if child_result.has_error():
                    raise exceptions.SyChildError()


class SerialNode(object):
    """Provides convenient access to a serialized node."""

    def __init__(self, node_data, typealiases, input_map, output_map,
                 socket_bundle, trans_map):
        (self.__source_file,
         self.__class_name,
         self.full_uuid,
         json_parameters) = node_data[1]
        self.__json_parameters = json.loads(json_parameters)
        self.translated_filename_map = trans_map

        for ports, portmap in [('inputs', input_map), ('outputs', output_map)]:
            if portmap:
                for port0 in self.__json_parameters['ports'][ports]:
                    port1 = portmap.get(port0['uuid'])
                    if port1:
                        self.port_update(port0, port1)

        self.__typealiases = typealiases
        self.__socket_bundle = socket_bundle
        self.__node_class = None
        self.__builder = None

    def port_update(self, port0, port1):
        fn0 = port0['file']
        fn1 = port1['file']
        if fn0:
            self.translated_filename_map[fn0] = fn1
        port0['type'] = port1['type']
        port0['file'] = fn1

    def _node_class(self):
        if not self.__node_class:
            context = {}
            context['sys'] = __import__('sys', context, context)

            mod = source_module(self.__source_file)
            self.__node_class = getattr(mod, self.__class_name)()
            self.__node_class.socket_bundle = self.__socket_bundle

        return self.__node_class

    def execute(self, inputs, outputs, is_output_node, objects):
        self.__builder = ManualContextBuilder(inputs, outputs, is_output_node,
                                              objects=objects)
        self._node_class()._sys_execute(self.__json_parameters,
                                        self.__typealiases, self.__builder)

    def __getattr__(self, key):
        self._node_class().__getattribute__(key)

    @property
    def inputs(self):
        return self.__builder.inputs

    @property
    def outputs(self):
        return self.__builder.outputs

    @property
    def input_fileobjs(self):
        return self.__builder.input_fileobjs

    @property
    def output_fileobjs(self):
        return self.__builder.output_fileobjs

    @property
    def input_files(self):
        return [port['file']
                for port in self.__json_parameters['ports']['inputs']]

    @property
    def output_files(self):
        return [port['file']
                for port in self.__json_parameters['ports']['outputs']]

    @property
    def label(self):
        try:
            return self.__json_parameters['label']
        except Exception:
            return 'Unknown label'


def flow_execute(nodes, input_nodes, output_nodes, node_deps,
                 input_ports, output_ports,
                 bypass_ports,
                 type_aliases, input_assign=None, output_assign=None,
                 objects=None, exit_func=None, node_settings=None,
                 socket_bundle=None, locked_top_level=False):

    def execute_node():
        if any(d in exec_failed or d in exec_blocked
               for deps in flip_deps[uuid] for d in deps):
            exec_blocked.add(uuid)

        else:
            try:
                node.execute(node_inputs, node_outputs, is_output_node,
                             dict(objects))
                child_result.valid = False
            except Exception:
                if not locked_top_level:
                    raise
                exec_failed.add(uuid)
                child_result.store_current_exception()
            else:
                exec_done.add(uuid)

            child_results.append((uuid, child_result))

    def release(node):
        pass

    def close(port):
        port.close()

    try:
        node_settings = state.node_state().attributes['node_settings']
    except KeyError:
        node_settings = {}

    exec_failed = set()
    exec_blocked = set()
    exec_done = set()
    child_results = []

    flip_deps = collections.defaultdict(lambda: [])
    for src, dst in node_deps:
        flip_deps[dst].append(src)

    state.node_state().attributes['node_settings'] = node_settings

    input_assign_map = {}

    for ports, assign in zip(input_ports, input_assign or []):
        for port in ports:
            input_assign_map[port] = assign

    output_assign_map = dict(zip(output_ports, output_assign or []))
    serial_nodes = collections.OrderedDict()

    if bypass_ports:
        bypass_port = int(bypass_ports[0])
        node_json = json.dumps(
            {'ports': {'inputs': [input_assign[bypass_port]],
                       'outputs': [output_assign[0]]},
             'parameters': {'data': {u'type': u'group'}, 'type': 'json'},
             'id': u'org.sysess.builtin.propagate'})
        node = [None, [None, 'Propagate', '{{{}}}'.format(uuidgen.uuid4()),
                       node_json]]
        nodes.append(node)

    ntot = len(nodes)
    translated_filename_map = {}

    for n, node in enumerate(nodes):
        child_full_uuid = node[1][2]
        serial_node = SerialNode(
            node, type_aliases, input_assign_map, output_assign_map,
            sub_progress_socket_bundle(socket_bundle, n, ntot, child_full_uuid,
                                       locked_top_level),
            translated_filename_map)
        serial_nodes[serial_node.full_uuid] = serial_node

    file_outputs = collections.OrderedDict()

    objects = {} if objects is None else objects

    for n, (uuid, node) in enumerate(serial_nodes.items()):
        node_inputs = collections.OrderedDict()
        node_outputs = collections.OrderedDict()

        for input_file in node.input_files:
            org_fn = input_file
            trans_fn = translated_filename_map.get(input_file)

            if trans_fn:
                input_file = trans_fn

            port = objects.get(input_file)

            if port is not None:
                node_inputs[org_fn] = port

        for output_file in node.output_files:
            port = objects.get(output_file)

            if port is not None:
                node_outputs[output_file] = port

        is_output_node = uuid in output_nodes
        child_result = node_result.NodeResult()

        if locked_top_level and capture_output:
            context = {}
            capture_stdouterr(context)
            try:
                execute_node()
            finally:
                store_stdouterr(child_result, context)
                restore_stdouterr(context)
        else:
            execute_node()

        if is_output_node:
            file_outputs.update(node.output_fileobjs)
        else:
            objects.update(node.outputs)

        release(node)
        if socket_bundle:

            if locked_top_level:
                socket_bundle.socket.write(
                    socket_bundle.output_func(
                        message.ChildNodeDoneMessage(
                            [node.full_uuid, child_result.to_dict()])))

                socket_bundle.socket.write(
                    socket_bundle.output_func(
                        message.ChildNodeProgressMessage(
                            [node.full_uuid, 100.0])))
            else:
                socket_bundle.socket.write(
                    socket_bundle.output_func(
                        message.ProgressMessage(100.0 * (n + 1) / ntot)))

            socket_bundle.socket.flush()

    if exit_func:
        exit_func()

    for file_output in reversed(file_outputs.values()):
        # Close file outputs to commit the data to disk.
        close(file_output)

    state.node_state().attributes['node_settings'] = node_settings
    return child_results


class Propagate(Node):
    """Propagate input to output."""

    author = 'Erik der Hagopian <erik.hagopian@combine.se>'
    copyright = '(C) 2017 Combine Control Systems AB'
    name = 'Propagate'
    description = 'Propagate input to output'
    nodeid = 'org.sysess.builtin.propagate'
    icon = 'empty.svg'
    version = '1.0'

    def execute(self, node_context):
        node_context.output[0].source(node_context.input[0])
