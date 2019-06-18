import unittest

from tcell_agent.instrumentation.headers_cleaner import headers_from_environ


class AppSensorMetaTest(unittest.TestCase):

    def test_remove_cookie_from_headers(self):
        headers = headers_from_environ({
            "HTTP_COOKIE": "_ga=GA1.1.1722707835.1481849908; csrftoken=cY830h4FJ9LfrwxFRWPldDC8spjpr7Bj",
            "SCRIPT_NAME": u"",
            "REQUEST_METHOD": "GET",
            "PATH_INFO": u"/",
            "SERVER_PROTOCOL": "HTTP/1.1",
            "QUERY_STRING": "",
            "HTTP_USER_AGENT": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36",
            "HTTP_CONNECTION": "keep-alive",
            "SERVER_NAME": "dfe30e3f783d",
            "REMOTE_ADDR": "192.168.99.1",
            "wsgi.url_scheme": "http",
            "SERVER_PORT": "3000",
            "uwsgi.node": "dfe30e3f783d",
            "uwsgi.core": 0,
            "HTTP_HOST": "192.168.99.100:3000",
            "wsgi.multithread": True,
            "HTTP_UPGRADE_INSECURE_REQUESTS": "1",
            "REQUEST_URI": "/",
            "HTTP_ACCEPT": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "wsgi.version": (1, 0),
            "wsgi.run_once": False,
            "wsgi.multiprocess": True,
            "HTTP_ACCEPT_LANGUAGE": "en-US,en;q=0.8",
            "uwsgi.version": "2.0.15",
            "HTTP_ACCEPT_ENCODING": "gzip, deflate, sdch",
            "HTTP_MY_CUSTOM_HTTP_HEADER": "my value"
        })

        self.assertEqual(
            headers,
            {
                "accept": ["text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"],
                "accept-encoding": ["gzip, deflate, sdch"],
                "accept-language": ["en-US,en;q=0.8"],
                "connection": ["keep-alive"],
                "host": ["192.168.99.100:3000"],
                "upgrade-insecure-requests": ["1"],
                "user-agent": ["Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"],
                "my-custom-http-header": ["my value"]
            }
        )

    def test_leave_in_content_length_and_content_type(self):
        headers = headers_from_environ({
            "HTTP_REFERER": "http://192.168.99.100:3033/waitlist_entries/",
            "SCRIPT_NAME": u"",
            "REQUEST_METHOD": "POST",
            "PATH_INFO": u"/waitlist_entries/",
            "HTTP_ORIGIN": "http://192.168.99.100:3033",
            "SERVER_PROTOCOL": "HTTP/1.1",
            "QUERY_STRING": "",
            "CONTENT_LENGTH": "731",
            "HTTP_USER_AGENT": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_5)",
            "HTTP_CONNECTION": "keep-alive",
            "HTTP_COOKIE": "_ga=GA1.1.1722707835.1481849908; csrftoken=cY830h4FJ9LfrwxFRWPldDC8spjpr7Bj",
            "SERVER_NAME": "2a6232a4d649",
            "REMOTE_ADDR": "192.168.99.1",
            "wsgi.url_scheme": "http",
            "SERVER_PORT": "3000",
            "uwsgi.node": "2a6232a4d649",
            "HTTP_HOST": "192.168.99.100:3033",
            "wsgi.multithread": True,
            "HTTP_UPGRADE_INSECURE_REQUESTS": "1",
            "HTTP_CACHE_CONTROL": "max-age=0",
            "REQUEST_URI": "/waitlist_entries/",
            "HTTP_ACCEPT": "text/html, application/xhtml+xml, application/xml;q=0.9, image/webp, image/apng, */*;q=0.8",
            "wsgi.multiprocess": True,
            "HTTP_ACCEPT_LANGUAGE": "en-US, en;q=0.8",
            "uwsgi.version": "2.0.15",
            "CONTENT_TYPE": "multipart/form-data; boundary=----WebKitFormBoundaryaJYTinr8oP5OBKdW",
            "CSRF_COOKIE": u"cY830h4FJ9LfrwxFRWPldDC8spjpr7Bj",
            "HTTP_ACCEPT_ENCODING": "gzip, deflate"})

        self.assertEqual(
            headers,
            {
                "accept-encoding": ["gzip, deflate"],
                "content-length": ["731"],
                "user-agent": ["Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_5)"],
                "referer": ["http://192.168.99.100:3033/waitlist_entries/"],
                "host": ["192.168.99.100:3033"],
                "accept-language": ["en-US, en;q=0.8"],
                "cache-control": ["max-age=0"],
                "connection": ["keep-alive"],
                "upgrade-insecure-requests": ["1"],
                "origin": ["http://192.168.99.100:3033"],
                "content-type": ["multipart/form-data; boundary=----WebKitFormBoundaryaJYTinr8oP5OBKdW"],
                "accept": ["text/html, application/xhtml+xml, application/xml;q=0.9, image/webp, image/apng, */*;q=0.8"]
            }
        )
