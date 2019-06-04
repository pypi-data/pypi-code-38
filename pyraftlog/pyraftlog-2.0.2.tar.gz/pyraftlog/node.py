import logging
import random
import sys
import threading
import time

import message
from .state import State, STATE_ROLE_FOLLOWER, STATE_ROLE_CANDIDATE, STATE_ROLE_LEADER, get_role_name

NODE_MODE_ACTIVE = 1
"""
ActiveNodes take part in all votes, keep track of the consensus log, and immediately converts to a Candidate
on election timeout.
"""

NODE_MODE_PASSIVE = 2
"""
Passive mode take part in all votes, keep track of the consensus log, but never nominates itself for leadership.
"""

NODE_MODE_RELUCTANT = 3
"""
ReluctantNodes take part in all votes, keep track of the consensus log, but only converts to a Candidate if it
receives only request requests from Candidates behind in the consensus log history.
"""

_modeNames = {
    NODE_MODE_ACTIVE: 'active',
    NODE_MODE_RELUCTANT: 'reluctant',
    NODE_MODE_PASSIVE: 'passive',
    'active': NODE_MODE_ACTIVE,
    'reluctant': NODE_MODE_RELUCTANT,
    'passive': NODE_MODE_PASSIVE,
}

"""
Consensus network has a leader and there is a majority of nodes connected.
"""
NODE_STATUS_GREEN = 'green'

"""
Consensus network has a leader, there is a majority of nodes connected, but applied index is significantly behind
commit index.
"""
NODE_STATUS_YELLOW = 'yellow'

"""
Consensus network either does not have a leader or there is not a majority of nodes connected.
"""
NODE_STATUS_RED = 'red'


def get_mode_name(mode):
    return _modeNames.get(mode, 'Unknown mode %s' % str(mode))


