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
"""Sqlserver RDBMS support

Supported drivers, in order of preference:
- pyodbc (recommended, others are not well tested)
- adodbapi

Use the sqlserverNNNN module as driver name
"""
__docformat__ = "restructuredtext en"

import datetime
import re
from warnings import warn

from logilab import database as db

class _BaseSqlServerAdapter(db.DBAPIAdapter):
    driver = 'Override in subclass'
    _use_trusted_connection = False
    _use_autocommit = False

    @classmethod
    def use_trusted_connection(cls, use_trusted=False):
        """
        pass True to this class method to enable Windows
        Authentication (i.e. passwordless auth)
        """
        cls._use_trusted_connection = use_trusted

    @classmethod
    def use_autocommit(cls, use_autocommit=False):
        """
        pass True to this class method to enable autocommit (required
        for backup and restore)
        """
        cls._use_autocommit = use_autocommit

    @classmethod
    def _process_extra_args(cls, arguments):
        arguments = arguments.lower().split(';')
        if 'trusted_connection' in arguments:
            cls.use_trusted_connection(True)
        if 'autocommit' in arguments:
            cls.use_autocommit(True)

    def connect(self, host='', database='', user='', password='', port=None,
                schema=None, extra_args=None):
        """Handles pyodbc connection format

        If extra_args is not None, it is expected to be a string
        containing a list of semicolon separated keywords. The only
        keyword currently supported is Trusted_Connection : if found
        the connection string to the database will include
        Trusted_Connection=yes (which for SqlServer will trigger using
        Windows Authentication, and therefore no login/password is
        required.
        """
        if schema is not None:
            # NOTE: SQLServer supports schemas
            # cf. http://msdn.microsoft.com/en-us/library/ms189462%28v=SQL.90%29.aspx
            warn('schema support is not implemented on sqlserver backends, ignoring schema %s'
                 % schema)
        class SqlServerCursor(object):
            """cursor adapting usual dict format to pyodbc/adobdapi format
            in SQL queries
            """
            def __init__(self, cursor):
                self._cursor = cursor

            def _replace_parameters(self, sql, kwargs, _date_class=datetime.date, many=False):
                if not many:
                    kwargs = [kwargs]

                if isinstance(kwargs[0], dict):
                    args_list = []
                    new_sql = re.sub(r'%\(([^\)]+)\)s', r'?', sql)
                    key_order = re.findall(r'%\(([^\)]+)\)s', sql)
                    for kwarg in kwargs:
                        args = []
                        for key in key_order:
                            arg = kwarg[key]
                            if arg.__class__ == _date_class:
                                arg = datetime.datetime.combine(arg, datetime.time(0))
                            elif isinstance(arg, str):
                                arg = arg.decode('utf-8')
                            args.append(arg)
                        args_list.append(tuple(args))

                    if many:
                        return new_sql, args_list
                    else:
                        return new_sql, args_list[0]
                else:
                    # XXX dumb
                    return re.sub(r'%s', r'?', sql), kwargs

            def execute(self, sql, kwargs=None):
                if kwargs is None:
                    self._cursor.execute(sql)
                else:
                    final_sql, args = self._replace_parameters(sql, kwargs)
                    self._cursor.execute(final_sql , args)

            def executemany(self, sql, kwargss):
                if not isinstance(kwargss, (list, tuple)):
                    kwargss = tuple(kwargss)
                final_sql, argss = self._replace_parameters(sql, kwargss, many=True)
                self._cursor.executemany(final_sql, argss)

            def _get_smalldate_columns(self):
                # XXX once CW uses the process_cursor method, we can move this to an upper level
                cols = []
                for i, coldef in enumerate(self._cursor.description):
                    if coldef[1] is datetime.datetime and coldef[3] == 16:
                        cols.append(i)
                return cols

            def fetchone(self):
                smalldate_cols = self._get_smalldate_columns()
                row = self._cursor.fetchone()
                return self._replace_smalldate(row, smalldate_cols)

            def fetchall (self):
                smalldate_cols = self._get_smalldate_columns()
                rows = []
                for row in self._cursor.fetchall():
                    rows.append(self._replace_smalldate(row, smalldate_cols))
                return rows

            def fetchmany(self, *args):
                smalldate_cols = self._get_smalldate_columns()
                rows = []
                for row in self._cursor.fetchmany(*args):
                    rows.append(self._replace_smalldate(row, smalldate_cols))
                return rows

            def _replace_smalldate(self, row, smalldate_cols):
                if smalldate_cols:
                    new_row = row[:]
                    for col in smalldate_cols:
                        if new_row[col] is not None:
                            new_row[col] = new_row[col].date()
                    return new_row
                else:
                    return row

            def __getattr__(self, attrname):
                return getattr(self._cursor, attrname)

        class SqlServerCnxWrapper:
            def __init__(self, cnx):
                self._cnx = cnx
            def cursor(self):
                return SqlServerCursor(self._cnx.cursor())
            def __getattr__(self, attrname):
                return getattr(self._cnx, attrname)
        cnx = self._connect(host=host, database=database, user=user, password=password, port=port, extra_args=extra_args)
        return self._wrap_if_needed(SqlServerCnxWrapper(cnx))

    def _transformation_callback(self, description, encoding='utf-8', binarywrap=None):
        typecode = description[1]
        assert typecode is not None, self
        transform = None
        if typecode == self.STRING and not self.returns_unicode:
            transform = lambda v: unicode(v, encoding, 'replace')
        elif typecode == self.BINARY:  # value is a python buffer
            if binarywrap is None:
                transforn = lambda v: v[:]
            else:
                transform = lambda v: binarywrap(v[:])
        elif typecode == self.UNKNOWN:
            # may occurs on constant selection for instance (e.g. SELECT 'hop')
            # with postgresql at least
            transform = lambda v: unicode(value, encoding, 'replace') if isinstance(v, str) else v
        return transform


class _PyodbcAdapter(_BaseSqlServerAdapter):
    def _connect(self, host='', database='', user='', password='',
                 port=None, extra_args=None):
        if extra_args is not None:
            self._process_extra_args(extra_args)
        #cnx_string_bits = ['DRIVER={%(driver)s}']
        variables = {'host' : host,
                     'database' : database,
                     'user' : user, 'password' : password,
                     'driver': self.driver}
        if self._use_trusted_connection:
            variables['Trusted_Connection'] = 'yes'
            del variables['user']
            del variables['password']
        if self._use_autocommit:
            variables['autocommit'] = True
        return self._native_module.connect(**variables)

    def _transformation_callback(self, description, encoding='utf-8', binarywrap=None):
        # Work around pyodbc setting BINARY to bytearray but description[1] to buffer
        # https://github.com/mkleehammer/pyodbc/pull/34
        typecode = description[1]
        if typecode is buffer:
            return binarywrap
        return super(_PyodbcAdapter, self)._transformation_callback(description, encoding, binarywrap)



class _AdodbapiAdapter(_BaseSqlServerAdapter):

    def _connect(self, host='', database='', user='', password='',
                 port=None, extra_args=None):
        if extra_args is not None:
            self._process_extra_args(extra_args)
        if self._use_trusted_connection:
            # this will open a MS-SQL table with Windows authentication
            auth = 'Integrated Security=SSPI'
        else:
            # this set opens a MS-SQL table with SQL authentication
            auth = 'user ID=%s; Password=%s;' % (user, password)
        constr = r"Initial Catalog=%s; Data Source=%s; Provider=SQLOLEDB.1; %s"\
                 % (database, host, auth)
        return self._native_module.connect(constr)


