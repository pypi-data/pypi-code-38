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
import collections
import logging
import itertools
import PySide.QtCore as QtCore

from sympathy.utils import port as port_util
from . types import NodeStatusInterface, Type, NodeInterface, Executors
from .. util import log_debug_message
from .. library import PortDefinition
from . import flowlib
from .. import datatypes
from . import exceptions


core_logger = logging.getLogger('core')
factories = collections.defaultdict(lambda: Node)

# TODO: Improve visual handling of ports so that limit can be removed.
max_nports = 6


class StateMachine(QtCore.QObject):

    def __init__(self, parent):
        super(StateMachine, self).__init__(parent)
        self._running = False
        self._containers = []

    def addContainer(self, container):
        if container in self._containers:
            raise Exception(
                'Multiple calls to addContainer with same container.')

        self._containers.append(container)

    def configuration(self):
        return [container.state for container in self._containers]

    def start(self):
        self._running = True
        for container in self._containers:
            container.state.entered.emit()

    def isRunning(self):
        return self._running


class StateContainer(QtCore.QObject):

    def __init__(self, state_machine):
        super(StateContainer, self).__init__(state_machine)
        self._state = None
        self._states = []
        self._state_machine = state_machine
        self._transitions = {}

        state_machine.addContainer(self)

    def addState(self, state):
        if state in self._states:
            raise Exception('Multiple calls to addState with same state.')

        self._states.append(state)

    def addTransition(self, signal, from_state, to_state):

        if signal not in self._transitions:

            def inner():
                self.transit(signal)

            signal.connect(inner)

        self._transitions.setdefault(signal, {})[from_state] = to_state

    def transit(self, signal):
        from_state = self._state
        to_state = self._transitions.get(signal, {}).get(from_state)

        if to_state:
            from_state.exited.emit()
            self._state = to_state
            to_state.entered.emit()

    def setInitialState(self, state):
        self._state = state

    @property
    def state(self):
        return self._state


class State(QtCore.QObject):
    entered = QtCore.Signal()
    exited = QtCore.Signal()

    def __init__(self, container):
        super(State, self).__init__(container)
        self._container = container
        self._container.addState(self)
        self._transitions = {}

    def addTransition(self, signal, state):
        if signal in self._transitions:
            raise Exception(
                'Multiple calls to addTransition with same signal.')

        self._container.addTransition(signal, self, state)
        # signal.connect(inner)

    def transit(self, state):
        self._container.transit(self, state)


