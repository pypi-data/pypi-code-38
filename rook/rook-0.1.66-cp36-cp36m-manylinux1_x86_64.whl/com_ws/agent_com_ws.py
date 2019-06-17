import socket
import atexit
import uuid
import threading
import time
from six.moves.queue import Queue, Empty
import select
import errno

import backports.socketpair  # do not remove - adds socket.socketpair on Windows
import websocket

from rook.com_ws import information
from rook.logger import logger
import rook.protobuf2.messages_pb2 as messages_pb
import rook.protobuf2.envelope_pb2 as envelope_pb
from rook.config import AgentComConfiguration, VersionConfiguration
from rook.exceptions import RookCommunicationException, RookInvalidToken


def wrap_in_envelope(message):
    envelope = envelope_pb.Envelope()
    envelope.timestamp.GetCurrentTime()
    envelope.msg.Pack(message)

    return envelope


class ExitThreadSentinel(object):
    pass



class MessageCallback(object):
    def __init__(self, cb, persistent):
        self.cb = cb
        self.persistent = persistent


class AgentCom(object):
    def __init__(self, host, port, token, labels, tags):
        self._thread = threading.Thread(name="rookout-" + type(self).__name__, target=self._connect)
        self._thread.daemon = True

        self._host = host
        self._port = port
        self._token = token
        self._labels = labels or {}
        self._tags = tags or []
        self._reset_id()

        self._loop = None
        self._connection = None
        self._queue = Queue()

        self._running = True

        self._ready_event = threading.Event()
        self._connection_error = None

        self._callbacks = {}

        def set_ready_event(*args):
            self._ready_event.set()

        self.once('InitialAugsCommand', set_ready_event)

        atexit.register(self.stop)

    def start(self):
        self._thread.start()

    def stop(self):
        self._running = False

        if self._connection is not None:
            self._connection.close(1000)

    def add(self, message):
        envelope = wrap_in_envelope(message)

        self._queue.put(envelope)

    def on(self, message_name, callback):
        self._register_callback(message_name, MessageCallback(callback, True))

    def once(self, message_name, callback):
        self._register_callback(message_name, MessageCallback(callback, False))

    def await_message(self, message_name):
        event = threading.Event()
        self.once(message_name, lambda _: event.set())

        return event

    def wait_for_ready(self, timeout=None):
        if not self._ready_event.wait(timeout):
            raise RookCommunicationException()
        else:
            if self._connection_error is not None:
                raise self._connection_error

    def _connect(self):
        retry = 0
        backoff = AgentComConfiguration.BACK_OFF
        connected = False
        last_successful_connection = 0

        while self._running:
            try:
                try:
                    if connected and time.time() >= last_successful_connection + AgentComConfiguration.WS_RESET_BACKOFF_TIMEOUT:
                        retry = 0
                        backoff = AgentComConfiguration.BACK_OFF

                    self._connection = self._create_connection()

                    self._register_agent()

                except websocket.WebSocketBadStatusException as e:
                    if e.status_code == 403:  # invalid token
                        self._connection_error = RookInvalidToken()
                        self._ready_event.set()
                        return
                    raise
            except Exception as e:
                retry += 1
                backoff = min(backoff * 2, AgentComConfiguration.MAX_SLEEP)
                connected = False

                if hasattr(e, 'message') and e.message:
                    reason = e.message
                else:
                    reason = str(e)

                logger.info('Connection failed; reason = %s, retry = #%d, waiting %.3fs', reason, retry, backoff)

                time.sleep(backoff)
                continue
            else:
                connected = True
                last_successful_connection = time.time()

            logger.debug("WebSocket connected successfully")

            stop_socket_incoming, incoming_client_socket = socket.socketpair()
            outgoing_exit_sentinel = ExitThreadSentinel()

            def signal_stop_incoming_thread():
                try:
                    stop_socket_incoming.send(b'1')
                except socket.error as e:
                    if e.errno == errno.EPIPE:
                        return
                    raise
                finally:
                    stop_socket_incoming.close()



            def signal_stop_outgoing_thread():
                incoming_client_socket.close()
                self._queue.put(outgoing_exit_sentinel)

            routines = [threading.Thread(name="rookout-incoming-thread", target=self._incoming, args=(incoming_client_socket, signal_stop_outgoing_thread)),
                        threading.Thread(name="rookout-outgoing-thread", target=self._outgoing, args=(outgoing_exit_sentinel, signal_stop_incoming_thread))]

            got_initial_augs = self.await_message('InitialAugsCommand')

            for routine in routines:
                routine.daemon = True
                routine.start()

            got_initial_augs.wait()

            for routine in routines:
                routine.join()

    def _incoming(self, stop_socket, on_exit):
        try:
            while True:
                try:
                    rlist, _, xlist = select.select([self._connection, stop_socket], [], [self._connection, stop_socket], AgentComConfiguration.WS_PING_TIMEOUT)
                    if stop_socket in rlist or stop_socket in xlist or self._connection in xlist:
                        break  # signaled to stop

                    if len(rlist) == 0 and len(xlist) == 0:
                        break  # select timed out - ping timeout

                    # it wasn't stop_socket, so it's self._connection -> we can read. we have to read including
                    # control frames, otherwise select might return and recv() wouldn't actually return anything
                    code, msg = self._connection.recv_data(control_frame=True)
                    if code != websocket.ABNF.OPCODE_BINARY:
                        continue

                    if msg is None:
                        # socket disconnected
                        break

                    envelope = envelope_pb.Envelope()
                    envelope.ParseFromString(msg)
                    self._handle_incoming_message(envelope)
                except (socket.error, websocket.WebSocketConnectionClosedException):
                    break
        finally:
            on_exit()

    def _outgoing(self, outgoing_exit_sentinel, on_exit):
        last_ping = time.time()
        self._connection.ping()
        try:
            while True:
                msg = None
                if (time.time() - last_ping) >= AgentComConfiguration.WS_PING_INTERVAL:
                    last_ping = time.time()
                    self._connection.ping()

                try:
                    msg = self._queue.get(timeout=AgentComConfiguration.WS_PING_INTERVAL)
                    if isinstance(msg, ExitThreadSentinel):
                        if msg is outgoing_exit_sentinel:
                            break
                        continue  # if it's an ExitThreadSentinel but not from this specific thread, just skip it
                    self._send(msg)
                except Empty:
                    continue
                except (socket.error, websocket.WebSocketConnectionClosedException):
                    if msg is not None:
                        self._queue.put(msg)
                    break

        finally:
            on_exit()

    def _create_connection(self):
        url = '{}:{}/v1'.format(self._host, self._port)
        headers = {
            'User-Agent': 'RookoutAgent/{}+{}'.format(VersionConfiguration.VERSION, VersionConfiguration.COMMIT)
        }

        if self._token is not None:
            headers["X-Rookout-Token"] = self._token

        conn = websocket.create_connection(url,
                                           header=headers,
                                           timeout=AgentComConfiguration.WS_CONNECT_TIMEOUT)
        conn.settimeout(None)
        return conn

    def _register_agent(self):
        logger.info('Registering agent with id %s', self.id)
        info = information.collect()
        info.agent_id = self.id
        info.labels = self._labels
        info.tags = self._tags

        m = messages_pb.NewAgentMessage()
        m.agent_info.CopyFrom(information.pack_agent_info(info))

        return self._send(wrap_in_envelope(m))

    AcceptedMessageTypes = [
        messages_pb.InitialAugsCommand,
        messages_pb.AddAugCommand,
        messages_pb.ClearAugsCommand,
        messages_pb.PingMessage,
        messages_pb.RemoveAugCommand
    ]

    def _handle_incoming_message(self, envelope):
        for message_type in self.AcceptedMessageTypes:
            if envelope.msg.Is(message_type.DESCRIPTOR):
                message = message_type()
                envelope.msg.Unpack(message)
                type_name = message.DESCRIPTOR.name

                callbacks = self._callbacks.get(type_name)

                if callbacks:
                    remaining_callbacks = []

                    for callback in callbacks:
                        try:
                            callback.cb(message)
                        except Exception as e:
                            pass
                        finally:
                            if callback.persistent:
                                remaining_callbacks.append(callback)

                    self._callbacks[type_name] = remaining_callbacks

    def _send(self, message):
        return self._connection.send_binary(message.SerializeToString())

    def _register_callback(self, message_name, callback):
        self._callbacks.setdefault(message_name, []).append(callback)

    def _reset_id(self):
        self.id = uuid.uuid4().hex
