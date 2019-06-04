import argparse
import logging
import os
import signal
import ssl
import sys

import pyraftlog

directory = os.environ.get('CONSENSUS_SSL_PATH', os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/certs')
key_file = os.path.join(directory, 'transport-consensus.key')
crt_file = os.path.join(directory, 'transport-consensus.crt')
ca_file = os.path.join(directory, 'transport-ca.pem')


def mock_run():
    parser = argparse.ArgumentParser(description='Run a mock localhost pyraftlog server')
    parser.add_argument('-t', '--type', default="active", help='Type of the node',
                        choices=['active', 'reluctant', 'passive'])
    parser.add_argument('-n', '--node', required=True, help='(host:)?port of this node. e.g. 7001 or node:7001')
    parser.add_argument('-b', '--neighbours', required=True, nargs='+', help='Port(s) of neighbour')
    parser.add_argument('-p', '--port', default=7500, type=int, help='Port for receiving commands')
    parser.add_argument('-r', '--log-reduction', action='store_true', default=False, help='Set log reduction to True')
    parser.add_argument('-l', '--log-level', default="WARNING", help='Logging level',
                        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'])
    parser.add_argument('-s', '--storage-type', default="pickle", help='Type of the storage',
                        choices=['pickle', 'sqlite'])
    parser.add_argument('-f', '--storage-file', default=None, help='Path to storage file')
    parser.add_argument('--transport', default='ssl_socket', help='Type of RPC transport',
                        choices=['socket', 'ssl_socket', 'redis'])
    args = parser.parse_args()

    for f in [ca_file, crt_file, key_file]:
        if not os.path.isfile(f):
            sys.exit("Missing file: %s" % f)

    # Get the node name and neighbourhood
    node_name = args.node if ':' in args.node else ('localhost:' + str(args.node))
    node_host, node_port = node_name.split(':', 1)
    neighbourhood = [node_name]
    for neighbour in args.neighbours:
        neighbourhood.append(neighbour if ':' in neighbour else ('localhost:' + neighbour))

    # Create the logger
    log_level = logging.getLevelName(args.log_level)
    logging.basicConfig(stream=sys.stderr, level=log_level,
                        format='%(asctime)s %(levelname)-8s %(message)s')
    logger = logging.getLogger(node_name)

    # Create the storage
    if args.storage_type == 'sqlite':
        storage = pyraftlog.SQLiteStorage(args.storage_file or node_name + '.sqlite')
    else:
        storage = pyraftlog.PickleStorage(args.storage_file or node_name + '.pickle')

    # Create the node
    node = pyraftlog.Node(pyraftlog.get_mode_name(args.type), node_name, neighbourhood, storage,
                          election_timeout=5.0, heartbeat_timeout=1.0, vote_timeout=3.0, logger=logger)

    # Create the transport
    if args.transport == 'socket':
        transport = pyraftlog.SocketTransport(node_port, keep_idle=1, keep_interval=1, keep_count=1)
    elif args.transport == 'ssl_socket':
        transport = pyraftlog.SslSocketTransport(node_port, key_file, crt_file, ca_file,
                                                 keep_idle=1, keep_interval=1, keep_count=1)
    elif args.transport == 'redis':
        transport = pyraftlog.RedisTransport()
    else:
        transport = None

    signal.signal(signal.SIGINT, node.handle_signal)

    #
    with node:
        # Activate the node transport
        node.activate(transport)

        # Create the HTTP server
        node.request_address = 'https://%s:%d' % (node_host, args.port)
        node.state.log_reduction = args.log_reduction
        httpd = pyraftlog.RaftHTTPServer(('', args.port), pyraftlog.RaftHTTPRequestHandler)
        httpd.raft = node
        httpd.daemon_threads = True
        httpd.transport = transport
        httpd.socket = ssl.wrap_socket(httpd.socket, keyfile=key_file, certfile=crt_file,
                                       server_side=True, cert_reqs=ssl.CERT_NONE,
                                       ssl_version=ssl.PROTOCOL_TLSv1_2, ca_certs=ca_file,
                                       ciphers=pyraftlog.SslSocketTransport.CIPHERS)

        httpd.serve_forever()


def main():
    mock_run()


if __name__ == '__main__':
    sys.exit(main())