@six.python_2_unicode_compatible
class NodeStateMachine(NodeStatusInterface, QtCore.QObject):
    """Implementation of the state machine for a regular executable Node."""
    execution_finished = QtCore.Signal()
    execution_started = QtCore.Signal()

    on_state_aborting = QtCore.Signal()
    on_state_armed = QtCore.Signal()
    on_state_done = QtCore.Signal()
    on_state_error = QtCore.Signal()
    on_state_executing = QtCore.Signal()
    on_state_invalid = QtCore.Signal()
    on_state_queued = QtCore.Signal()
    on_state_valid = QtCore.Signal()
    on_state_validating = QtCore.Signal()

    state_changed = QtCore.Signal()

    node_error_occured = QtCore.Signal()
    node_execution_finished = QtCore.Signal()
    node_locked_execution_finished = QtCore.Signal()
    node_has_aborted = QtCore.Signal()
    node_is_aborting = QtCore.Signal()
    node_is_armed = QtCore.Signal()
    node_is_disarmed = QtCore.Signal()
    node_is_executing = QtCore.Signal()
    node_is_queued = QtCore.Signal()
    parameters_are_being_validated = QtCore.Signal()
    parameters_are_invalid = QtCore.Signal()
    parameters_are_valid = QtCore.Signal()
    pending_call_returned = QtCore.Signal()
    pending_call_sent = QtCore.Signal()

    def __init__(self, *args, **kwargs):
        parent = kwargs.get('parent')
        super(NodeStateMachine, self).__init__(*args, **kwargs)
        self._parent = parent

        self._init_state_machine()

    def _init_state_machine(self):
        self._init_states()
        self._init_state_transitions()
        self._init_state_signals()
        self._node_state_container.setInitialState(self._initializing)
        self._pending_state_container.setInitialState(self._idle)
        # self._state_machine.setInitialState(self._parallel_state_container)
        self._state_machine.start()
        self._conf = self._state_machine.configuration()

    def _init_states(self):
        self._state_machine = StateMachine(self)

        self._node_state_container = StateContainer(
            self._state_machine)
        # State during first startup
        self._initializing = State(self._node_state_container)
        # State during validation of configuration.
        self._validating = State(self._node_state_container)
        # Error state.
        self._error = State(self._node_state_container)
        # Invalid configuration.
        self._invalid = State(self._node_state_container)
        # Valid configuration, but not armed.
        self._valid = State(self._node_state_container)
        # Armed for execution.
        self._armed = State(self._node_state_container)
        # Queued for execution.
        self._queued = State(self._node_state_container)
        # Executing.
        self._executing = State(self._node_state_container)
        # Aborting execution.
        self._aborting = State(self._node_state_container)
        # Aborting execution.
        self._aborting_valid = State(self._node_state_container)
        # Execution done.
        self._done = State(self._node_state_container)
        # Execution done, in locked mode.
        self._done_locked = State(self._node_state_container)

        self._pending_state_container = StateContainer(
            self._state_machine)
        # Node has no outstanding calls.
        self._idle = State(self._pending_state_container)
        # Waiting for result from a pending command
        # in a language interface.
        self._pending = State(self._pending_state_container)

    def _init_state_transitions(self):
        # Initializing - directly to invalid
        self._initializing.addTransition(
            self.parameters_are_being_validated, self._validating)

        # Validating ->
        self._validating.addTransition(
            self.parameters_are_invalid, self._invalid)
        self._validating.addTransition(self.parameters_are_valid, self._valid)

        # Invalid ->
        self._invalid.addTransition(
            self.parameters_are_being_validated, self._validating)

        # Valid ->
        self._valid.addTransition(
            self.parameters_are_being_validated, self._validating)
        self._valid.addTransition(self.node_is_armed, self._armed)

        # Armed ->
        self._armed.addTransition(self.node_is_queued, self._queued)
        self._armed.addTransition(self.node_is_executing, self._executing)
        self._armed.addTransition(
            self.parameters_are_being_validated, self._validating)
        self._armed.addTransition(self.node_is_disarmed, self._valid)

        # Queued ->
        self._queued.addTransition(self.node_is_aborting, self._aborting)
        self._queued.addTransition(self.node_is_executing, self._executing)
        self._queued.addTransition(self.node_is_armed, self._aborting)
        self._queued.addTransition(self.node_is_disarmed, self._aborting_valid)

        # Executing ->
        self._executing.addTransition(self.node_is_aborting, self._aborting)
        self._executing.addTransition(self.node_is_armed, self._aborting)
        self._executing.addTransition(
            self.node_is_disarmed, self._aborting_valid)
        self._executing.addTransition(self.node_execution_finished, self._done)
        self._executing.addTransition(self.node_locked_execution_finished,
                                      self._done_locked)
        self._executing.addTransition(self.node_error_occured, self._error)

        # Done ->
        for done in [self._done, self._done_locked]:
            done.addTransition(
                self.parameters_are_being_validated, self._validating)
            done.addTransition(self.node_is_queued, self._queued)
            done.addTransition(self.node_is_executing, self._executing)
            done.addTransition(self.node_is_armed, self._armed)
            done.addTransition(self.node_is_disarmed, self._valid)

        self._done_locked.addTransition(
            self.node_execution_finished, self._done)

        # Aborting ->
        self._aborting.addTransition(self.node_has_aborted, self._armed)

        # Aborting valid ->
        self._aborting_valid.addTransition(self.node_has_aborted, self._valid)

        # Error ->
        self._error.addTransition(
            self.parameters_are_being_validated, self._validating)
        self._error.addTransition(self.node_is_armed, self._armed)
        self._error.addTransition(self.node_is_disarmed, self._valid)

        # Idle ->
        self._idle.addTransition(self.pending_call_sent, self._pending)

        # Pending ->
        self._pending.addTransition(self.pending_call_returned, self._idle)

    def _init_state_signals(self):
        self._initializing.entered.connect(self._state_changed)
        self._validating.entered.connect(self.state_changed)
        self._error.entered.connect(self.state_changed)
        self._invalid.entered.connect(self.state_changed)
        self._valid.entered.connect(self.state_changed)
        self._armed.entered.connect(self.state_changed)
        self._queued.entered.connect(self.state_changed)
        self._executing.entered.connect(self.state_changed)
        self._aborting.entered.connect(self.state_changed)
        self._aborting_valid.entered.connect(self.state_changed)
        self._done.entered.connect(self.state_changed)
        self._done_locked.entered.connect(self.state_changed)

        self._idle.entered.connect(self.state_changed)
        self._pending.entered.connect(self.state_changed)

        self._executing.entered.connect(self.execution_started)
        self._executing.exited.connect(self.execution_finished)

        self._validating.entered.connect(self.on_state_validating)
        self._error.entered.connect(self.on_state_error)
        self._invalid.entered.connect(self.on_state_invalid)
        self._valid.entered.connect(self.on_state_valid)
        self._armed.entered.connect(self.on_state_armed)
        self._queued.entered.connect(self.on_state_queued)
        self._executing.entered.connect(self.on_state_executing)
        self._aborting.entered.connect(self.on_state_aborting)
        self._aborting_valid.entered.connect(self.on_state_aborting)
        self._done.entered.connect(self.on_state_done)
        self._done_locked.entered.connect(self.on_state_done)

        self.state_changed.connect(self._state_changed)

    def __str__(self):
        current_states = []
        configuration = self.configuration()

        if not self._state_machine.isRunning():
            current_states.append('State Machine is not running!')

        if self._initializing in configuration:
            current_states.append('Initialized')

        if self._validating in configuration:
            current_states.append('Validating')

        if self._error in configuration:
            current_states.append('Error')

        if self._invalid in configuration:
            current_states.append('Invalid')

        if self._valid in configuration:
            current_states.append('Valid')

        if self._armed in configuration:
            current_states.append('Armed')

        if self._queued in configuration:
            current_states.append('Queued')

        if self._executing in configuration:
            current_states.append('Executing')

        if (self._aborting in configuration or
                self._aborting_valid in configuration):
            current_states.append('Aborting')

        if self._done_locked in configuration:
            current_states.append('Done-Locked')

        if self._done in configuration:
            current_states.append('Done')

        if self._idle in configuration:
            current_states.append('Idle')

        if self._pending in configuration:
            current_states.append('Pending')

        return 'States: ' + ', '.join(current_states)

    def configuration(self):
        return self._conf

    def is_executing_or_queued_or_done(self):
        s = self.configuration()
        return self._executing in s or self._queued in s or self.is_done()

    def is_dependent_armable(self):
        s = self._node_state_container.state
        return s in (self._armed, self._done, self._done_locked,
                     self._executing, self._queued)

    def is_configurable(self):
        s = self.configuration()
        return self._idle in s and (
            self._error in s or
            self._valid in s or
            self._invalid in s or
            self._armed in s or
            self.is_done())

    def is_executable(self):
        s = self.configuration()
        return self._idle in s and self._armed in s

    def is_debuggable(self):
        return self.is_executable()

    def is_profileable(self):
        return self.is_executable()

    def is_abortable(self):
        s = self.configuration()
        return self._idle in s and (self._queued in s or self._executing in s)

    def is_reloadable(self):
        s = self.configuration()
        return self._idle in s and (
            self._error in s or
            self._valid in s or
            self._invalid in s or
            self._armed in s or
            self._done_locked in s or
            self._done in s)

    def is_armable(self):
        c = self.configuration()
        return self._idle in c and any(s in c for s in
                                       (self._done,
                                        self._done_locked,
                                        self._valid,
                                        self._error))

    def is_disarmable(self):
        c = self.configuration()
        return self._idle in c and any(s in c for s in
                                       (self._done,
                                        self._done_locked,
                                        self._armed,
                                        self._error))

    def is_deletable(self):
        return True

    def is_queueable(self):
        s = self.configuration()
        return self._idle in s and (self._armed in s or self.is_done())

    def is_armed(self):
        return self._armed in self.configuration()

    def is_queued(self):
        return self._queued in self.configuration()

    def is_executing(self):
        return self._executing in self.configuration()

    def has_pending_request(self):
        return self._pending in self.configuration()

    def is_successfully_executed(self):
        return self.is_done()

    def in_error_state(self):
        return self._error in self.configuration()

    def is_configuration_valid(self):
        s = self.configuration()
        return self.is_initialized() and (self._invalid not in s and
                                          self._validating not in s)

    def is_initialized(self):
        s = self.configuration()
        return self._state_machine.isRunning() and self._initializing not in s

    def is_valid(self):
        return self._valid in self.configuration()

    def is_done(self):
        s = self.configuration()
        return self._done in s or self._done_locked in s

    def is_done_locked(self):
        s = self.configuration()
        return self._done_locked in s

    def is_error(self):
        s = self.configuration()
        return self._error in s

    def validate(self):
        core_logger.debug("node.NodeStateMachine.validate called for node %s",
                          self._parent.uuid)
        self.pending_call_sent.emit()
        self.parameters_are_being_validated.emit()

    def validate_done(self, result):
        core_logger.debug(
            "node.NodeStateMachine.validate_done called for node %s",
            self._parent.uuid)
        self.pending_call_returned.emit()
        if result and result > 0:
            self.parameters_are_valid.emit()
        else:
            self.parameters_are_invalid.emit()

    def execute(self):
        self.pending_call_sent.emit()
        self.node_is_executing.emit()

    def execute_done(self, result, locked):
        log_debug_message('execute_done {} with result {}'.format(
            self._parent.uuid, result))
        self.pending_call_returned.emit()
        if result > 0:
            if locked:
                self.node_locked_execution_finished.emit()
            else:
                self.node_execution_finished.emit()
        else:
            self.node_error_occured.emit()

    def abort(self):
        self.pending_call_sent.emit()
        self.node_is_aborting.emit()

    def abort_done(self):
        self.pending_call_returned.emit()
        self.node_has_aborted.emit()

    @QtCore.Slot()
    def _state_changed(self):
        self._conf = self._state_machine.configuration()
        # core_logger.debug('NEW STATE {}'.format(str(self)))


