import socket
import os
import logging
from threading import Lock

logger = logging.getLogger("conplyent")


class SynchronizedDict(dict):
    def __init__(self, *args, **kwargs):
        self.__lock = Lock()
        super(SynchronizedDict, self).__init__(*args, **kwargs)

    def __getitem__(self, key):
        self.__lock.acquire()
        try:
            return super(SynchronizedDict, self).__getitem__(key)
        finally:
            self.__lock.release()

    def __setitem__(self, key, value):
        self.__lock.acquire()
        try:
            super(SynchronizedDict, self).__setitem__(key, value)
        finally:
            self.__lock.release()


def ipv4():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        host_name = s.getsockname()[0]
        s.close()
        return host_name
    except KeyboardInterrupt:
        raise
    except Exception:
        return None


def os_name():
    return {"nt": "windows", "posix": "linux", "mac": "mac"}[os.name]
