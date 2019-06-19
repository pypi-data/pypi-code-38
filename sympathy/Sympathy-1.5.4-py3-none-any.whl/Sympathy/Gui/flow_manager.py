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
import PySide.QtCore as QtCore


class FlowManager(QtCore.QObject):
    # I'll be waiting with these until they are really necessary
    # document_inserted = QtCore.Signal(unicode)
    # document_removed = QtCore.Signal(unicode)
    # node_state_changed = QtCore.Signal(unicode, unicode)
    # connection_state_changed = QtCore.Signal(unicode, unicode)
    # node_parameter_validation_requested = QtCore.Signal(unicode, unicode)
    # execution_started = QtCore.Signal(unicode, unicode)
    # execution_finished = QtCore.Signal(unicode, unicode)

    def __init__(self, parent=None):
        super(FlowManager, self).__init__(parent)
        self._flows = {}

    def flow(self, namespace_uuid):
        return self._flows[namespace_uuid]

    def insert_flow(self, flow):
        self._flows[flow.namespace_uuid()] = flow

    def remove_flow(self, flow):
        if flow.namespace_uuid() in self._flows:
            del self._flows[flow.namespace_uuid()]

    def is_empty(self):
        return len(self._flows) == 0

    def flows(self):
        return self._flows.values()
