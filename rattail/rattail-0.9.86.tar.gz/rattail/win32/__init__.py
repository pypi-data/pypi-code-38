# -*- coding: utf-8 -*-
################################################################################
#
#  Rattail -- Retail Software Framework
#  Copyright © 2010-2017 Lance Edgar
#
#  This file is part of Rattail.
#
#  Rattail is free software: you can redistribute it and/or modify it under the
#  terms of the GNU General Public License as published by the Free Software
#  Foundation, either version 3 of the License, or (at your option) any later
#  version.
#
#  Rattail is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
#  FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
#  details.
#
#  You should have received a copy of the GNU General Public License along with
#  Rattail.  If not, see <http://www.gnu.org/licenses/>.
#
################################################################################
"""
Windows Platform Utilities
"""

from __future__ import unicode_literals

import platform


def is_64bit():
    """
    Determine if the host machine runs a 64-bit version of Windows.
    """
    return platform.machine() == 'AMD64'


def file_is_free(path):
    """
    Returns boolean indicating whether or not the file located at ``path`` is
    currently tied up in any way by another process.
    """

    # This code was borrowed from Nikita Nemkin:
    # http://stackoverflow.com/a/2848266

    import win32file
    from pywintypes import error
    from winerror import ERROR_SHARING_VIOLATION

    handle = None
    try:
        handle = win32file.CreateFile(
            path,
            win32file.GENERIC_WRITE,
            0,
            None,
            win32file.OPEN_EXISTING,
            win32file.FILE_ATTRIBUTE_NORMAL,
            None)
        return True
    except error as e:
        if e.winerror == ERROR_SHARING_VIOLATION:
            return False
        raise
    finally:
        if handle:
            win32file.CloseHandle(handle)


def process_is_elevated():
    """
    Check if the current process is running with an "elevated token."

    This is meant to indicate whether administrative privileges are in effect.
    Returns a boolean value.
    """

    from win32api import GetCurrentProcess
    from win32security import OpenProcessToken, GetTokenInformation, TokenElevation
    from win32con import TOKEN_READ
    from pywintypes import error
    from winerror import ERROR_INVALID_PARAMETER

    hProcess = GetCurrentProcess()
    hToken = OpenProcessToken(hProcess, TOKEN_READ)
    try:
        elevated = GetTokenInformation(hToken, TokenElevation)
    except error as e:
        if e.winerror == ERROR_INVALID_PARAMETER:
            return True # feign success if OS doesn't support this check
        raise
    return bool(elevated)


def require_elevation():
    """
    Exit properly if the current process does not have an "elevated token."

    If the result of :func:`process_is_elevated()` is ``False``, this function
    will print a brief message to ``sys.stderr`` and exit with the error code
    recommended by Microsoft for this scenario.
    """

    import sys
    from winerror import ERROR_ELEVATION_REQUIRED

    if process_is_elevated():
        return

    sys.stderr.write("This command requires administrative privileges.\n")
    sys.exit(ERROR_ELEVATION_REQUIRED)
