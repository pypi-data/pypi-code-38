# Server local side
# ----------------------------------------------------------------------------------------------------------------------
# Exit node

import logging
from twisted.internet import protocol, reactor
from twisted.internet.protocol import Factory

from parse_stream import Packet
from remote_factory import RemoteFactory
from util import unpack_address


class ServerProtocol(protocol.Protocol):

    def __init__(self, server_factory):
        self.server_factory = server_factory
        self.remote_protocol = None
        self.buffer = bytes()
        self.message_buffer = bytes()

    def connectionMade(self):
        address = self.transport.getPeer()
        self.host_address = self.transport.getHost()
        logging.debug("{}:{}, {}, Receive requests from {}:{}"
                      .format(self.host_address.host, self.host_address.port, self.__class__.__name__,
                              address.host, address.port))

    def dataReceived(self, data):
        data_to_parse = self.message_buffer + data
        messages, self.message_buffer = Packet.parse_stream(data_to_parse)
        for m in messages:
            msg_type = m.msg_type
            if msg_type == 'addr':
                self.handle_REMOTEADDR(m)

            elif msg_type == 'data':
                self.handle_REQUEST(m)

            elif msg_type == 'ping':
                self.handle_PING(m)

    def handle_REMOTEADDR(self, message):
        host, port, request = unpack_address(message.data)
        logging.debug("{}:{}, {}, Forward to target server {}:{}"
                      .format(self.host_address.host, self.host_address.port, self.__class__.__name__,
                              host, port))
        remote_factory = RemoteFactory(self, 's')
        reactor.connectTCP(host, port, remote_factory)
        self.buffer = request

    def handle_REQUEST(self, message):
        data_to_send = message.data
        if self.remote_protocol is not None:
            self.remote_protocol.write(data_to_send)
        else:
            self.buffer += data_to_send

    def handle_PING(self, message):
        pong = Packet(0, 'pong', '').to_bytes()
        self.write(pong)

    def write(self, data):
        self.transport.write(data)

    def connectionLost(self, reason):
        logging.error("connection lost:{}".format(reason))
        self.transport.loseConnection()


class ServerFactory(Factory):
    def __init__(self, proxy):
        self.proxy = proxy
        self.factories = {}

    def buildProtocol(self, addr):
        return ServerProtocol(self)
