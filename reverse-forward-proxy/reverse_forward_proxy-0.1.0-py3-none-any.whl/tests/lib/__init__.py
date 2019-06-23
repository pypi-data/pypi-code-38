import copy
import logging
import selectors
import signal
import socket
import subprocess
import tempfile
import threading
import time

from collections import namedtuple
from contextlib import contextmanager, ExitStack
from dataclasses import dataclass
from pathlib import Path
from typing import Tuple

from proxy import Client, HTTP
import pytest


logger = logging.getLogger()


def poll(address, timeout=10, retry_interval=0.1):
    def timedout():
        return time.time() - start > timeout

    start = time.time()

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        while not timedout():
            try:
                sock.connect(address)
            except ConnectionRefusedError:
                pass
            else:
                return True
            time.sleep(retry_interval)
        else:
            return False


@dataclass
class ClientConnect:
    address: Tuple[str, int]


class LoggingProxy(HTTP):
    """Implements shutdown ability and client connection tracking for tests.
    """
    def __init__(self, *args, events, lock, **kwargs):
        super().__init__(*args, **kwargs)
        self.stop = threading.Event()
        self.selector = selectors.DefaultSelector()
        self.events = events
        self._lock = lock

    def run(self):
        try:
            logger.info('Starting server on port %d' % self.port)
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.socket.bind((self.hostname, self.port))
            self.socket.listen(self.backlog)
            self.selector.register(self.socket, selectors.EVENT_READ)
            while not self.stop.is_set():
                result = self.selector.select(timeout=0.1)
                if result:
                    conn, addr = self.socket.accept()
                    with self._lock:
                        self.events.append(ClientConnect(addr))
                    client = Client(conn, addr)
                    self.handle(client)
        except Exception as e:
            logger.exception('Exception while running the server %r' % e)
        finally:
            logger.info('Closing server socket')
            self.selector.unregister(self.socket)
            self.socket.close()


@contextmanager
def get_proxy(port, timeout=10):
    lock = threading.RLock()
    proxy_events = []
    proxy = LoggingProxy(
        events=proxy_events,
        lock=lock,
        hostname='127.0.0.1',
        port=port,
        backlog=100,
        auth_code=None,
        server_recvbuf_size=8192,
        client_recvbuf_size=8192,
    )
    t = threading.Thread(target=proxy.run)
    t.daemon = True
    t.start()

    class Proxy:
        def __init__(self, address):
            self.address = address

        @property
        def events(self):
            with lock:
                return copy.deepcopy(proxy_events)

    proxy_data = Proxy(f'http://127.0.0.1:{port}/')

    try:
        if not poll(('127.0.0.1', port)):
            raise RuntimeError('Could not connect to proxy')

        yield proxy_data
    finally:
        proxy.stop.set()
        t.join()
