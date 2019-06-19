# This file is part of Sympathy for Data.
# Copyright (c) 2016 Combine Control Systems AB
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
import collections
import logging
import PySide.QtCore as QtCore

from sympathy.platform import message
from . flow import types

core_logger = logging.getLogger('core')


def nodups(lst):
    return reversed(
        collections.OrderedDict.fromkeys(reversed(lst)).keys())


class MessageManager(QtCore.QObject):
    message_output = QtCore.Signal(int, message.Message)

    def __init__(self, appcore):
        super(MessageManager, self).__init__(appcore)
        self._appcore = appcore

    def _got_agg_config_update(self, ident, msg):
        data = msg.data
        uuid = data['uuid']
        core_logger.info('AggConfigUpdateMessage for: %s', uuid)
        self._appcore.handle_subflow_parameter_view_done(uuid, data)

    def _dependent_node_status(self, node):
        error = False
        nodes = []
        inodes = list(nodups(node._incoming_nodes()))

        def locked_origin_nodes(node):
            node_list = list(nodups(node._incoming_nodes()))
            res = []
            prev_locked = False
            for prev_node in node_list:
                if prev_node.is_done_locked():
                    prev_locked = True
                    res.extend(locked_origin_nodes(prev_node))
            if not prev_locked:
                res.append(node)
            return res

        locked_prev_nodes = []

        for inode in inodes:
            if inode.is_done_locked():
                locked_prev_nodes.extend(locked_origin_nodes(inode))

        locked_prev_nodes = list(nodups(locked_prev_nodes))

        for inode in inodes:
            if inode.is_executing():
                pass
            elif inode.is_done():
                if inode.is_done_locked():
                    nodes.append(inode)
            elif inode.is_queued() or inode.is_armed():
                nodes.append(inode)
            else:
                error = True
                break
        return error, nodes, inodes, locked_prev_nodes

    def _got_data_request(self, ident, msg):
        uuid = msg.data
        core_logger.info('DataRequestMessage for: %s', uuid)
        node = self._appcore.get_flode(uuid)
        error, nodes, inodes, locked_prev = self._dependent_node_status(node)

        if not error:
            for prev_node in locked_prev:
                if prev_node.is_done_locked():
                    prev_node.clear_locked_done()

            for inode in inodes:
                inode.flow.execute_node(inode)

            if not inodes:
                self.message_output.emit(
                    -1, message.DataReadyMessage(node.full_uuid))
            elif not nodes:
                self.message_output.emit(
                    -1, message.DataReadyMessage(node.full_uuid))

    @QtCore.Slot(int, message.Message)
    def message_input(self, ident, msg):

        if msg.type == message.DataRequestMessage:
            self._got_data_request(ident, msg)

        elif msg.type == message.AggConfigUpdateMessage:
            self._got_agg_config_update(ident, msg)

        if msg.type == message.StatusDataRequestMessage:
            uuid = msg.data
            node = self._appcore.get_flode(uuid)
            error = self._dependent_node_status(node)[0]
            if error:
                self.message_output.emit(
                    ident, message.DataBlockedMessage(node.full_uuid))

    def execution_done(self, node):
        if node.type == types.Type.Node:
            # TODO(erik): implement proper support for flows and stop using
            # private Node member.

            for onode in nodups(node._outgoing_nodes()):
                if onode.all_incoming_nodes_are_successfully_executed():
                    ready = [onode]

                    if onode.type == types.Type.Flow and onode.is_locked():
                        ready.extend(
                            n for n in onode._start_nodes(
                                all_subflows_as_atom=True) if
                            n.all_incoming_nodes_are_successfully_executed())

                    for n in ready:
                        self.message_output.emit(
                            -1, message.DataReadyMessage(n.full_uuid))
