# SPDX-License-Identifier: GPL-3.0-or-later

import contextlib
import logging
import socket
import threading

import pexpect
import pexpect.fdpexpect

import alpy.pexpect_log
import alpy.utils

PORT = 2023


def create_socket():
    return socket.socket(socket.AF_INET, socket.SOCK_STREAM)


def connect_socket(sock, host="127.0.0.1", port=PORT):
    log = alpy.utils.context_logger(__name__)
    with log("Connect to console"):
        sock.connect((host, port))


def create(connected_socket, timeout):
    logger = logging.getLogger(__name__)
    console = pexpect.fdpexpect.fdspawn(connected_socket, timeout=timeout)
    console.logfile_read = alpy.pexpect_log.LogfileRead(logger)
    console.logfile_send = alpy.pexpect_log.LogfileSend(logger)
    return console


def flush_log(console):
    console.logfile_read.log_remaining_text()


def close(console):
    log = alpy.utils.context_logger(__name__)
    with log("Close console"):
        console.expect_exact([pexpect.EOF, pexpect.TIMEOUT], timeout=1)
        console.close()
        flush_log(console)


@contextlib.contextmanager
def connect(*, host="127.0.0.1", port=PORT, timeout):
    sock = create_socket()
    connect_socket(sock, host, port)
    console = create(sock, timeout)
    try:
        yield console
    finally:
        close(console)


def read_until(console, event):
    while not event.is_set() and console.expect_exact(
        [pexpect.EOF, pexpect.TIMEOUT], timeout=0.5
    ):
        pass


@contextlib.contextmanager
def read_in_background(console):
    stop_reading = threading.Event()
    thread = threading.Thread(target=read_until, args=(console, stop_reading))
    thread.start()
    try:
        yield
    finally:
        stop_reading.set()
        thread.join()
