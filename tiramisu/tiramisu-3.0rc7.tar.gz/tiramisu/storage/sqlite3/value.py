# -*- coding: utf-8 -*-
"default plugin for value: set it in a simple dictionary"
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
from .storage import delete_session
from ...setting import undefined, owners
from ...i18n import _
from ...log import log


class Values(Sqlite3DB):
    __slots__ = ('__weakref__',)

    def __init__(self, storage):
        """init plugin means create values storage
        """
        super(Values, self).__init__(storage)

    # sqlite
    def _sqlite_select(self, path, index):
        request = "SELECT value FROM value WHERE path = ? AND session_id = ? "
        params = (path, self._session_id)
        if index is not None:
            request += "and idx = ? "
            params = (path, self._session_id, index)
        request += "LIMIT 1"
        return self._storage.select(request, params)

    def commit(self):
        self._storage.commit()

    # value
    def setvalue(self,
                 path,
                 value,
                 owner,
                 index,
                 commit):
        """set value for an option
        a specified value must be associated to an owner
        """
        log.debug('setvalue %s %s %s %s %s', path, value, owner, index, commit)
        path = self._sqlite_encode_path(path)
        if index is not None:
            self.resetvalue_index(path,
                                  index,
                                  commit=False)
            self._storage.execute("INSERT INTO value(path, value, owner, idx, session_id) VALUES "
                                  "(?, ?, ?, ?, ?)", (path, self._sqlite_encode(value),
                                                      str(owner),
                                                      index,
                                                      self._session_id),
                                  commit=commit)
        else:
            self.resetvalue(path,
                            commit=False)
            self._storage.execute("INSERT INTO value(path, value, owner, session_id) VALUES "
                                  "(?, ?, ?, ?)", (path, self._sqlite_encode(value),
                                                   str(owner),
                                                   self._session_id),
                                  commit=commit)

    def hasvalue(self,
                 path,
                 index=None):
        """if opt has a value
        return: boolean
        """
        log.debug('hasvalue %s %s', path, index)
        path = self._sqlite_encode_path(path)
        return self._sqlite_select(path, index) is not None


    def reduce_index(self, path, index):
        """
        _values == ((path1, path2), ((idx1_1, idx1_2), None),
                    ((value1_1, value1_2), value2), ((owner1_1, owner1_2), owner2))
        """
        log.debug('reduce_index %s %s %s', path, index, id(self))
        self._storage.execute("UPDATE value SET idx = ? WHERE path = ? and idx = ? "
                              "AND session_id = ?",
                              (index - 1, path, index, self._session_id))

    def resetvalue_index(self,
                         path,
                         index,
                         commit=True):
        """remove value means delete value in storage
        """
        log.debug('resetvalue_index %s %s %s', path, index, commit)
        path = self._sqlite_encode_path(path)
        self._storage.execute("DELETE FROM value WHERE path = ? AND session_id = ? AND idx = ?",
                              (path, self._session_id, index),
                              commit=commit)

    def resetvalue(self,
                   path,
                   commit):
        """remove value means delete value in storage
        """
        log.debug('resetvalue %s %s', path, commit)
        path = self._sqlite_encode_path(path)
        self._storage.execute("DELETE FROM value WHERE path = ? AND session_id = ?",
                              (path, self._session_id),
                              commit=commit)

    # owner
    def setowner(self,
                 path,
                 owner,
                 index=None):
        """change owner for an option
        """
        log.debug('setowner %s %s %s', path, owner, index)
        path = self._sqlite_encode_path(path)
        if index is None:
            self._storage.execute("UPDATE value SET owner = ? WHERE path = ? AND session_id = ?",
                                 (str(owner), path, self._session_id))
        else:
            self._storage.execute("UPDATE value SET owner = ? WHERE path = ? and idx = ? AND session_id = ?",
                                 (str(owner), path, index, self._session_id))

    def getowner(self,
                 path,
                 default,
                 index=None,
                 with_value=False):
        """get owner for an option
        return: owner object
        """
        log.debug('getowner %s %s %s %s', path, default, index, with_value)
        path = self._sqlite_encode_path(path)
        request = "SELECT owner, value FROM value WHERE path = ? AND session_id = ?"
        if index is not None:
            request += " AND idx = ?"
            params = (path, self._session_id, index)
        else:
            params = (path, self._session_id)
        request += ' LIMIT 1'
        owner = self._storage.select(request, params)
        if owner is None:
            if not with_value:
                return default
            else:
                return default, None
        else:
            # autocreate owners
            try:
                nowner = getattr(owners, owner[0])
            except AttributeError:  # pragma: no cover
                owners.addowner(owner[0])
                nowner = getattr(owners, owner[0])
            if not with_value:
                return nowner
            else:
                value = self._sqlite_decode(owner[1])
                return nowner, value

    def set_information(self, path, key, value):
        """updates the information's attribute
        (which is a dictionary)

        :param key: information's key (ex: "help", "doc"
        :param value: information's value (ex: "the help string")
        """
        log.debug('set_information %s %s', key, value)
        path = self._sqlite_encode_path(path)
        self._storage.execute("DELETE FROM information WHERE key = ? AND session_id = ? AND path = ?",
                             (key, self._session_id, path),
                             False)
        self._storage.execute("INSERT INTO information(key, value, session_id, path) VALUES "
                             "(?, ?, ?, ?)", (key, self._sqlite_encode(value), self._session_id, path))

    def get_information(self, path, key, default):
        """retrieves one information's item

        :param key: the item string (ex: "help")
        """
        log.debug('get_information %s %s', key, default)
        path = self._sqlite_encode_path(path)
        value = self._storage.select("SELECT value FROM information WHERE key = ? AND "
                                     "session_id = ? AND path = ?",
                                    (key, self._session_id, path))
        if value is None:
            if default is undefined:
                raise ValueError(_("information's item"
                                   " not found: {0}").format(key))
            return default
        else:
            return self._sqlite_decode(value[0])

    def del_information(self, path, key, raises):
        log.debug('del_information %s %s', key, raises)
        path = self._sqlite_encode_path(path)
        if raises and self._storage.select("SELECT value FROM information WHERE key = ? "
                                           "AND session_id = ? AND path = ?",
                                           (key, self._session_id, path)) is None:
            raise ValueError(_("information's item not found {0}").format(key))
        self._storage.execute("DELETE FROM information WHERE key = ? AND session_id = ? AND path = ?",
                              (key, self._session_id, path))

    def list_information(self, path):
        path = self._sqlite_encode_path(path)
        rows = self._storage.select("SELECT key FROM information WHERE session_id = ? AND path = ?",
                                    (self._session_id, path),
                                    only_one=False)
        for row in rows:
            yield self._sqlite_decode_path(row[0])

    def del_informations(self):
        self._storage.execute("DELETE FROM information WHERE session_id = ?",
                              (self._session_id,))

    def exportation(self):
        log.debug('exportation')
        rows = self._storage.select("SELECT path, value, owner, idx FROM value WHERE "
                                    "session_id = ?;", (self._session_id,), only_one=False)
        ret = [[], [], [], []]
        for row in rows:
            path = self._sqlite_decode_path(row[0])
            value = self._sqlite_decode(row[1])
            owner = row[2]
            index = row[3]
            if index is None:
                ret[0].append(path)
                ret[1].append(index)
                ret[2].append(value)
                ret[3].append(owner)
            else:
                if path in ret[0]:
                    path_idx = ret[0].index(path)
                    ret[1][path_idx].append(index)
                    ret[2][path_idx].append(value)
                    ret[3][path_idx].append(owner)
                else:
                    ret[0].append(path)
                    ret[1].append([index])
                    ret[2].append([value])
                    ret[3].append([owner])

        return ret

    def importation(self, export):
        log.debug('importation')
        request = "DELETE FROM value WHERE session_id = ?"
        self._storage.execute(request, (self._session_id,),
                              commit=False)
        for idx, path in enumerate(export[0]):
            path = self._sqlite_encode_path(path)
            index = export[1][idx]
            value = export[2][idx]
            owner = export[3][idx]
            if index is None:
                self._storage.execute("INSERT INTO value(path, value, owner, idx, session_id) VALUES "
                                      "(?, ?, ?, ?, ?)", (path, self._sqlite_encode(value),
                                                          str(owner), index,
                                                          self._session_id), commit=False)
            else:
                for val in zip(index, value, owner):
                    self._storage.execute("INSERT INTO value(path, value, owner, idx, session_id)"
                                          "VALUES (?, ?, ?, ?, ?)", (path,
                                                                     self._sqlite_encode(val[1]),
                                                                     str(val[2]), val[0],
                                                                     self._session_id),
                                          commit=False)
        self._storage._conn.commit()

    def get_max_length(self,
                       path):
        log.debug('get_max_length %s', path)
        val_max = self._storage.select("SELECT max(idx) FROM value WHERE path = ? AND session_id = ?",
                                       (path, self._session_id), False)
        if val_max[0][0] is None:
            return 0
        return val_max[0][0] + 1
