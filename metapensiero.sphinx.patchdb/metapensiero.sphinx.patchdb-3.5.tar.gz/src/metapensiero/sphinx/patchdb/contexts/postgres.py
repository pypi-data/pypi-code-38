# -*- coding: utf-8 -*-
# :Project:   PatchDB -- PostgreSQL script execution context
# :Created:   sab 31 mag 2014 13:03:33 CEST
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


class PostgresContext(SqlContext):
    def makeConnection(self, dsn):
        import psycopg2 as dbapi
        import re

        self.dsn = dsn
        logger.debug('Connecting to %s', self.dsn)
        self.connection = dbapi.connect(self.dsn)
        cursor = self.connection.cursor()
        cursor.execute("set client_encoding to unicode;")

        cursor.execute("SELECT version()")
        v = cursor.fetchone()[0]
        self.connection.rollback()

        m = re.match(r'PostgreSQL (\d+)\.?(\d+)?(?:\.(\d+))?(?:\.\d+)?(?:devel|beta|rc)?', v)
        assert m, "Could not determine PostgreSQL version from %r" % v

        pg_version = tuple([int(x) for x in m.group(1, 2) if x is not None])
        if len(pg_version) < 2:
            pg_version = pg_version + (0,)

        self.assertions.update({
            'postgres': True,
            'postgres_%d' % pg_version[0]: True,
            'postgres_%d_%d' % pg_version: True,
            'postgres_9_x': (9, 0) <= pg_version < (10, 0),
            'postgres_8_x': (8, 0) <= pg_version < (9, 0),
            'postgres_7_x': (7, 0) <= pg_version < (8, 0),
            'postgresql': True,
            'postgresql_%d' % pg_version[0]: True,
            'postgresql_%d_%d' % pg_version: True,
            'postgresql_9_x': (9, 0) <= pg_version < (10, 0),
            'postgresql_8_x': (8, 0) <= pg_version < (9, 0),
            'postgresql_7_x': (7, 0) <= pg_version < (8, 0),
            })

    def setupContext(self):
        from ..patch import MAX_PATCHID_LEN

        cursor = self.connection.cursor()
        cursor.execute("SELECT tablename"
                       " FROM pg_tables"
                       " WHERE tablename = 'patchdb'")
        result = cursor.fetchone()
        if not result:
            logger.info('Creating patchdb table')
            cursor.execute("CREATE TABLE patchdb ("
                           " patchid VARCHAR(%d) NOT NULL PRIMARY KEY,"
                           " revision SMALLINT NOT NULL,"
                           " applied TIMESTAMP WITH TIME ZONE NOT NULL"
                           ")" % MAX_PATCHID_LEN)
        self.connection.commit()

    def savePoint(self, point):
        if not self.connection.autocommit:
            cursor = self.connection.cursor()
            cursor.execute("SAVEPOINT point_%s" % point)

    def rollbackPoint(self, point):
        if not self.connection.autocommit:
            cursor = self.connection.cursor()
            cursor.execute("ROLLBACK TO SAVEPOINT point_%s" % point)

    def commitTransaction(self):
        """Complete current transaction."""
        if not self.connection.autocommit:
            super(PostgresContext, self).commitTransaction()
        else:
            self.connection.autocommit = False

    def rollbackTransaction(self):
        """Rollback current transaction."""
        if not self.connection.autocommit:
            super(PostgresContext, self).rollbackTransaction()
        else:
            self.connection.autocommit = False

    def apply(self, patch, options=None):
        if patch.autocommit:
            self.connection.autocommit = True
        super(PostgresContext, self).apply(patch, options)

    def classifyError(self, exc):
        msg = exc.pgerror
        if hasattr(msg, 'decode'):
            try:
                msg = msg.decode('utf-8')
            except UnicodeDecodeError:
                msg = msg.decode('latin1', 'ignore')
        code = exc.pgcode
        msg = '[%s] %s' % (code, msg)
        # See http://www.postgresql.org/docs/9.3/static/errcodes-appendix.html
        syntaxerror = code in ('42000', '42601')
        nonexistingobj = code in ('42883', '42P01', '42704')
        return msg, syntaxerror, nonexistingobj

    def backup(self, dir):
        state = self.state
        if state is None:
            logger.debug("Skipping initial backup")
            return

        if not isdir(dir):
            makedirs(dir)

        outfname = join(dir, state.state)
        cmd = ['pg_dump', '-d', self.dsn, '-Fc', '-Z9', '-f', outfname]
        subprocess.check_call(cmd)

        with StatesIndex(dir) as index:
            index.append(state)

        logger.info("Wrote pg_dump compressed backup to %s", outfname)

    def restore(self, backup):
        cmd = ['pg_restore', '-d', self.dsn, '-c', backup]
        subprocess.check_call(cmd)
        logger.info("Restored PostgreSQL database from %s", backup)
