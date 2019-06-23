# -*- coding: utf-8 -*-
import threading

import argparse
import asyncore
import datetime
import errno
import json
import logging
import os
import signal
import socket
import struct
import subprocess
import sys
import time
from contextlib import closing
import six

import requests
from requests import RequestException

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S')


def setup_logging(log_file):
    logging.basicConfig()

    new_logger = logging.getLogger('log_monitor')
    new_logger.setLevel(logging.DEBUG)
    new_logger.propagate = False

    formatter = logging.Formatter('%(asctime)s.%(msecs)03d %(name)s %(levelname)s %(message)s', '%Y-%m-%d %H:%M:%S')

    if log_file is not None:
        ch2 = logging.FileHandler(log_file)
        ch2.setLevel(logging.DEBUG)
        ch2.setFormatter(formatter)
        new_logger.addHandler(ch2)
    else:
        new_logger.addHandler(logging.NullHandler())

    return new_logger


logger = setup_logging(os.environ.get('ML_LOG_MONITOR_LOG_FILE'))


# This is a clone of threading.Timer with minor change to the run() method
# @see: https://github.com/python/cpython/blob/master/Lib/threading.py#L1142-L1167
class PerpetualTimer(threading.Thread):
    """Call a function repeatedly in a specified number of seconds:
            timer = PerpetualTimer(30.0, f, args=None, kwargs=None)
            timer.start()
            timer.cancel()     # stop the timer's action if it's still waiting
    """
    def __init__(self, interval, function, args=None, kwargs=None):
        threading.Thread.__init__(self)
        self.interval = interval
        self.function = function
        self.args = args if args is not None else []
        self.kwargs = kwargs if kwargs is not None else {}
        self.finished = threading.Event()

    def cancel(self):
        """Stop the timer if it hasn't finished yet."""
        self.finished.set()

    def run(self):
        while True:
            self.finished.wait(self.interval)
            self.function(*self.args, **self.kwargs)
            if self.finished.is_set():
                return


# noinspection PyClassicStyleClass
class DataHandler:
    max_saved_items = 1000
    max_batch_send = 50
    send_every_x_seconds = 5

    def __init__(self, endpoint, session=None):
        self._pending_data = None
        self._endpoint = endpoint

        headers = {'Content-type': 'application/json'}

        session = session or requests.session()
        session.headers.update(headers)

        self._session = session if endpoint is not None else None
        self._unhandled_exception = False
        self._exception_stack_trace = ''
        self._items = []
        self._sending_thread_lock = threading.RLock()
        self._sending_thread = None

    def close(self):
        if self._sending_thread is not None:
            self._sending_thread.cancel()

        self._send_all_items()

        if self._sending_thread is not None:
            self._sending_thread.cancel()

    def _send_all_items(self):
        self._send_items(send_all_items=True)

    def __batch_send_items(self, items):
        if self._session is None:
            headers = {'Content-type': 'application/json'}

            session = requests.session()
            session.headers.update(headers)

            self._session = session

        r = self._session.post(self._endpoint, data=json.dumps(items))
        try:
            r.raise_for_status()
        except RequestException as ex:
            logger.info('request failed %s', ex)

    def _send_items(self, send_all_items=False):
        while True:
            with self._sending_thread_lock:
                total_send = min(len(self._items), self.max_batch_send)
                items = self._items[:total_send]

                self._items = self._items[total_send:]

            if not items:
                break

            self.__batch_send_items(items)

            if not send_all_items:
                break

    def _create_timer(self):
        return PerpetualTimer(self.send_every_x_seconds, self._send_items)

    def post_json(self, data):
        with self._sending_thread_lock:
            self._items.append(data)

            if len(self._items) > self.max_saved_items:
                self._items = self._items[-self.max_saved_items:]

            if self._sending_thread is None:
                self._sending_thread = self._create_timer()
                self._sending_thread.start()

    def on_line(self, line):
        try:
            data = json.loads(line)
        except ValueError:
            return

        if data.get('category') == 'unhandled':
            self._unhandled_exception = True

            message = data.get('message')

            if message is not None:
                self._exception_stack_trace += message

        if self._session is not None:
            self.post_json(data)

    def process_text(self, text):
        if not text:
            return

        lines = text.split('\n')

        for i, line in enumerate(lines):
            if self._pending_data is not None:
                line = self._pending_data + line
                self._pending_data = None

            if i == len(lines) - 1:  # last or first (and only one)
                if len(line) == 0 or text[-1] != '\n':
                    self._pending_data = line
                    continue

            self.on_line(line)


