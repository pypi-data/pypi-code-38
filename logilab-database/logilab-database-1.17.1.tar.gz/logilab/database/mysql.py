# copyright 2003-2013 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
# contact http://www.logilab.fr/ -- mailto:contact@logilab.fr
#
# This file is part of logilab-database.
#
# logilab-database is free software: you can redistribute it and/or modify it
# under the terms of the GNU Lesser General Public License as published by the
# Free Software Foundation, either version 2.1 of the License, or (at your
# option) any later version.
#
# logilab-database is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License
# for more details.
#
# You should have received a copy of the GNU Lesser General Public License along
# with logilab-database. If not, see <http://www.gnu.org/licenses/>.
"""Mysql RDBMS support, using the mysqldb driver

Full-text search based on MyISAM full text search capabilities.
"""
__docformat__ = "restructuredtext en"

from warnings import warn

from six import PY2

from logilab import database as db
from logilab.database.fti import normalize_words, tokenize

class _MySqlDBAdapter(db.DBAPIAdapter):
    """Simple mysql Adapter to DBAPI
    """
    BOOLEAN = 'XXX' # no specific type code for boolean

    def __init__(self, native_module, pywrap=False):
        db.DBAPIAdapter.__init__(self, native_module, pywrap)
        self._init_module()

    def _init_module(self):
        """initialize mysqldb to use mx.DateTime for date and timestamps"""
        natmod = self._native_module
        if hasattr(natmod, '_lc_initialized'):
            return
        natmod._lc_initialized = 1
        # date/time types handling
        if db.USE_MX_DATETIME:
            from MySQLdb import times
            from mx import DateTime as mxdt
            times.Date = times.date = mxdt.Date
            times.Time = times.time = mxdt.Time
            times.Timestamp = times.datetime = mxdt.DateTime
            times.TimeDelta = times.timedelta = mxdt.TimeDelta
            times.DateTimeType = mxdt.DateTimeType
            times.DateTimeDeltaType = mxdt.DateTimeDeltaType

    def connect(self, host='', database='', user='', password='', port=None,
                unicode=True, charset='utf8', schema=None, extra_args=None):
        """Handles mysqldb connection format
        the unicode named argument asks to use Unicode objects for strings
        in result sets and query parameters
        """
        if schema is not None:
            warn('schema support is not implemented on mysql backends, ignoring schema %s'
                 % schema)
        kwargs = {'host' : host or '', 'db' : database,
                  'user' : user, 'passwd' : password,
                  'use_unicode' : unicode}
        # MySQLdb doesn't support None port
        if port:
            kwargs['port'] = int(port)
        cnx = self._native_module.connect(**kwargs)
        if unicode:
            if charset.lower() == 'utf-8':
                charset = 'utf8'
            cnx.set_character_set(charset)
        return self._wrap_if_needed(cnx)

    def _transformation_callback(self, description, encoding='utf-8', binarywrap=None):
        typecode = description[1]
        # hack to differentiate mediumtext (String) and tinyblob/longblog
        # (Password/Bytes) which are all sharing the same type code :(
        if typecode == self.BINARY:
            def _transform(value):
                if hasattr(value, 'tostring'): # may be an array
                    value = value.tostring()
                maxsize = description[3]
                # mediumtext can hold up to (2**24 - 1) characters (16777215)
                # but if utf8 is set, each character is stored on 3 bytes words,
                # so we have to test for 3 * (2**24 - 1)  (i.e. 50331645)
                # XXX: what about other encodings ??
                if maxsize in (16777215, 50331645): # mediumtext (2**24 - 1)
                    if PY2 and isinstance(value, str):
                        return unicode(value, encoding, 'replace')
                    return value
                #if maxsize == 255: # tinyblob (2**8 - 1)
                #    return value
                if binarywrap is None:
                    return value
                return binarywrap(value)
        else:
            return super(_MySqlDBAdapter, self)._transformation_callback(description,
                                                                         encoding, binarywrap)

    def binary_to_str(self, value):
        """turn raw value returned by the db-api module into a python string"""
        if hasattr(value, 'tostring'): # may be an array
            return value.tostring()
        return value

    def type_code_test(self, cursor):
        for typename in ('STRING', 'BOOLEAN', 'BINARY', 'DATETIME', 'NUMBER'):
            self.logger.debug('%s %s', typename, getattr(self, typename))
        try:
            cursor.execute("""CREATE TABLE _type_code_test(
            varchar_field varchar(50),
            text_field text unicode,
            mtext_field mediumtext,
            binary_field tinyblob,
            blob_field blob,
            lblob_field longblob
            )""")
            cursor.execute("INSERT INTO _type_code_test VALUES ('1','2','3','4', '5', '6')")
            cursor.execute("SELECT * FROM _type_code_test")
            descr = cursor.description
            self.logger.info('db fields type codes')
            for i, name in enumerate(('varchar', 'text', 'mediumtext',
                                      'binary', 'blob', 'longblob')):
                self.logger.info('%s %s', name, descr[i])
        finally:
            cursor.execute("DROP TABLE _type_code_test")


