from stackifyapm.instrumentation.packages.base import AbstractInstrumentedModule
from stackifyapm.instrumentation.packages.dbapi2 import extract_signature
from stackifyapm.traces import CaptureSpan
from stackifyapm.utils import compat
from stackifyapm.utils import get_method_name
from stackifyapm.utils.helper import is_async_span


class CassandraInstrumentation(AbstractInstrumentedModule):
    name = "cassandra"

    instrument_list = [
        ("cassandra.cluster", "Session.execute"),
        ("cassandra.cluster", "Cluster.connect"),
    ]

    def call(self, module, method, wrapped, instance, args, kwargs):
        signature = self.get_wrapped_name(wrapped, instance, method)
        extra_data = {
            "wrapped_method": get_method_name(method),
            "provider": self.name,
            "type": "Cassandra",
        }
        if method == "Cluster.connect":
            kind = "db.cassandra.connect"
            extra_data["sub_type"] = "database_connect"
        else:
            kind = "db.cassandra.query"
            query = args[0] if args else kwargs.get("query")
            if hasattr(query, "query_string"):
                query_str = query.query_string
            elif hasattr(query, "prepared_statement") and hasattr(query.prepared_statement, "query"):
                query_str = query.prepared_statement.query
            elif isinstance(query, compat.string_types):
                query_str = query
            else:
                query_str = None
            if query_str:
                signature = extract_signature(query_str)
                extra_data["sub_type"] = "database_sql"
                extra_data["statement"] = query_str

        with CaptureSpan(signature, kind, extra_data, is_async=is_async_span()):
            return wrapped(*args, **kwargs)