# noinspection PyClassicStyleClass
class IncomingDataHandler(asyncore.dispatcher):
    def __init__(self, port, endpoint, data_handler=None):
        asyncore.dispatcher.__init__(self)

        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.connect(('', port))
        except Exception:
            logger.exception('failed to connect')
            raise

        self.data_handler = data_handler or DataHandler(endpoint)
        self.closed_by_application = False
        self._handle_error = False

    def writable(self):
        return False

    def close(self):
        asyncore.dispatcher.close(self)

        if self.data_handler is not None:
            self.data_handler.close()

    def read_at_least(self, size, wait_for_data):
        data = b''

        while len(data) < size:
            try:
                current_data = self.recv(size)
                data += current_data
            except socket.error as why:
                if why.errno == errno.EAGAIN:
                    if wait_for_data:
                        time.sleep(0.1)
                        continue
                    else:
                        logger.info('socket.error', why)
                        return data

                logger.exception('socket.error')

                raise

            if len(data) == 0:
                return data

        return data

    def handle_read(self):
        total_read = 0
        logger.info('handle_read begin')

        data = self.read_at_least(4, wait_for_data=False)
        if len(data) > 0:
            size = struct.unpack('!i', data[:4])[0]

            if size == 0:  # the application sent zero size in order to close this
                logger.info('closed_by_application: True')
                self.closed_by_application = True
                self.close()
            elif size > 0:  # the application sent zero size in order to close this
                data = self.read_at_least(size, wait_for_data=True)

                current_block = data.decode('utf8')

                total_read += 4 + size

                self.data_handler.process_text(current_block)

        logger.info('handle_read end %s', total_read)

        return total_read

    def handle_close(self):
        logger.info('socket closed')
        self.close()
        self.data_handler.close()

    def handle_error(self):
        asyncore.dispatcher.handle_error(self)

        self._handle_connection_refused()

    @staticmethod
    def _handle_connection_refused():
        exc_class, exc_value, tb_info = sys.exc_info()

        try:
            ConnectionRefusedError
        except NameError:
            # Python2 does not have ConnectionRefusedError, and this issue does not happen there
            return

        # if we got a ConnectionRefusedError exception, no use to keep trying to connect
        if exc_class is ConnectionRefusedError:
            logger.warning("Got ConnectionRefusedError, exiting log monitor process")
            six.reraise(exc_class, exc_value, tb_info)


class App(object):
    def __init__(self, sys_args=None):
        args = self._create_args_parser(sys_args)

        if not args.isRoot:
            if sys_args is not None:
                sys_args = [__file__] + sys_args

            restart_params = sys_args[:] if sys_args else sys.argv[:]
            restart_params += [self.root_param_name()]

            restart_params = [sys.executable] + restart_params

            self._restart(restart_params)

        self.args = args

    @classmethod
    def _create_args_parser(cls, sys_args):
        parser = argparse.ArgumentParser(description='listen socket for logs.')
        parser.add_argument('--port', type=int, required=True)
        parser.add_argument('--endpoint', required=True)
        parser.add_argument('--terminate-endpoint')
        parser.add_argument('--parent-pid', type=int, required=True)

        parser.add_argument(cls.root_param_name(), action='store_true')

        return parser.parse_args(sys_args)

    @classmethod
    def root_param_name(cls):
        return '--isRoot'

    @classmethod
    def _restart(cls, restart_params):
        subprocess.Popen(restart_params)
        sys.exit(0)

    def _post_terminate(self, unhandled_exception, ctrl_c=False, exception_stack_trace=None):
        if not self.args.terminate_endpoint:
            logger.info('post_terminate skipped (no --terminate-endpoint)')
            return

        logger.info('post_terminate unhandled_exception: %s ctrl_c: %s', unhandled_exception, ctrl_c)

        headers = {'content-type': 'application/json'}
        body = {
            'ts': datetime.datetime.utcnow().isoformat(),
            'ctrl_c': ctrl_c,
            'unhandled_exception': unhandled_exception,
            'exception_stack_trace': exception_stack_trace,
        }
        data = json.dumps(body)

        requests.post(self.args.terminate_endpoint, data=data, headers=headers)

    # noinspection PyUnusedLocal
    def _signal_handler(self, current_signal, frame):
        logger.info('signal', current_signal)
        self._post_terminate(unhandled_exception=False, ctrl_c=True)
        sys.exit(0)

    @classmethod
    def _win_pid_exists(cls, pid):
        import psutil

        return psutil.pid_exists(pid)

    @classmethod
    def _pid_exists(cls, pid):
        if os.name == 'nt':
            return cls._win_pid_exists(pid)

        try:
            os.kill(pid, 0)
        except OSError as err:
            if err.errno == errno.ESRCH:
                # ESRCH == No such process
                return False
            elif err.errno == errno.EPERM:
                # EPERM clearly means there's a process to deny access to
                return True
            else:
                # According to "man 2 kill" possible error values are
                # (EINVAL, EPERM, ESRCH)
                raise
        else:
            return True

    def main(self):
        signal.signal(signal.SIGINT, self._signal_handler)  # ctrl-c from console

        logger.info('log monitor started on pid %s', os.getpid())

        while True:
            with closing(IncomingDataHandler(self.args.port, self.args.endpoint)) as handler:
                asyncore.loop()

                if handler.closed_by_application or not self._pid_exists(self.args.parent_pid):
                    break

                logger.info('trying to reconnect')
                time.sleep(1)

        logger.info('asyncore exit')

        closed_by_ctrl_c = not handler.closed_by_application

        self._post_terminate(unhandled_exception=handler.data_handler._unhandled_exception, ctrl_c=closed_by_ctrl_c,
                             exception_stack_trace=handler.data_handler._exception_stack_trace)


if __name__ == "__main__":  # pragma: no cover
    # noinspection PyBroadException
    try:
        app = App()
        app.main()
    except Exception as ex:
        if ex is not SystemExit:
            logger.exception('exit log monitor')
