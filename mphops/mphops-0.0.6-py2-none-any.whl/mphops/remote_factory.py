# Remote side
# ----------------------------------------------------------------------------------------------------------------------
# Used by socks5/forwarder/server protocol

import time

import logging
from twisted.internet import protocol
from twisted.internet.protocol import ClientFactory

from parse_stream import Packet


class RemoteProtocol(protocol.Protocol, object):

    def __init__(self, remote_factory):
        self.remote_factory = remote_factory

    def write(self, data):
        self.transport.write(data)

    def connectionMade(self):
        self.remote_factory.local_protocol.remote_protocol = self
        self.write(self.remote_factory.local_protocol.buffer)
        self.remote_factory.local_protocol.buffer = ''

        self.send_ping()

    def send_ping(self):
        ping = Packet(0, 'ping', '').to_bytes()
        self.send_time = time.time()
        self.write(ping)

    def pre_process(self, data):
        return self.buffer + data

    def dataReceived(self, data):
        data_to_send = self.pre_process(data)
        self.on_data(data_to_send)

    def on_data(self, data):
        messages, self.buffer = Packet.parse_stream(data)
        for message in messages:
            if message.msg_type == 'pong':
                self.handle_PONG()
            elif message.msg_type == 'recv':
                self.handle_RECV(message)

    def handle_PONG(self):
        recv_time = time.time()
        RTT = recv_time - self.send_time
        address = self.transport.getPeer()
        logging.debug("RTT: {}, receive PONG from {}".format(RTT, address))


class ClientRemoteProtocol(RemoteProtocol):

    def __init__(self, remote_factory):
        super(ClientRemoteProtocol, self).__init__(remote_factory)
        self.buffer = bytes()

    def handle_RECV(self, message):
        data_to_send = message.data
        self.remote_factory.local_protocol.write(data_to_send)


class ForwarderRemoteProtocol(RemoteProtocol):

    def __init__(self, remote_factory):
        super(ForwarderRemoteProtocol, self).__init__(remote_factory)
        self.buffer = bytes()

    def handle_RECV(self, message):
        data_to_send = Packet(0, 'recv', message.data).to_bytes()
        self.remote_factory.local_protocol.write(data_to_send)


class ServerRemoteProtocol(RemoteProtocol):

    def send_ping(self):
        pass

    def pre_process(self, data):
        return data

    def on_data(self, data):
        try:
            message, _ = Packet.parse_stream(data)
            if message.data_type == 'pong':
                self.handle_PONG()
        except:
            logging.debug("receive data from target server, send remote data back to forwarder.")
            self.handle_RECV(data)

    def handle_RECV(self, data):
        data_to_send = Packet(0, 'recv', data).to_bytes()
        self.remote_factory.local_protocol.write(data_to_send)


class RemoteFactory(ClientFactory):

    def __init__(self, local_protocol, role):
        """ Initialize local protocols(socks5/forwarder/server)"""
        self.local_protocol = local_protocol
        self.role = role

    def buildProtocol(self, addr):
        if self.role == 's':
            return ServerRemoteProtocol(self)
        elif self.role == 'c':
            return ClientRemoteProtocol(self)
        elif self.role == 'f':
            return ForwarderRemoteProtocol(self)
        else:
            logging.error("No such remote protocol.")
