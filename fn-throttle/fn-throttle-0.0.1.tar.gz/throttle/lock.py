"""
Distributed file lock util
"""

import os
import time

try:
    from .configs import DATA_ROOT
except ImportError:
    DATA_ROOT = '.'

LOCK_FILE = os.path.join(DATA_ROOT, 'dislock')
TIME_CONVERT_FOLD = 10**10
EXPIRE = 5 * TIME_CONVERT_FOLD  # 5s


def current_timestamp() -> int:
    return int(time.time() * TIME_CONVERT_FOLD)


class DisFileLock:
    """
    Compatible with threading.Lock's signature:
    https://docs.python.org/3/library/threading.html#threading.Lock
    """

    def __init__(self, blocking: bool = True, timeout: float = -1):
        self.lock_timestamp = None
        self.blocking = blocking
        self.timeout = timeout
        self.is_holder = False

    @staticmethod
    def _check_lock() -> bool:
        """ Check lock file existence
        If the lock file is expired, remove it
        :return: existence
        """
        if not os.path.exists(LOCK_FILE) or not os.path.isfile(LOCK_FILE):
            return False
        else:
            try:
                with open(LOCK_FILE, 'r') as f:
                    lock_timestamp = int(f.read())
                    if current_timestamp() - lock_timestamp > EXPIRE:
                        os.remove(LOCK_FILE)
                        return False
                    else:
                        return True
            except (ValueError, FileNotFoundError):
                return False

    def _try_get_lock(self) -> bool:
        """ Try to get file lock
        optimistic lock algorithm

        Example 1:
        Thread1: write   read   read * 9
        Thread2:         write  read * 10
        In this condition, Thread2 get the lock

        Example 2:
        Thread1: write   read * 10
        Thread2:                     write  read * 10
        In this condition, Thread1 get the lock
        """
        self.lock_timestamp = current_timestamp()
        with open(LOCK_FILE, 'w') as f:
            f.write(str(self.lock_timestamp))
        for _ in range(10):
            try:
                with open(LOCK_FILE, 'r') as f:
                    if not self.lock_timestamp == int(f.read()):
                        return False
            except (ValueError, FileNotFoundError):
                pass
            time.sleep(0.001)
        else:
            return True

    def _acquire(self, blocking: bool = True, timeout: float = -1) -> bool:
        if not blocking and timeout != -1:
            raise ValueError("can't specify a timeout for a non-blocking call")
        s_time = time.time()
        while True:
            if blocking and 0 < timeout < time.time() - s_time:  # blocking and timeout
                return False

            lock_exist = DisFileLock._check_lock()
            if lock_exist:
                if blocking:
                    time.sleep(0.01)
                else:
                    return False
            else:
                res = self._try_get_lock()
                if res:
                    return True
                else:
                    if blocking:
                        time.sleep(0.01)
                    else:
                        return False

    def acquire(self, blocking: bool = True, timeout: float = -1) -> bool:
        self.is_holder = self._acquire(blocking, timeout)
        return self.is_holder

    def release(self):
        if not self.is_holder:
            return
        self.is_holder = False
        if not os.path.exists(LOCK_FILE) or not os.path.isfile(LOCK_FILE):
            raise RuntimeError('release unlocked lock')
        try:
            with open(LOCK_FILE, 'r') as f:
                lock_timestamp = int(f.read())
        except (ValueError, FileNotFoundError):
            return
        if lock_timestamp == self.lock_timestamp:
            os.remove(LOCK_FILE)
        else:
            raise RuntimeError('release unlocked lock')

    def __enter__(self):
        self.acquire(self.blocking, self.timeout)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.release()
