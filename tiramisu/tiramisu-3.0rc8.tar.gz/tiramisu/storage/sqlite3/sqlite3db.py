# -*- coding: utf-8 -*-
"sqlite3 cache"
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
try:
    from cPickle import loads, dumps
except ImportError:
    from pickle import loads, dumps
from ..util import Cache


class Sqlite3DB(Cache):
    __slots__ = ('_session_id',)
    def __init__(self, storage):
        self._session_id = storage.session_id
        super(Sqlite3DB, self).__init__(storage)

    def _sqlite_decode_path(self, path):
        if path == '_none':
            return None
        else:
            return path

    def _sqlite_encode_path(self, path):
        if path is None:
            return '_none'
        else:
            return path

    def _sqlite_decode(self, value):
        return loads(value)

    def _sqlite_encode(self, value):
        if isinstance(value, tuple):
            value = list(value)
        return dumps(value)
