from __future__ import absolute_import

import json
import logging

from stackifyapm import CaptureSpan
from stackifyapm.instrumentation.packages.base import AbstractInstrumentedModule
from stackifyapm.utils.helper import is_async_span

logger = logging.getLogger(__name__)


API_METHOD_KEY_NAME = "__stackify_apm_api_method_name"
BODY_REF_NAME = "__stackify_apm_body_ref"


class ElasticsearchConnectionInstrumentation(AbstractInstrumentedModule):
    name = "elasticsearch_connection"

    instrument_list = [
        ("elasticsearch.connection.http_urllib3", "Urllib3HttpConnection.perform_request"),
        ("elasticsearch.connection.http_requests", "RequestsHttpConnection.perform_request"),
    ]

    query_methods = ("Elasticsearch.search", "Elasticsearch.count", "Elasticsearch.delete_by_query")

    def call(self, module, method, wrapped, instance, args, kwargs):
        args_len = len(args)
        http_method = args[0] if args_len else kwargs.get("method")
        http_path = args[1] if args_len > 1 else kwargs.get("url")
        params = args[2] if args_len > 2 else kwargs.get("params")
        body = params.pop(BODY_REF_NAME, None) if params else None

        api_method = params.pop(API_METHOD_KEY_NAME, None) if params else None

        signature = "ES {} {}".format(http_method, http_path)
        extra_data = {
            "wrapped_method": "Execute",
            "provider": self.name,
            "type": "ElasticSearch",
            "sub_type": "send",
            "request_method": http_method,
            "url": http_path,
            "params": params,
        }

        if api_method in self.query_methods:
            query = []
            if params and "q" in params:
                query.append("q=" + params["q"].decode("utf-8", errors="replace"))
            if isinstance(body, dict) and "query" in body:
                query.append(json.dumps(body["query"]))
            extra_data["statement"] = "\n\n".join(query)
        elif api_method == "Elasticsearch.update":
            if isinstance(body, dict) and "script" in body:
                extra_data["statement"] = json.dumps({"script": body["script"]})

        with CaptureSpan(signature, "db.elasticsearch", extra=extra_data, skip_frames=2, leaf=True, is_async=is_async_span()):
            return wrapped(*args, **kwargs)


class ElasticsearchInstrumentation(AbstractInstrumentedModule):
    name = "elasticsearch"

    body_positions = {
        2: {
            "count_percolate": 3,
            "create": 2,
            "field_stats": 1,
            "mpercolate": 0,
            "percolate": 3,
            "put_script": 2,
            "search_exists": 2,
            "suggest": 0,
        },
        5: {
            "count_percolate": 3,
            "create": 3,
            "field_stats": 1,
            "mpercolate": 0,
            "percolate": 3,
            "put_script": 2,
            "suggest": 0,
        },
        6: {"create": 3, "put_script": 1},
        "all": {
            "bulk": 0,
            "clear_scroll": 1,
            "count": 2,
            "delete_by_query": 1,
            "explain": 3,
            "field_caps": 1,
            "index": 2,
            "mget": 0,
            "msearch": 0,
            "msearch_template": 0,
            "mtermvectors": 2,
            "put_template": 1,
            "reindex": 0,
            "render_search_template": 1,
            "scroll": 1,
            "search": 2,
            "search_template": 2,
            "termvectors": 3,
            "update": 3,
            "update_by_query": 2,
        },
    }

    instrument_list = [
        ("elasticsearch.client", "Elasticsearch.delete_by_query"),
        ("elasticsearch.client", "Elasticsearch.search"),
        ("elasticsearch.client", "Elasticsearch.count"),
        ("elasticsearch.client", "Elasticsearch.update"),
    ]

    def __init__(self):
        super(ElasticsearchInstrumentation, self).__init__()
        try:
            from elasticsearch import VERSION

            self.version = VERSION[0]
        except ImportError:
            self.version = None

    def instrument(self, client=None):
        if self.version and not 2 <= self.version < 7:
            logger.debug("Instrumenting version %s of Elasticsearch is not supported by Stackify APM", self.version)
            return
        super(ElasticsearchInstrumentation, self).instrument()

    def call(self, module, method, wrapped, instance, args, kwargs):
        params = kwargs.pop("params", {})

        params = params.copy() if params is not None else {}

        cls_name, method_name = method.split(".", 1)
        body_pos = (
            self.body_positions["all"].get(method_name) or self.body_positions[self.version].get(method_name) or None
        )

        body = args[body_pos] if (body_pos is not None and len(args) > body_pos) else kwargs.get("body")
        params[BODY_REF_NAME] = body
        params[API_METHOD_KEY_NAME] = method

        kwargs["params"] = params
        return wrapped(*args, **kwargs)
