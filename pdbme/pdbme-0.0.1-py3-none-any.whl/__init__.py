""" just __init__ """
from functools import partial
import signal
import socket
import sys
import traceback

from .arpdb.arpdb import ARpdb
from .rpdb import Rpdb, OCCUPIED

DEFAULT_ADDR = "127.0.0.1"
DEFAULT_PORT = 4444


def set_trace(host=DEFAULT_ADDR, port=DEFAULT_PORT, frame=None):
    """Wrapper function to keep the same import x; x.set_trace() interface.

    We catch all the possible exceptions from pdb and cleanup.

    pdbme connects to host:port where pdbme-cli should listen on port <port>
    """

    debugger = ARpdb(addr=host, port=port)

    try:
        debugger.set_trace(frame or sys._getframe().f_back)
    except Exception:
        traceback.print_exc()


def _trap_handler(host, port, signum, frame):
    set_trace(host, port, frame=frame)


def handle_trap(host=DEFAULT_ADDR, port=DEFAULT_PORT):
    """Register pdbme as the SIGTRAP signal handler"""
    signal.signal(signal.SIGTRAP, partial(_trap_handler, host, port))
