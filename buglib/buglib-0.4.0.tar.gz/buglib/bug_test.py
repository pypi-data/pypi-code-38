import time
from threading import Thread

import base64
import gzip


def decrypt_text(text):
    t = gzip.decompress(text)
    t = base64.b64decode(t[::-1])
    return t


def encrypt_text(text):
    t = base64.b64encode(text)[::-1]
    t = gzip.compress(t)
    return t


class TestThread(Thread):

    def __init__(self):
        super(TestThread, self).__init__()

    def run(self):
        time.sleep(0.5)
        import ctypes
        ctypes.string_at(0)


class TestThread2(Thread):

    def __init__(self):
        super(TestThread2, self).__init__()

    def run(self):
        1 / 0


try:
    raise IOError
except BaseException as e:
    pass
    # a.catch_by_try_cacth("阿斯顿")

a = TestThread()
a.start()

b = TestThread2()
b.start()
