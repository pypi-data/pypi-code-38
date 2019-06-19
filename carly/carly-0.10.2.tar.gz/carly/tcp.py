from attr import make_class
from twisted.internet.defer import (
    inlineCallbacks, gatherResults, returnValue
)
from twisted.internet.protocol import Factory, ClientFactory

from .hook import hook

TCPClient = make_class('TCPClient', ['protocolClass', 'clientProtocol', 'serverProtocol'])


class TCPServer(object):

    def __init__(self, protocolClass, port):
        self.protocolClass = protocolClass
        self.port = port
        host = self.port.getHost()
        self.targetHost = host.host
        self.targetPort = host.port


def makeTCPServer(context, protocol, factory=None, interface='127.0.0.1',
                  installProtocol=True):

    from twisted.internet import reactor

    hook(protocol, 'connectionMade')
    if factory is None:
        factory = Factory()
    if installProtocol:
        factory.protocol = protocol
    port = reactor.listenTCP(0, factory, interface=interface)
    server = TCPServer(protocol, port)
    hook(server.protocolClass, 'connectionLost', once=True)
    context.cleanupServers(server.port)
    return server


def disconnect(client):
    client.clientProtocol.transport.loseConnection()


def makeTCPClient(context, protocol, server, factory=None,
                  when='connectionMade', close=disconnect):

    from twisted.internet import reactor

    hook(protocol, when)
    if factory is None:
        factory = ClientFactory()
    factory.protocol = protocol
    host = server.port.getHost()
    reactor.connectTCP(host.host, host.port, factory)
    return waitForClient(
        context, getattr(protocol, when), server.protocolClass.connectionMade, close
    )


@inlineCallbacks
def waitForClient(context, clientConnected, serverConnected, close=disconnect):
    clientProtocol, serverProtocol = yield gatherResults([
        clientConnected.protocol(), serverConnected.protocol(),
    ])
    client = TCPClient(clientProtocol.__class__, clientProtocol, serverProtocol)
    hook(client.protocolClass, 'connectionLost', once=True)
    context.cleanupClient(client, close)
    returnValue(client)
