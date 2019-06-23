# -*- coding: utf-8 -*-

# TODO: module description
# TODO: copyright notice

import os
import sys
import inspect
import signal
import logging
import threading
from collections import defaultdict, namedtuple

import zmq

from .zmessage import ZMessage

try:
    from typing import Any, Dict, List, Optional, Type
    from .zmessage import ZMessageType
except ImportError:
    pass


# Socket configuration type
SocketConfig = namedtuple('SocketConfig', ('name', 'method', 'type', 'addr', 'attrs'))


class ZException(Exception):
    """Base class of all exceptions created by ZNode"""
    pass


class ConnectionError(ZException):
    """
    Error connecting to a socket.

    Original exception raised by ZMQ is in :py:attr:`zmq_exc`.
    """
    zmq_exc = None  # type: zmq.error.ZMQError

    def __init__(self, *args, **kwargs):  # type: (*Any, **Any) -> None
        self.zmq_exc = kwargs.pop('zmq_exc', None)
        super(ConnectionError, self).__init__(*args, **kwargs)


class InvalidRequest(ZException):
    """
    Request failed validation by :py:meth:`is_valid()` when checked before
    sending or after receiving it.
    """
    pass


class MessageFormatError(ZException):
    """
    Received message cannot be transformed into a ZMessage object because it's
    not in the required format.
    """
    pass