db._PREFERED_DRIVERS['mysql'] = ['MySQLdb']#, 'pyMySQL.MySQL']
db._ADAPTER_DIRECTORY['mysql'] = {'MySQLdb': _MySqlDBAdapter,
                         }

class _MyAdvFuncHelper(db._GenericAdvFuncHelper):
    """MySQL helper, taking advantage of postgres SEQUENCE support
    """
    backend_name = 'mysql'
    needs_from_clause = True
    ilike_support = False # insensitive search by default
    case_sensitive = True

    TYPE_MAPPING = db._GenericAdvFuncHelper.TYPE_MAPPING.copy()
    TYPE_MAPPING['Password'] = 'tinyblob'
    TYPE_MAPPING['String'] = 'mediumtext'
    TYPE_MAPPING['Bytes'] = 'longblob'
    # don't use timestamp which is automatically updated on row update
    TYPE_MAPPING['Datetime'] = 'datetime'

    TYPE_CONVERTERS = db._GenericAdvFuncHelper.TYPE_CONVERTERS.copy()

    def mycmd(self, cmd, dbhost, dbport, dbuser):
        cmd = [cmd]
        # XXX compress
        dbhost = dbhost or self.dbhost
        if dbhost is not None:
            cmd += ('-h', dbhost)
        dbport = dbport or self.dbport
        if dbport is not None:
            cmd += ('-P', str(dbport))
        cmd += ('-u', dbuser or self.dbuser)
        return cmd

    def system_database(self):
        """return the system database for the given driver"""
        return ''

    def backup_commands(self, backupfile, keepownership=True,
                        dbname=None, dbhost=None, dbport=None, dbuser=None, dbschema=None):
        cmd = self.mycmd('mysqldump', dbhost, dbport, dbuser)
        cmd += ('-p', '-r', backupfile, dbname or self.dbname)
        return [cmd]

    def restore_commands(self, backupfile, keepownership=True, drop=True,
                         dbname=None, dbhost=None, dbport=None, dbuser=None,
                         dbencoding=None, dbschema=None):
        dbname = dbname or self.dbname
        cmds = []
        mysqlcmd = ' '.join(self.mycmd('mysql', dbhost, dbport, dbuser))
        if drop:
            cmd = 'echo "DROP DATABASE %s;" | %s -p' % (
                dbname, mysqlcmd)
            cmds.append(cmd)
        cmd = 'echo "%s;" | %s -p' % (
            self.sql_create_database(dbname, dbencoding), mysqlcmd)
        cmds.append(cmd)
        cmd = '%s -p %s < %s' % (mysqlcmd, dbname, backupfile)
        cmds.append(cmd)
        return cmds

    def sql_temporary_table(self, table_name, table_schema,
                            drop_on_commit=True):
        if not drop_on_commit:
            return "CREATE TEMPORARY TABLE %s (%s);" % (
                table_name, table_schema)
        return "CREATE TEMPORARY TABLE %s (%s) ON COMMIT DROP;" % (
            table_name, table_schema)

    def sql_create_database(self, dbname, dbencoding=None):
        sql = 'CREATE DATABASE "%(dbname)s"'
        dbencoding = dbencoding or self.dbencoding
        if dbencoding:
            sql += " CHARACTER SET %(dbencoding)s"
        return sql % locals()

    def sql_rename_col(self, table, column, newname, coltype, null_allowed):
        if null_allowed:
            cmd = 'DEFAULT'
        else:
            cmd = 'NOT'
        return 'ALTER TABLE %s CHANGE %s %s %s %s NULL' % (
            table, column, newname, coltype, cmd)

    def sql_change_col_type(self, table, column, coltype, null_allowed):
        if null_allowed:
            cmd = 'DEFAULT'
        else:
            cmd = 'NOT'
        return 'ALTER TABLE %s MODIFY COLUMN %s %s %s NULL' % (
            table, column, coltype, cmd)

    def sql_set_null_allowed(self, table, column, coltype, null_allowed):
        return self.sql_change_col_type(table, column, coltype, null_allowed)

    def create_database(self, cursor, dbname, owner=None, dbencoding=None):
        """create a new database"""
        cursor.execute(self.sql_create_database(dbname, dbencoding))
        if owner:
            cursor.execute('GRANT ALL ON `%s`.* to %s' % (dbname, owner))

    def sql_regexp_match_expression(self, pattern):
        """pattern matching using regexp"""
        return "REGEXP %s" % pattern

    def list_users(self, cursor):
        """return the list of existing database users"""
        # Host, Password
        cursor.execute("SELECT User FROM mysql.user")
        return [r[0] for r in cursor.fetchall()]

    def list_databases(self, cursor):
        """return the list of existing databases"""
        cursor.execute('SHOW DATABASES')
        return [r[0] for r in cursor.fetchall()]

    def list_tables(self, cursor):
        """return the list of tables of a database"""
        cursor.execute("SHOW TABLES")
        return [r[0] for r in cursor.fetchall()]

    def list_indices(self, cursor, table=None):
        """return the list of indices of a database, only for the given table if
        specified
        """
        if table:
            cursor.execute("SHOW INDEX FROM %s" % table)
            return [r[2] for r in cursor.fetchall()]
        allindices = []
        for table in self.list_tables(cursor):
            allindices += self.list_indices(cursor, table)
        return allindices

    # full-text search customization ###########################################

    fti_table = 'appears'
    fti_need_distinct = False

    def cursor_index_object(self, uid, obj, cursor):
        """Index an object, using the db pointed by the given cursor.
        """
        uid = int(uid)
        ftwords = []
        # sort for test predictability
        for weight, words in sorted(obj.get_words().items()):
            ftwords += normalize_words(words)
        if ftwords:
            cursor.execute("INSERT INTO appears(uid, words) "
                           "VALUES (%(uid)s, %(wrds)s);",
                           {'uid':uid, 'wrds': ' '.join(ftwords)})

    def fulltext_search(self, querystr, cursor=None):
        """Execute a full text query and return a list of 2-uple (rating, uid).
        """
        if isinstance(querystr, str):
            querystr = unicode(querystr, self.dbencoding)
        words = normalize_words(tokenize(querystr))
        cursor = cursor or self._cnx.cursor()
        cursor.execute('SELECT 1, uid FROM appears '
                       'WHERE MATCH (words) AGAINST (%(words)s IN BOOLEAN MODE)',
                       {'words': ' '.join(words)})
        return cursor.fetchall()

    def fti_restriction_sql(self, tablename, querystr, jointo=None, not_=False):
        """Execute a full text query and return a list of 2-uple (rating, uid).
        """
        if PY2 and isinstance(querystr, str):
            querystr = unicode(querystr, self.dbencoding)
        words = normalize_words(tokenize(querystr))
        sql = "MATCH (%s.words) AGAINST ('%s' IN BOOLEAN MODE)" % (tablename, ' '.join(words))
        if not_:
            sql = 'NOT (%s)' % sql
        if jointo is None:
            return sql
        return "%s AND %s.uid=%s" % (sql, tablename, jointo)

    def sql_init_fti(self):
        """Return the sql definition of table()s used by the full text index.
        """
        return """CREATE TABLE appears (
   `uid` integer NOT NULL,
   words text,
   FULLTEXT (words)
) ENGINE = MyISAM;
"""

    def sql_drop_fti(self):
        """Drop tables used by the full text index."""
        return 'DROP TABLE appears;'

    def sql_grant_user_on_fti(self, user):
        return 'GRANT ALL ON appears TO %s;' % (user)


db._ADV_FUNC_HELPER_DIRECTORY['mysql'] = _MyAdvFuncHelper
