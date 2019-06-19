"""A module for some common shared utilities."""


import logging
import os
import subprocess
import time


def execute(args, cwd=None):
    """Execute a command with subprocess to obtain the stdout, stderr, and return code."""
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
    """Wrap a given amount of seconds."""
    logging.debug('Sleeping: %d', number)
    time.sleep(number)


def which(name):
    """Attempt to find a binary file like the system this is being run upon."""
    for path_dir in os.environ['PATH'].split(os.pathsep):
        abs_name = os.path.join(os.path.expandvars(path_dir), name)
        if os.path.isfile(abs_name):
            return abs_name
    return None
