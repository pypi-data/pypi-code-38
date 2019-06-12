import uuid
import argparse
import logging

from twisted.internet import reactor

from multiproxy import MultiProxyInitiator, MultiProxyForwarder, MultiProxyServer
from ipv8.configuration import get_default_configuration
from ipv8_service import IPv8, _COMMUNITIES

# show logs
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)-8s %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S', filemode='a+')


def proxy(nodes_num):
    _COMMUNITIES['MultiProxyInitiator'] = MultiProxyInitiator
    _COMMUNITIES['MultiProxyForwarder'] = MultiProxyForwarder
    _COMMUNITIES['MultiProxyServer'] = MultiProxyServer

    client_num, forwarder_num, server_num = nodes_num
    logging.debug("Initialize {} clients, {} forwarder, {} server"
                  .format(client_num, forwarder_num, server_num))

    def set_nodes(role, id_with_key):
        configuration = get_default_configuration()
        configuration['keys'] = [{
            'alias': "my peer",
            'generation': u"curve25519",
            # 'file': u"ec_{1}{0}.pem".format(*id_with_key)
            'file': u"ec{}_{}_{!r}.pem".format(*((id_with_key) + (str(uuid.uuid4()),)))
        }]
        configuration['logger'] = {
            'level': 'ERROR'
        }
        configuration['overlays'] = [{
            'class': role,
            'key': "my peer",
            'walkers': [{
                'strategy': "RandomWalk",
                'peers': 10,
                'init': {
                    'timeout': 3.0
                }
            }],
            'initialize': {},
            'on_start': [('started',)]
        }]
        IPv8(configuration)

    key = 1
    for _ in range(client_num):
        set_nodes('MultiProxyInitiator', (key, 'c'))
        key += 1

    for _ in range(forwarder_num):
        set_nodes('MultiProxyForwarder', (key, 'f'))
        key += 1

    for _ in range(server_num):
        set_nodes('MultiProxyServer', (key, 's'))
        key += 1


def main():
    parser = argparse.ArgumentParser(description="Please input the node identity and the number of nodes")
    parser.add_argument('--client', type=int, nargs='?', const=0, dest='client_number',
                        help="The number of the clients")
    parser.add_argument('--forwarder', type=int, nargs='?', const=0, dest='forwarder_number',
                        help="The number of the forwarders")
    parser.add_argument('--server', type=int, nargs='?', const=0, dest='server_number',
                        help="The number of the servers")
    args = parser.parse_args()
    nodes = [args.client_number, args.forwarder_number, args.server_number]
    nodes = [i if i else 0 for i in nodes]
    print(nodes)
    proxy(nodes)
    reactor.run()


if __name__ == '__main__':
    main()
    # Usage: python multiproxy.py --client 2 --forwarder 1 --server 2
    # Usage: python multiproxy.py --client 1
