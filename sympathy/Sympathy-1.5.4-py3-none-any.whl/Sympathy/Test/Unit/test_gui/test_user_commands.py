# -*- coding:utf-8 -*-
# This file is part of Sympathy for Data.
# Copyright (c) 2013-2016 Combine Control Systems AB
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
import os
import sys
import json
import unittest
import logging

import PySide.QtCore as QtCore
import PySide.QtGui as QtGui

import Gui.task_manager2
import Gui.application
import Gui.common
import Gui.sy
import Gui.util
import launch
from Gui import user_commands
from Gui import flow_serialization
import Gui.graph
import Gui.version

REPEAT = 5

# Tests were previously using the now removed old example nodes.
# Here they are replaced with other nodes that have the same port types.
EXAMPLE_NODES = [
    'org.sysess.sympathy.examples.outputexample',
    'org.sysess.sympathy.data.table.table2adaf',
    'org.sysess.sympathy.data.adaf.interpolateadaf']


class UserCommandTestTraits(object):
    def vertex_count(self, flow_):
        """
        Count number of vertices.
        :return: Vertex count in graph.
        """
        return len(flow_._graph.vertices())

    def edge_count(self, flow_):
        """
        Count number of edges.
        :return: Edge count in graph.
        """
        return len(flow_._graph.edges())

    def dot(self, flow_):
        """
        dot-string for visualization of graph in GraphViz.
        :return: dot-language string.
        """
        return str(flow_._graph._g)

    def connection_count(self, flow_):
        """
        Count number of connections in flow.
        :param flow_: Current flow.
        :return: Number of connections in flow.
        """
        return len(flow_.connections())

    def node_count(self, flow_):
        """
        Count number of nodes in flow.
        :param flow_: Current flow.
        :return: Number of nodes in flow.
        """
        return len(flow_._nodes)

    def subflow_count(self, flow_):
        """
        Count number of sub-flows in flow.
        :param flow_: Current flow.
        :return: Number of sub-flows in flow.
        """
        return len(flow_._subflows)

    def flow_input_count(self, flow_):
        """
        Count number of flow inputs in flow.
        :param flow_: Current flow.
        :return: Number of flow inputs in flow.
        """
        return len(flow_._flow_inputs)

    def flow_output_count(self, flow_):
        """
        Count number of flow outputs in flow.
        :param flow_: Current flow.
        :return: Number of flow outputs in flow.
        """
        return len(flow_._flow_outputs)

    def text_field_count(self, flow_):
        """
        Count number of text fields in flow.
        :param flow_: Current flow.
        :return: Number of text fields in flow.
        """
        return len(flow_.shallow_text_fields())

    def vertex_expect(self, flow_, x, repeat=None):
        """
        Test that expected number of vertices is valid.
        :param flow_: Flow to test graph in.
        :param x: Expected number of vertices.
        :param repeat: Repeat number in undo/redo loop.
        """
        n = self.vertex_count(flow_)
        self.assertEqual(n, x,
                         'REPEAT {}: Expected {} vertices, got {}. Dot:\n{}'.
                         format(repeat, x, n, self.dot(flow_)))

    def edge_expect(self, flow_, x, repeat=None):
        """
        Test that expected number of edges is valid.
        :param flow_: Flow to test graph in.
        :param x: Expected number of edges.
        :param repeat: Repeat number in undo/redo loop.
        """
        n = self.edge_count(flow_)
        self.assertEqual(n, x,
                         'REPEAT {}: Expected {} edges, got {}. Dot:\n{}'.
                         format(repeat, x, n, self.dot(flow_)))

    def connection_expect(self, flow_, x, repeat=None):
        """
        Test that expected number of connections is valid.
        :param flow_: Flow to test.
        :param x: Expected number of connections.
        :param repeat: Repeat number in undo/redo loop.
        """
        n = self.connection_count(flow_)
        self.assertEqual(n, x,
                         'REPEAT {}: Expected {} connections, got {}.'.
                         format(repeat, x, n))

    def node_expect(self, flow_, x, repeat=None):
        """
        Test that expected number of node is valid.
        :param flow_: Flow to test.
        :param x: Expected number of nodes.
        :param repeat: Repeat number in undo/redo loop.
        """
        n = self.node_count(flow_)
        self.assertEqual(n, x,
                         'REPEAT {}: Expected {} nodes, got {}.'.
                         format(repeat, x, n))

    def subflow_expect(self, flow_, x, repeat=None):
        """
        Test that the expected number of sub-flows is valid.
        :param flow_: Flow to test.
        :param x: Expected number of sub-flows.
        :param repeat: Undo/redo repeat count.
        """
        n = self.subflow_count(flow_)
        self.assertEqual(n, x,
                         'REPEAT {}: Expected {} subflows, got {}.'.
                         format(repeat, x, n))

    def flow_input_expect(self, flow_, x, repeat=None):
        """
        Test that the expected number of flow inputs is valid.
        :param flow_: Flow to test.
        :param x: Expected number of flow inputs.
        :param repeat: Undo/redo repeat count.
        """
        n = self.flow_input_count(flow_)
        self.assertEqual(n, x,
                         'REPEAT {}: Expected {} nodes, got {}.'.
                         format(repeat, x, n))

    def flow_output_expect(self, flow_, x, repeat=None):
        """
        Test that the expected number of flow outputs is valid.
        :param flow_: Flow to test.
        :param x: Expected number of flow outputs.
        :param repeat: Undo/redo repeat count.
        """
        n = self.flow_output_count(flow_)
        self.assertEqual(n, x,
                         'REPEAT {}: Expected {} nodes, got {}.'.
                         format(repeat, x, n))

    def text_field_expect(self, flow_, x, repeat=None):
        """
        Test that the expected number of text fields is valid.
        :param flow_: Flow to test.
        :param x: Expected number of text fields.
        :param repeat: Undo/redo repeat count.
        """
        n = self.text_field_count(flow_)
        self.assertEqual(n, x,
                         'REPEAT {}: Expected {} nodes, got {}.'.
                         format(repeat, x, n))


