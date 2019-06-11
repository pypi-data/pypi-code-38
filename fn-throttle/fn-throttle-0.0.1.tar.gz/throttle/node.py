import logging
import time
from typing import Any, Callable, Tuple, Dict
from uuid import uuid4

from .configs import PORT_CHOICES
from .controller import MinIntervalController
from .lock import DisFileLock
from .web import MasterServer, SlaveClient

MAX_JOIN_RETRIES = 5


class ThrottleNode:

    def __init__(self):
        self.guid = str(uuid4())
        self.role = None  # master or slave
        self.master_port = None
        self.master_server_thread = None  # this is not None of only master node
        self._join()

    def _join(self, try_cnt=1):
        """ Join local network """
        if try_cnt > MAX_JOIN_RETRIES:
            raise Exception(f'Node({self.guid}) cannot join local network')
        logging.info(f'Node({self.guid}) try to join local network, cnt: {try_cnt}')
        port, found = self._detect_master()
        if found:
            self.role = 'slave'
            self.master_port = port
        else:  # try to be the master
            with DisFileLock(blocking=False) as lock:
                if lock.is_holder:  # get the lock
                    self.master_server_thread = MasterServer(controller_clz=MinIntervalController, daemon=True)
                    self.master_server_thread.start()
                else:
                    time.sleep(1)
                    return self._join(try_cnt + 1)
            self.role = 'master'
            self.master_port = self.master_server_thread.port
        logging.info(f'Node({self.guid}) join local network success, role: {self.role}, master port: {self.master_port}')  # noqa

    def _detach(self):
        """ Detach local network
        NOT implemented in current version, which means a mater dying
        """

    # noinspection PyMethodMayBeStatic
    def _detect_master(self) -> (int, bool):
        """ Detect master node's port
        :return port, found
        """
        client = SlaveClient(0)
        for port in PORT_CHOICES:
            if client.ping(port):
                return port, True
        else:
            return -1, False

    @staticmethod
    def function_to_key(fn: Callable):
        # noinspection PyUnresolvedReferences
        return f'{fn.__module__}.{fn.__name__}'

    def registry(self, fn: Callable, **kwargs) -> bool:
        """ Registry function fn """
        key = ThrottleNode.function_to_key(fn)
        client = SlaveClient(port=self.master_port)
        return client.regist(key, kwargs)

    def run(self, fn: Callable, args: Tuple = None, kwargs: Dict = None) -> Any:
        """ Run function fn """
        args = args or ()
        kwargs = kwargs or {}

        key = ThrottleNode.function_to_key(fn)
        client = SlaveClient(port=self.master_port)
        while True:
            admit = client.admit(key)
            if admit:
                return fn(*args, **kwargs)
            else:
                time.sleep(0.01)
