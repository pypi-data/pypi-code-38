import argparse
import logging
import os

from . import ENV_SSL_CERT_FILE
from .server import make_server


def enable_debug():
    logging.basicConfig(level=logging.DEBUG)
    requests_log = logging.getLogger('requests.packages.urllib3')
    requests_log.setLevel(logging.DEBUG)
    requests_log.propagate = True

    from http.client import HTTPConnection, HTTPSConnection
    HTTPConnection.debuglevel = 2


def main():
    parser = argparse.ArgumentParser(description='reverse proxy for forward proxy')
    parser.add_argument('--proxy', help='forward proxy address, e.g. 192.168.1.2:8080')
    parser.add_argument('--listen-port', type=int, help='host:port to bind to, for frontend')
    parser.add_argument('--cacert', help='CA cert path')
    parser.add_argument('--verbose', '-v', action='store_true', help='enable verbose logging')
    args = parser.parse_args()

    if not args.verbose:
        args.verbose = os.environ.get('REVERSE_FORWARD_PROXY_VERBOSE') == '1'

    if args.verbose:
        enable_debug()
    else:
        logging.basicConfig(level=logging.INFO)

    http_proxy = args.proxy

    if not http_proxy:
        http_proxy = os.environ['HTTP_PROXY']
        https_proxy = os.environ.get('HTTPS_PROXY', http_proxy)

    if not args.cacert:
        args.cacert = os.environ.get(ENV_SSL_CERT_FILE, True)

    if not args.listen_port:
        args.listen_port = int(os.environ.get('REVERSE_FORWARD_PROXY_PORT', '8080'))

    target_header = os.environ.get(
        'REVERSE_FORWARD_PROXY_TARGET_HEADER',
        'X-Reverse-Forward-Proxy-Target',
    )

    address = ('', args.listen_port)
    server = make_server(
        server_address=address,
        http_proxy=http_proxy,
        https_proxy=https_proxy,
        cacert=args.cacert,
        target_header=target_header,
    )

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('Killed')
