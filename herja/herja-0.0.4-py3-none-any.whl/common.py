"""A module for some common shared utilities."""


import os
import subprocess
import time

from .assertions import assert_type
from .conversions import to_bytes, to_str
from .logging import get_logger
from .logging.decorators import debug


LOGGER = get_logger()


@debug.args
@debug.result
def execute(args, cwd=None):
    """Execute a command with subprocess to obtain the stdout, stderr, and return code."""
    if cwd is None:
        cwd = os.getcwd()

    # ensure the arguments given to this function are valid
    assert_type(args, list)

    # force everything into byte strings
    args = [to_bytes(arg) for arg in args]

    LOGGER.info('[%s]$ %s', os.path.basename(cwd), ' '.join(quotify(to_str(a)) for a in args))

    process = subprocess.Popen(
        args,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=cwd
    )
    stdout, stderr = process.communicate()
    return stdout, stderr, process.returncode


def quotify(data):
    """Wrap a string or bytes in quotes, if a space is inside."""
    assert_type(data, bytes, str)
    quote, space = (b'"', b' ') if isinstance(data, bytes) else ('"', ' ')
    return quote + data + quote if space in data else data


def sleep(number):
    """Sleep a given amount of seconds."""
    LOGGER.debug('Sleeping: %d', number)
    time.sleep(number)


@debug.args
@debug.result
def spawn(args, cwd=None):
    """Spawn a process and do not wait for it to return."""
    if cwd is None:
        cwd = os.getcwd()
    return subprocess.Popen(args, cwd=cwd)