class ZNode(object):
    """
    Base class for socket handlers.

    Usually it is enough to setup the sockets configuration in
    :py:meth:`__init__()` and the request handling code in :py:meth:`run()`:

    ::

        class ResultSink(ZNode):
            def __init__(self):
                super(ResultSink, self).__init__()
                self.add_socket('from_workers', 'bind', 'PULL', 'tcp://127.0.0.1:5558')

            def run(self):
                while True:
                    request = self.receive('from_workers')
                    type = request.type

                    if type == 'shutdown':
                        break
                    elif type == 'job done':
                        ...

        ResultSink().start()
    """
    pid = 0  # process ID
    name = ''  # identifier for this object
    in_thread = False  # if True, SIGINT handler will not be installed
    signal_num = signal.SIGINT  # signal that will trigger handler
    sockets = None  # type: Dict[str, zmq.Socket]  # holds connected ZMQ sockets that were added through add_socket()
    logger = None  # type: logging.Logger  # logging instance with name 'zmessage.znode'
    context = None  # type: zmq.Context  # ZMQ context
    _socket_configs = None  # type: List[SocketConfig]

    def __init__(self):  # type: () -> None
        self.pid = os.getpid()
        self.name = '{}.{}'.format(self.__class__.__name__, self.pid)
        self.logger = logging.getLogger(__name__)
        self._socket_configs = []
        self.sockets = {}
        self.messages_received_count = defaultdict(int)  # type: Dict[str, int]
        self.messages_sent_count = defaultdict(int)  # type: Dict[str, int]
        self._cleaned_up = False

    def init(self, install_sig_handler=True):  # type: (Optional[bool]) -> None
        """
        Initialize sockets and install a signal handler.

        Creates ZMQ context, calls :py:meth:`connect()` to bind/connect all
        sockets and optionally installs the method :py:meth:`signal_handler()`
        as handler for signal :py:attr:`self.signal_num` (default SIGINT).

        If used as an aggregate and a ZMQ context already exist, set
        :py:attr:`context` before calling :py:meth:`init()` or
        :py:meth:`start()`.

        Regardless of `install_sig_handler` the signal handler will *not* be
        installed if :py:attr:`self.in_thread` is True or the currents threads
        name is not `MainThread`.

        All methods called :py:meth:`pre_init_*()` will be called
        (lexicographically sorted) at the start of :py:meth:`init()`, and all
        methods called :py:meth:`post_init_*()` will be called (lex. sorted)
        at the end of :py:meth:`init()`.

        :param bool install_sig_handler: whether to  install a signal handler
        :return: None
        """
        self._call_pre_inits()
        self.pid = os.getpid()
        if not self.context:
            self.context = zmq.Context()
        self.connect()
        self.in_thread = self.in_thread or (threading.current_thread().getName() != 'MainThread')
        if install_sig_handler and not self.in_thread:
            signal.signal(self.signal_num, self.signal_handler)
        self._call_post_inits()

    def signal_handler(self, signum, frame):  # type: (int, Any) -> None
        """
        Handler for signal :py:attr:`self.signal_num` (default SIGINT) if
        installed by :py:meth:`init()`.

        Default implementation will run `self.cleanup(); sys.exit(0)`.

        :param int signum: the signal that lead to calling this function
        :param frame: current stack frame
        :type frame: None or frame object
        :return:
        """
        self.logger.warn('[%s] Received signal %r, shutting down.', self.name, 'SIGINT' if signum == 2 else signum)
        self.cleanup()
        sys.exit(1)

    def add_socket(self, name, method, socket_type, addr, **attrs):  # type: (str, str, str, str, **Any) -> None
        """
        Add a socket configuration. The socket will be connected / bound in
        :py:meth:`connect()` -> :py:meth:`connect_socket()` which will be
        called by :py:meth:`start()` -> :py:meth:`init()`. The order of
        :py:meth:`add_socket()` calls will be honored when connecting/binding.

        It will *then* be available as :py:attr:`self.sockets.name`. The
        attributes in `attrs` will be set before connecting/binding.

        :param str name: the socket will be available as :py:attr:`self.sockets.name`.
        :param str method: either `bind` or `connect`
        :param str socket_type: ZeroMQ socket type (e.g. `DEALER`, `PAIR`, `PUB`, ...)
        :param str addr: ZeroMQ protocol and address string (e.g. `tcp://*:5555`)
        :param attrs: attributes and values to apply to socket object, eg. rcvhwm=100, sndhwm=100
        :return: None
        :raises AssertionError: when an argument is invalid
        """
        assert name not in [c.name for c in self._socket_configs], 'Socket name already used.'
        assert method in ('bind', 'connect'), 'Unknown socket connect method.'
        assert socket_type in ('DEALER', 'PAIR', 'PUB', 'PULL', 'PUSH', 'REP', 'REQ', 'ROUTER', 'SUB'), 'Unknown socket type.'
        assert hasattr(zmq, socket_type), 'Unknown socket type.'
        assert any(addr.startswith('{}://'.format(proto)) for proto in ('inproc', 'ipc', 'tcp', 'pgm', 'epgm')), 'Unknown protocol.'

        self._socket_configs.append(SocketConfig(name, method, getattr(zmq, socket_type), addr, attrs))

    def connect_socket(self, socket_config):  # type: (SocketConfig) -> zmq.Socket
        """
        Create ZMQ socket and connect or bind it according to its configuration
        previously created by :py:meth:`add_socket()`.

        :param SocketConfig socket_config: configuration of socket
        :return: ZMQ socket
        :rtype: zmq.Socket
        :raises zmq.error.ZMQError: when a socket cannot be bound/connected to
        """
        socket = self.context.socket(socket_config.type)
        for k, v in socket_config.attrs.items():
            setattr(socket, k, v)
        connect_or_bind_method = getattr(socket, socket_config.method)
        connect_or_bind_method(socket_config.addr)
        return socket

    def connect(self):  # type: () -> None
        """
        Create ZMQ sockets and connect or bind them according to their
        configuration previously created by :py:meth:`add_socket()`.

        :return: None
        :raises zmq.error.ZMQError: when a socket cannot be bound/connected to
        """
        for socket_config in self._socket_configs:
            try:
                socket = self.connect_socket(socket_config)
            except zmq.error.ZMQError as exc:
                msg = '[{}] Error {} socket {!r} to {!r}: {}'.format(
                    self.name,
                    'binding' if socket_config.method == 'bind' else 'connecting',
                    socket_config.name,
                    socket_config.addr,
                    exc)
                raise ConnectionError(msg, zmq_exc=exc)
            self.sockets[socket_config.name] = socket

    def run(self, *args, **kwargs):  # type: (*Any, **Any) -> Any
        """
        Put your logic here.

        If a custom ZMessage subclass with expanded :py:meth:`.is_valid()` is
        used, tests for invalid :py:attr:`type` can be omitted.

        ::

            def run(self):
                while True:
                    request = self.receive('from_ventilator', VentilatorMessage)
                    if request.type == 'do stuff':
                        ...
                        self.send('to_sink', result)
                    elif request.type == 'shutdown':
                        break

        :return: whatever you want
        """
        raise NotImplementedError()

    def start(self, install_sig_handler=True, cleanup=True, *args, **kwargs):
        # type: (Optional[bool], Optional[bool], *Any, **Any) -> Any
        """
        Use this function to start your application objects execution.

        It simply runs :py:meth:`init()`; :py:meth:`run()` and
        :py:func:`finally` :py:meth:`cleanup()`.

        :param bool install_sig_handler: will be passed to :py:meth:`init()`
        :param bool cleanup: whether to automatically call :py:meth:`cleanup()` after :py:meth:`run()`
        :param args: will be passed to :py:meth:`run()`
        :param kwargs: will be passed to :py:meth:`run()`
        :return: whatever :py:meth:`run()` returns
        """
        self.init(install_sig_handler)
        try:
            return self.run(*args, **kwargs)
        finally:
            if cleanup:
                self.cleanup()

    def cleanup(self):  # type: () -> None
        """
        Close sockets and terminate context.

        :return: None
        """

        if self._cleaned_up:
            return

        def context_term_handler(signum, frame):  # type: (int, Any) -> None
            # context will automatically be closed when this is garbage collected
            pass

        self.logger.debug('%r exiting after receiving messages: %r and sending messages: %r.',
                          self.name,
                          dict(self.messages_received_count) if self.messages_received_count else 0,
                          dict(self.messages_sent_count) if self.messages_sent_count else 0)

        self.logger.debug('[%s] Cleanup of network sockets...', self.name)
        for socket_config in self._socket_configs:
            self.sockets[socket_config.name].close()
        previous_handler = None
        if not self.in_thread:
            previous_handler = signal.signal(signal.SIGALRM, context_term_handler)
            signal.alarm(1)
        self.context.term()
        if previous_handler:
            signal.signal(signal.SIGALRM, previous_handler)
        self._cleaned_up = True
        self.logger.debug('[%s] Cleanup done.', self.name)

    def send(self, socket_name, request):  # type: (str, ZMessageType) -> None
        """
        Send a request.

        :param str socket_name: name of socket to send from
        :param ZMessage request: message to send
        :return: None
        :raises InvalidRequest: when `request` not :py:meth:`is_valid()`
        """
        assert socket_name in self.sockets, 'Unknown socket {!r}.'.format(socket_name)
        if not request.is_valid():
            raise InvalidRequest('[{}] Not sending invalid request: {}.'.format(self.name, request))
        socket = self.sockets[socket_name]
        socket.send_json(request.to_dict())
        self.messages_sent_count[request.type] += 1

    def receive(self, socket_name, message_cls=ZMessage):  # type: (str, Optional[Type[ZMessage]]) -> ZMessageType
        """
        Receive a message.

        :param str socket_name: the socket to receive from
        :param type message_cls: class to create message object from
        :return: the received message
        :rtype: ZMessage
        :raises MessageFormatError: when received message cannot be converted to a ZMessage
        :raises InvalidRequest: when received ZMessage not :py:meth`is_valid()`
        """
        assert socket_name in self.sockets, 'Unknown socket {!r}.'.format(socket_name)
        assert issubclass(message_cls, ZMessage), "Argument 'message_cls' must be a ZMessage (sub)class."

        socket = self.sockets[socket_name]
        message = socket.recv_json()  # type: dict
        try:
            request = message_cls.from_dict(message)  # type: ZMessageType
            request.id = message['id']
            self.messages_received_count[request.type] += 1
        except (IndexError, TypeError) as exc:
            self.messages_received_count['_bad_format_'] += 1
            raise MessageFormatError('[{}] Received request has bad format: {}.'.format(self.name, exc))
        if not request.is_valid():
            self.messages_received_count['_invalid_request_'] += 1
            raise InvalidRequest('[{}] Received invalid request: {}.'.format(self.name, request))
        return request

    def _call_pre_inits(self):
        """Run all methods with a name starting with 'pre_init_' (in lexicographical order)."""
        methods = [name for name, member in inspect.getmembers(self, inspect.ismethod) if name.startswith('pre_init_')]
        for method in sorted(methods):
            method()

    def _call_post_inits(self):
        """Run all methods with a name starting with 'post_init_' (in lexicographical order)."""
        methods = [name for name, member in inspect.getmembers(self, inspect.ismethod) if name.startswith('post_init_')]
        for method in sorted(methods):
            method()
