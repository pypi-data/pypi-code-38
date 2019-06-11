"""
Tests for qz7.shell.run_remote module.
"""
#pylint: disable=missing-docstring

import os

import pytest

from qz7.shell.cmdlist import command_format
from qz7.shell.run_remote import run_remote, RemoteCalledProcessError

HOSTNAME = os.environ["TEST_SSH_HOST"]

def test_echo():
    test_str = "hello world"

    x = command_format("echo {}", test_str)
    p = run_remote(HOSTNAME, x, capture_output=True, text=True)

    assert p.stdout.strip() == test_str

def test_false():
    x = command_format("false")
    p = run_remote(HOSTNAME, x)

    assert p.returncode == 1

def test_check():
    x = command_format("false")

    with pytest.raises(RemoteCalledProcessError):
        run_remote(HOSTNAME, x, check=True)
