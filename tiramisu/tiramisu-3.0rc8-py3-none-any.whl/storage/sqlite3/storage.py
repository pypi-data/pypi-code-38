# -*- coding: utf-8 -*-
"default plugin for cache: set it in a simple dictionary"
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
from os.path import join
import sqlite3
from ...error import ConflictError


global CONN
CONN = None


class Setting:
    """:param extension: database file extension (by default: db)
    :param dir_database: root database directory (by default: /tmp)
    """
    __slots__ = ('extension',
                 'dir_database',
                 'name')

    def __init__(self):
        self.extension = 'db'
        self.dir_database = '/tmp'
        self.name = 'tiramisu'

    def __setattr__(self, key, value):
        if CONN is not None:  # pragma: no cover
            raise Exception(_('cannot change setting when connexion is already '
                              'opened'))
        super().__setattr__(key, value)


PERSISTENT = True
SETTING = Setting()


def _gen_filename():
    return join(SETTING.dir_database, '{0}.{1}'.format(SETTING.name, SETTING.extension))


def list_sessions():
    cursor = CONN.cursor()
    names = [row[0] for row in cursor.execute("SELECT session FROM session").fetchall()]
    return names


def delete_session(session_id,
                   _session_id=None):
    cursor = CONN.cursor()
    if _session_id is None:
        _session_id = cursor.execute("SELECT session_id FROM session WHERE session = ?",
                                     (session_id,)).fetchone()
        if _session_id is not None:
            _session_id = _session_id[0]
    if _session_id is not None:
        cursor.execute("DELETE FROM property WHERE session_id = ?", (_session_id,))
        cursor.execute("DELETE FROM permissive WHERE session_id = ?", (_session_id,))
        cursor.execute("DELETE FROM value WHERE session_id = ?", (_session_id,))
        cursor.execute("DELETE FROM information WHERE session_id = ?", (_session_id,))
        cursor.execute("DELETE FROM session WHERE session_id = ?", (_session_id,))
        CONN.commit()
    cursor.close()


class Storage(object):
    __slots__ = ('_conn', '_cursor', 'persistent', 'session_id', 'session_name', 'created')
    storage = 'sqlite3'

    def __init__(self, session_id, persistent, test=False):
        self.created = False
        self.persistent = persistent
        global CONN
        init = False
        if CONN is None:
            init = True
            CONN = sqlite3.connect(_gen_filename())
            CONN.text_factory = str
        self._conn = CONN
        self._cursor = self._conn.cursor()
        self.session_name = session_id
        if init:
            session_table = 'CREATE TABLE IF NOT EXISTS session(session_id INTEGER, '
            session_table += 'session TEXT UNIQUE, persistent BOOL, PRIMARY KEY(session_id))'
            settings_table = 'CREATE TABLE IF NOT EXISTS property(path TEXT,'
            settings_table += 'properties text, session_id INTEGER, PRIMARY KEY(path, session_id), '
            settings_table += 'FOREIGN KEY(session_id) REFERENCES session(session_id))'
            permissives_table = 'CREATE TABLE IF NOT EXISTS permissive(path TEXT,'
            permissives_table += 'permissives TEXT, session_id INTEGER, PRIMARY KEY(path, session_id), '
            permissives_table += 'FOREIGN KEY(session_id) REFERENCES session(session_id))'
            values_table = 'CREATE TABLE IF NOT EXISTS value(path TEXT, '
            values_table += 'value TEXT, owner TEXT, idx INTEGER, session_id INTEGER, '\
                            'PRIMARY KEY (path, idx, session_id), '
            values_table += 'FOREIGN KEY(session_id) REFERENCES session(session_id))'
            informations_table = 'CREATE TABLE IF NOT EXISTS information(key TEXT,'
            informations_table += 'value TEXT, session_id INTEGER, path TEXT, '
            informations_table += 'PRIMARY KEY (key, session_id), '
            informations_table += 'FOREIGN KEY(session_id) REFERENCES session(session_id))'
            self.execute(session_table, commit=False)
            self.execute(values_table, commit=False)
            self.execute(informations_table, commit=False)
            self.execute(settings_table, commit=False)
            self.execute(permissives_table, commit=False)
        self.session_id = None
        if self.persistent:
            select = self.select("SELECT session_id FROM session WHERE session = ?", (session_id,))
            if select is not None:
                self.session_id = select[0]
        if self.session_id is None:
            try:
                self.execute('INSERT INTO session(session, persistent) VALUES (?, ?)',
                             (session_id, persistent))
            except sqlite3.IntegrityError:  # pragma: no cover
                raise ConflictError(_('session "{}" already used').format(session_id))
            self.session_id = self._cursor.lastrowid
        self.created = True

    def commit(self):
        self._conn.commit()

    def execute(self, sql, params=None, commit=True):
        #print(sql, params, commit)
        if params is None:
            params = tuple()
        self._cursor.execute(sql, params)
        if commit:
            self.commit()

    def select(self, sql, params=None, only_one=True):
        self.execute(sql, params=params, commit=False)
        if only_one:
            return self._cursor.fetchone()
        else:
            return self._cursor.fetchall()

    def __del__(self):
        self._cursor.close()
        if self.created and not self.persistent:
            if delete_session is not None:
                session_id = getattr(self, 'session_id', None)
                delete_session(self.session_name,
                               session_id)


def getsession():
    pass
