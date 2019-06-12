# -*- coding: utf-8 -*-
import datetime
import json
import os
import socket
import subprocess
import sys
import time
from logging.handlers import SocketHandler
from struct import pack
from missinglink_kernel.callback.root_logger_sniffer import RootLoggerSniffer
from missinglink_kernel.callback.monkey_patch_process import MonkeyPatchProcess
from missinglink_kernel.callback.trie import Trie
from missinglink_kernel.callback.utilities.socket_utils import is_socket_ready_to_read


class ReverseSocketHandler(SocketHandler):
    def __init__(self, sock):
        SocketHandler.__init__(self, '', 0)
        self.closeOnError = False
        self.sock = sock
        self._log_handler = None

    def shutdown(self):
        self.close()

    def _shutdown_socket(self):
        try:
            self.sock.sendall(pack('!i', 0))
            self.sock.shutdown(socket.SHUT_WR)
        except OSError:
            pass

    def close(self):
        self.acquire()
        try:
            if self.sock is not None:
                self._shutdown_socket()
        finally:
            self.release()

        super(ReverseSocketHandler, self).close()

    def makePickle(self, record):
        alt_zone = -time.altzone

        ei = record.exc_info
        if ei:
            # just to get traceback text into record.exc_text ...
            dummy = self.format(record)
            record.exc_info = None  # to avoid Unpickleable error
            record.msg = dummy
            record.args = ()

        timezone = '%s%02d:%02d' % ('+' if alt_zone > 0 else '-', abs(alt_zone) / 3600, abs(alt_zone) % 60)
        try:
            message = record.msg % record.args
        except (TypeError, ValueError, RuntimeError) as e:
            message = '[{}] message: `{}` args: {}'.format(str(e), record.msg, record.args)

        params = {
            'level': record.levelname,
            'message': message,
            'category': record.name,
            'ts': datetime.datetime.fromtimestamp(record.created).isoformat() + timezone
        }

        data = (json.dumps(params) + '\n').encode('utf-8')
        val = pack('!i', len(data))

        return val + data

    def makeSocket(self, **kwargs):
        return self.sock


class RemoteLoggerHandler(RootLoggerSniffer):
    MAX_BACKLOGS = 1000

    def __init__(
            self, session_id, endpoint, log_level, logs_so_far, log_filter=None, terminate_endpoint=None):
        super(RemoteLoggerHandler, self).__init__(log_level)

        self._clients = None

        self.session_id = session_id
        self.log_level = log_level
        server_socket, port = self._start_log_server()

        self._server_socket = server_socket
        self._socket_log_handler = None
        self._logs_so_far = logs_so_far[:]
        self._port = port
        self._terminate_endpoint = terminate_endpoint
        self._endpoint = endpoint
        self._filter_log = None
        self.parse_filter_log(log_filter, log_level)
        self._process = None
        self._closed = False
        self._activate()

    def parse_filter_log(self, filter_log, global_log_level):
        if filter_log is None:
            filter_log = 'root:%s' % global_log_level

        self._filter_log = Trie()
        for key_val in filter_log.split(';'):
            name, level = key_val.split(':')

            if not name.startswith('root'):
                name = 'root.' + name

            level = int(level)
            self._filter_log[name] = level

    @property
    def port(self):
        return self._port

    def _filter_log_by_name_level(self, name, level):
        if self._filter_log is None:
            return True

        name = name or ''

        if not name.startswith('root'):
            name = 'root.' + name

        parts = name.split('.')

        for i in range(len(parts)):
            try:
                current_name = '.'.join(parts)
                value = self._filter_log[current_name]

                return 0 < value <= level
            except KeyError:
                parts.pop()
                continue

        return True

    def activate_if_needed(self):
        if self._socket_log_handler is None:
            self._check_waiting_clients()

    def on_root_log(self, record):
        if self._closed:
            return

        self.activate_if_needed()

        if not self._filter_log_by_name_level(record.name, record.levelno):
            return

        if self._socket_log_handler is None:
            self._logs_so_far.append(record)

            while len(self._logs_so_far) > self.MAX_BACKLOGS:
                self._logs_so_far.pop(0)

            return

        self._socket_log_handler.emit(record)

    def start_remote_script(self, disable_process_monkey_patch, is_root=False):
        current_script_dir = os.path.dirname(__file__)
        script_path = os.path.join(current_script_dir, 'log_monitor.py')

        params = [sys.executable, script_path, '--endpoint', self._endpoint, '--port', str(self._port)]

        if self._terminate_endpoint is not None:
            params.append('--terminate-endpoint')
            params.append(self._terminate_endpoint)

        params.append('--parent-pid')
        params.append(str(os.getpid()))

        if is_root:
            params.append('--isRoot')

        MonkeyPatchProcess.unmonkey_process_functions(disable_process_monkey_patch)
        try:
            return subprocess.Popen(params)
        finally:
            MonkeyPatchProcess.restore_monkey_process_functions(disable_process_monkey_patch)

    @classmethod
    def _start_log_server(cls):
        server_socket = socket.socket()
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind(('127.0.0.1', 0))
        server_socket.listen(1)

        port = server_socket.getsockname()[1]

        return server_socket, port

    def _check_waiting_clients(self, timeout=0):
        is_ready = is_socket_ready_to_read(self._server_socket, timeout)
        if not is_ready:
            return False

        client_socket, address = self._server_socket.accept()

        self._create_socket_log(client_socket)

        return True

    def _create_socket_log(self, sock):
        log_handler = ReverseSocketHandler(sock)

        for record in self._logs_so_far:
            if not self._filter_log_by_name_level(record.name, record.levelno):
                continue

            log_handler.emit(record)

        self._logs_so_far = None
        self._socket_log_handler = log_handler

    def close(self):
        log_handler = self._socket_log_handler
        self._closed = True
        if log_handler is not None:
            self._socket_log_handler = None
            log_handler.shutdown()

        super(RemoteLoggerHandler, self).close()
