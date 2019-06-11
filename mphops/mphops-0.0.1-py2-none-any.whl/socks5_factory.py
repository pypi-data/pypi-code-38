# Client local side
# ----------------------------------------------------------------------------------------------------------------------
# Browser sends requests to here

import logging
from twisted.internet import protocol, reactor
from twisted.internet.protocol import Factory

from socks5_ipv8.hops.parse_stream import Packet
from socks5_ipv8.hops.remote_factory import RemoteFactory
from socks5_ipv8.hops.util import unpack_request_data, socks5_server_reply


class Socks5Protocol(protocol.Protocol):

    def __init__(self, factory):
        self.socks5_factory = factory
        self.remote_protocol = None
        self.state = 'NEGOTIATION'
        self.buffer = bytes()

    def connectionMade(self):
        address = self.transport.getPeer()
        self.host_address = self.transport.getHost()
        logging.info("{}:{}, {}, Receive {} connection from {}:{}"
                     .format(self.host_address.host, self.host_address.port,
                             self.__class__.__name__, address.type, address.host, address.port))

    def dataReceived(self, data):
        if self.state == 'NEGOTIATION':
            self.handle_NEGOTIATION(data)
            self.state = 'REQUEST'

        elif self.state == 'REQUEST':
            self.handle_REQUEST(data)
            self.state = 'TRANSMISSION'

        elif self.state == 'TRANSMISSION':
            self.handle_TRANSMISSION(data)

    def handle_NEGOTIATION(self, data):
        self.transport.write('\x05\x00')

    def handle_REQUEST(self, data):
        addr_to_send = unpack_request_data(data)
        # send to remote
        self.send_address(addr_to_send)
        # reply to local
        socks5_server_port = self.socks5_factory.proxy.socks5_port
        self.transport.write(socks5_server_reply(socks5_server_port))

    def send_address(self, addr_to_send):
        # use tcp endpoint
        remote_factory = RemoteFactory(self, 'c')
        circuit = self.socks5_factory.circuit_peers.values()[0]
        # print "circuit.hs_session_keys", repr(circuit.hs_session_keys), circuit.hops
        host, port = circuit.peer.address
        self.cir_id = self.socks5_factory.circuit_peers.keys()[0]  # circuit_id
        self.buffer = Packet(self.cir_id, 'addr', addr_to_send).to_bytes()
        reactor.connectTCP(host, port, remote_factory)
        logging.info("{}:{}, {}, Connected to {}:{}"
                     .format(self.host_address.host, self.host_address.port, self.__class__.__name__, host, port))

    def handle_TRANSMISSION(self, data):
        """ Send packed data to server """
        data_send = Packet(self.cir_id, 'data', data).to_bytes()
        if self.remote_protocol is not None:
            self.remote_protocol.write(data_send)
        else:
            self.buffer += data_send

    def write(self, data):
        self.transport.write(data)


class Socks5Factory(Factory):

    def __init__(self, proxy):
        self.proxy = proxy
        self.circuit_peers = {}
        self.exit_node = {}

    def buildProtocol(self, addr):
        return Socks5Protocol(self)
