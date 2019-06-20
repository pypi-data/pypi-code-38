""" System utility functions """

import os

__author__ = "Databio Lab"
__email__ = "nathan@code.databio.org"

__all__ = ["is_command_callable"]


def is_command_callable(command):
    """
    Check if command can be called.

    :param str command: actual command to call
    :return bool: whether given command's call succeeded
    :raise ValueError: if the alleged command clearly isn't one
    """
    if not command:
        raise ValueError("Not a command: {} ()".
                         format(command, type(command).__name__))
    # Use `command` to see if command is callable, store exit code
    code = os.system(
        "command -v {0} >/dev/null 2>&1 || {{ exit 1; }}".format(command))
    return not bool(code)
