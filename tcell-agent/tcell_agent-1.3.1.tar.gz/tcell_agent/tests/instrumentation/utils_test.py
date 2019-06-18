import unittest

from tcell_agent.instrumentation.utils import header_keys_from_request_env


class InstrumentationUtils(unittest.TestCase):
    def test_flask_header_keys_from_request_env(self):
        header_keys = header_keys_from_request_env(
            {"wsgi.multiprocess": False,
             "HTTP_COOKIE": "mp_None_mixpanel=some-value; csrftoken=YoEiRg1; sessionid=1olmi; _ga=GA1.1.1722707835.1481849908",
             "SERVER_SOFTWARE": "Werkzeug/0.9.6",
             "SCRIPT_NAME": "",
             "REQUEST_METHOD": "GET",
             "PATH_INFO": "/",
             "SERVER_PROTOCOL": "HTTP/1.1",
             "QUERY_STRING": "",
             "werkzeug.server.shutdown": "<function shutdown_server at 0x7f8ed4764668>",
             "CONTENT_LENGTH": "",
             "HTTP_USER_AGENT": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.95 Safari/537.36",
             "HTTP_CONNECTION": "keep-alive",
             "SERVER_NAME": "0.0.0.0",
             "REMOTE_PORT": 55799,
             "wsgi.url_scheme": "http",
             "SERVER_PORT": "8002",
             "werkzeug.request": "<Request \"http://192.168.99.100:8002/\" [GET]>",
             "wsgi.input": "<socket._fileobject object at 0x7f8ed6b2c050>",
             "HTTP_HOST": "192.168.99.100:8002",
             "wsgi.multithread": False,
             "HTTP_UPGRADE_INSECURE_REQUESTS": "1",
             "HTTP_ACCEPT": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
             "wsgi.version": (1, 0),
             "wsgi.run_once": False,
             "wsgi.errors": "<open file \"<stderr>l\", mode \"w\" at 0x7f8ee141a1e0>",
             "REMOTE_ADDR": "192.168.99.1",
             "HTTP_ACCEPT_LANGUAGE": "en-US,en;q=0.8",
             "CONTENT_TYPE": "",
             "HTTP_ACCEPT_ENCODING": "gzip, deflate, sdch"})

        self.assertSetEqual(
            set(header_keys),
            set(["COOKIE", "CONTENT_LENGTH", "USER_AGENT", "CONNECTION", "HOST", "UPGRADE_INSECURE_REQUESTS", "ACCEPT",
                 "ACCEPT_LANGUAGE", "CONTENT_TYPE", "ACCEPT_ENCODING"]))

    def test_django_header_keys_from_request_env(self):
        header_keys = header_keys_from_request_env(
            {"HTTP_REFERER": "http://192.168.99.100:3000/",
             "SCRIPT_NAME": u"",
             "REQUEST_METHOD": "GET",
             "PATH_INFO": u"/waitlist_entries/",
             "SERVER_PROTOCOL": "HTTP/1.1",
             "QUERY_STRING": "",
             "HTTP_USER_AGENT": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.95 Safari/537.36",
             "HTTP_CONNECTION": "keep-alive",
             "HTTP_COOKIE": "mp_None_mixpanel=some-value; _ga=GA1.1.1722707835.1481849908; _gat=1; csrftoken=ODH20G82vO39cxdvIVvDkBfprSW3946a",
             "SERVER_NAME": "24910e18bcd9",
             "REMOTE_ADDR": "192.168.99.1",
             "wsgi.url_scheme": "http",
             "SERVER_PORT": "3000",
             "uwsgi.node": "24910e18bcd9",
             "wsgi.input": "<uwsgi._Input object at 0x7fefcb427960>",
             "HTTP_HOST": "192.168.99.100:3000",
             "wsgi.multithread": False,
             "HTTP_UPGRADE_INSECURE_REQUESTS": "1",
             "REQUEST_URI": "/waitlist_entries/",
             "HTTP_ACCEPT": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
             "wsgi.version": (1, 0),
             "wsgi.run_once": False,
             "wsgi.errors": "<open file \"wsgi_errors\", mode \"w\" at 0x7fefce051e40>",
             "wsgi.multiprocess": False,
             "HTTP_ACCEPT_LANGUAGE": "en-US,en;q=0.8",
             "uwsgi.version": "2.0.14",
             "wsgi.file_wrapper": "<built-in function uwsgi_sendfile>",
             u"CSRF_COOKIE": u"ODH20G82vO39cxdvIVvDkBfprSW3946a",
             "HTTP_ACCEPT_ENCODING": "gzip, deflate, sdch"})

        self.assertSetEqual(
            set(header_keys),
            set(["COOKIE", "USER_AGENT", "CONNECTION", "REFERER", "HOST", "UPGRADE_INSECURE_REQUESTS",
                 "ACCEPT", "ACCEPT_LANGUAGE", "ACCEPT_ENCODING"]))
