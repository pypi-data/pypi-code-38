from stackifyapm.instrumentation.packages.dbapi2 import (
    ConnectionProxy,
    CursorProxy,
    DbApi2Instrumentation,
    extract_signature,
)
from stackifyapm.traces import CaptureSpan
from stackifyapm.utils import default_ports, get_method_name
from stackifyapm.utils.helper import is_async_span


class PGCursorProxy(CursorProxy):
    provider_name = "postgresql"

    def _bake_sql(self, sql):
        if hasattr(sql, "as_string"):
            return sql.as_string(self.__wrapped__)
        return sql

    def extract_signature(self, sql):
        return extract_signature(sql)


class PGConnectionProxy(ConnectionProxy):
    cursor_proxy = PGCursorProxy


class Psycopg2Instrumentation(DbApi2Instrumentation):
    name = "psycopg2"

    instrument_list = [("psycopg2", "connect")]

    def call(self, module, method, wrapped, instance, args, kwargs):
        signature = "psycopg2.connect"

        host = kwargs.get("host")
        if host:
            signature += " " + str(host)

            port = kwargs.get("port")
            if port:
                port = str(port)
                if int(port) != default_ports.get("postgresql"):
                    signature += ":" + port
        else:
            pass

        extra_data = {
            "wrapped_method": get_method_name(method),
            "provider": self.name,
            "type": "Database",
            "sub_type": "database_connect",
        }
        with CaptureSpan(signature, "db.postgresql.connect", extra_data, is_async=is_async_span()):
            return PGConnectionProxy(wrapped(*args, **kwargs))


class Psycopg2RegisterTypeInstrumentation(DbApi2Instrumentation):
    name = "psycopg2-register-type"

    instrument_list = [
        ("psycopg2.extensions", "register_type"),
        ("psycopg2._json", "register_json"),
    ]

    def call(self, module, method, wrapped, instance, args, kwargs):
        if "conn_or_curs" in kwargs and hasattr(kwargs["conn_or_curs"], "__wrapped__"):
            kwargs["conn_or_curs"] = kwargs["conn_or_curs"].__wrapped__
        elif len(args) == 2 and hasattr(args[1], "__wrapped__"):
            args = (args[0], args[1].__wrapped__)
        elif method == "register_json":
            if args and hasattr(args[0], "__wrapped__"):
                args = (args[0].__wrapped__,) + args[1:]

        return wrapped(*args, **kwargs)