def node_factory(node_id=None, **kwargs):
    cls = factories[node_id]
    return cls(identifier=node_id, **kwargs)


class StatefulNode(NodeStatusInterface, NodeInterface):

    """A node is the """
    initialized = QtCore.Signal()
    parameters_are_valid = QtCore.Signal()
    parameters_are_invalid = QtCore.Signal()
    parameters_are_being_validated = QtCore.Signal()
    node_is_aborting = QtCore.Signal()
    node_has_aborted = QtCore.Signal()
    node_is_queued = QtCore.Signal()
    node_is_executing = QtCore.Signal()
    node_error_occured = QtCore.Signal()
    node_execution_finished = QtCore.Signal()
    node_is_armed = QtCore.Signal()
    pending_call_sent = QtCore.Signal()
    pending_call_returned = QtCore.Signal()

    def __init__(self, **kwargs):
        super(StatefulNode, self).__init__(**kwargs)
        self._init_state_machine_()
        self._ok = True

    def _init_state_machine_(self):
        # Start the state machine and propagate the signals
        self._state_machine = NodeStateMachine(parent=self)
        self._state_machine.execution_finished.connect(self.execution_finished)
        self._state_machine.execution_started.connect(self.execution_started)
        self._state_machine.on_state_aborting.connect(self.on_state_aborting)
        self._state_machine.on_state_armed.connect(self.on_state_armed)
        self._state_machine.on_state_done.connect(self.on_state_done)
        self._state_machine.on_state_error.connect(self.on_state_error)
        self._state_machine.on_state_executing.connect(self.on_state_executing)
        self._state_machine.on_state_invalid.connect(self.on_state_invalid)
        self._state_machine.on_state_queued.connect(self.on_state_queued)
        self._state_machine.on_state_valid.connect(self.on_state_valid)
        self._state_machine.on_state_validating.connect(
            self.on_state_validating)
        self._state_machine.state_changed.connect(self.state_changed)

        self.node_is_queued.connect(self._state_machine.node_is_queued)
        self.node_is_executing.connect(self._state_machine.node_is_executing)

    # Transfer NodeStatusInterface functions

    def is_armed(self):
        return self._state_machine.is_armed()

    def is_queued(self):
        return self._state_machine.is_queued()

    def is_executing(self):
        return self._state_machine.is_executing()

    def has_pending_request(self):
        return self._state_machine.has_pending_request()

    def is_successfully_executed(self):
        return self._state_machine.is_successfully_executed()

    def in_error_state(self):
        return self._state_machine.in_error_state() or not self._ok

    def is_configuration_valid(self):
        return self._state_machine.is_configuration_valid()

    def is_done(self):
        return self._state_machine.is_done()

    def is_done_locked(self):
        return self._state_machine.is_done_locked()

    def is_configurable(self):
        return (self._state_machine.is_configurable() and
                self._incoming_ports_permit_configuration() and
                self._ok)

    def is_executing_or_queued_or_done(self):
        return self._state_machine.is_executing_or_queued_or_done()

    def is_executable(self):
        return (self._state_machine.is_executable() and self._ok)

    def is_armable(self):
        return self._state_machine.is_armable() and self._ok

    def is_debuggable(self):
        return self._state_machine.is_debuggable()

    def is_profileable(self):
        return self._state_machine.is_executable()

    def is_abortable(self):
        return self._state_machine.is_abortable()

    def is_reloadable(self):
        return (self._state_machine.is_reloadable() and self._ok)

    def is_valid(self):
        return self._state_machine.is_valid()

    def is_state_deletable(self):
        return self._state_machine.is_deletable()

    def is_queueable(self):
        return (self._state_machine.is_queueable() and
                self._inputs_are_connected() and self._ok)

    def is_deletable(self):
        # A node is deletable if the state-machine says so
        # and if the node is not involved in any execution chain.
        state_ok = self.is_state_deletable()
        outgoing = self._outgoing_nodes()
        outgoing_ok = all([node.is_state_deletable() for node in outgoing])

        return state_ok and outgoing_ok

    def state_string(self):
        return str(self._state_machine)

    def _incoming_nodes(self):
        incoming = []
        for port in self._inputs:
            source = self._flow.source_port(port)
            if source is None:
                incoming.append(None)
            elif source.node.type in (Type.Node, Type.Flow):
                incoming.append(source.node)
        return incoming

    def _outgoing_nodes(self):
        return [
            dst.node
            for port in self._outputs
            for dst in self._flow.destination_ports(port, atom=True)
            if dst is not None]

    def _outgoing_ports(self):
        return [
            dst
            for port in self._outputs
            for dst in self._flow.destination_ports(port, atom=True)
            if dst is not None]

    def _disarm_all_dependent_nodes(self):
        for port in self._outgoing_ports():
            port.node.disarm(port)

    def is_dependent_armable(self):
        return self._state_machine.is_dependent_armable()

    def _is_source_port_dependent_armable(self, port):
        # TODO(erik): fix proper handling for locked subflows.
        # Currently, the handling relies on treating locked subflows
        # as individual nodes that happen to be set to some fake state.
        sp = self._flow.source_port(port)
        if sp:
            try:
                return sp.node.is_dependent_armable()
            except AttributeError:
                return False
        return False

    def arm(self, port=None):
        if all(self._is_source_port_dependent_armable(p)
               for p in self._inputs):
            self._state_machine.node_is_armed.emit()

    def disarm(self, port=None):
        self._state_machine.node_is_disarmed.emit()

    def clear_error(self):
        if self.in_error_state() and self._ok:
            self._state_machine.node_is_armed.emit()

    def clear_locked_done(self):
        if self._ok and self.in_error_state() or self.is_done_locked():
            self._state_machine.node_is_armed.emit()

    def _arm_all_valid_dependent_nodes(self):
        for port in self._outgoing_ports():
            if port.node.is_valid():
                port.node.arm(port)

    def _arm_all_dependent_nodes(self):
        if self.is_dependent_armable():
            for port in self._outgoing_ports():
                port.node.arm(port)

    def _all_incoming_nodes_are_armed(self):
        incoming = self._incoming_nodes()
        if None in incoming:
            return False

        for node in incoming:
            if not node.is_executable():
                return False
        return True

    def _incoming_ports_permit_configuration(self):
        return True

    def all_incoming_nodes_are_successfully_executed(self):
        incoming = self._incoming_nodes()
        if None in incoming:
            return False
        else:
            for node in incoming:
                if not node.is_successfully_executed() or (
                        node.is_done_locked()):
                    return False
        return True

    def all_incoming_nodes_are_queued_or_executing_or_done(self):
        incoming = self._incoming_nodes()

        if None in incoming:
            return False
        else:
            for node in incoming:
                if not node.is_executing_or_queued_or_done():
                    return False
        return True

    def execution_allowed(self):
        return (
            self.all_incoming_nodes_are_successfully_executed() and
            not self.is_successfully_executed() and
            not self.is_queued())

    def update_progress(self, progress):
        if self.is_executing():
            p = int(progress)
            if p != self._progress:
                self._progress = p
                self.progress_changed.emit(p)

    def progress(self):
        return self._progress

    #
    # State change handlers
    #

    @QtCore.Slot()
    def on_state_validating(self):
        core_logger.debug(
            "Calling appcore.AppCore.validate_node for node %s",
            self.uuid)
        self._flow.app_core.validate_node(self)

    @QtCore.Slot()
    def on_state_error(self):
        self._disarm_all_dependent_nodes()

    @QtCore.Slot()
    def on_state_invalid(self):
        self._disarm_all_dependent_nodes()

    @QtCore.Slot()
    def on_state_valid(self):
        self._disarm_all_dependent_nodes()
        self.arm()

    @QtCore.Slot()
    def on_state_armed(self):
        self._arm_all_dependent_nodes()

    @QtCore.Slot()
    def on_state_queued(self):
        pass

    @QtCore.Slot()
    def on_state_executing(self):
        self._progress = 0

    @QtCore.Slot()
    def on_state_aborting(self):
        self._flow.abort_node(self)

    @QtCore.Slot()
    def on_state_done(self):
        self._arm_all_valid_dependent_nodes()

    @QtCore.Slot()
    def execute(self):
        log_debug_message('execute {}'.format(self.uuid))
        try:
            self._flow.execute_node(self)
        except exceptions.SyFloatingInputError:
            # TODO(Erik): Improve handling of node state in Lambdas.
            pass

    @QtCore.Slot()
    def debug(self):
        self._flow.debug_node(self)

    @QtCore.Slot()
    def profile(self):
        self._flow.profile_node(self)

    @QtCore.Slot()
    def abort(self):
        self._state_machine.abort()

    @QtCore.Slot()
    def set_aborting(self, child_nodes=None):
        self.abort()

    @QtCore.Slot()
    def set_queued(self):
        self._state_machine.node_is_queued.emit()

    @QtCore.Slot()
    def set_started(self):
        self._state_machine.node_is_executing.emit()

    @QtCore.Slot(int)
    def set_done(self, result, locked=False):
        self._state_machine.execute_done(result, locked)

    @QtCore.Slot(int)
    def abort_done(self, child_nodes=None):
        self._progress = 0
        self._state_machine.abort_done()

    @QtCore.Slot(int)
    def validate_done(self, result):
        self._progress = 0
        self._state_machine.validate_done(result)

    def is_initialized(self):
        return self._state_machine.is_initialized()

    def _inputs_are_connected(self):
        connected = [p.is_connected() for p in self.inputs]
        result = False
        if len(connected) == 0:
            result = True
        elif False not in connected:
            result = True

        return result

    def inputs_are_connected(self):
        return self._inputs_are_connected()

    @QtCore.Slot()
    def validate(self):
        if self._ok:
            self._state_machine.validate()

    def configure(self):
        self.clear_error()
        self._flow.app_core.execute_node_parameter_view(self)

    def input_connection_added(self, port):
        self.arm()

    def input_connection_removed(self, port):
        self.disarm()


