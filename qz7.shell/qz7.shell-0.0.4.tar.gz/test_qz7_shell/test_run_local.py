"""
Tests for qz7.shell.run_local module.
"""
#pylint: disable=missing-docstring

import subprocess

import pytest

from qz7.shell.cmdlist import command_format
from qz7.shell.run_local import run_local

def test_echo():
    test_str = "hello world"

    x = command_format("echo {}", test_str)
    p = run_local(x, capture_output=True, text=True)

    assert p.stdout.strip() == test_str

def test_false():
    x = command_format("false")
    p = run_local(x)

    assert p.returncode == 1

def test_check():
    x = command_format("false")

    with pytest.raises(subprocess.CalledProcessError):
        run_local(x, check=True)
