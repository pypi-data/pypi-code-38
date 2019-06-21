# -*- coding: utf-8 -*-
# :Project:   PatchDB -- Firebird SQL script execution context
# :Created:   sab 31 mag 2014 13:01:51 CEST
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2014, 2016, 2017 Lele Gaifax
#

from os import makedirs
from os.path import isdir, join
import subprocess

from ..states import StatesIndex
from . import logger
from .sql import SqlContext


class FirebirdContext(SqlContext):
    # fdb uses qmarks as param style
    GET_PATCH_REVISION_STMT = ("SELECT revision"
                               " FROM patchdb"
                               " WHERE patchid = ?")
    INSERT_PATCH_STMT = ("INSERT INTO patchdb (patchid, revision, applied)"
                         " VALUES (?, ?, ?)")
    UPDATE_PATCH_STMT = ("UPDATE patchdb"
                         " SET revision = ?, applied = ?"
                         " WHERE patchid = ?")
    GET_LAST_APPLIED_STMT = ("SELECT FIRST 1 patchid, revision"
                             " FROM patchdb"
                             " ORDER BY applied DESC")
    DELETE_PATCH_STMT = "DELETE FROM patchdb WHERE patchid = ?"

    def makeConnection(self, dsn, username, password):
        import fdb as dbapi

        self.dsn = dsn
        self.username = username
        self.password = password
        logger.debug('Connecting to %s', self.dsn)
        self.connection = dbapi.connect(dsn=self.dsn,
                                        user=self.username,
                                        password=self.password)

        fb_version = tuple([int(x) for x in self.connection.version.split('.')])

        self.assertions.update({
            'firebird': True,
            'firebird_2_x': (2, 0) <= fb_version < (3, 0),
            'firebird_3_x': (3, 0) <= fb_version < (4, 0),
            })

    def setupContext(self):
        from ..patch import MAX_PATCHID_LEN

        cursor = self.connection.cursor()
        cursor.execute("SELECT rdb$relation_name"
                       " FROM rdb$relations"
                       " WHERE rdb$relation_name = 'PATCHDB'")
        result = cursor.fetchone()
        if not result:
            logger.info('Creating patchdb table')
            cursor.execute("CREATE TABLE patchdb ("
                           " patchid VARCHAR(%d) NOT NULL PRIMARY KEY,"
                           " revision SMALLINT NOT NULL,"
                           " applied TIMESTAMP NOT NULL"
                           ")" % MAX_PATCHID_LEN)
            self.connection.commit()

    def classifyError(self, exc):
        msg, sqlcode, gdscode = exc.args
        return msg, sqlcode in (-104,), sqlcode in (-607,)

    def backup(self, dir):
        state = self.state
        if state is None:
            logger.debug("Skipping initial backup")
            return

        if not isdir(dir):
            makedirs(dir)

        outfname = join(dir, state.state)
        cmd = 'gbak -b -user %s -pas %s %s stdout | gzip -9 > %s' % (
            self.username, self.password, self.dsn, outfname)
        subprocess.check_call(cmd, shell=True)

        with StatesIndex(dir) as index:
            index.append(state)

        logger.info("Wrote gbak gzipped backup to %s", outfname)

    def restore(self, backup):
        cmd = 'gzip -dc %s | gbak -rep -user %s -pas %s stdin %s' % (
            backup, self.username, self.password, self.dsn)
        subprocess.check_call(cmd, shell=True)
        logger.info("Restored Firebird database %s from %s", self.dsn, backup)
