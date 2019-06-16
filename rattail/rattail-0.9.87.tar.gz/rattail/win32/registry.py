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
Windows registry utils
"""

from __future__ import unicode_literals, absolute_import


def RegDeleteTree(key, subkey):
    """
    This is a clone of ``win32api.RegDeleteTree()``, since that apparently
    requires Vista or later.
    """
    import pywintypes
    import win32api
    import win32con
    import winerror

    def delete_contents(key):
        subkeys = []
        for name, reserved, class_, mtime in win32api.RegEnumKeyEx(key):
            subkeys.append(name)
        for subkey_name in subkeys:
            subkey = win32api.RegOpenKeyEx(key, subkey_name, 0, win32con.KEY_ALL_ACCESS)
            delete_contents(subkey)
            win32api.RegCloseKey(subkey)
            win32api.RegDeleteKey(key, subkey_name)
        values = []
        i = 0
        while True:
            try:
                name, value, type_ = win32api.RegEnumValue(key, i)
            except pywintypes.error as e:
                if e[0] == winerror.ERROR_NO_MORE_ITEMS:
                    break
            values.append(name)
            i += 1
        for value in values:
            win32api.RegDeleteValue(key, value)

    orig_key = key
    try:
        key = win32api.RegOpenKeyEx(orig_key, subkey, 0, win32con.KEY_ALL_ACCESS)
    except pywintypes.error as e:
        if e[0] != winerror.ERROR_FILE_NOT_FOUND:
            raise
    else:
        delete_contents(key)
        win32api.RegCloseKey(key)
    try:
        win32api.RegDeleteKey(orig_key, subkey)
    except pywintypes.error as e:
        if e[0] == winerror.ERROR_FILE_NOT_FOUND:
            pass
