#!/usr/bin/env python

"""
Provides a context manager for talking to serial devices over term server
"""
from __future__ import (print_function, unicode_literals, division, absolute_import)
import socket
from contextlib import contextmanager

@contextmanager
def netdevice(host, port, timeout=5):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.settimeout(timeout)
        s.connect((host, port))
        yield s
    finally:
        s.close()
