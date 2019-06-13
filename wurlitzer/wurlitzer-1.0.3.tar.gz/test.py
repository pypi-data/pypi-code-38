# coding: utf-8
from __future__ import print_function

import io
import os
from tempfile import TemporaryFile
import time

import mock

from wurlitzer import (
    libc, pipes, STDOUT, PIPE, c_stderr_p, c_stdout_p,
    sys_pipes, sys_pipes_forever,
    stop_sys_pipes,
    Wurlitzer,
)

def printf(msg):
    """Call C printf"""
    libc.printf((msg + '\n').encode('utf8'))

def printf_err(msg):
    """Cal C fprintf on stderr"""
    libc.fprintf(c_stderr_p, (msg + '\n').encode('utf8'))

def test_pipes():
    with pipes(stdout=PIPE, stderr=PIPE) as (stdout, stderr):
        printf(u"Hellø")
        printf_err(u"Hi, stdérr")

    assert stdout.read() == u"Hellø\n"
    assert stderr.read() == u"Hi, stdérr\n"

def test_pipe_bytes():
    with pipes(encoding=None) as (stdout, stderr):
        printf(u"Hellø")
        printf_err(u"Hi, stdérr")

    assert stdout.read() == u"Hellø\n".encode('utf8')
    assert stderr.read() == u"Hi, stdérr\n".encode('utf8')

def test_forward():
    stdout = io.StringIO()
    stderr = io.StringIO()
    with pipes(stdout=stdout, stderr=stderr) as (_stdout, _stderr):
        printf(u"Hellø")
        printf_err(u"Hi, stdérr")
        assert _stdout is stdout
        assert _stderr is stderr

    assert stdout.getvalue() == u"Hellø\n"
    assert stderr.getvalue() == u"Hi, stdérr\n"

def test_pipes_stderr():
    stdout = io.StringIO()
    with pipes(stdout=stdout, stderr=STDOUT) as (_stdout, _stderr):
        printf(u"Hellø")
        libc.fflush(c_stdout_p)
        time.sleep(0.1)
        printf_err(u"Hi, stdérr")
        assert _stdout is stdout
        assert _stderr is None

    assert stdout.getvalue() == u"Hellø\nHi, stdérr\n"

def test_flush():
    stdout = io.StringIO()
    w = Wurlitzer(stdout=stdout, stderr=STDOUT)
    with w:
        printf_err(u"Hellø")
        time.sleep(0.5)
        assert stdout.getvalue().strip() == u"Hellø"

def test_sys_pipes():
    stdout = io.StringIO()
    stderr = io.StringIO()
    with mock.patch('sys.stdout', stdout), mock.patch('sys.stderr', stderr), sys_pipes():
        printf(u"Hellø")
        printf_err(u"Hi, stdérr")

    assert stdout.getvalue() == u"Hellø\n"
    assert stderr.getvalue() == u"Hi, stdérr\n"

def test_redirect_everything():
    stdout = io.StringIO()
    stderr = io.StringIO()
    with mock.patch('sys.stdout', stdout), mock.patch('sys.stderr', stderr):
        sys_pipes_forever()
        printf(u"Hellø")
        printf_err(u"Hi, stdérr")
        stop_sys_pipes()
    assert stdout.getvalue() == u"Hellø\n"
    assert stderr.getvalue() == u"Hi, stdérr\n"


def count_fds():
    """utility for counting file descriptors"""
    proc_fds = '/proc/{}/fd'.format(os.getpid())
    if os.path.isdir(proc_fds):
        return len(proc_fds)
    else:
        # this is an approximate count,
        # but it should at least be stable if we aren't leaking
        with TemporaryFile() as tf:
            return tf.fileno()


def test_fd_leak():
    base_count = count_fds()
    with pipes():
        print('ok')
    assert count_fds() == base_count
    for i in range(10):
        with pipes():
            print('ok')
        assert count_fds() == base_count


def test_buffer_full():
    with pipes(stdout=None, stderr=io.StringIO()) as (stdout, stderr):
        long_string = "x" * 1000000  # create a very long string
        printf_err(long_string)

    # Test never reaches here as the process hangs.
    assert stderr.getvalue() == long_string + "\n"
