# -*- coding: utf-8 -*-
# :Project:   PatchDB -- MySQL script execution context
# :Created:   lun 02 giu 2014 09:21:14 CEST
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2014, 2016, 2017 Lele Gaifax
#

from os import makedirs
from os.path import isdir, join
import subprocess

from ..states import StatesIndex
from . import logger
from .sql import FakeDataDomainsMixin, SqlContext, statement_starts_with, Keyword


class MySQLContext(FakeDataDomainsMixin, SqlContext):
    def __init__(self, **args):
        SqlContext.__init__(self, **args)

        self._domains = {}
        "A dictionary containing defined domains."

    def makeConnection(self, host, port, db, username, password, charset, driver):
        import importlib
        import re

        self.dbapi = importlib.import_module(driver)
        self.host = host
        self.port = port
        self.db = db
        self.username = username
        self.password = password
        self.charset = charset
        logger.debug('Connecting to %s/%s', self.host, self.db)
        self.connection = self.dbapi.connect(host=self.host,
                                             port=self.port,
                                             user=self.username,
                                             passwd=self.password,
                                             db=self.db,
                                             charset=self.charset,
                                             use_unicode=True)
        cursor = self.connection.cursor()
        cursor.execute("SELECT version()")
        v = cursor.fetchone()
        m = re.match('(\d+)\.(\d+)\.(\d+)', v[0])
        assert m, "Could not determine mysql version"
        version = tuple([int(x) for x in m.group(1, 2)])

        self.assertions.update({
            'mysql': True,
            'mysql_6_x': (6, 0) <= version < (7, 0),
            'mysql_5_x': (5, 0) <= version < (6, 0),
            'mysql_4_x': (4, 0) <= version < (5, 0),
            })

    def setupContext(self):
        from ..patch import MAX_PATCHID_LEN

        cursor = self.connection.cursor()
        try:
            cursor.execute("DESCRIBE patchdb")
        except self.dbapi.err.ProgrammingError:
            logger.info('Creating patchdb table')
            cursor.execute("CREATE TABLE patchdb ("
                           " patchid VARCHAR(%d) CHARACTER SET utf8mb4 NOT NULL PRIMARY KEY,"
                           " revision SMALLINT NOT NULL,"
                           " applied DATETIME(6) NOT NULL"
                           ")" % MAX_PATCHID_LEN)

    def classifyError(self, exc):
        if hasattr(exc, 'errmsg'):
            msg = exc.errmsg
            code = exc.errno
        else:
            code, msg = exc.args
        if hasattr(msg, 'decode'):
            try:
                msg = msg.decode('utf-8')
            except UnicodeDecodeError:
                msg = msg.decode('latin1', 'ignore')
        msg = '[%d] %s' % (code, msg)
        # See http://dev.mysql.com/doc/refman/5.6/en/error-messages-server.html
        syntaxerror = code in (1064, 1149)
        nonexistingobj = code in (
            1051,  # ER_BAD_TABLE_ERROR
            1091,  # ER_CANT_DROP_FIELD_OR_KEY
            1141,  # ER_NONEXISTING_GRANT
            1146,  # ER_NO_SUCH_TABLE
        )
        return msg, syntaxerror, nonexistingobj

    def shouldIgnoreNonExistingObjectError(self, stmt):
        return statement_starts_with(stmt, ([(Keyword.DDL, 'DROP'), (Keyword, 'REVOKE')],))

    def backup(self, dir):
        state = self.state
        if state is None:
            logger.debug("Skipping initial backup")
            return

        if not isdir(dir):
            makedirs(dir)

        outfname = join(dir, state.state)
        cmd = 'mysqldump -h %s -P %s %s %s --add-drop-database -B %s | gzip -9 > %s' % (
            self.host, self.port,
            ('-u %s' % self.username) if self.username else '',
            ('-p%s' % self.password) if self.password else '',
            self.db, outfname)
        subprocess.check_call(cmd, shell=True)

        with StatesIndex(dir) as index:
            index.append(state)

        logger.info("Wrote mysqldump gzipped backup to %s", outfname)

    def restore(self, backup):
        cmd = 'gzip -dc %s | mysql -h %s -P %s %s %s' % (
            backup, self.host, self.port,
            ('-u %s' % self.username) if self.username else '',
            ('-p%s' % self.password) if self.password else '')
        subprocess.check_call(cmd, shell=True)
        logger.info("Restored MySQL database %s from %s", self.db, backup)