class Node(object):
    """
    A Consensus Node can be in one of three states:

    1.  `Follower`: the default state
    2.  `Candidate`: leader has timed out
    3.  `Leader`: elected leader, responsible for accepting commands

    There are also three different modes a consensus node can be in:

    1.  `NODE_MODE_ACTIVE`: the standard mode and will attempt to become leader on timeout
    2.  `NODE_MODE_RELUCTANT`: non-standard mode that will only become a leader while no eligible nodes are available
    3.  `NODE_MODE_PASSIVE`: non-standard mode that will never become a leader

    A consensus node needs to know to location of all other nodes in the network and must be able to persist its
    current state so that in the event of a failure it can be restored.
    """

    def __init__(self, mode, name, neighbourhood, storage,
                 election_timeout=0.5, heartbeat_timeout=0.25, vote_timeout=0.15,
                 logger=None):
        """
        :param mode: `NODE_MODE_ACTIVE`|`NODE_MODE_PASSIVE`|`NODE_MODE_RELUCTANT`
        :param name: <hostname/ip_address>:<port>
        :param neighbourhood: List of neighbours
        :param storage: Storage for the Node's state
        :param election_timeout: follower election timeout in seconds
        :param heartbeat_timeout: leader heartbeat timeout in seconds
        :param vote_timeout: candidate vote timeout in seconds
        :param logger:
        :type mode: int
        :type name: str
        :type neighbourhood: list[str]
        :type storage: pyraftlog.storage.Storage
        :type election_timeout: float
        :type heartbeat_timeout: float
        :type vote_timeout: float
        :type logger: logging.Logger
        """
        self.mode = mode
        self.neighbourhood = list(neighbourhood)
        self.neighbours = list(neighbourhood)
        self.storage = storage

        # Ensure neighbourhood includes this node
        self.neighbourhood.append(name)
        self.neighbourhood = list(set(self.neighbourhood))
        # Ensure neighbours excludes this node
        self.neighbours = list(set(self.neighbours))
        self.neighbours.remove(name)

        self.election_timeout = election_timeout
        self.heartbeat_timeout = heartbeat_timeout
        self.vote_timeout = vote_timeout

        self.logger = logger or logging.getLogger(__name__)

        self.apply_event = threading.Event()
        self.timeout_event = threading.Event()
        self.lock = threading.Lock()
        self.leader = (None, None)
        self.transport = None
        self.request_address = None
        self.state = storage.retrieve(State(STATE_ROLE_FOLLOWER, name, neighbourhood))
        self.time_outs = dict.fromkeys(self.neighbours, time.time())
        self.back_offs = dict.fromkeys(self.neighbours, 0.0)
        self.last_heard = dict.fromkeys(self.neighbours)
        self.processing_message = dict.fromkeys(self.neighbours, False)
        self.synchronised = dict.fromkeys(self.neighbours, False)

        self.leadership_required = self.mode == NODE_MODE_ACTIVE
        self.apply_thread = None
        self.transport_thread = None
        self.neighbour_threads = {}
        self.active = False
        self.shutdown_flag = False

        self.start_time = time.time()
        self.extend_timeout()

    def __del__(self):
        self.storage.persist(self.state)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.storage.persist(self.state)

    @property
    def name(self):
        return self.state.name

    def handle_signal(self, signum, frame):
        """
        Handles a SIGINT signal, which will cause the node to shutdown and then call `sys.exit(signum)`.

        :param signum:
        :param frame:
        :type signum: int
        :rtype: None
        """
        self.shutdown()
        sys.exit(signum)

    def reset_state(self, new_data):
        """
        @TODO clarify how this functions.
        Reset the state of the consensus node to a previous point.

        :param new_data:
        :type new_data: dict
        :rtype: None
        """
        self.log(logging.CRITICAL, 'Resetting state: %s', new_data)
        self.state.role = STATE_ROLE_FOLLOWER
        self.state.set_current_state(new_data)

        for neighbour in self.neighbours:
            self.state.next_index[neighbour] = self.state.log.index() + 1
            self.state.match_index[neighbour] = 0

    def is_leader(self, neighbour=None):
        """
        If no `neighbour` is given this whether this `Node` is the leader
        otherwise if `neighbour` is the leader.

        :param neighbour: If provided, check if the neighbour is leader
        :type neighbour: str
        :return: If this `Node` is the leader or if `neighbour` is the leader
        :rtype: bool
        """
        if neighbour is None:
            return self.state.role == STATE_ROLE_LEADER
        else:
            return self.leader[0] == neighbour

    def is_eligible(self, transport=None):
        """
        Check whether the node is eligible for leadership.

        :param transport: Transport being used
        :type transport: pyraftlog.transport.Transport
        :return: Whether the node is eligible to become leader
        :rtype: bool
        """
        # Passive nodes are never eligible
        if self.mode == NODE_MODE_PASSIVE:
            return False

        # Reluctant nodes are only eligible if leadership is required
        if self.mode == NODE_MODE_RELUCTANT and not self.leadership_required:
            return False

        # Active nodes are always eligible (while they have majority)
        return not transport or self.has_majority(1 + len(transport.connected()))

    def has_leader(self):
        """
        :return: True if there currently is an elected Leader
        :rtype: bool
        """
        return self.is_leader() or self.leader[0] is not None

    def get_leader(self):
        """
        :return: The current leader
        :rtype: str
        """
        return self.name if self.is_leader() else self.leader[0]

    def get_request_address(self):
        """
        :return: The address and port that commands should be sent to
        :rtype: str
        """
        return self.request_address if self.is_leader() else self.leader[1]

    def has_majority(self, count):
        """
        Check if the number provided is a majority of nodes in the consensus network.

        :param count: A number of consensus node
        :type count: int
        :return: True if `count` is a majority
        :rtype: bool
        """
        return count > int((len(self.neighbourhood) - 1) / 2)

    def status(self):
        """
        :return: The status of the node
        :rtype: str
        """
        # If there is no transport available or no leader has been elected
        if self.transport is None or not self.has_leader():
            return NODE_STATUS_RED
        # If this node is the leader but there is not a majority to gain consensus
        elif self.is_leader() and not self.has_majority(len(self.transport.connected()) + 1):
            return NODE_STATUS_RED
        # If this node is the leader but not all neighbours are connected
        elif self.is_leader() and len(self.transport.connected()) != len(self.neighbours):
            return NODE_STATUS_YELLOW
        # If the difference between committed and applied is too large
        elif (self.state.last_applied - self.state.commit_index) > 500:
            return NODE_STATUS_YELLOW
        # If the log is being reduced and the log length is too large
        elif self.state.log_reduction and len(self.state.log) > 500:
            return NODE_STATUS_YELLOW
        else:
            return NODE_STATUS_GREEN

    def log(self, level, msg, *args):
        """
        Log a message of the specified level.

        :param level: logging level
        :param msg: Message to be logged
        :param args: Arguments to be applied to `msg`
        :type level: int
        :type msg: str
        :rtype: None
        """
        args = args or tuple()
        basic = (self.name, get_mode_name(self.mode), get_role_name(self.state.role), self.state.current_term)
        self.logger.log(level, '[%s][%s] %-9s (%d) ' + msg, *(basic + args))

    def append_entry(self, command):
        """
        Append a new command entry.

        :param command: Command to be performed
        :type command: Any
        :return: The index of the created entry
        :rtype: int|False
        """
        entry_index = self.state.append_log_entry(command)
        self.timeout_event.set()

        # Only persist if there were changes
        if entry_index:
            self.log(logging.DEBUG, 'Appended log entry at index %d', entry_index)
            self.storage.persist(self.state)

        return entry_index

    def apply_entry(self, state):
        """
        Apply the next entry.

        :param state:
        :type state: pyraftlog.state.State
        :rtype: None
        """
        # increment the state's last applied
        state.last_applied += 1
        state.cluster_applied[self.name] = state.last_applied

        # persist changes
        self.storage.persist(state)

        self.log(logging.INFO, 'Applied entry: %s', state.last_applied)

        self.state.statistics.set_applied_timestamp(self.state.commit_index, time.time())

    def on_message(self, msg):
        """
        Perform the appropriate action(s) based on the message received.

        :param msg: The message to process
        :type msg: pyraftlog.message.Message
        :return: The response message
        :rtype: pyraftlog.message.Message|None
        """
        with self.lock:
            response = None
            extend_timeout = False
            self.log(logging.DEBUG, 'Message received: %s', msg)
            self.last_heard[msg.sender] = time.time()
            self.processing_message[msg.sender] = True

            # If request/response message term > our current term become a follower
            if msg.term > self.state.current_term:
                self.log(logging.INFO, 'This Node is behind the current term of %s (term=%d)', msg.sender, msg.term)
                if self.state.role == STATE_ROLE_LEADER:
                    self.state.role = STATE_ROLE_FOLLOWER
                self.state.current_term = msg.term

            # Perform an action based on the received message type and current state
            if msg.procedure == message.APPEND_ENTRIES:
                if self.state.role != STATE_ROLE_FOLLOWER:
                    self.state.role = STATE_ROLE_FOLLOWER
                    self.state.current_term = msg.term

                # Note if the leadership has changed
                if self.leader[0] != msg.sender:
                    self.log(logging.CRITICAL, 'Accepted Leadership: %s', msg.sender)

                self.leader = (msg.sender, msg.data['request_address'])
                response = self.state.on_append_entries(self, msg)
                self.log(logging.INFO, 'Append entries: %r (%s)', response.data['response'], response.data['reason'])

                # Extend the timeout for the message sender
                extend_timeout = True

            elif msg.procedure == message.VOTE_REQUEST:
                response = self.state.on_vote_request(self, msg)

                # Extend timeout if the candidate was eligible and we're a follower
                extend_timeout = response.data['eligible'] and self.state.role == STATE_ROLE_FOLLOWER

                # Leadership might be required
                self.leadership_required = self.mode == NODE_MODE_ACTIVE or \
                    self.state.current_term not in self.state.voted_for or \
                    self.state.voted_for[self.state.current_term] == self.name or \
                    not response.data['response']

                if self.mode == NODE_MODE_RELUCTANT and not response.data['eligible']:
                    self.log(logging.INFO, 'Candidate was not eligible: %s', msg.sender)

            elif msg.procedure == message.VOTE_RESPONSE:
                response = self.state.on_vote_response(self, msg)

            elif msg.procedure == message.APPEND_RESPONSE:
                response = self.state.on_append_response(self, msg)
                # Check if the message sender is an eligible leader
                eligible = msg.mode == NODE_MODE_ACTIVE and self.state.log.index() == self.state.match_index[msg.sender]
                # Leadership is no longer required if (any) sender is eligible
                self.leadership_required = self.leadership_required and not eligible
                if self.mode == NODE_MODE_RELUCTANT and eligible:
                    self.log(logging.INFO, 'Message sender is eligible: %s', msg.sender)

            # Entries are applied elsewhere

            # Update the current state
            if extend_timeout:
                self.extend_timeout(msg.sender)
            self.processing_message[msg.sender] = False

            # Return the response
            if response and response.recipient in self.neighbours:
                self.log(logging.DEBUG, 'Sending response : %s', response)
                return response
            return None

    def get_wait_for(self, neighbour, cur_time=None):
        """
        Calculate the number of seconds to wait before checking timeouts.

        :param neighbour: Neighbour to check
        :param cur_time: Current time
        :type neighbour: str
        :type cur_time: float
        :return: Seconds to wait
        :rtype: float
        """
        cur_time = cur_time if cur_time is not None else time.time()
        timeout = max(self.time_outs.values()) if self.state.role == STATE_ROLE_FOLLOWER else self.time_outs[neighbour]

        return max(timeout, self.back_offs[neighbour]) - cur_time

    def has_timed_out(self, neighbour=None, cur_time=None):
        """
        Check if `neighbour` has timed out. Alternatively, if no `neighbour` is provided check if all neighbours have
        timed out.

        :param neighbour: Neighbour to check
        :param cur_time: Current time
        :type neighbour: str
        :type cur_time: float
        :return: True if `neighbour` has timed out
        :rtype: bool
        """
        cur_time = cur_time if cur_time is not None else time.time()

        if neighbour is None:
            return not any(self.processing_message.values()) and max(self.time_outs.values()) <= cur_time
        else:
            return not self.processing_message[neighbour] and self.time_outs[neighbour] <= cur_time

    def has_back_off(self, neighbour=None, cur_time=None):
        """
        Check if `neighbour` has backed off. Alternatively, if no `neighbour` is provided check if any neighbour has
        backed off.

        :param neighbour: Neighbour to check
        :param cur_time: Current time
        :type neighbour: str
        :type cur_time: float
        :return: True if `neighbour` has timed out
        :rtype: bool
        """
        cur_time = cur_time if cur_time is not None else time.time()

        if neighbour is None:
            return max(self.back_offs.values()) > cur_time
        else:
            return self.back_offs[neighbour] > cur_time

    def reset_timeout(self, neighbour=None, timeout_time=None):
        """
        Reset the `neighbour` timeout to the `timeout_time`.
        If `timeout_time` is not provided reset to `time.time()` which will cause the neighbour to immediately timeout.
        If `neighbour` is not provided reset all neighbours which will cause all neighbours to immediately timeout.

        :param neighbour: Neighbour to reset timeout
        :param timeout_time: The new timeout out
        :type neighbour: str
        :type timeout_time: float
        :rtype: None
        """
        timeout_time = timeout_time or time.time()
        if neighbour is not None:
            self.log(logging.DEBUG, 'Timeout reset for %s', neighbour)
            self.time_outs[neighbour] = timeout_time
        else:
            self.log(logging.DEBUG, 'Timeouts reset')
            self.time_outs = dict.fromkeys(self.neighbours, timeout_time)

    def extend_timeout(self, neighbour=None):
        """
        Extend the timeout of `neighbour`. If `neighbour` is not provided extend the timeout of all neighbours.

        :param neighbour: Neighbour to extend to timeout
        :type neighbour: str|None
        :rtype: None
        """
        cur_time = time.time()
        if neighbour is not None:
            current = self.time_outs[neighbour]
            updated = self.next_timeout(current, cur_time)
            self.log(logging.DEBUG, 'Timeout extended for %s [%+f]', neighbour, updated-cur_time)
            self.time_outs[neighbour] = updated

        else:
            current = max(self.time_outs.values())
            updated = self.next_timeout(current, cur_time)
            self.log(logging.DEBUG, 'Timeout extended [%+f]', updated-cur_time)
            self.time_outs = dict.fromkeys(self.neighbours, updated)

    def next_timeout(self, prev_time, cur_time=None):
        """
        Get the next timeout time.

        :param prev_time: Previous timeout time
        :param cur_time: Current time
        :type prev_time: float
        :type cur_time: float
        :rtype: float
        """
        cur_time = cur_time if cur_time is not None else time.time()
        # If leader, next timeout is when the next heartbeat is due
        if self.state.role == STATE_ROLE_LEADER:
            multiplier = 1 + int((cur_time - prev_time) / self.heartbeat_timeout)
            return max(prev_time, prev_time + (multiplier * self.heartbeat_timeout))

        # If active candidate, next timeout is uniformly random between vote timeout and two times that
        elif self.state.role == STATE_ROLE_CANDIDATE and self.leadership_required:
            return max(prev_time, cur_time + random.uniform(self.vote_timeout, 2 * self.vote_timeout))

        # If reluctant candidate, next timeout is maximum (passive node's should never become/remain candidates)
        elif self.state.role == STATE_ROLE_CANDIDATE:
            return max(prev_time, cur_time + (2 * self.vote_timeout))

        # If active follower, next timeout is uniformly random between election timeout and two times that
        elif self.state.role == STATE_ROLE_FOLLOWER and self.leadership_required:
            return max(prev_time, cur_time + random.uniform(self.election_timeout, 2 * self.election_timeout))

        # If reluctant/passive follower, next timeout is maximum
        else:
            return max(prev_time, cur_time + (2 * self.election_timeout))

    def activate(self, transport):
        """
        Start the threads to active this node.

        :param transport: Transport to activate and use for inter node communication
        :type transport: pyraftlog.transport.Transport
        :rtype: None
        """
        self.log(logging.WARN, 'Node starting')
        self.active = True
        self.shutdown_flag = False

        self.transport = transport
        self.extend_timeout()

        # Apply entries thread
        self.apply_thread = threading.Thread(target=self.thread_apply_entries)
        self.apply_thread.daemon = True
        self.apply_thread.start()

        # Publish/timeout thread
        for neighbour in self.neighbours:
            thread = threading.Thread(target=self.thread_neighbour_timeout, args=[transport, neighbour])
            thread.daemon = True
            thread.start()
            self.neighbour_threads[neighbour] = thread

        # Subscribe thread
        self.transport_thread = threading.Thread(target=transport.subscribe, args=[self])
        self.transport_thread.daemon = True
        self.transport_thread.start()

    def deactivate(self):
        """
        Stop all threads gracefully and deactivate this node (Leaves API running).

        :rtype: None
        """
        self.log(logging.WARN, 'Deactivating Node')
        # Set active flag to False
        self.active = False
        if self.transport:
            self.transport.shutdown()

        # Wait for threads to stop
        while self.apply_thread and self.apply_thread.is_alive():
            self.apply_event.set()

        neighbours_stopped = False
        while not neighbours_stopped:
            self.timeout_event.set()
            neighbours_stopped = True
            for thread in self.neighbour_threads.values():
                if thread.is_alive():
                    neighbours_stopped = False

        # Revert to a follower
        self.state.role = STATE_ROLE_FOLLOWER

    def shutdown(self):
        """
        Stop all threads gracefully and shutdown this node.

        :rtype: None
        """
        self.log(logging.INFO, 'Node shutting down')
        self.deactivate()
        self.shutdown_flag = True

    def thread_apply_entries(self):
        """
        Start a while true loop to apply committed entries.

        :rtype: None
        """
        self.log(logging.DEBUG, 'Starting to apply entries')
        while self.active:
            # If commit index > last applied and not set to auto apply
            if self.state.commit_index > self.state.last_applied:
                try:
                    self.apply_entry(self.state)
                except Exception as e:
                    self.log(logging.CRITICAL, '(%s) %s', type(e), e)

                # Yield to whatever other thread may be ready
                time.sleep(0)
            else:
                # Wait for the next apply event
                self.apply_event.wait()
                self.apply_event.clear()

        self.log(logging.DEBUG, 'Thread for applying entries has stopped')

    def thread_neighbour_timeout(self, transport, neighbour):
        """
        While node is active, check for the appropriate timeouts and perform the appropriate action.

        :param transport: Transport to be used
        :param neighbour: Neighbour that will be monitored
        :type transport: pyraftlog.transport.Transport
        :type neighbour: str
        :rtype: None
        """
        self.log(logging.DEBUG, 'Starting thread to work with %s', neighbour)
        while self.active:
            # Wait until the next timeout, respecting back offs but waking for append entry commands
            if self.has_back_off(neighbour) or not self.state.missing_entries(neighbour):
                self.timeout_event.wait(self.get_wait_for(neighbour))
                self.timeout_event.clear()

            try:
                if self.state.role == STATE_ROLE_LEADER and self.state.missing_entries(neighbour):
                    self.on_behind_entries(transport, neighbour)

                elif self.state.role == STATE_ROLE_LEADER and self.has_timed_out(neighbour):
                    self.on_timeout_leader(transport, neighbour)

                elif self.state.role == STATE_ROLE_CANDIDATE and self.has_timed_out(neighbour):
                    self.on_timeout_candidate(transport, neighbour)

                elif self.state.role == STATE_ROLE_FOLLOWER and self.has_timed_out():
                    self.on_timeout_follower(transport, neighbour)

            except Exception as e:
                self.synchronised[neighbour] = False
                transport.handle_exception(neighbour, e)
                self.extend_timeout(neighbour)
                # Back off this neighbour until the next time out is reached
                self.back_offs[neighbour] = self.time_outs[neighbour]

        self.log(logging.DEBUG, 'Thread for neighbour %s has stopped', neighbour)

    def on_behind_entries(self, transport, neighbour):
        """
        Send up to `pyraftlog.state.APPEND_MAX` missing entries over to `neighbour`.

        :param transport: Transport to be used
        :param neighbour: Neighbour in question
        :type transport: pyraftlog.transport.Transport
        :type neighbour: str
        :rtype: None
        """
        # Send the message to the neighbour
        response = transport.publish(self, self.state.append_entry_message(self, neighbour))

        # Process any response given
        if response:
            self.on_message(response)
            self.extend_timeout(neighbour)
        else:
            # If failed to respond back off
            self.back_offs[neighbour] = self.time_outs[neighbour]

    def on_timeout_leader(self, transport, neighbour):
        """
        Send `neighbour` a heartbeat.

        :param transport: Transport to be used
        :param neighbour: Neighbour in question
        :type transport: pyraftlog.transport.Transport
        :type neighbour: str
        :rtype: None
        """
        # Check we are still eligible
        if not self.is_eligible(transport):
            self.state.role = STATE_ROLE_FOLLOWER
            self.transport.close(neighbour)
            self.extend_timeout()
            return

        self.log(logging.DEBUG, 'Firing heartbeat for %s', neighbour)
        response = transport.publish(self, self.state.append_entry_message(self, neighbour, True))
        self.extend_timeout(neighbour)

        if response:
            self.on_message(response)
        else:
            # If failed to respond back off
            self.back_offs[neighbour] = self.time_outs[neighbour]

    def on_timeout_candidate(self, transport, neighbour):
        """
        Trigger an election (and potentially increment the current term).

        :param transport: Transport to be used
        :param neighbour: Neighbour in question
        :type transport: pyraftlog.transport.Transport
        :type neighbour: str
        :rtype: None
        """
        # Check we are still eligible
        if not self.is_eligible():
            self.state.role = STATE_ROLE_FOLLOWER
            return

        # Increment current term
        if self.state.increment_term(self.name, neighbour):
            self.log(logging.INFO, 'Starting new election')

            # Persist changes
            self.storage.persist(self.state)

            # Reset timeouts to send the initial vote request
            self.reset_timeout()

        self.log(logging.DEBUG, 'Sending vote request to %s', neighbour)
        # Send out vote request
        response = transport.publish(self, self.state.vote_request_message(self, neighbour))
        if response:
            self.on_message(response)

        # Only extend timeout if we failed to become leader
        if self.state.role != STATE_ROLE_LEADER:
            self.extend_timeout(neighbour)

    def on_timeout_follower(self, transport, neighbour):
        """
        Based on node mode, either convert to candidate, note leadership as being required, or do nothing.

        :param transport: Transport to be used
        :param neighbour: Neighbour in question
        :type transport: pyraftlog.transport.Transport
        :type neighbour: str
        :rtype: None
        """
        if self.leader[0] is not None and self.leader[0] != neighbour:
            self.extend_timeout(neighbour)
            return

        # Only put ourselves forward as a candidate if we are eligible
        if not self.is_eligible():
            if not self.leadership_required:
                self.log(logging.INFO, 'Leadership might be required of this reluctant node')
            self.leadership_required = self.mode in [NODE_MODE_ACTIVE, NODE_MODE_RELUCTANT]
            self.extend_timeout()
            return

        with self.lock:
            if self.state.role != STATE_ROLE_FOLLOWER:
                return

            self.log(logging.WARN, 'Converting to candidate (Leader: %s)', self.get_leader())

            # Clear the current leader
            self.leader = (None, None)

            # Reset timeouts to send the initial vote request
            self.reset_timeout()

            # Convert to candidate and increment term
            self.state.role = STATE_ROLE_CANDIDATE
            self.state.increment_term(self.name, neighbour)
            self.log(logging.INFO, 'Starting election')
