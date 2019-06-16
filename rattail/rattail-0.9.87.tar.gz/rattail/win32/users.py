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
Windows User Utilities
"""

from __future__ import unicode_literals

import socket
import logging


log = logging.getLogger(__name__)


def user_exists(username, server=None):
    """
    Determine if a Windows user account exists.

    :param username: Username to be checked.

    :param server: Optional server name.  If not specified, only local accounts
       will be checked.
    """
    import win32net
    from pywintypes import error

    # This constant doesn't seem to be importable from anywhere.
    NERR_UserNotFound = 2221

    try:
        info = win32net.NetUserGetInfo(server, username, 0)
    except error as e:
        if e.winerror == NERR_UserNotFound:
            return False
        raise
    return True


def create_user(username, password, full_name=None, comment=None):
    """
    Create a system user account for Rattail.
    """
    import win32net
    import win32netcon

    if user_exists(username):
        log.warning("user already exists: {0}".format(username))
        return False

    if not full_name:
        full_name = "{0} User".format(username.capitalize())
    if not comment:
        comment = "System user account for Rattail applications"

    win32net.NetUserAdd(None, 2, {
            'name': username,
            'password': password,
            'priv': win32netcon.USER_PRIV_USER,
            'comment': comment,
            'flags': (win32netcon.UF_NORMAL_ACCOUNT
                      | win32netcon.UF_PASSWD_CANT_CHANGE
                      | win32netcon.UF_DONT_EXPIRE_PASSWD),
            'full_name': full_name,
            'acct_expires': win32netcon.TIMEQ_FOREVER,
            })

    win32net.NetLocalGroupAddMembers(None, 'Users', 3, [
            {'domainandname': r'{0}\{1}'.format(socket.gethostname(), username)}])

    hide_user_account(username)
    return True


def hide_user_account(username):
    """
    Hide a user account from the Welcome screen.

    This also hides it from the User Accounts control panel applet.
    """

    import win32api
    import win32con
    from rattail.win32 import is_64bit

    if is_64bit():
        key64 = win32api.RegOpenKeyEx(
            win32con.HKEY_LOCAL_MACHINE,
            r'SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon',
            0, win32con.KEY_ALL_ACCESS|win32con.KEY_WOW64_64KEY)
        key = win32api.RegCreateKey(key64, 'SpecialAccounts\\UserList')
        win32api.RegCloseKey(key64)
    else:
        key = win32api.RegCreateKey(
            win32con.HKEY_LOCAL_MACHINE,
            'SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Winlogon\\SpecialAccounts\\UserList')

    win32api.RegSetValueEx(key, username, 0, win32con.REG_DWORD, 0)
    win32api.RegCloseKey(key)


def allow_logon_as_service(username):
    """
    Grant the "Log On As Service" right to a local user account.

    .. note::
       The user account is assumed to already exist.
    """
    import win32security
    import win32con

    sid, domain, sid_type = win32security.LookupAccountName(None, username)
    policy = win32security.LsaOpenPolicy(None, win32con.GENERIC_WRITE)
    win32security.LsaAddAccountRights(policy, sid, [win32security.SE_SERVICE_LOGON_NAME])
    win32security.LsaClose(policy)
