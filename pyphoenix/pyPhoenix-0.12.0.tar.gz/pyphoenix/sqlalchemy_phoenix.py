# Copyright 2017 Dimitri Capitaine
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from future.standard_library import install_aliases
install_aliases()

import urllib.parse
import pyphoenix

from sqlalchemy.engine.default import DefaultDialect

from sqlalchemy.sql.compiler import DDLCompiler
from sqlalchemy.exc import CompileError

from sqlalchemy import types
from sqlalchemy.types import INTEGER, BIGINT, SMALLINT, VARCHAR, CHAR, \
    FLOAT, DATE, BOOLEAN, DECIMAL, TIMESTAMP, TIME, VARBINARY


class PhoenixDDLCompiler(DDLCompiler):

    def visit_primary_key_constraint(self, constraint):
        if constraint.name is None:
            raise CompileError("can't create primary key without a name")
        return DDLCompiler.visit_primary_key_constraint(self, constraint)


class PhoenixDialect(DefaultDialect):

    name = "phoenix"

    driver = "pyphoenix"

    ddl_compiler = PhoenixDDLCompiler

    @classmethod
    def dbapi(cls):

        return pyphoenix

    def create_connect_args(self, url):
        phoenix_url = urllib.parse.urlunsplit(urllib.parse.SplitResult(
            scheme='http',
            netloc='{}:{}'.format(url.host, url.port or 8765),
            path='/',
            query=urllib.parse.urlencode(url.query),
            fragment='',
        ))
        return [phoenix_url], {'autocommit': True}

    def do_rollback(self, dbapi_conection):
        pass

    def do_commit(self, dbapi_conection):
        pass

    def has_table(self, connection, table_name, schema=None):
        if schema is None:
            query = "SELECT 1 FROM system.catalog WHERE table_name = ? LIMIT 1"
            params = [table_name.upper()]
        else:
            query = "SELECT 1 FROM system.catalog WHERE table_name = ? AND TABLE_SCHEM = ? LIMIT 1"
            params = [table_name.upper(), schema.upper()]
        return connection.execute(query, params).first() is not None

    def get_schema_names(self, connection, **kw):
        query = "SELECT DISTINCT TABLE_SCHEM FROM SYSTEM.CATALOG"
        return [row[0] for row in connection.execute(query)]

    def get_table_names(self, connection, schema=None, **kw):
        if schema is None:
            query = "SELECT DISTINCT table_name FROM SYSTEM.CATALOG"
            params = []
        else:
            query = "SELECT DISTINCT table_name FROM SYSTEM.CATALOG WHERE TABLE_SCHEM = ? "
            params = [schema.upper()]
        return [row[0] for row in connection.execute(query, params)]

    def get_columns(self, connection, table_name, schema=None, **kw):
        if schema is None:
            query = "SELECT COLUMN_NAME,  DATA_TYPE, NULLABLE " \
                    "FROM system.catalog " \
                    "WHERE table_name = ? " \
                    "ORDER BY ORDINAL_POSITION"
            params = [table_name.upper()]
        else:
            query = "SELECT COLUMN_NAME, DATA_TYPE, NULLABLE " \
                    "FROM system.catalog " \
                    "WHERE TABLE_SCHEM = ? " \
                    "AND table_name = ? " \
                    "ORDER BY ORDINAL_POSITION"
            params = [schema.upper(), table_name.upper()]

        # get all of the fields for this table
        c = connection.execute(query, params)
        cols = []
        # first always none
        c.fetchone()
        while True:
            row = c.fetchone()
            if row is None:
                break
            name = row[0]
            col_type = COLUMN_DATA_TYPE[row[1]]
            nullable = row[2] == 1 if True else False

            col_d = {
                'name': name,
                'type': col_type,
                'nullable': nullable,
                'default': None
            }

            cols.append(col_d)
        return cols

    def get_pk_constraint(self, conn, table_name, schema=None, **kw):
        return []

    def get_foreign_keys(self, conn, table_name, schema=None, **kw):
        return []

    def get_indexes(self, conn, table_name, schema=None, **kw):
        return []


class TINYINT(types.Integer):
    __visit_name__ = "INTEGER"


class UTINYINT(types.Integer):
    __visit_name__ = "INTEGER"


class UINTEGER(types.Integer):
    __visit_name__ = "INTEGER"


class DOUBLE(types.BIGINT):
    __visit_name__ = "BIGINT"


class DOUBLE(types.BIGINT):
    __visit_name__ = "BIGINT"


class UDOUBLE(types.BIGINT):
    __visit_name__ = "BIGINT"


class UFLOAT(types.FLOAT):
    __visit_name__ = "FLOAT"


class ULONG(types.BIGINT):
    __visit_name__ = "BIGINT"


class UTIME(types.TIME):
    __visit_name__ = "TIME"


class UDATE(types.DATE):
    __visit_name__ = "DATE"


class UTIMESTAMP(types.TIMESTAMP):
    __visit_name__ = "TIMESTAMP"


class ROWID (types.String):
    __visit_name__ = "VARCHAR"


COLUMN_DATA_TYPE = {
    -6: TINYINT,
    -5: BIGINT,
    -3: VARBINARY,
    1: CHAR,
    3: DECIMAL,
    4: INTEGER,
    5: SMALLINT,
    6: FLOAT,
    8: DOUBLE,
    9: UINTEGER,
    10: ULONG,
    11: UTINYINT,
    12: VARCHAR,
    13: ROWID,
    14: UFLOAT,
    15: UDOUBLE,
    16: BOOLEAN,
    18: UTIME,
    19: UDATE,
    20: UTIMESTAMP,
    91: DATE,
    92: TIME,
    93: TIMESTAMP
}
