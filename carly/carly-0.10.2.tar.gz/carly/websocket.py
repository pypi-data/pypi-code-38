from autobahn.websocket.protocol import WebSocketClientProtocol as AbstractProtocol
from autobahn.twisted import WebSocketClientProtocol, WebSocketClientFactory

from .tcp import makeTCPClient


def makeWebSocketClient(context, server, protocol=None,
                        factory=None, factoryClass=None, endpoint='', close='sendClose'):
    if factory is None:
        url = "ws://{}:{}{}".format(server.targetHost, server.targetPort, endpoint)
        if factoryClass is None:
            factoryClass = WebSocketClientFactory
        factory = factoryClass(url)
    if protocol is None:
        protocol = factory.protocol
        if protocol is AbstractProtocol:
            # bug in autobahn?
            protocol = WebSocketClientProtocol
    return makeTCPClient(context, protocol, server, factory, when='onOpen', close=close)