class Node(StatefulNode):

    _type = Type.Node
    executor = Executors.Node
    _conf_port_name = '__sy_conf__'
    _out_port_name = '__sy_out__'
    _err_port_name = '__sy_err__'
    _both_port_name = '__sy_both__'

    def __init__(self, identifier=None, ports=None,
                 port_format=None, library_node=None, only_conf=None,
                 version=None, name=None, **kwargs):
        assert(identifier)
        super(Node, self).__init__(**kwargs)
        self._identifier = identifier
        self._name = 'No name'
        self._output = ''
        self._progress = 0
        self._generics_map = {}
        if library_node is None:
            library_node = self._flow.app_core.library_node(identifier)
        self._node = library_node
        self._ok = self._node.ok
        self._name = name or self._node.name
        self._version = version
        if version is None and self._node is not None:
            self._version = library_node.version
        self._base_parameter_model = self._node.parameter_model
        self._override_parameter_models = []
        self._ports = ports
        self._port_format = port_format or '1.0'
        self._only_conf_output = only_conf

    def initialize(self):
        """Initialize this node, should be performed after the NodeView has
        been created."""

        def get_def(port_dict, index):
            port_dict = dict(port_dict)
            port_dict['index'] = index
            port_dict['type'] = port_dict['type_base']
            return PortDefinition.from_definition(port_dict)

        if self._ports and self._port_format == '1.1':
            # Build ports from instances.
            for i, input_ in enumerate(self._ports.get('inputs', [])):
                self.create_input(
                    get_def(input_, i), generics_map=self._generics_map)

            for i, output_ in enumerate(self._ports.get('outputs', [])):
                self.create_output(
                    get_def(output_, i), generics_map=self._generics_map)
        else:
            # Build ports from node definition.
            for input_ in self._node.inputs:
                self.create_input(input_, generics_map=self._generics_map)
            for output_ in self._node.outputs:
                self.create_output(output_, generics_map=self._generics_map)

    def update_library_node(self, libraries=None):
        if self._ok:
            if not self._flow.app_core.is_node_in_library(
                    self._identifier, libraries=libraries):
                self._ok = False
                self._update_ports()
                self._state_machine.state_changed.emit()
        else:
            if self._flow.app_core.is_node_in_library(
                    self._identifier, libraries=libraries):
                self._node = self._flow.app_core.library_node(self._identifier)
                self._ok = self._node.ok
                if self._ok:
                    self._update_ports()
                    self.validate()
                    self._state_machine.state_changed.emit()

    def to_copy_dict(self, base_params=False):
        node_dict = self.to_dict()
        node_dict['full_uuid'] = self.full_uuid
        if base_params:
            parameters = self._base_parameter_model.to_ordered_dict()
        else:
            parameters = self.parameter_model.to_dict()
        node_dict['parameters'] = {'data': parameters, 'type': 'json'}
        return node_dict

    def to_dict(self, execute=False):
        inputs = []
        for input_ in self._inputs:
            inputs.append(input_.to_dict(execute))
        outputs = []
        for output_ in self._outputs:
            outputs.append(output_.to_dict(execute))

        if execute:
            parameters = self.parameter_model.to_dict()
        else:
            parameters = self._base_parameter_model.to_ordered_dict()

        result = {
            'id': self.node_identifier,
            'version': self.version,
            'description': self.description,
            'copyright': self.copyright,
            'library': self.library,
            'author': self.author,
            'uuid': self.uuid,
            'x': self.position.x(),
            'y': self.position.y(),
            'width': self.size.width(),
            'height': self.size.height(),
            'label': self.name,
            'parameters': collections.OrderedDict([('data', parameters),
                                                   ('type', 'json')]),
            'ports': {'inputs': inputs,
                      'outputs': outputs},
            'source_file': self.source_file}

        if self._only_conf_output:
            result['only_conf'] = True

        port_format = self._current_port_format()
        if port_format != '1.0':
            result['port_format'] = port_format

        if self.icon:
            result['icon'] = self.icon
        result['source_file'] = self.source_file
        return result

    @property
    def identifier(self):
        """Returns the node identifier (from the node class)."""
        return self.node_identifier

    def add(self, flow=None):
        if flow is not None:
            self._flow = flow
        self._flow.add_node(self)
        for port in self._inputs:
            port.add(flow)
        for port in self._outputs:
            port.add(flow)

    def remove(self):
        # TODO: Remove any overrides for this node?
        self._flow.remove_node(self)

    def needs_filename(self, port):
        return port.node is self and port.type == Type.OutputPort

    def port_viewer(self, port):
        self._flow.app_core.port_viewer(port)

    @property
    def exec_conf_only(self):
        return self._only_conf_output or False

    @exec_conf_only.setter
    def exec_conf_only(self, value):
        self._only_conf_output = value
        self.arm()

    @property
    def base_parameter_model(self):
        return self._base_parameter_model

    def _verify_overrides(self):
        """Verify overrides and remove any invalid overrides."""
        pass

    def has_overrides(self):
        self._verify_overrides()
        return bool(len(self._override_parameter_models))

    def get_overrides_flow(self):
        self._verify_overrides()
        if not self.has_overrides():
            return None

        uuid = self._override_parameter_models[-1][1]
        flow_ = self.flow
        while flow_ is not None:
            if uuid == flow_.uuid:
                return flow_
            flow_ = flow_.flow
        return None

    def get_override_parameter_models_dict(self):
        """A string version of the entire overrides structure."""
        self._verify_overrides()
        return [(m.to_dict(), uuid)
                for m, uuid in self._override_parameter_models]

    def get_override_parameter_model(self, flow):
        self._verify_overrides()
        for m, uuid in self._override_parameter_models:
            if uuid == flow.uuid:
                return m
        return None

    def set_override_parameter_model(self, parameter_model, flow):
        self._verify_overrides()

        uuids = []
        flow_ = self.flow
        while flow_ is not None:
            uuids.append(flow_.uuid)
            flow_ = flow_.flow
        old_full_indexes = [uuids.index(uuid)
                            for m, uuid in self._override_parameter_models]
        new_full_index = uuids.index(flow.uuid)

        # new_index is the index of the new override parameters in the existing
        # list of overrides.
        new_index = sorted(set(old_full_indexes + [new_full_index])).index(
            new_full_index)

        if parameter_model is None:
            # Delete override parameters
            if new_full_index in old_full_indexes:
                # Delete one of the old overrides.
                del self._override_parameter_models[new_index]
            else:
                # Trying to delete override parameters that don't exist.
                return
                # raise Exception(
                #     "Trying to delete override parameters that don't exist.")
        else:
            # Add or update override parameters
            if new_full_index in old_full_indexes:
                # Update one of the old overrides.
                self._override_parameter_models[new_index] = (
                    parameter_model, flow.uuid)
            elif new_index >= len(self._override_parameter_models):
                # Append a new layer of overrides.
                self._override_parameter_models.append(
                    (parameter_model, flow.uuid))
            else:
                # Insert a new layer of overrides.
                self._override_parameter_models.insert(
                    new_index, (parameter_model, flow.uuid))

    def _port_definition_name_lookup(self, defs):
        return {d.get('name'): d for d in defs}

    def _port_name_group(self, ports, name):
        return [port for port in ports if port.port_definition.name == name]

    def _any_connection_is_connected(self):
        return any(itertools.chain(
            (self.flow.source_port(p, False, True)
             for p in self._inputs),
            (self.flow.destination_ports(p, False, False)
             for p in self._outputs)))

    def _infertype_replace(self, replacements):
        flowlib.infertype_flow(self.flow, check=True, replace=replacements)

    def _create_port_type_replacements(self, kind, name):
        res = {}

        inputs = self._port_definition.get('inputs', [])
        outputs = self._port_definition.get('outputs', [])
        ns = self._enumerate_port_names({kind[:-1]: {name: 1}})
        inputs, outputs = port_util.instantiate(inputs, outputs, ns)

        # Drop the extra definition.
        i = None
        ports_ = {'inputs': inputs, 'outputs': outputs}[kind]
        for j, port in enumerate(ports_):
            if port.get('name', '') == name:
                i = j
        del ports_[i]

        mapping = {}
        for pdef, port in itertools.chain(zip(inputs, self._inputs),
                                          zip(outputs, self._outputs)):

            dtype = datatypes.DataType.from_str(pdef['type'])
            dtype.identify(mapping)
            res[port] = dtype

        return res

    def _delete_port_type_replacements(self, kind, name):
        res = {}
        inputs = self._port_definition.get('inputs', [])
        outputs = self._port_definition.get('outputs', [])

        ns = self._enumerate_port_names()

        i = None
        ports_ = {'inputs': self._inputs, 'outputs': self._outputs}[kind]
        for j, port in enumerate(ports_):
            if port.name == name:
                i = j

        ns[kind[:-1]][name] -= 1
        inputs, outputs = port_util.instantiate(inputs, outputs, ns)

        mapping = {}
        for ports_ in [inputs, outputs]:
            for port in ports_:
                dtype = datatypes.DataType.from_str(port['type'])
                dtype.identify(mapping)

        dtype = datatypes.DataType.from_str('<a>')
        dtype.identify({})
        ports_.insert(i, {'type': dtype})

        for pdef, port in itertools.chain(zip(inputs, self._inputs),
                                          zip(outputs, self._outputs)):
            dtype = datatypes.DataType.from_str(pdef['type'])
            dtype.identify(mapping)
            res[port] = dtype

        return res

    def _can_create_port(self, kind, ports, name):
        res = False
        lookup = self._port_definition_name_lookup(
            self._port_definition.get(kind, []))
        if name:
            try:
                def_ = lookup[name]
            except KeyError:
                return False
            maxn = port_util.maxno(def_.get('n', 1))
            if len(self._port_name_group(ports, name)) < maxn:
                try:
                    self._infertype_replace(
                        self._create_port_type_replacements(kind, name))
                    res = True
                except exceptions.SyInferTypeError:
                    pass
                except KeyError:
                    return False
        return res

    def _can_delete_port(self, kind, ports, port):
        res = False

        lookup = self._port_definition_name_lookup(
            self._port_definition.get(kind, []))
        name = port.name
        if name:
            def_ = lookup[name]
            minn = port_util.minno(def_.get('n', 1))
            ok = len(self._port_name_group(ports, name)) > minn
            if ok:
                try:
                    self._infertype_replace(
                        self._delete_port_type_replacements(kind, name))
                    res = True
                except exceptions.SyInferTypeError:
                    pass
                except KeyError:
                    return False
        return res

    def can_create_input(self, name):
        return len(self._inputs) < max_nports and self._can_create_port(
            'inputs', self._inputs, name)

    def can_delete_input(self, port):
        return self._can_delete_port('inputs', self._inputs, port)

    def can_create_output(self, name):
        output_names = set([output.name for output in self._outputs])

        ok = True
        if name in {self._out_port_name, self._err_port_name}:
            ok = self._both_port_name not in output_names
        elif name == self._both_port_name:
            ok = all(p not in output_names
                     for p in [self._out_port_name, self._err_port_name])
        return ok and (
            len(self._outputs) < max_nports and self._can_create_port(
                'outputs', self._outputs, name))

    def can_delete_output(self, port):
        return self._can_delete_port('outputs', self._outputs, port)

    def _enumerate_port_names(self, ns=None):
        ns = dict(ns or {})

        for kind, group in [('input', self._inputs),
                            ('output', self._outputs)]:
            ns_kind = ns.setdefault(kind, {})
            for p in group:
                name_ = p.name
                if name_:
                    ns_kind.setdefault(name_, 0)
                    ns_kind[name_] += 1
        return ns

    def _update_ports(self):
        inputs = self._port_definition.get('inputs', [])
        outputs = self._port_definition.get('outputs', [])
        ns = self._enumerate_port_names()
        inputs, outputs = port_util.instantiate(inputs, outputs, ns)
        self._update_port_types(inputs, outputs)

    def _update_port_types(self, inputs, outputs):
        self._generics_map.clear()
        for def_, p in itertools.chain(zip(inputs, self._inputs),
                                       zip(outputs, self._outputs)):
            p.datatype_base = datatypes.DataType.from_str(def_['type'])
        flowlib.infertype_flow(self.flow)

    def _create_named_port(self, name, kind, ports_fn, create_fn):
        ns = self._enumerate_port_names({kind: {name: 1}})

        inputs = self._port_definition.get('inputs', [])
        outputs = self._port_definition.get('outputs', [])
        inputs, outputs = port_util.instantiate(inputs, outputs, ns)

        pos = 0
        pc = None
        for i, p in enumerate(ports_fn(inputs, outputs)):
            if p.get('name') == name:
                pos = i
                pc = p

        port = create_fn(
            self,
            port_definition=PortDefinition.from_definition(pc),
            generics_map=self._generics_map, pos=pos)

        self._update_port_types(inputs, outputs)
        return port

    def _delete_port(self, port):
        inputs = self._port_definition.get('inputs', [])
        outputs = self._port_definition.get('outputs', [])
        ns = self._enumerate_port_names()
        inputs, outputs = port_util.instantiate(inputs, outputs, ns)
        self._update_port_types(inputs, outputs)

    def delete_input(self, port):
        self.remove_input(port)
        self.flow.remove_input_port(port)
        self._delete_port(port)
        self.arm()

    def delete_output(self, port):
        self.remove_output(port)
        self.flow.remove_output_port(port)
        self._delete_port(port)

    def create_named_output(self, name):
        port = self._create_named_port(
            name, 'output', lambda i, o: o, self._flow.create_output_port)
        self.output_port_created.emit(port)
        self.arm()
        return port

    def create_named_input(self, name):
        port = self._create_named_port(
            name, 'input', lambda i, o: i, self._flow.create_input_port)
        self.input_port_created.emit(port)
        self.disarm()
        return port

    def insert_named_input(self, pos, port):
        self.insert_input(pos, port)
        self._delete_port(port)
        self.input_port_created.emit(port)

    def insert_named_output(self, pos, port):
        self.insert_output(pos, port)
        self._delete_port(port)
        self.output_port_created.emit(port)
        self.arm()

    def _creatable_port_defs(self, defs):
        return [def_ for def_ in defs if (
            port_util.maxno(def_.get('n', 1)) >
            port_util.minno(def_.get('n', 1)))]

    def createable_input_defs(self):
        return self._creatable_port_defs(
            self._port_definition.get('inputs', []))

    def createable_output_defs(self):
        return self._creatable_port_defs(
            self._port_definition.get('outputs', []))

    def _current_port_format(self):
        # Any numbered ports in use.
        ns = self._enumerate_port_names()
        ns_default = {}
        for kind in ['input', 'output']:
            ns_kind = ns_default.setdefault(kind, {})
            for def_ in self._port_definition.get(kind + 's', []):
                name = def_.get('name')
                if name:
                    defno = port_util.defno(def_.get('n'))
                    if defno > 0:
                        ns_kind[name] = defno

        return '1.0' if ns == ns_default else '1.1'

    @property
    def author(self):
        return self._node.author

    @property
    def description(self):
        return self._node.description

    @property
    def copyright(self):
        return self._node.copyright

    @property
    def version(self):
        return self._version or self._node.version

    @version.setter
    def version(self, version):
        self._version = version

    @property
    def library_node_name(self):
        return self._node.name

    @property
    def library_node(self):
        return self._node

    @property
    def library(self):
        return self._node.library

    @property
    def has_svg_icon(self):
        return self._node.has_svg_icon

    @property
    def has_docs(self):
        return self._node.has_docs

    @property
    def html_docs(self):
        return self._node.html_docs

    @property
    def html_base_uri(self):
        return self._node.html_base_uri

    @property
    def svg_icon_data(self):
        return self._node.svg_icon_data

    @property
    def node_identifier(self):
        return self._node.node_identifier

    @property
    def icon(self):
        return self._node.icon

    @property
    def has_conf_output(self):
        for port in self.outputs:
            if port.name == self._conf_port_name:
                return True
        return False

    @property
    def _port_definition(self):
        inputs = self._node.port_definition.get('inputs', [])
        outputs = self._node.port_definition.get('outputs', [])
        parameter_model = self._node.parameter_model
        bdefs_in = []
        bdefs_out = [
            collections.OrderedDict(
                [('name', name), ('description', desc),
                 ('n', (0, 1, 0)), ('scheme', 'hdf5'), ('type', 'text')])
            for (name, desc) in [('__sy_out__', 'Output Text'),
                                 ('__sy_err__', 'Warning Text'),
                                 ('__sy_both__', 'Output and Warning Text')]]
        if not (parameter_model and
                parameter_model.is_empty(ignore_group=True)):
            for bdefs in [bdefs_in, bdefs_out]:
                bdefs.append(collections.OrderedDict(
                    [('name', self._conf_port_name),
                     ('description', 'Configuration port'),
                     ('n', (0, 1, 0)), ('scheme', 'hdf5'), ('type', 'json')]))
        return collections.OrderedDict(
            [('inputs', inputs + bdefs_in),
             ('outputs', outputs + bdefs_out)])

    def _get_parameter_model(self):
        self._verify_overrides()
        if len(self._override_parameter_models):
            return self._override_parameter_models[-1][0]
        return self._base_parameter_model

    def _set_parameter_model(self, new_model):
        self._verify_overrides()
        if len(self._override_parameter_models):
            flow_uuid = self._override_parameter_models[-1][1]
            self._override_parameter_models[-1] = (new_model, flow_uuid)
        self._base_parameter_model = new_model

    # # Using lambda to delay attribute lookup on self._get_parameter_model and
    # # self._set_parameter_model to allow overriding those methods.
    # parameter_model = property(lambda self: self._get_parameter_model(),
    #                            lambda self, m: self._set_parameter_model(m))

    @property
    def parameter_model(self):
        return self._get_parameter_model()

    @parameter_model.setter
    def parameter_model(self, value):
        return self._set_parameter_model(value)

    @property
    def parent(self):
        return self._node.parent

    @property
    def tags(self):
        return self._node.tags

    @property
    def source_file(self):
        return self._node.source_uri

    @property
    def class_name(self):
        return self._node.class_name

    @property
    def needs_validate(self):
        return self._node.needs_validate

    @property
    def quit_after_exec(self):
        return False


class BuiltinNode(Node):

    @property
    def needs_validate(self):
        return False

    # def is_configuration_valid(self):
    #     return True
