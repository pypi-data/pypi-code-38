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
"""Sqlserver 2005 RDBMS support

Supported drivers, in order of preference:
- pyodbc (recommended, others are not well tested)
- adodbapi
"""

import os
import sys
import shutil
from warnings import warn

from six.moves import range

from logilab import database as db
from logilab.database.sqlserver import _PyodbcAdapter, _AdodbapiAdapter

class _PyodbcSqlServer2005Adapter(_PyodbcAdapter):
    driver = "SQL Server Native Client 10.0"

class _AdodbapiSqlServer2005Adapter(_AdodbapiAdapter):
    driver = "SQL Server Native Client 10.0"

db._PREFERED_DRIVERS.update({
    'sqlserver2005' : ['pyodbc', 'adodbapi', ],
    })
db._ADAPTER_DIRECTORY.update({
    'sqlserver2005' : {'adodbapi': _AdodbapiSqlServer2005Adapter,
                       'pyodbc': _PyodbcSqlServer2005Adapter},
    })


class _SqlServer2005FuncHelper(db._GenericAdvFuncHelper):
    backend_name = 'sqlserver2005'
    ilike_support = False
    TYPE_MAPPING = db._GenericAdvFuncHelper.TYPE_MAPPING.copy()
    TYPE_MAPPING['String'] =   'nvarchar(max)'
    TYPE_MAPPING['Boolean'] =  'bit'
    TYPE_MAPPING['Date'] =     'smalldatetime'
    TYPE_MAPPING['Datetime'] = 'datetime'
    TYPE_MAPPING['Password'] = 'varbinary(255)'
    TYPE_MAPPING['Bytes'] =    'varbinary(max)'
    TYPE_MAPPING['SizeConstrainedString'] = 'nvarchar(%s)'
    TYPE_CONVERTERS = db._GenericAdvFuncHelper.TYPE_CONVERTERS.copy()

    def list_tables(self, cursor):
        """return the list of tables of a database"""
        cursor.execute('''sys.sp_tables @table_type = "'TABLE'"''')
        return [row[2] for row in cursor.fetchall()]
        # cursor.tables()
        # return  [row.table_name for row in cursor.fetchall()]

    def list_views(self, cursor):
        cursor.execute('SELECT table_name FROM INFORMATION_SCHEMA.VIEWS;')
        return [row[0] for row in cursor.fetchall()]

    def list_indices(self, cursor, table=None):
        """return the list of indices of a database, only for the given table if specified"""
        sql = "SELECT name FROM sys.indexes"
        if table:
            sql = ("SELECT ind.name FROM sys.indexes as ind, sys.objects as obj WHERE "
                   "obj.object_id = ind.object_id AND obj.name = '%s'"
                   % table)
        cursor.execute(sql)
        return [r[0] for r in cursor.fetchall()]

    def backup_commands(self, backupfile, keepownership=True,
                        dbname=None, dbhost=None, dbport=None, dbuser=None, dbschema=None):
        return [[sys.executable, os.path.normpath(__file__),
                 "_SqlServer2005FuncHelper._do_backup", dbhost or self.dbhost,
                 dbname or self.dbname, backupfile]]

    def restore_commands(self, backupfile, keepownership=True, drop=True,
                         dbname=None, dbhost=None, dbport=None, dbuser=None,
                         dbencoding=None, dbschema=None):
        return [[sys.executable, os.path.normpath(__file__),
                "_SqlServer2005FuncHelper._do_restore", dbhost or self.dbhost,
                 dbname or self.dbname, backupfile],
                ]

    def sql_current_date(self):
        """Return sql for the current date. """
        return 'GETDATE()'

    def _index_names(self, cursor, table, column):
        """
        return the list of index_information for table.column
        index_information is a tuple:
        (name, index_type, is_unique, is_unique_constraint)

        See http://msdn.microsoft.com/en-us/library/ms173760.aspx for more
        information
        """
        has_index_sql = """\
SELECT i.name AS index_name,
       i.type_desc,
       i.is_unique,
       i.is_unique_constraint
FROM sys.indexes AS i, sys.index_columns as j, sys.columns as k
WHERE is_hypothetical = 0 AND i.index_id <> 0
AND i.object_id = j.object_id
AND i.index_id = j.index_id
AND i.object_id = OBJECT_ID('%(table)s')
AND k.name = '%(col)s'
AND k.object_id=i.object_id
AND j.column_id = k.column_id;"""
        cursor.execute(has_index_sql % {'table': table, 'col': column})
        return cursor.fetchall()

    def index_exists(self, cursor, table, column, unique=False):
        indexes = self._index_names(cursor, table, column)
        if unique:
            for name, itype, is_unique, is_utc in indexes:
                if is_unique and not is_utc:
                    return True
            return False
        return len(indexes) > 0

    def sql_concat_string(self, lhs, rhs):
        return '%s + %s' % (lhs, rhs)

    def sql_temporary_table(self, table_name, table_schema,
                            drop_on_commit=True):
        table_name = self.temporary_table_name(table_name)
        return "CREATE TABLE %s (%s);" % (table_name, table_schema)

    def sql_change_col_type(self, table, column, coltype, null_allowed):
        raise NotImplementedError('use .change_col_type()')

    def sql_set_null_allowed(self, table, column, coltype, null_allowed):
        raise NotImplementedError('use .set_null_allowed()')

    def sql_rename_table(self, oldname, newname):
        return  'EXEC sp_rename %s, %s' % (oldname, newname)

    def sql_add_limit_offset(self, sql, limit=None, offset=0, orderby=None):
        """
        modify the sql statement to add LIMIT and OFFSET clauses
        (or to emulate them if the backend does not support these SQL extensions)
        reference: http://stackoverflow.com/questions/2135418/equivalent-of-limit-and-offset-for-sql-server
        """
        if limit is None and not offset:
            return sql
        if offset is None: # not sure if this can happen
            offset = 0
        if not sql.startswith('SELECT ') or 'FROM' not in sql:
            raise ValueError(sql)
        union_queries = sql.split('UNION ALL')
        rewritten_union_queries = []
        for _sql in union_queries:
            _sql = _sql.strip()
            raw_columns, tables = _sql.split('FROM', 1)
            columns = raw_columns[7:].split(',') # 7 == len('SELECT ')
            aliases_cols = [] # list of (colname, alias)
            alias_counter = 1
            for c in columns:
                if 'AS' in c:
                    aliases_cols.append(c.strip().split('AS'))
                else:
                    aliases_cols.append([c.strip(), '_L%02d' % alias_counter])
                    alias_counter += 1
            cooked_columns = ', '.join(' AS '.join(alias_col) for alias_col in aliases_cols)
            new_sql = ' '.join(['SELECT', cooked_columns, 'FROM', tables])
            rewritten_union_queries.append(new_sql)
        new_sql = '\nUNION ALL\n'.join(rewritten_union_queries)
        outer_aliases = ', '.join(alias for _colname, alias in aliases_cols)
        if orderby is None:
            order_by = outer_aliases
        else:
            order_by = []
            for i, term in enumerate(orderby):
                split = term.split()
                try:
                    idx = int(split[0]) - 1 
                except ValueError:
                    idx = i
                split[0] = aliases_cols[idx][1]
                order_by.append(' '.join(split))
            order_by = ', '.join(order_by)
        new_query = ['WITH orderedrows AS (',
                     'SELECT ', outer_aliases, ', '
                     "ROW_NUMBER() OVER (ORDER BY %s) AS __RowNumber" % order_by,
                     'FROM (',
                     new_sql,
                     ') AS _SQ1 )',
                     #columns,
                     'SELECT ', outer_aliases,
                     'FROM orderedrows WHERE ']
        limitation = []
        if limit is not None:
            limitation.append('__RowNumber <= %d' % (offset+limit))
        if offset:
            limitation.append('__RowNumber > %d' % offset) # row number is 1 based
        new_query.append(' AND '.join(limitation))
        sql = '\n'.join(new_query)
        return sql

    def sql_add_order_by(self, sql, sortterms, selection, needwrap, has_limit_or_offset):
        """
        add an ORDER BY clause to the SQL query, and wrap the query if necessary
        :sql: the original sql query
        :sortterms: a list of term with sorting order, as strings
        :selection: the selection that must be gathered after ORDER BY
        :needwrap: boolean, True if the query must be wrapped in a subquery
        :has_limit_or_offset: if true, do nothing: the sorting is handled by
                              sql_add_limit_offset
        """
        if has_limit_or_offset:
            return sql
        if sortterms and needwrap:
            selection = ['T1.C%s' % i for i in range(len(selection))]
            renamed_sortterms = []
            for term in sortterms:
                split = term.split()
                split[0] = 'T1.C%s' % (int(split[0])-1)
                renamed_sortterms.append(' '.join(split))
            sql = 'SELECT %s FROM (%s) AS T1\nORDER BY %s' % (','.join(selection),
                                                            sql,
                                                            ','.join(renamed_sortterms))
        else:
            sql += '\nORDER BY %s' % ','.join(sortterms)

        return sql

    def sqls_create_multicol_unique_index(self, table, columns, indexname=None):
        columns = sorted(columns)
        view = 'utv_%s_%s' % (table, indexname or '_'.join(columns))
        where = ' AND '.join(['%s IS NOT NULL' % c for c in columns])
        if indexname is None:
            warn('You should provide an explicit index name else you risk '
                 'a silent truncation of the computed index name.',
                 DeprecationWarning)
            indexname = 'unique_%s_%s_idx' % (table, '_'.join(columns))
        sql = ['CREATE VIEW %s WITH SCHEMABINDING AS SELECT %s FROM dbo.%s WHERE %s ;'%(view.lower(), 
                                                      ', '.join(columns),
                                                      table,
                                                      where),
               'CREATE UNIQUE CLUSTERED INDEX %s ON %s(%s);' % (indexname.lower(),
                                                                view.lower(),
                                                                ','.join(columns))
            ]
        return sql

    def sqls_drop_multicol_unique_index(self, table, columns, indexname=None):
        if indexname is None:
            warn('You should provide an explicit index name else you risk '
                 'a silent truncation of the computed index name.',
                 DeprecationWarning)
        columns = sorted(columns)
        view = 'utv_%s_%s' % (table, indexname or '_'.join(columns))
        sql = ("IF OBJECT_ID ('%(v)s', 'V') IS NOT NULL DROP VIEW %(v)s"
               % {'v': view.lower()}) # also drops the index
        return [sql]

    def sql_drop_index(self, table, column, unique=False):
        if unique:
            return super(_SqlServer2005FuncHelper, self).sql_drop_index(table, column, unique)
        else:
            idx = self._index_name(table, column, unique)
            return 'DROP INDEX %s ON %s;' % (idx, table)


    def change_col_type(self, cursor, table, column, coltype, null_allowed):
        alter = []
        drops = []
        creates = []
        for idx_name, idx_type, is_unique, is_unique_cstr in self._index_names(cursor, table, column):
            if is_unique_cstr:
                drops.append('ALTER TABLE %s DROP CONSTRAINT %s' % (table, idx_name))
                creates.append('ALTER TABLE %s ADD CONSTRAINT %s UNIQUE (%s)' % (table, idx_name, column))
            else:
                drops.append('DROP INDEX %s ON %s' % (idx_name, table))
                if is_unique:
                    unique = 'UNIQUE'
                else:
                    unique = ''
                creates.append('CREATE %s %s INDEX %s ON %s(%s)' % (unique, idx_type, idx_name, table, column))
        for view_name in self.list_views(cursor):
            if not view_name.startswith('utv_%s_' % table.lower()):
                continue
            cursor.execute('SELECT column_name from information_schema.columns where table_name = %(t)s', {'t': view_name})
            columns = [row[0] for row in cursor.fetchall()]
            if column not in columns:
                continue
            indexname = view_name.split('_', 3)[-1]
            drops += self.sqls_drop_multicol_unique_index(table, columns, indexname)
            creates += self.sqls_create_multicol_unique_index(table, columns, indexname)

        if null_allowed:
            null = 'NULL'
        else:
            null = 'NOT NULL'
        alter.append('ALTER TABLE %s ALTER COLUMN %s %s %s' % (table, column, coltype, null))
        for stmt in drops + alter + creates:
            cursor.execute(stmt)

    def set_null_allowed(self, cursor, table, column, coltype, null_allowed):
        return self.change_col_type(cursor, table, column, coltype, null_allowed)

    def temporary_table_name(self, table_name):
        if not table_name.startswith('#'):
            table_name = '#' + table_name
        return table_name

    @staticmethod
    def _do_backup():
        import time
        from logilab.database import get_connection
        dbhost = sys.argv[2]
        dbname = sys.argv[3]
        filename = sys.argv[4]
        cnx = get_connection(driver='sqlserver2005',
                             host=dbhost, database=dbname,
                             extra_args='autocommit;trusted_connection')
        cursor = cnx.cursor()
        sql_server_local_filename = r"C:\Backups\%s" % dbname
        file_share_filename = r"\\%s\Backups\%s" % (dbhost, dbname)
        cursor.execute("BACKUP DATABASE %(db)s TO DISK= %(path)s ",
                       {'db':dbname,
                        'path':sql_server_local_filename,
                        })
        prev_size = -1
        err_count = 0
        same_size_count = 0
        while err_count < 10 and same_size_count < 10:
            time.sleep(1)
            try:
                size = os.path.getsize(file_share_filename)
            except OSError as exc:
                self.logger.exception('error accessing %s', file_share_filename)
                err_count += 1
            if size > prev_size:
                same_size_count = 0
                prev_size = size
            else:
                same_size_count += 1
        shutil.copy(file_share_filename, filename)
        os.remove(file_share_filename)
        cnx.close()
        sys.exit(0)

    @staticmethod
    def _do_restore():
        """return the SQL statement to restore a backup of the given database"""
        from logilab.database import get_connection
        dbhost = sys.argv[2]
        dbname = sys.argv[3]
        filename = sys.argv[4]
        sql_server_local_filename = r"C:\Backups\%s" % dbname
        file_share_filename = r"\\%s\Backups\%s" % (dbhost, dbname)
        shutil.copy(filename, file_share_filename)
        cnx = get_connection(driver='sqlserver2005',
                             host=dbhost, database='master',
                             extra_args='autocommit;trusted_connection')

        cursor = cnx.cursor()
        cursor.execute("RESTORE DATABASE %(db)s FROM DISK= %(path)s WITH REPLACE",
                       {'db':dbname,
                        'path':sql_server_local_filename,
                        })
        import time
        sleeptime = 10
        while True:
            time.sleep(sleeptime)
            try:
                cnx = get_connection(driver='sqlserver2005',
                                     host=dbhost, database=dbname,
                                     extra_args='trusted_connection')
                break
            except:
                sleeptime = min(sleeptime*2, 300)
        os.remove(file_share_filename)
        sys.exit(0)


db._ADV_FUNC_HELPER_DIRECTORY['sqlserver2005'] = _SqlServer2005FuncHelper




if __name__ == "__main__": # used to backup sql server db
    func_call = sys.argv[1]
    eval(func_call+'()')
