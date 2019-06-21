# -*- coding: utf-8 -*-
# Copyright (C) 2013-2019 Team tiramisu (see AUTHORS for all contributors)
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU Lesser General Public License as published by the
# Free Software Foundation, either version 3 of the License, or (at your
# option) any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
# ____________________________________________________________
from ...i18n import _
from ...error import ConflictError


class Setting:
    """Dictionary storage has no particular setting.
    """
    __slots__ = tuple()


SETTING = Setting()
_list_sessions = []
PERSISTENT = False


def list_sessions():
    return _list_sessions


class Storage(object):
    __slots__ = ('session_id', 'persistent')
    storage = 'dictionary'
    # if object could be serializable
    serializable = True

    def __init__(self, session_id, persistent, test=False):
        if not test and session_id in _list_sessions:
            raise ConflictError(_('session "{}" already used').format(session_id))
        if persistent:
            raise ValueError(_('a dictionary cannot be persistent'))
        self.session_id = session_id
        self.persistent = persistent
        _list_sessions.append(self.session_id)

    def __del__(self):
        try:
            _list_sessions.remove(self.session_id)
        except AttributeError:
            pass


def getsession():
    pass
