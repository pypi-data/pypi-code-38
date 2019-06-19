from twisted.internet.protocol import DatagramProtocol

from .hook import hook


class UDP(DatagramProtocol):

    def __init__(self, port, protocol):
        self.port = port
        self.protocol = protocol
        host = self.port.getHost()
        self.targetHost = host.host
        self.targetPort = host.port

    def startProtocol(self):
        self.transport.connect(self.targetHost, self.targetPort)

    def send(self, datagram):
        self.transport.write(datagram)


def makeUDP(context, protocol, interface='127.0.0.1'):

    from twisted.internet import reactor

    hook(protocol.__class__, 'datagramReceived')
    port = reactor.listenUDP(0, protocol, interface)
    udp = UDP(port, protocol)
    sendPort = reactor.listenUDP(0, udp, interface)
    context.cleanupServers(port, sendPort)
    return udp

