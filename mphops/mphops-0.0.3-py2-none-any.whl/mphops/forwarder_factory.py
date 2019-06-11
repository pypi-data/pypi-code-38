# Forwarder local side
# ----------------------------------------------------------------------------------------------------------------------
# Receive data from other peers

import logging
from twisted.internet import protocol, reactor
from twisted.internet.protocol import Factory

from parse_stream import Packet
from remote_factory import RemoteFactory


class ForwardProtocol(protocol.Protocol):

    def __init__(self, forward_factory):
        self.state = 'REQUEST'
        self.forward_factory = forward_factory
        self.remote_protocol = None
        self.buffer = bytes()
        self.message_buffer = bytes()

    def connectionMade(self):
        address = self.transport.getPeer()
        self.host_address = self.transport.getHost()
        logging.debug("{}:{}, {}, Receive connection from {}:{}"
                      .format(self.host_address.host, self.host_address.port, self.__class__.__name__,
                              address.host, address.port))

    def dataReceived(self, data):
        data_to_parse = self.message_buffer + data
        messages, self.message_buffer = Packet.parse_stream(data_to_parse)

        for m in messages:
            if m.msg_type == 'ping':
                self.handle_PING()

            elif m.msg_type == 'addr':
                self.handle_REQUEST(m)

            elif m.msg_type == 'data':
                self.handle_TRANSMISSION(m)

    def handle_PING(self):
        # send pong back to client
        pong = Packet(0, 'pong', '').to_bytes()
        self.write(pong)

    def handle_REQUEST(self, message):
        from_cir_id, msg_type, data = message.cir_id, message.msg_type, message.data
        to_cir_id = self.forward_factory.circuit_id[from_cir_id]
        host, port = self.forward_factory.circuit_peers[from_cir_id]
        logging.debug("{}:{}, {}, Connect to {}:{}, to_circuit id is:{}"
                      .format(self.host_address.host, self.host_address.port,
                              self.__class__.__name__, host, port, to_cir_id))
        remote_factory = RemoteFactory(self, 'f')
        reactor.connectTCP(host, port, remote_factory)
        self.buffer = Packet(to_cir_id, msg_type, data).to_bytes()

    def handle_TRANSMISSION(self, message):
        from_cir_id, msg_type, data = message.cir_id, message.msg_type, message.data
        # print "to_cir_id", from_cir_id, self.forward_factory.circuit_peers
        to_cir_id = self.forward_factory.circuit_id[from_cir_id]
        data_to_send = Packet(to_cir_id, msg_type, data).to_bytes()
        if self.remote_protocol is not None:
            self.remote_protocol.write(data_to_send)
        else:
            self.buffer += data_to_send

    def write(self, data):
        self.transport.write(data)


class ForwardFactory(Factory):

    def __init__(self, proxy):
        self.proxy = proxy
        self.circuit_peers = {}  # {1006213219: ('145.94.162.154', 8093), 1288425294L: ('145.94.162.154', 8091)}
        self.circuit_id = {}  # {1006213219: 1288425294L}
        self.exit_node = {}

    def buildProtocol(self, addr):
        return ForwardProtocol(self)
