import logging
import os
import shutil

from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler

import requests

from yarl import URL

from . import DEFAULT_TARGET_HEADER, ENV_SSL_CERT_FILE


logger = logging.getLogger(__name__)


_cacert_default = object()


def make_server(
    server_address,
    http_proxy,
    https_proxy=None,
    cacert=_cacert_default,
    target_header=DEFAULT_TARGET_HEADER,
):
    if cacert == _cacert_default:
        cacert = os.environ.get(ENV_SSL_CERT_FILE, True)

    defaults = {
        'proxies': {
            'http': http_proxy,
            'https': https_proxy or http_proxy,
        },
        'verify': cacert,
    }

    Handler = get_handler(defaults, target_header)

    return ThreadingHTTPServer(server_address, Handler)


def get_handler(requests_defaults, target_header_name):
    class Handler(ProxyRequestHandler):
        defaults = requests_defaults

        target_header = target_header_name

    return Handler


class ProxyRequestHandler(BaseHTTPRequestHandler):
    # Support headers as expected from remote peers.
    protocol_version = 'HTTP/1.1'

    defaults = {}

    target_header = DEFAULT_TARGET_HEADER

    def do_GET(self):
        # Session per request to avoid concurrency issues, see
        # kennethreitz/requests#2766.
        session = requests.Session()

        header_key = self.target_header
        target = self.headers[header_key]

        if target is None:
            self.send_error(400, message=f"Expected header {header_key}.")
            return

        target_url = URL(target)

        if not target_url.is_absolute():
            self.send_error(400, message=f"{header_key} must be absolute.")
            return

        if not target_url.scheme:
            self.send_error(400, message=f"{header_key} must have scheme.")
            return

        if target_url.path != '/':
            self.send_error(400, message=f"{header_key} must not have path.")
            return

        # TODO: Trace incoming request info.
        logger.info('Request for %s', self.path)
        path = URL(self.path)

        # Remove incoming host header, let it be populated by the client library.
        del self.headers['host']

        url = (
            target_url
            .with_path(path.path)
            .with_query(path.query)
        )
        # TODO: Error handling, connect timeout.
        req = requests.Request(method='GET', url=str(url), headers=self.headers)
        prep = req.prepare()
        # Override any encoding done by requests.
        # https://github.com/kennethreitz/requests/issues/1454#issuecomment-20832874
        prep.url = str(url)

        try:
            response = session.send(prep, stream=True, **self.defaults)
        except requests.exceptions.ProxyError as e:
            logger.exception("Error retrieving %s", url)
            self.send_error(502, 'Bad gateway')
            return
        except requests.exceptions.SSLError as e:
            logger.exception("Error retrieving %s", url)
            self.send_error(503, 'Service unavailable')
            return

        self.send_response(response.status_code)
        for k, v in response.headers.items():
            self.send_header(k, v)
        self.end_headers()

        chunked = 'chunked' in response.headers.get('transfer-encoding', '')

        if not chunked:
            shutil.copyfileobj(response.raw, self.wfile)
            return

        CRLF = b'\r\n'
        END_CHUNKS = b'0\r\n\r\n'

        for chunk in response.raw.stream(decode_content=False):
            # e.g. 0xf00
            size = hex(len(chunk))
            # chunk header: size, CRLF
            self.wfile.write(size[2:].upper().encode('ascii'))
            self.wfile.write(CRLF)

            # body
            self.wfile.write(chunk)

            # trailer: CRLF
            self.wfile.write(CRLF)

        self.wfile.write(END_CHUNKS)

        # TODO: Avoid traced errors related to Connection reset
