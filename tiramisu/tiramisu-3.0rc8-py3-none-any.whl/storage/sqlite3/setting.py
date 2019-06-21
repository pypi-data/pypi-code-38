# -*- coding: utf-8 -*-
"default plugin for setting: set it in a simple dictionary"
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
from .sqlite3db import Sqlite3DB
from ...log import log


class Properties(Sqlite3DB):
    __slots__ = tuple()

    def __init__(self, storage):
        super(Properties, self).__init__(storage)

    # properties
    def setproperties(self, path, properties):
        path = self._sqlite_encode_path(path)
        self._storage.execute("DELETE FROM property WHERE path = ? AND session_id = ?",
                              (path, self._session_id),
                              False)
        self._storage.execute("INSERT INTO property(path, properties, session_id) VALUES "
                              "(?, ?, ?)", (path,
                                         self._sqlite_encode(properties),
                                         self._session_id))

    def getproperties(self, path, default_properties):
        path = self._sqlite_encode_path(path)
        value = self._storage.select("SELECT properties FROM property WHERE "
                                     "path = ? AND session_id = ? LIMIT 1", (path, self._session_id))
        if value is None:
            return set(default_properties)
        else:
            return set(self._sqlite_decode(value[0]))

    def delproperties(self, path):
        path = self._sqlite_encode_path(path)
        self._storage.execute("DELETE FROM property WHERE path = ? AND session_id = ?",
                              (path, self._session_id))

    def exportation(self):
        """return all modified settings in a dictionary
        example: {'path1': set(['prop1', 'prop2'])}
        """
        ret = {}
        for path, properties, _ in self._storage.select("SELECT * FROM property "
                                                        "WHERE session_id = ?",
                                                        (self._session_id,),
                                                        only_one=False):
            path = self._sqlite_decode_path(path)
            ret[path] = self._sqlite_decode(properties)
        return ret

    def importation(self, properties):
        self._storage.execute("DELETE FROM property WHERE session_id = ?", (self._session_id,), commit=False)
        for path, property_ in properties.items():
            path = self._sqlite_encode_path(path)
            self._storage.execute("INSERT INTO property(path, properties, session_id) "
                                  "VALUES (?, ?, ?)", (path,
                                                       self._sqlite_encode(property_),
                                                       self._session_id,
                                                      ), False)
        self._storage._conn.commit()


class Permissives(Sqlite3DB):
    __slots__ = tuple()

    # permissive
    def setpermissives(self, path, permissive):
        path = self._sqlite_encode_path(path)
        log.debug('setpermissive %s %s %s', path, permissive, id(self))
        self._storage.execute("DELETE FROM permissive WHERE path = ? AND session_id = ?",
                              (path, self._session_id),
                              False)
        self._storage.execute("INSERT INTO permissive(path, permissives, session_id) "
                              "VALUES (?, ?, ?)", (path,
                                                   self._sqlite_encode(permissive),
                                                   self._session_id))

    def getpermissives(self, path='_none'):
        path = self._sqlite_encode_path(path)
        permissives = self._storage.select("SELECT permissives FROM "
                                           "permissive WHERE path = ? AND session_id = ? LIMIT 1",
                                           (path, self._session_id))
        if permissives is None:
            ret = frozenset()
        else:
            ret = frozenset(self._sqlite_decode(permissives[0]))
        log.debug('getpermissive %s %s %s', path, ret, id(self))
        return ret

    def delpermissive(self, path):
        path = self._sqlite_encode_path(path)
        self._storage.execute("DELETE FROM permissive WHERE path = ? AND session_id = ?",
                              (path, self._session_id))

    def exportation(self):
        """return all modified permissives in a dictionary
        example: {'path1': set(['perm1', 'perm2'])}
        """
        ret = {}
        for path, permissives in self._storage.select("SELECT path, permissives FROM permissive "
                                                      "WHERE session_id = ?",
                                                      (self._session_id,),
                                                      only_one=False):
            path = self._sqlite_decode_path(path)
            ret[path] = self._sqlite_decode(permissives)
        return ret

    def importation(self, permissives):
        self._storage.execute("DELETE FROM permissive WHERE session_id = ?", (self._session_id,),
                              commit=False)
        for path, permissive in permissives.items():
            path = self._sqlite_encode_path(path)
            self._storage.execute("INSERT INTO permissive(path, permissives, session_id) "
                                  "VALUES (?, ?, ?)", (path,
                                                       self._sqlite_encode(permissive),
                                                       self._session_id,
                                                      ), False)
        self._storage._conn.commit()
