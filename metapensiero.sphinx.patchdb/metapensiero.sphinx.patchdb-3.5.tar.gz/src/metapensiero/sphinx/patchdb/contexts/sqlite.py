# -*- coding: utf-8 -*-
# :Project:   PatchDB -- SQLite specialized context
# :Created:   lun 22 feb 2016 11:02:21 CET
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2016, 2017 Lele Gaifax
#

from os import makedirs, rename
from os.path import exists, isdir, join
import subprocess

from ..states import StatesIndex
from . import logger
from .sql import FakeDataDomainsMixin, SqlContext


class SQLiteContext(FakeDataDomainsMixin, SqlContext):
    # SQLite uses qmarks as param style
    GET_PATCH_REVISION_STMT = ("SELECT revision"
                               " FROM patchdb"
                               " WHERE patchid = ?")
    INSERT_PATCH_STMT = ("INSERT INTO patchdb (patchid, revision, applied)"
                         " VALUES (?, ?, ?)")
    UPDATE_PATCH_STMT = ("UPDATE patchdb"
                         " SET revision = ?, applied = ?"
                         " WHERE patchid = ?")
    DELETE_PATCH_STMT = "DELETE FROM patchdb WHERE patchid = ?"

    def makeConnection(self, database):
        from sqlite3 import connect, sqlite_version_info

        self.database = database
        logger.debug('Connecting to %s', self.database)
        self.connection = connect(database)
        # See http://bugs.python.org/issue10740
        self.connection.isolation_level = None

        self.assertions.update({
            'sqlite': True,
            'sqlite3': sqlite_version_info[0] == 3,
            })

    def setupContext(self):
        from ..patch import MAX_PATCHID_LEN

        cursor = self.connection.cursor()
        cursor.execute("PRAGMA table_info('patchdb')")
        result = cursor.fetchone()
        if not result:
            logger.info('Creating patchdb table')
            cursor.execute("CREATE TABLE patchdb ("
                           " patchid VARCHAR(%d) NOT NULL PRIMARY KEY,"
                           " revision SMALLINT NOT NULL,"
                           " applied DATETIME NOT NULL"
                           ")" % MAX_PATCHID_LEN)
            self.connection.commit()

    def savePoint(self, point):
        cursor = self.connection.cursor()
        cursor.execute("savepoint point_%s" % point)

    def rollbackPoint(self, point):
        cursor = self.connection.cursor()
        cursor.execute("rollback to savepoint point_%s" % point)

    def classifyError(self, exc):
        msg = str(exc)
        syntaxerror = msg.endswith('syntax error')
        nonexistingobj = msg.startswith('no such')
        return msg, syntaxerror, nonexistingobj

    def backup(self, dir):
        state = self.state
        if state is None:
            logger.debug("Skipping initial backup")
            return

        if not isdir(dir):
            makedirs(dir)

        outfname = join(dir, state.state)
        cmd = 'sqlite3 %s .dump | gzip -9 > %s' % (self.database, outfname)
        subprocess.check_call(cmd, shell=True)

        with StatesIndex(dir) as index:
            index.append(state)

        logger.info("Wrote sqlite3 gzipped backup to %s", outfname)

    def restore(self, backup):
        oldname = None
        if exists(self.database):
            oldname = self.database + '.old'
            logger.debug("Renaming old SQLite database %s to %s", self.database, oldname)
            rename(self.database, oldname)

        cmd = 'gzip -dc %s | sqlite3 %s' % (backup, self.database)
        try:
            subprocess.check_call(cmd, shell=True)
        except subprocess.CalledProcessError as e:
            logger.error("Restore failed: %s", e)
            if oldname is not None:
                logger.warning("Restoring old SQLite database %s", self.database)
                rename(oldname, self.database)
        else:
            logger.info("Restored SQLite database %s from %s", self.database, backup)
