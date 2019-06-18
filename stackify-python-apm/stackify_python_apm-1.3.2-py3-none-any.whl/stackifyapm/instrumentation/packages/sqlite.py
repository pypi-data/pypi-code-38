from stackifyapm.instrumentation.packages.dbapi2 import (
    ConnectionProxy,
    CursorProxy,
    DbApi2Instrumentation,
    extract_signature,
)
from stackifyapm.traces import CaptureSpan
from stackifyapm.utils import get_method_name
from stackifyapm.utils.helper import is_async_span


class SQLiteCursorProxy(CursorProxy):
    provider_name = "sqlite"
    name = "GENERIC"

    def extract_signature(self, sql):
        return extract_signature(sql)


class SQLiteConnectionProxy(ConnectionProxy):
    cursor_proxy = SQLiteCursorProxy
    provider_name = "sqlite"
    name = "GENERIC"

    def _trace_sql(self, method, sql, params):
        signature = extract_signature(sql)
        kind = "db.sqlite.sql"
        extra_data = {
            "wrapped_method": get_method_name(method),
            "provider": self.name,
            "type": "Database",
            "sub_type": "database_sql",
            "statement": sql,
        }

        with CaptureSpan(signature, kind, extra_data, is_async=is_async_span()):
            if params is None:
                return method(sql)
            else:
                return method(sql, params)

    def execute(self, sql, params=None):
        return self._trace_sql(self.__wrapped__.execute, sql, params)

    def executemany(self, sql, params=None):
        return self._trace_sql(self.__wrapped__.executemany, sql, params)


class SQLiteInstrumentation(DbApi2Instrumentation):
    name = "GENERIC"

    instrument_list = [
        ("sqlite3", "connect"),
        ("sqlite3.dbapi2", "connect"),
        ("pysqlite2.dbapi2", "connect"),
    ]

    def call(self, module, method, wrapped, instance, args, kwargs):
        signature = ".".join([module, method])

        if len(args) == 1:
            signature += " " + str(args[0])

        extra_data = {
            "wrapped_method": get_method_name(method),
            "provider": self.name,
            "type": "Database",
            "sub_type": "database_connect",
        }

        with CaptureSpan(signature, "db.sqlite.connect", extra_data, is_async=is_async_span()):
            return SQLiteConnectionProxy(wrapped(*args, **kwargs))