class TestUserCommands(unittest.TestCase, UserCommandTestTraits):

    @classmethod
    def setUpClass(cls):
        environ = os.environ
        environ['PYTHONPATH'] = os.path.pathsep.join(
            [environ.get('PYTHONPATH', ''),
             launch.sy_application_dir, launch.sy_python_support])

        cls.popen, port = Gui.task_manager2.start_external(
            'Gui.task_worker_subprocess:worker', 1,
            dict(os.environ), False)

        cls.app = QtGui.QApplication.instance()
        if cls.app is None:
            cls.app = QtGui.QApplication(sys.argv)

        cls.app.setApplicationName(Gui.version.application_name())
        cls.app.setApplicationVersion(Gui.version.version)

        environ['SY_TASK_MANAGER_PORT'] = str(port)
        cls.app_core, cls.exe_core = Gui.application.common_setup(cls.app)
        cls.app_core.reload_node_library()
        cls.app.processEvents()

    @classmethod
    def tearDownClass(cls):
        Gui.application.common_teardown(cls.app_core)
        cls.popen.terminate()
        cls.popen = None

    def setUp(self):
        Gui.graph.global_vertex_id = 0
        Gui.graph.global_edge_id = 0
        self.undo_stack = QtGui.QUndoStack(TestUserCommands.app_core)

    def tearDown(self):
        pass

    def _load_flow(self, filename):
        fq_filename = os.path.join(
            os.path.dirname(__file__), "Workflows", filename)
        self.flow = Gui.common.read_flow_from_file(self.app_core, fq_filename)

    def _empty_flow(self):
        self.flow = TestUserCommands.app_core.create_flow()

    def _pump(self):
        logging.info('Processing events')
        TestUserCommands.app.processEvents()

    def _rinse_and_repeat(self, states):
        for i in range(REPEAT):
            for check_state in reversed(states[:-1]):
                self.undo_stack.undo()
                self._pump()
                check_state()

            for check_state in states[1:]:
                self.undo_stack.redo()
                self._pump()
                check_state()

    def test_create_node_command(self):
        self._empty_flow()
        self.vertex_expect(self.flow, 2)

        position = QtCore.QPointF(50.0, 60.0)
        identifier = EXAMPLE_NODES[0]
        cmd = user_commands.CreateNodeCommand(
            node_id=identifier, position=position, flow=self.flow)
        self._pump()

        logging.info('Pushing CreateNodeCommand')
        self.undo_stack.push(cmd)
        self._pump()

        # The default value of the create element is None. If the element was
        # created properly it contains a Node object.
        node = cmd.created_element()
        self.assertIsNotNone(node, 'Node element was not created.')
        self.assertIsInstance(node, Gui.flow.node.Node,
                              'Expected a Node class.')
        # We have entry + exit vertices, one node vertex and one output port
        # vertex.
        self.vertex_expect(self.flow, 4)

        node_uuid = cmd.element_uuid()

        self.assertEqual(self.app_core.get_node(node.full_uuid), node,
                         'Could not get node through app_core.')

        for i in range(REPEAT):
            logging.info('Repeat {}'.format(i))
            self.undo_stack.undo()
            self._pump()
            self.vertex_expect(self.flow, 2)
            self.node_expect(self.flow, 0)

            self.undo_stack.redo()
            self._pump()
            self.vertex_expect(self.flow, 4)
            self.node_expect(self.flow, 1)
            self.assertEqual(list(self.flow._nodes.values())[0].uuid,
                             node_uuid,
                             'REPEAT {}: UUID do not match.'.format(i))
            self.assertEqual(self.flow.node(node_uuid), node,
                             'REPEAT {}: UUID lookup did not give the same '
                             'object.'.format(i))
            self.assertEqual(
                list(self.flow._nodes.values())[0], node,
                'REPEAT {}: Stored node is not correct.'.format(i))
            self.assertTrue(node in self.flow._object_to_graph,
                            'REPEAT {}: Node is not present in '
                            'graph.'.format(i))
            vertex = self.flow._object_to_graph[node]
            self.assertTrue(
                vertex in self.flow._graph.vertices(),
                'REPEAT {}: Vertex not present in graph.'.format(i))
            # Entry, Exit, Node and Port.
            self.vertex_expect(self.flow, 4)

    @unittest.skip("Not implemented")
    def test_create_node_with_uuid_command(self):
        pass

    def test_create_subflow_command(self):
        self._empty_flow()
        subflow_pos = QtCore.QPointF(0.0, 0.0)
        subflow_cmd = user_commands.CreateSubflowCommand(
            position=subflow_pos,
            flow=self.flow)
        self.undo_stack.push(subflow_cmd)
        self._pump()

        subflow = subflow_cmd.created_element()
        subflow_uuid = subflow_cmd.element_uuid()

        self.assertIsNotNone(subflow, 'Subflow may not be None.')
        # Graph:
        # 0 -> 4 -> 1
        self.vertex_expect(self.flow, 3)
        self.edge_expect(self.flow, 2)
        self.subflow_expect(self.flow, 1)

        # Sub-graph:
        # 2 3
        self.vertex_expect(subflow, 2)
        self.edge_expect(subflow, 0)

        for i in range(REPEAT):
            self.undo_stack.undo()
            self._pump()
            self.vertex_expect(self.flow, 2, i)
            self.edge_expect(self.flow, 0, i)
            self.subflow_expect(self.flow, 0, i)

            self.undo_stack.redo()
            self._pump()
            self.vertex_expect(self.flow, 3, i)
            self.edge_expect(self.flow, 2, i)
            self.subflow_expect(self.flow, 1, i)
            self.assertEqual(subflow_uuid, subflow_cmd.element_uuid(),
                             'Sub-flow UUID differs from initial.')

    @unittest.skip("Not implemented")
    def test_create_subflow_with_uuid_command(self):
        pass

    def test_create_subflow_from_selection_command(self):
        self._empty_flow()
        node_pos = [QtCore.QPointF(x, 0.0) for x in (-100.0, 0.0, 100.0)]
        node_cmd = [user_commands.CreateNodeCommand(node_id=id_, position=pos,
                                                    flow=self.flow)
                    for id_, pos in zip(EXAMPLE_NODES, node_pos)]

        for cmd in node_cmd:
            self.undo_stack.push(cmd)
        self._pump()

        nodes = [cmd.created_element() for cmd in node_cmd]

        conn_cmd = [user_commands.CreateConnectionCommand(nodes[0].outputs[0],
                                                          nodes[1].inputs[0],
                                                          self.flow),
                    user_commands.CreateConnectionCommand(nodes[1].outputs[0],
                                                          nodes[2].inputs[0],
                                                          self.flow)]
        for cmd in conn_cmd:
            self.undo_stack.push(cmd)
        self._pump()

        def test_before_command(repeat=None):
            # Graph:
            # 0 -> 2 -> 3 -> 5 -> 4 -> 6 -> 8 -> 7 -> 9 -> 1
            # 0: entry
            # 1: exit
            # 2: node Example1
            # 3: output port Example1
            # 4: node Example2
            # 5: input port Example2
            # 6: output port Example2
            # 7: node Example3
            # 8: input port Example3
            # 9: output port Example3
            self.vertex_expect(self.flow, 10, repeat)
            self.edge_expect(self.flow, 9, repeat)
            self.node_expect(self.flow, 3, repeat)
            self.connection_expect(self.flow, 2, repeat)
        test_before_command()

        subflow_pos = node_pos[1]
        element_list = [nodes[1]]

        subflow_cmd = user_commands.CreateSubflowFromSelectionCommand(
            subflow_pos, element_list, self.flow)
        self.undo_stack.push(subflow_cmd)
        self._pump()

        subflow = subflow_cmd.created_element()

        def test_after_command(repeat=None):
            # Graph:
            # 0 -> 2 -> 3 -> 21 -> 12 -> 18 -> 8 -> 7 -> 9 -> 1
            # 12: subflow node
            # 21: subflow input port
            # 18: subflow output port
            self.vertex_expect(self.flow, 10, repeat)
            self.edge_expect(self.flow, 9, repeat)
            self.node_expect(self.flow, 2, repeat)
            self.subflow_expect(self.flow, 1, repeat)
            self.connection_expect(self.flow, 2, repeat)

            self.assertIsNotNone(subflow, 'No subflow element was created')

            # Subflow graph:
            # 10 -> 19 -> 20 -> 14 -> 13 -> 15 -> 17 -> 16 -> 11
            # 10: entry
            # 19: flow input node
            # 20: flow input output port
            # 14: Example2 node input port
            # 13: Example2 node
            # 15: Example2 node output port
            # 17: flow output input port
            # 16: flow output node
            # 11: exit
            self.vertex_expect(subflow, 9, repeat)
            self.edge_expect(subflow, 8, repeat)
            self.node_expect(subflow, 1, repeat)
            self.flow_input_expect(subflow, 1, repeat)
            self.flow_output_expect(subflow, 1, repeat)
            self.connection_expect(subflow, 2, repeat)
        test_after_command()

        for i in range(REPEAT):
            logging.info('Repeat: {}  :: Undo Level: {}'.
                         format(i, self.undo_stack.index()))
            self.undo_stack.undo()
            self._pump()
            logging.info(self.dot(self.flow))
            test_before_command(i)

            logging.info('Repeat: {}  :: Redo Level: {}'.
                         format(i, self.undo_stack.index()))
            self.undo_stack.redo()
            self._pump()
            # self.assertEqual(subflow, subflow_cmd.created_element(),
            #                  'Sub-flows are not the same.')
            logging.info(self.dot(self.flow))
            logging.info(self.dot(subflow))
            test_after_command(i)

    @unittest.skip("Not implemented")
    def test_insert_link_command(self):
        pass

    def test_reorder_subflow_input_port_order_command(self):
        """
        Create an undo stack for the following pseudo operations.
        Reverse and Rotate are implemented using flow port reordering.
        Then check that after moving back and forth in the undo stack,
        the ports have the desired order.

        x = [CreateFlowIO() for _ in range(nports)]
        y = Reverse(x)
        w = r = Rotate(x, 1)
        for _ in len(nports):
            r = Rotate(r, 1)

        Tested commands:

        - ChangeFlowInputOrderCommand
        - ChangeFlowOutputOrderCommand
        """
        inputs = []
        outputs = []
        nports = 3

        def assert_initial(ports, subflow_ports):
            self.assertEqual(ports, subflow_ports,
                             'Invalid initial port order.')

        def assert_reversed(ports, subflow_ports):
            self.assertEqual(list(reversed(ports)), subflow_ports,
                             'Invalid reversed port order.')

        def assert_rotated(ports, subflow_ports):
            reversed_ports = list(reversed(ports))
            rotated_ports = [reversed_ports[2], reversed_ports[0],
                             reversed_ports[1]]
            self.assertEqual(rotated_ports, subflow_ports,
                             'Invalid rotated port order.')

        def assert_rotated_equal(ports, subflow_ports):
            self.assertEqual(ports, subflow_ports,
                             'Invalid rotated port order.')

        self._empty_flow()
        subflow_pos = QtCore.QPointF(0.0, 0.0)
        subflow_cmd = user_commands.CreateSubflowCommand(
            position=subflow_pos,
            flow=self.flow)
        self.undo_stack.push(subflow_cmd)
        self._pump()

        subflow = subflow_cmd.created_element()

        # x = [CreateFlowIO() for _ in range(nports)]

        for i in range(nports):
            flow_input_cmd = user_commands.CreateFlowInputCommand(
                position=QtCore.QPointF(float(i * 50), 0.0), flow=subflow)
            flow_output_cmd = user_commands.CreateFlowOutputCommand(
                position=QtCore.QPointF(float(i * -50), 0.0), flow=subflow)
            self.undo_stack.push(flow_input_cmd)
            self.undo_stack.push(flow_output_cmd)
            self._pump()
            inputs.append(flow_input_cmd.created_element().parent_port)
            outputs.append(flow_output_cmd.created_element().parent_port)

        assert_initial(inputs, subflow.inputs)
        assert_initial(outputs, subflow.outputs)

        # y = Reverse(x).

        reversed_order = list(reversed(range(nports)))

        reorder_input_cmd = user_commands.ChangeFlowInputOrderCommand(
            subflow, reversed_order)
        reorder_output_cmd = user_commands.ChangeFlowOutputOrderCommand(
            subflow, reversed_order)
        self.undo_stack.push(reorder_input_cmd)
        self.undo_stack.push(reorder_output_cmd)
        self._pump()

        assert_reversed(inputs, subflow.inputs)
        assert_reversed(outputs, subflow.outputs)

        # w = r = Rotate(y, 1)

        rotate_right1_order = [2, 0, 1]

        reorder_input_cmd = user_commands.ChangeFlowInputOrderCommand(
            subflow, rotate_right1_order)
        reorder_output_cmd = user_commands.ChangeFlowOutputOrderCommand(
            subflow, rotate_right1_order)
        self.undo_stack.push(reorder_input_cmd)
        self.undo_stack.push(reorder_output_cmd)
        self._pump()

        inputs_rotated = list(subflow.inputs)
        outputs_rotated = list(subflow.outputs)

        for _ in range(nports):
            # r = Rotate(r, 1)
            reorder_input_cmd = user_commands.ChangeFlowInputOrderCommand(
                subflow, rotate_right1_order)
            reorder_output_cmd = user_commands.ChangeFlowOutputOrderCommand(
                subflow, rotate_right1_order)

            self.undo_stack.push(reorder_input_cmd)
            self._pump()
            self.undo_stack.push(reorder_output_cmd)
            self._pump()

        for i in range(REPEAT):

            assert_rotated_equal(inputs_rotated, subflow.inputs)
            assert_rotated_equal(outputs_rotated, subflow.outputs)

            for _ in range(nports):
                self.undo_stack.undo()
                self._pump()
                self.undo_stack.undo()
                self._pump()

            assert_rotated_equal(inputs_rotated, subflow.inputs)
            assert_rotated_equal(outputs_rotated, subflow.outputs)
            assert_rotated(inputs, subflow.inputs)
            assert_rotated(outputs, subflow.outputs)

            self.undo_stack.undo()
            self._pump()
            self.undo_stack.undo()
            self._pump()

            assert_reversed(inputs, subflow.inputs)
            assert_reversed(outputs, subflow.outputs)

            self.undo_stack.undo()
            self._pump()
            self.undo_stack.undo()
            self._pump()

            assert_initial(inputs, subflow.inputs)
            assert_initial(outputs, subflow.outputs)

            self.undo_stack.redo()
            self._pump()
            self.undo_stack.redo()
            self._pump()

            assert_reversed(inputs, subflow.inputs)
            assert_reversed(outputs, subflow.outputs)

            self.undo_stack.redo()
            self._pump()
            self.undo_stack.redo()
            self._pump()

            assert_rotated(inputs, subflow.inputs)
            assert_rotated(outputs, subflow.outputs)

            for _ in range(nports):
                self.undo_stack.redo()
                self._pump()
                self.undo_stack.redo()
                self._pump()

    def test_create_and_delete_node_inputs(self):
        """
        Create, duplicate and delete node inputs.

        Tested commands:

        - DuplicateInputPortCommand
        - CreateNamedInputPortCommand
        - DeleteInputPortCommand
        """
        self._empty_flow()

        nodeid = 'org.sysess.sympathy.tuple.ziptuple2'
        pos = QtCore.QPointF(50.0, 60.0)

        cmd = user_commands.CreateNodeCommand(node_id=nodeid, position=pos,
                                              flow=self.flow)
        self.undo_stack.push(cmd)
        self._pump()
        node = cmd.created_element()
        inputs = list(node.inputs)

        cmd = user_commands.CreateNamedInputPortCommand(node, 'input')
        self.undo_stack.push(cmd)
        self._pump()
        port = cmd.created_element()
        inputs.append(port)

        cmd = user_commands.DuplicateInputPortCommand(port)
        self.undo_stack.push(cmd)
        self._pump()
        inputs.append(cmd.created_element())

        self.assertEqual(len(inputs), 4)

        cmd = user_commands.DeleteInputPortCommand(inputs[-1])
        self.undo_stack.push(cmd)
        self._pump()

        cmd = user_commands.DeleteInputPortCommand(inputs[-2])
        self.undo_stack.push(cmd)
        self._pump()

        for i in range(REPEAT):
            for j in [2, 3, 4, 3]:
                self.assertEqual(inputs[:j], node.inputs)
                self.undo_stack.undo()
                self._pump()

            for j in [2, 3, 4, 3]:
                self.assertEqual(inputs[:j], node.inputs)
                self.undo_stack.redo()
                self._pump()

    def test_create_and_delete_node_outputs(self):
        """
        Create, duplicate and delete node outputs.

        Tested commands:

        - DuplicateOutputPortCommand
        - CreateNamedOutputPortCommand
        - DeleteOutputPortCommand
        """
        self._empty_flow()

        nodeid = 'org.sysess.sympathy.tuple.unziptuple2'
        pos = QtCore.QPointF(150.0, 60.0)

        cmd = user_commands.CreateNodeCommand(node_id=nodeid, position=pos,
                                              flow=self.flow)
        self.undo_stack.push(cmd)
        self._pump()
        node = cmd.created_element()
        outputs = list(node.outputs)

        cmd = user_commands.CreateNamedOutputPortCommand(node, 'output')
        self.undo_stack.push(cmd)
        self._pump()
        port = cmd.created_element()
        outputs.append(port)

        cmd = user_commands.DuplicateOutputPortCommand(cmd.created_element())
        self.undo_stack.push(cmd)
        self._pump()
        outputs.append(cmd.created_element())

        cmd = user_commands.DeleteOutputPortCommand(outputs[-1])
        self.undo_stack.push(cmd)
        self._pump()

        cmd = user_commands.DeleteOutputPortCommand(outputs[-2])
        self.undo_stack.push(cmd)
        self._pump()

        for i in range(REPEAT):
            for j in [2, 3, 4, 3]:
                self.assertEqual(outputs[:j], node.outputs)
                self.undo_stack.undo()
                self._pump()

            for j in [2, 3, 4, 3]:
                self.assertEqual(outputs[:j], node.outputs)
                self.undo_stack.redo()
                self._pump()

    def test_create_flow_input_and_output_commands(self):
        self._empty_flow()
        subflow_pos = QtCore.QPointF(0.0, 0.0)
        subflow_cmd = user_commands.CreateSubflowCommand(
            position=subflow_pos,
            flow=self.flow)
        self.undo_stack.push(subflow_cmd)
        self._pump()

        subflow = subflow_cmd.created_element()

        flow_input_pos = QtCore.QPointF(-50.0, 0.0)
        flow_input_cmd = user_commands.CreateFlowInputCommand(
            position=flow_input_pos, flow=subflow)
        flow_output_pos = QtCore.QPointF(50.0, 0.0)
        flow_output_cmd = user_commands.CreateFlowOutputCommand(
            position=flow_output_pos, flow=subflow)

        self.undo_stack.push(flow_input_cmd)
        self.undo_stack.push(flow_output_cmd)
        self._pump()

        flow_input = flow_input_cmd.created_element()
        flow_output = flow_output_cmd.created_element()

        self.assertIsNotNone(flow_input)
        self.assertIsNotNone(flow_output)

        # Graph:
        # 0 -> 7 -> 4 -> 10 -> 1
        # 0: Entry
        # 7: Sub-flow input port
        # 4: Sub-flow
        # 10: Sub-flow output port
        # 1: Exit
        self.vertex_expect(self.flow, 5)
        self.edge_expect(self.flow, 4)
        self.subflow_expect(self.flow, 1)

        # Sub-graph:
        #   5 - 6
        #  /     \
        # 2       3
        #  \     /
        #   9 - 8
        self.vertex_expect(subflow, 6)
        self.edge_expect(subflow, 6)
        self.flow_input_expect(subflow, 1)
        self.flow_output_expect(subflow, 1)

        self.assertEqual(len(subflow.inputs), 1,
                         'Invalid number of input ports {}. Expected 1.'.
                         format(len(subflow.inputs)))
        self.assertEqual(len(subflow.outputs), 1,
                         'Invalid number of outputs ports {}. Expected 1.'.
                         format(len(subflow.outputs)))
        self.assertEqual(subflow.inputs[0], flow_input.parent_port,
                         'Input port mismatch.')
        self.assertEqual(subflow.outputs[0], flow_output.parent_port,
                         'Output port mismatch.')

        for i in range(REPEAT):
            self.undo_stack.undo()  # remove flow output
            self._pump()
            self.assertEqual(len(subflow.inputs), 1)
            self.assertEqual(len(subflow.outputs), 0)
            self.undo_stack.undo()  # remove flow input
            self._pump()
            self.assertEqual(len(subflow.inputs), 0)
            self.assertEqual(len(subflow.outputs), 0)
            self.undo_stack.undo()  # remove sub-flow
            self._pump()

            self.undo_stack.redo()  # add sub-flow
            self._pump()
            self.assertEqual(len(subflow.inputs), 0)
            self.assertEqual(len(subflow.outputs), 0)
            self.undo_stack.redo()  # add flow input
            self._pump()
            self.assertEqual(len(subflow.inputs), 1)
            self.assertEqual(len(subflow.outputs), 0)
            self.undo_stack.redo()  # add flow output
            self._pump()
            self.assertEqual(len(subflow.inputs), 1)
            self.assertEqual(len(subflow.outputs), 1)

            self.vertex_expect(self.flow, 5)
            self.edge_expect(self.flow, 4)
            self.subflow_expect(self.flow, 1)

            self.vertex_expect(subflow, 6)
            self.edge_expect(subflow, 6)
            self.flow_input_expect(subflow, 1)
            self.flow_output_expect(subflow, 1)

    @unittest.skip("Not implemented")
    def test_create_flow_input_with_uuid_command(self):
        pass

    @unittest.skip("Not implemented")
    def test_create_flow_output_with_uuid_command(self):
        pass

    def test_create_connection_command(self):
        self._empty_flow()
        pos1 = QtCore.QPointF(50.0, 60.0)
        pos2 = QtCore.QPointF(150.0, 80.0)

        id1 = EXAMPLE_NODES[0]
        id2 = EXAMPLE_NODES[1]

        cmd1 = user_commands.CreateNodeCommand(node_id=id1, position=pos1,
                                               flow=self.flow)
        cmd2 = user_commands.CreateNodeCommand(node_id=id2, position=pos2,
                                               flow=self.flow)

        self.undo_stack.push(cmd1)
        self._pump()
        # Current graph:
        # 0 -> 2 -> 3 -> 1
        #
        # 0: entry
        # 2: node
        # 3: port
        # 1: exit
        #
        self.vertex_expect(self.flow, 4)
        self.edge_expect(self.flow, 3)
        self.node_expect(self.flow, 1)
        self.connection_expect(self.flow, 0)

        self.undo_stack.push(cmd2)
        self._pump()
        # Current graph:
        #   2 ----- 3
        #  /         \
        # 0           1
        #  \         /
        #   5 - 4 - 6
        #
        # 0: entry
        # 1: exit
        # 2: node
        # 3: port
        # 5: port
        # 4: node
        # 6: port
        #
        self.vertex_expect(self.flow, 7)
        self.edge_expect(self.flow, 7)
        self.node_expect(self.flow, 2)
        self.connection_expect(self.flow, 0)

        node1 = cmd1.created_element()
        node2 = cmd2.created_element()

        port1 = node1.outputs[0]
        port2 = node2.inputs[0]

        cmd3 = user_commands.CreateConnectionCommand(port1, port2, self.flow)
        self.undo_stack.push(cmd3)
        self._pump()
        # Current graph:
        # 0 -> 2 -> 3 -> 5 -> 4 -> 6 -> 1
        #
        # 0: entry
        # 1: exit
        # 2: node
        # 3: port
        # 5: port
        # 4: node
        # 6: port
        #
        self.vertex_expect(self.flow, 7)
        self.edge_expect(self.flow, 6)
        self.node_expect(self.flow, 2)
        self.connection_expect(self.flow, 1)

        self.assertIsNotNone(cmd3.created_element(), 'Element is None.')
        self.assertIsInstance(cmd3.created_element(),
                              Gui.flow.connection.Connection,
                              'Element is not a Connection.')
        connection_count = lambda: len(self.flow.connections())  # noqa

        for i in range(REPEAT):
            self.undo_stack.undo()
            self._pump()
            self.vertex_expect(self.flow, 7, i)
            self.edge_expect(self.flow, 7, i)
            self.node_expect(self.flow, 2, i)
            self.connection_expect(self.flow, 0, i)

            self.assertEqual(connection_count(), 0, 'REPEAT {}: Expected zero '
                                                    'connections.'.format(i))

            self.undo_stack.undo()
            self._pump()
            self.vertex_expect(self.flow, 4, i)
            self.edge_expect(self.flow, 3, i)
            self.node_expect(self.flow, 1, i)
            self.connection_expect(self.flow, 0, i)

            self.undo_stack.undo()
            self._pump()
            self.vertex_expect(self.flow, 2, i)
            self.edge_expect(self.flow, 0, i)
            self.node_expect(self.flow, 0, i)
            self.connection_expect(self.flow, 0, i)

            self.undo_stack.redo()
            self._pump()
            self.vertex_expect(self.flow, 4, i)
            self.edge_expect(self.flow, 3, i)
            self.node_expect(self.flow, 1, i)
            self.connection_expect(self.flow, 0, i)

            self.undo_stack.redo()
            self._pump()
            self.vertex_expect(self.flow, 7, i)
            self.edge_expect(self.flow, 7, i)
            self.node_expect(self.flow, 2, i)
            self.connection_expect(self.flow, 0, i)

            self.undo_stack.redo()
            self._pump()
            self.vertex_expect(self.flow, 7, i)
            self.edge_expect(self.flow, 6, i)
            self.node_expect(self.flow, 2, i)
            self.connection_expect(self.flow, 1, i)

            self.assertEqual(cmd3.created_element(),
                             self.flow.connections()[0],
                             'REPEAT {}: Connection objects do not '
                             'match.'.format(i))
            self.assertEqual(cmd3.created_element().source, port1,
                             'REPEAT {}: Incorrect source port.'.format(i))
            self.assertEqual(
                cmd3.created_element().destination, port2,
                'REPEAT {}: Incorrect destination port.'.format(i))

    @unittest.skip("Not implemented")
    def test_create_connection_with_uuid_command(self):
        pass

    @unittest.skip("Not implemented")
    def test_create_text_field_command(self):
        pass

    @unittest.skip("Not implemented")
    def test_create_text_field_with_uuid_command(self):
        pass

    def test_paste_element_list_command(self):
        self._empty_flow()
        pos1 = QtCore.QPointF(50.0, 60.0)
        pos2 = QtCore.QPointF(150.0, 60.0)
        pos3 = QtCore.QPointF(100.0, 120.0)

        id1 = EXAMPLE_NODES[0]
        id2 = EXAMPLE_NODES[1]

        cmd1 = user_commands.CreateNodeCommand(node_id=id1, position=pos1,
                                               flow=self.flow)
        cmd2 = user_commands.CreateNodeCommand(node_id=id2, position=pos2,
                                               flow=self.flow)

        self.undo_stack.push(cmd1)
        self._pump()
        # Current graph:
        # 0 -> 2 -> 3 -> 1
        #
        # 0: entry
        # 2: node
        # 3: port
        # 1: exit
        #
        self.vertex_expect(self.flow, 4)
        self.edge_expect(self.flow, 3)
        self.node_expect(self.flow, 1)
        self.connection_expect(self.flow, 0)

        self.undo_stack.push(cmd2)
        self._pump()
        # Current graph:
        #   2 ----- 3
        #  /         \
        # 0           1
        #  \         /
        #   5 - 4 - 6
        #
        # 0: entry
        # 1: exit
        # 2: node
        # 3: port
        # 5: port
        # 4: node
        # 6: port
        #
        self.vertex_expect(self.flow, 7)
        self.edge_expect(self.flow, 7)
        self.node_expect(self.flow, 2)
        self.connection_expect(self.flow, 0)

        node1 = cmd1.created_element()
        node2 = cmd2.created_element()

        port1 = node1.outputs[0]
        port2 = node2.inputs[0]

        cmd3 = user_commands.CreateConnectionCommand(port1, port2, self.flow)
        self.undo_stack.push(cmd3)
        self._pump()
        # Current graph:
        # 0 -> 2 -> 3 -> 5 -> 4 -> 6 -> 1
        #
        # 0: entry
        # 1: exit
        # 2: node
        # 3: port
        # 5: port
        # 4: node
        # 6: port
        #
        self.vertex_expect(self.flow, 7)
        self.edge_expect(self.flow, 6)
        self.node_expect(self.flow, 2)
        self.connection_expect(self.flow, 1)

        copy_data = json.dumps(flow_serialization.partial_dict(
            self.flow, [node1, node2]))

        cmd4 = user_commands.PasteElementListCommand(
            self.flow, copy_data, pos3, self.app_core)
        self.undo_stack.push(cmd4)
        self._pump()
        # Current graph:
        #   2 -> 3  ->  5 -> 4 -> 6
        #  /                       \
        # 0                         1
        #  \                       /
        #   7 -> 8 -> 10 -> 9 -> 11
        #
        # 0: entry
        # 1: exit
        # 2: node
        # 3: port
        # 5: port
        # 4: node
        # 6: port
        # 7: node
        # 8: port
        # 10: port
        # 9: node
        # 11: port
        #
        self.vertex_expect(self.flow, 12)
        self.edge_expect(self.flow, 12)
        self.node_expect(self.flow, 4)
        self.connection_expect(self.flow, 2)

        for i in range(REPEAT):
            self.undo_stack.undo()
            self._pump()
            self.vertex_expect(self.flow, 7, i)
            self.edge_expect(self.flow, 6, i)
            self.node_expect(self.flow, 2, i)
            self.connection_expect(self.flow, 1, i)

            self.undo_stack.undo()
            self._pump()
            self.vertex_expect(self.flow, 7, i)
            self.edge_expect(self.flow, 7, i)
            self.node_expect(self.flow, 2, i)
            self.connection_expect(self.flow, 0, i)

            self.undo_stack.undo()
            self._pump()
            self.vertex_expect(self.flow, 4, i)
            self.edge_expect(self.flow, 3, i)
            self.node_expect(self.flow, 1, i)
            self.connection_expect(self.flow, 0, i)

            self.undo_stack.undo()
            self._pump()
            self.vertex_expect(self.flow, 2, i)
            self.edge_expect(self.flow, 0, i)
            self.node_expect(self.flow, 0, i)
            self.connection_expect(self.flow, 0, i)

            self.undo_stack.redo()
            self._pump()
            self.vertex_expect(self.flow, 4, i)
            self.edge_expect(self.flow, 3, i)
            self.node_expect(self.flow, 1, i)
            self.connection_expect(self.flow, 0, i)

            self.undo_stack.redo()
            self._pump()
            self.vertex_expect(self.flow, 7, i)
            self.edge_expect(self.flow, 7, i)
            self.node_expect(self.flow, 2, i)
            self.connection_expect(self.flow, 0, i)

            self.undo_stack.redo()
            self._pump()
            self.vertex_expect(self.flow, 7, i)
            self.edge_expect(self.flow, 6, i)
            self.node_expect(self.flow, 2, i)
            self.connection_expect(self.flow, 1, i)

            self.undo_stack.redo()
            self._pump()
            self.vertex_expect(self.flow, 12, i)
            self.edge_expect(self.flow, 12, i)
            self.node_expect(self.flow, 4, i)
            self.connection_expect(self.flow, 2, i)

    @unittest.skip("Not implemented")
    def test_remove_element_command(self):
        pass

    @unittest.skip("Not implemented")
    def test_remove_element_list_command(self):
        pass

    @unittest.skip("Not implemented")
    def test_cut_element_list_command(self):
        pass

    @unittest.skip("Not implemented")
    def test_move_element_command(self):
        pass

    @unittest.skip("Not implemented")
    def test_resize_element_command(self):
        pass

    @unittest.skip("Not implemented")
    def test_edit_node_label_command(self):
        pass

    @unittest.skip("Not implemented")
    def test_edit_text_field_command(self):
        pass

    def test_expand_subflow_command(self):
        self._empty_flow()
        subflow_pos = QtCore.QPointF(0.0, 0.0)
        subflow_cmd = user_commands.CreateSubflowCommand(
            position=subflow_pos,
            flow=self.flow)
        self.undo_stack.push(subflow_cmd)
        self._pump()

        subflow = subflow_cmd.created_element()

        flow_input_pos = QtCore.QPointF(-100.0, 0.0)
        flow_input_cmd = user_commands.CreateFlowInputCommand(
            position=flow_input_pos, flow=subflow)
        flow_output_pos = QtCore.QPointF(100.0, 0.0)
        flow_output_cmd = user_commands.CreateFlowOutputCommand(
            position=flow_output_pos, flow=subflow)

        self.undo_stack.push(flow_input_cmd)
        self.undo_stack.push(flow_output_cmd)
        self._pump()

        flow_input = flow_input_cmd.created_element()
        flow_output = flow_output_cmd.created_element()

        self.assertIsNotNone(flow_input)
        self.assertIsNotNone(flow_output)

        # Graph:
        # 0 -> 7 -> 4 -> 10 -> 1
        # 0: Entry
        # 7: Sub-flow input port
        # 4: Sub-flow
        # 10: Sub-flow output port
        # 1: Exit
        self.vertex_expect(self.flow, 5)
        self.edge_expect(self.flow, 4)
        self.subflow_expect(self.flow, 1)

        # Sub-graph:
        #   5 - 6
        #  /     \
        # 2       3
        #  \     /
        #   9 - 8
        # 2: Entry
        # 5: FlowInput
        # 6: FlowInput: output port
        # 9: FlowOutput
        # 8: FlowOutput: input port
        # 3: Exit
        self.vertex_expect(subflow, 6)
        self.edge_expect(subflow, 6)
        self.flow_input_expect(subflow, 1)
        self.flow_output_expect(subflow, 1)
        node_pos = [QtCore.QPointF(x, 0.0) for x in (-100.0, 0.0, 100.0)]
        node_flow = [self.flow, subflow, self.flow]
        node_cmd = [
            user_commands.CreateNodeCommand(node_id=id_, position=pos,
                                            flow=flow)
            for id_, pos, flow in zip(EXAMPLE_NODES, node_pos, node_flow)]

        for cmd in node_cmd:
            self.undo_stack.push(cmd)
        self._pump()

        nodes = [cmd.created_element() for cmd in node_cmd]
        for node in nodes:
            self.assertIsNotNone(node)

        conn_cmd = [
            user_commands.CreateConnectionCommand(
                nodes[0].outputs[0], flow_input.parent_port, self.flow),
            user_commands.CreateConnectionCommand(
                flow_input.port, nodes[1].inputs[0], subflow),
            user_commands.CreateConnectionCommand(
                nodes[1].outputs[0], flow_output.port, subflow),
            user_commands.CreateConnectionCommand(
                flow_output.parent_port, nodes[2].inputs[0], self.flow)]

        for cmd in conn_cmd:
            self.undo_stack.push(cmd)
        self._pump()

        # Graph:
        # 0 -> 11 -> 12 -> 7 -> 4 -> 10 -> 17 -> 16 -> 18 -> 1
        # 0: Entry
        # 11: Example1 node
        # 12: Example1 output port
        # 7: Sub-flow input port
        # 4: Sub-flow
        # 10: Sub-flow output port
        # 17: Example3 input port
        # 16: Example3 node
        # 18: Example3 output port
        # 1: Exit
        self.vertex_expect(self.flow, 10)
        self.edge_expect(self.flow, 9)
        self.subflow_expect(self.flow, 1)
        self.node_expect(self.flow, 2)

        # Sub-graph:
        # 2 -> 5 -> 6 -> 14 -> 13 -> 15 -> 9 -> 8 -> 3
        # 2: Entry
        # 5: FlowInput
        # 6: FlowInput: port
        # 14: Example2 input port
        # 13: Example2 node
        # 15: Example2 output port
        # 9: FlowOutput
        # 8: FlowOutput: port
        # 3: Exit
        self.vertex_expect(subflow, 9)
        self.edge_expect(subflow, 8)
        self.node_expect(subflow, 1)
        self.flow_input_expect(subflow, 1)
        self.flow_output_expect(subflow, 1)

        expand_cmd = user_commands.ExpandSubflowCommand(subflow)
        self.undo_stack.push(expand_cmd)

        # Graph:
        # 0 -> 11 -> 12 -> 14 -> 13 -> 15 -> -> 17 -> 16 -> 18 -> 1
        # 0: Entry
        # 11: Example1 node
        # 12: Example1 output port
        # 14: Example2 input port
        # 13: Example2 node
        # 15: Example2 output port
        # 17: Example3 input port
        # 16: Example3 node
        # 18: Example3 output port
        # 1: Exit
        self.vertex_expect(self.flow, 10)
        self.edge_expect(self.flow, 9)
        self.subflow_expect(self.flow, 0)
        self.node_expect(self.flow, 3)

        for i in range(REPEAT):
            self.undo_stack.undo()  # undo expand subflow
            self._pump()

            self.vertex_expect(self.flow, 10)
            self.edge_expect(self.flow, 9)
            self.subflow_expect(self.flow, 1)
            self.node_expect(self.flow, 2)
            self.vertex_expect(subflow, 9)
            self.edge_expect(subflow, 8)
            self.node_expect(subflow, 1)
            self.flow_input_expect(subflow, 1)
            self.flow_output_expect(subflow, 1)

            self.undo_stack.undo()  # remove connection
            self._pump()
            self.undo_stack.undo()  # remove connection
            self._pump()
            self.undo_stack.undo()  # remove connection
            self._pump()
            self.undo_stack.undo()  # remove connection
            self._pump()
            self.undo_stack.undo()  # remove example3
            self._pump()
            self.undo_stack.undo()  # remove example2
            self._pump()
            self.undo_stack.undo()  # remove example1
            self._pump()
            self.assertEqual(len(subflow.inputs), 1)
            self.assertEqual(len(subflow.outputs), 1)
            self.undo_stack.undo()  # remove flow output
            self._pump()
            self.undo_stack.undo()  # remove flow input
            self._pump()
            self.assertEqual(len(subflow.inputs), 0)
            self.assertEqual(len(subflow.outputs), 0)
            self.undo_stack.undo()  # remove sub-flow
            self._pump()

            self.vertex_expect(self.flow, 2, i)
            self.edge_expect(self.flow, 0, i)
            self.subflow_expect(self.flow, 0, i)
            self.node_expect(self.flow, 0, i)

            self.undo_stack.redo()  # add sub-flow
            self._pump()
            self.assertEqual(len(subflow.inputs), 0)
            self.assertEqual(len(subflow.outputs), 0)
            self.undo_stack.redo()  # add flow input
            self._pump()
            self.undo_stack.redo()  # add flow output
            self._pump()
            self.assertEqual(len(subflow.inputs), 1)
            self.assertEqual(len(subflow.outputs), 1)
            self.undo_stack.redo()  # add example1
            self._pump()
            self.undo_stack.redo()  # add example2
            self._pump()
            self.undo_stack.redo()  # add example3
            self._pump()
            self.undo_stack.redo()  # add connection
            self._pump()
            self.undo_stack.redo()  # add connection
            self._pump()
            self.undo_stack.redo()  # add connection
            self._pump()
            self.undo_stack.redo()  # add connection
            self._pump()

            self.vertex_expect(self.flow, 10, i)
            self.edge_expect(self.flow, 9, i)
            self.subflow_expect(self.flow, 1, i)
            self.node_expect(self.flow, 2, i)
            self.vertex_expect(subflow, 9, i)
            self.edge_expect(subflow, 8, i)
            self.node_expect(subflow, 1, i)
            self.flow_input_expect(subflow, 1, i)
            self.flow_output_expect(subflow, 1, i)

            self.undo_stack.redo()  # redo expand subflow
            self._pump()

            self.vertex_expect(self.flow, 10, i)
            self.edge_expect(self.flow, 9, i)
            self.subflow_expect(self.flow, 0, i)
            self.node_expect(self.flow, 3, i)

    @unittest.skip("Not implemented")
    def test_edit_node_parameters(self):
        pass

    @unittest.skip("Not implemented")
    def test_edit_subflow_parameters_command(self):
        pass

    def test_link_subflow_command(self):
        self._empty_flow()
        subflow_pos = QtCore.QPointF(0.0, 0.0)
        subflow_cmd = user_commands.CreateSubflowCommand(
            position=subflow_pos,
            flow=self.flow)
        self.undo_stack.push(subflow_cmd)
        self._pump()

        subflow = subflow_cmd.created_element()

        def check_state1():
            self.assertFalse(subflow.is_linked)
            self.assertEqual(subflow.source_uri, '')
        check_state1()

        filename1 = 'some_filename.syx'
        link_cmd1 = user_commands.LinkSubflowCommand(subflow, filename1)
        self.undo_stack.push(link_cmd1)
        self._pump()

        def check_state2():
            self.assertTrue(subflow.is_linked)
            self.assertEqual(subflow.source_uri, filename1)
        check_state2()

        filename2 = 'some_other_filename.syx'
        link_cmd2 = user_commands.LinkSubflowCommand(subflow, filename2)
        self.undo_stack.push(link_cmd2)
        self._pump()

        def check_state3():
            self.assertTrue(subflow.is_linked)
            self.assertEqual(subflow.source_uri, filename2)
        check_state3()

        self._rinse_and_repeat([check_state1, check_state2, check_state3])

    def test_unlink_subflow(self):
        """
        Test that the unlinked subflow is the same after redo, undo, redo, undo
        and that it is in the parent flow.

        The test for similarity checks that the number of objects is the same.
        and that some properties are.
        """

        self._load_flow('unlink.syx')

        def flow_count(flow_):
            return {'vertex': self.vertex_count(flow_),
                    'edge': self.edge_count(flow_),
                    'node': self.node_count(flow_),
                    'subflow': self.subflow_count(flow_),
                    'flow_input': self.flow_input_count(flow_),
                    'flow_output': self.flow_output_count(flow_),
                    'connection': self.connection_count(flow_),
                    'text_field': self.text_field_count(flow_)}

        def check_count(flow_, count_dict):
            self.vertex_expect(flow_, count_dict['vertex'])
            self.edge_expect(flow_, count_dict['edge'])
            self.node_expect(flow_, count_dict['node'])
            self.subflow_expect(flow_, count_dict['subflow'])
            self.flow_input_expect(
                flow_, count_dict['flow_input'])
            self.flow_output_expect(
                flow_, count_dict['flow_output'])
            self.connection_expect(
                flow_, count_dict['connection'])
            self.text_field_expect(
                flow_, count_dict['text_field'])

        def check_subflow(parent, subflow):
            self.assertIn(subflow, parent.shallow_subflows())

        def check_subflows(parent, subflow1, subflow2):
            self.assertIn(subflow1, parent.shallow_subflows())
            self.assertNotIn(subflow2, parent.shallow_subflows())
            self.assertEqual(subflow1.name, subflow2.name)
            self.assertEqual(subflow1._version, subflow2._version)
            self.assertEqual(subflow1._tag, subflow2._tag)
            self.assertEqual(subflow1.icon_filename, subflow2.icon_filename)
            self.assertEqual(subflow1._min_version, subflow2._min_version)
            self.assertEqual(subflow1.description, subflow2.description)
            self.assertEqual(subflow1._copyright, subflow2._copyright)
            self.assertEqual(subflow1._author, subflow2._author)
            self.assertFalse(subflow1.is_linked and subflow2.is_linked)

        for subflow in self.flow.shallow_subflows():
            check_subflow(self.flow, subflow)
            subflow_count = flow_count(subflow)
            parent_flow_count = flow_count(self.flow)
            cmd = user_commands.UnlinkSubflowCommand(subflow)

            self.undo_stack.push(cmd)
            self._pump()
            check_count(self.flow, parent_flow_count)
            check_count(subflow, subflow_count)
            check_count(cmd.created_element(), subflow_count)
            check_subflows(self.flow, cmd.created_element(), subflow)

            self.undo_stack.undo()
            self._pump()
            check_count(self.flow, parent_flow_count)
            check_count(subflow, subflow_count)
            check_count(cmd.created_element(), subflow_count)
            check_subflows(self.flow, subflow, cmd.created_element())

            self.undo_stack.redo()
            self._pump()
            check_count(self.flow, parent_flow_count)
            check_count(subflow, subflow_count)
            check_count(cmd.created_element(), subflow_count)
            check_subflows(self.flow, cmd.created_element(), subflow)

            self.undo_stack.undo()
            self._pump()
            check_count(self.flow, parent_flow_count)
            check_count(subflow, subflow_count)
            check_count(cmd.created_element(), subflow_count)
            check_subflows(self.flow, subflow, cmd.created_element())

    def test_paste_subflow_w_overrides(self):
        self._load_flow('overrides.syx')

        def check_state1():
            # Current graph:
            # 0 -> 2 -> 1
            #
            # 0: entry
            # 2: subflow
            # 1: exit
            #
            self.vertex_expect(self.flow, 3)
            self.edge_expect(self.flow, 2)
            self.node_expect(self.flow, 0)
            self.subflow_expect(self.flow, 1)
            self.connection_expect(self.flow, 0)

            # Get node and subflow
            subflow1 = self.flow.shallow_nodes()[0]
            self.assertTrue(subflow1.is_linked)
            all_nodes = self.flow.all_nodes()
            self.assertEqual(len(all_nodes), 1)
            node1 = all_nodes[0]

            # Check that overrides and base parameters are correct
            all_overrides = node1.get_override_parameter_models_dict()
            self.assertEqual(len(all_overrides), 1)
            overrides, uuid = all_overrides[0]
            self.assertEqual(uuid, subflow1.uuid)
            self.assertEqual(overrides['greeting']['value'], u'Override!')
            base_params = node1.base_parameter_model.to_dict()
            self.assertEqual(base_params['greeting']['value'], u'Hello world!')
        check_state1()

        # Go to state2
        subflow1 = self.flow.shallow_nodes()[0]
        copy_data = json.dumps(flow_serialization.partial_dict(
            self.flow, [subflow1]))
        pos2 = QtCore.QPointF(50.0, 60.0)
        cmd2 = user_commands.PasteElementListCommand(
            self.flow, copy_data, pos2, self.app_core)
        self.undo_stack.push(cmd2)
        self._pump()

        def check_state2():
            # Current graph:
            #   2
            #  / \
            # 0   1
            #  \ /
            #   3
            #
            # 0: entry
            # 1: exit
            # 2: subflow
            # 3: subflow
            #
            self.vertex_expect(self.flow, 4)
            self.edge_expect(self.flow, 4)
            self.subflow_expect(self.flow, 2)
            self.node_expect(self.flow, 0)
            self.connection_expect(self.flow, 0)

            # Get pasted node and subflow
            all_pasted_elements = cmd2.created_top_level_elements()
            self.assertEqual(len(all_pasted_elements), 1)
            subflow2 = all_pasted_elements[0]
            self.node_expect(subflow2, 1)
            node2 = subflow2.shallow_nodes()[0]

            # Check that overrides and base parameters are correct
            all_pasted_overrides = node2.get_override_parameter_models_dict()
            self.assertEqual(len(all_pasted_overrides), 1)
            pasted_overrides, pasted_uuid = all_pasted_overrides[0]
            self.assertEqual(pasted_uuid, subflow2.uuid)
            self.assertEqual(pasted_overrides['greeting']['value'],
                             u'Override!')
            base_params = node2.base_parameter_model.to_dict()
            self.assertEqual(base_params['greeting']['value'], u'Hello world!')
        check_state2()

        self._rinse_and_repeat([check_state1, check_state2])

    def test_paste_node_w_overrides(self):
        self._load_flow('overrides.syx')

        def check_state1():
            # Current graph:
            # 0 -> 2 -> 1
            #
            # 0: entry
            # 2: subflow
            # 1: exit
            #
            self.vertex_expect(self.flow, 3)
            self.edge_expect(self.flow, 2)
            self.node_expect(self.flow, 0)
            self.subflow_expect(self.flow, 1)
            self.connection_expect(self.flow, 0)

            # Get node and subflow
            subflow1 = self.flow.shallow_nodes()[0]
            self.assertTrue(subflow1.is_linked)
            all_nodes = self.flow.all_nodes()
            self.assertEqual(len(all_nodes), 1)
            node1 = all_nodes[0]

            # Check that overrides and base parameters are correct
            all_overrides = node1.get_override_parameter_models_dict()
            self.assertEqual(len(all_overrides), 1)
            overrides, uuid = all_overrides[0]
            self.assertEqual(uuid, subflow1.uuid)
            self.assertEqual(overrides['greeting']['value'], u'Override!')
            base_params = node1.base_parameter_model.to_dict()
            self.assertEqual(base_params['greeting']['value'], u'Hello world!')
        check_state1()

        # Go to state2
        subflow1 = self.flow.shallow_nodes()[0]
        node1 = self.flow.all_nodes()[0]
        copy_data = json.dumps(flow_serialization.partial_dict(
            subflow1, [node1]))
        pos2 = QtCore.QPointF(50.0, 60.0)
        cmd2 = user_commands.PasteElementListCommand(
            self.flow, copy_data, pos2, self.app_core)
        self.undo_stack.push(cmd2)
        self._pump()

        def check_state2():
            # Current graph:
            #   2
            #  / \
            # 0   1
            #  \ /
            #   3
            #
            # 0: entry
            # 1: exit
            # 2: subflow
            # 3: node
            #
            self.vertex_expect(self.flow, 4)
            self.edge_expect(self.flow, 4)
            self.subflow_expect(self.flow, 1)
            self.node_expect(self.flow, 1)
            self.connection_expect(self.flow, 0)

            # Get pasted node and subflow
            all_pasted_elements = cmd2.created_top_level_elements()
            self.assertEqual(len(all_pasted_elements), 1)
            node2 = all_pasted_elements[0]

            # Check that overrides and base parameters are correct
            all_pasted_overrides = node2.get_override_parameter_models_dict()
            self.assertEqual(len(all_pasted_overrides), 0)
            self.assertFalse(node2.has_overrides())
            base_params = node2.base_parameter_model.to_dict()
            self.assertEqual(base_params['greeting']['value'], u'Override!')
        check_state2()

        self._rinse_and_repeat([check_state1, check_state2])

    def test_save_linked_subflow_w_overrides(self):
        self._load_flow('overrides.syx')
        orig_filename = 'inner.syx'

        subflow = self.flow.shallow_nodes()[0]
        node1 = self.flow.all_nodes()[0]

        def check_state1():
            self.assertTrue(subflow.is_linked)
            self.assertEqual(subflow.source_uri, orig_filename)

            # Check that overrides and base parameters are correct
            all_overrides = node1.get_override_parameter_models_dict()
            self.assertEqual(len(all_overrides), 1)
            overrides, uuid = all_overrides[0]
            self.assertEqual(uuid, subflow.uuid)
            self.assertEqual(overrides['greeting']['value'], u'Override!')
            base_params = node1.base_parameter_model.to_dict()
            self.assertEqual(base_params['greeting']['value'], u'Hello world!')
        check_state1()

        new_filename = 'some_other_filename.syx'
        link_cmd = user_commands.LinkSubflowCommand(subflow, new_filename)
        self.undo_stack.push(link_cmd)
        self._pump()

        def check_state2():
            self.assertTrue(subflow.is_linked)
            self.assertEqual(subflow.source_uri, new_filename)

            # Check that overrides and base parameters are correct
            all_overrides = node1.get_override_parameter_models_dict()
            self.assertEqual(len(all_overrides), 1)
            overrides, uuid = all_overrides[0]
            self.assertEqual(uuid, subflow.uuid)
            self.assertEqual(overrides['greeting']['value'], u'Override!')
            base_params = node1.base_parameter_model.to_dict()
            self.assertEqual(base_params['greeting']['value'], u'Hello world!')
        check_state2()

        self._rinse_and_repeat([check_state1, check_state2])
