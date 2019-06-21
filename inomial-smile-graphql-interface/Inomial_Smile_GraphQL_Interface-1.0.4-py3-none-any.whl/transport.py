from gql import Client, gql
from gql.transport.requests import RequestsHTTPTransport


class Transport:
    def __init__(self, host, *args, **kwargs):
        auth = kwargs.get("auth")
        timeout = kwargs.get("timeout", 30)
        enable_debug = kwargs.get("debug", False)
        self._enable_debug(kwargs.get("debug"))
        transport = kwargs.get(
            "transport",
            RequestsHTTPTransport(url=host, auth=auth, use_json=True, timeout=timeout),
        )
        self.client = Client(transport=transport, fetch_schema_from_transport=True)

    def _enable_debug(self, debug_flag):
        if debug_flag:
            import logging

            try:
                import http.client as http_client
            except ImportError:
                # Python 2
                import httplib as http_client
            http_client.HTTPConnection.debuglevel = 1
            logging.basicConfig()
            logging.getLogger().setLevel(logging.DEBUG)
            requests_log = logging.getLogger("requests.packages.urllib3")
            requests_log.setLevel(logging.DEBUG)
            requests_log.propagate = True
