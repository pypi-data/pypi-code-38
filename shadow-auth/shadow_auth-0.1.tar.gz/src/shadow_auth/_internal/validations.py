"""This script contains all the logic related to Validations"""

import os
from sys import platform
from shutil import which
from typing import Callable
from shadow_auth._internal.exceptions import (
    # Exceptions
    PrerequisiteException,
    InvalidArgumentType,

    # Exception Messages
    MESSAGE_INVALID_OS,
    MESSAGE_NO_SHADOW_FILE,
    MESSAGE_INVALID_PERMISSIONS_SHADOW_FILE,
    MESSAGE_CAT_NOT_INSTALLED,
    MESSAGE_GREP_NOT_INSTALLED,
    MESSAGE_OPENSSL_NOT_INSTALLED,
    MESSAGE_PASSWD_NOT_INSTALLED,
    MESSAGE_ARGUMENT_NOT_CALLABLE
)


def check_os() -> None:
    """
    Check that the module is used only in Linux.

    :raises PrerequisiteException:
    """
    if "linux" not in platform.lower():
        raise PrerequisiteException(MESSAGE_INVALID_OS)


def check_shadow_file_exists() -> None:
    """
    Check that the shadow file is used in the Linux system.

    :raises PrerequisiteException:
    """
    if not os.path.exists("/etc/shadow"):
        raise PrerequisiteException(MESSAGE_NO_SHADOW_FILE)


def check_user_can_access_shadow_file() -> None:
    """
    Check that the Linux user using the module has read access to the shadow file.

    :raises PrerequisiteException:
    """
    if not os.access("/etc/shadow", os.R_OK):
        raise PrerequisiteException(MESSAGE_INVALID_PERMISSIONS_SHADOW_FILE)


def check_cat_is_installed() -> None:
    """
    Check that the Linux system has 'cat' installed.

    :raises PrerequisiteException:
    """
    if which("cat") is None:
        raise PrerequisiteException(MESSAGE_CAT_NOT_INSTALLED)


def check_grep_is_installed() -> None:
    """
    Check that the Linux system has 'grep' installed.

    :raises PrerequisiteException:
    """
    if which("grep") is None:
        raise PrerequisiteException(MESSAGE_GREP_NOT_INSTALLED)


def check_openssl_is_installed() -> None:
    """
    Check that the Linux system has 'openssl' installed.

    :raises PrerequisiteException:
    """
    if which("openssl") is None:
        raise PrerequisiteException(MESSAGE_OPENSSL_NOT_INSTALLED)


def check_passwd_is_installed() -> None:
    """
    Check that the Linux system has 'passwd' installed.

    :raises PrerequisiteException:
    """
    if which("paswd") is None:
        raise PrerequisiteException(MESSAGE_PASSWD_NOT_INSTALLED)


def validate_system_requirements_first(func: Callable) -> Callable:
    """
    Execute the prerequisite validations before calling a function.

    :param func: Function that is going to be executed after the prerequisite validations
    :return: A wrapper function that executes the validations and then runs the function
    :raises InvalidArgumentType, PrerequisiteException:
    """
    if not isinstance(func, Callable):
        raise InvalidArgumentType(MESSAGE_ARGUMENT_NOT_CALLABLE)

    def func_wrapper(*args, **kwargs):
        check_os()
        check_shadow_file_exists()
        check_user_can_access_shadow_file()
        check_cat_is_installed()
        check_grep_is_installed()
        check_openssl_is_installed()
        return func(*args, **kwargs)
    return func_wrapper

