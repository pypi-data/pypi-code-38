import logging
import struct

from twisted.internet import defer
from twisted.internet.protocol import Factory
from twisted.protocols.basic import Int32StringReceiver

from trosnoth.model.hub import Hub, Node
from trosnoth.utils import netmsg

log = logging.getLogger(__name__)


AGENT_REQUEST_ID_LIMIT = (1 << 16)

CLIENT_CONNECT_AGENT = b'c'
CLIENT_DISCONNECT_AGENT = b'd'
CLIENT_REQUEST = b'm'

SERVER_GENERAL_MESSAGE = b'g'
SERVER_TARGETED_MESSAGE = b't'
SERVER_CONNECTED_AGENT = b'c'
SERVER_DISCONNECTED_AGENT = b'd'


class MsgClientProtocol(Int32StringReceiver, Hub):
    messages = netmsg.MessageCollection()
    greeting = None     # Override this in subclasses

    def connectionMade(self):
        self.agentRequests = {}
        self.nextAgentRequestId = 0
        self.sendString(self.greeting)
        self.agentIds = set()

    def connectionLost(self, reason=None):
        if self.node:
            while self.agentIds:
                agentId = self.agentIds.pop()
                self.node.agentDisconnected(agentId)
        else:
            self.agentIds.clear()

    def stringReceived(self, string):
        kind, body = string[:1], string[1:]
        try:
            if kind == SERVER_GENERAL_MESSAGE:
                self.receivedGeneralMessageString(body)
            elif kind == SERVER_TARGETED_MESSAGE:
                self.receivedTargetedMessageString(body)
            elif kind == SERVER_CONNECTED_AGENT:
                self.receivedAgentConnectedString(body)
            elif kind == SERVER_DISCONNECTED_AGENT:
                self.receivedAgentDisconnectedString(body)
            else:
                self.receivedBadString(string)
        except Exception:
            log.exception('Error responding to received message')

    def receivedBadString(self, string):
        log.warning(
            'Got unexpected string from remote end, dropping connection.')
        self.transport.abortConnection()

    def receivedGeneralMessageString(self, string):
        msg = self.buildMessage(string)
        if msg:
            msg.tracePoint(self, 'receivedGeneralMessageString')
            self.gotGeneralMsg(msg)
        else:
            self.receivedBadString(string)

    def gotGeneralMsg(self, msg):
        if self.node:
            self.node.gotServerCommand(msg)

    def receivedTargetedMessageString(self, string):
        agentId, body = string[:2], string[2:]

        msg = self.buildMessage(body)
        if not msg:
            self.receivedBadString(string)
        elif self.node:
            msg.tracePoint(self, 'receivedTargetedMessageString')
            self.node.gotMessageToAgent(agentId, msg)

    def buildMessage(self, string):
        try:
            return self.messages.buildMessage(string)
        except netmsg.NetworkMessageError:
            return None

    def receivedAgentConnectedString(self, string):
        reqId, agentId = string[:2], string[2:]
        try:
            d = self.agentRequests.pop(reqId)
        except KeyError:
            return
        self.agentIds.add(agentId)
        d.callback(agentId)

    def receivedAgentDisconnectedString(self, agentId):
        self.agentIds.discard(agentId)
        if self.node:
            self.node.agentDisconnected(agentId)

    def connectNewAgent(self, authTag=0):
        if len(self.agentRequests) >= AGENT_REQUEST_ID_LIMIT:
            raise OverflowError('Too many concurrent requests for new agents')
        while True:
            reqId = struct.pack('!H', self.nextAgentRequestId)
            self.nextAgentRequestId += 1
            self.nextAgentRequestId %= AGENT_REQUEST_ID_LIMIT
            if reqId not in self.agentRequests:
                break
        authTagStr = struct.pack('!Q', authTag)
        d = defer.Deferred()
        self.agentRequests[reqId] = d
        self.sendString(CLIENT_CONNECT_AGENT + reqId + authTagStr)

        return d

    def disconnectAgent(self, agentId):
        self.sendString(CLIENT_DISCONNECT_AGENT + agentId)

    def sendRequestToGame(self, agentId, msg):
        msg.tracePoint(self, 'sendRequestToGame')
        self.sendString(CLIENT_REQUEST + agentId + msg.pack())


class MsgServerProtocol(Int32StringReceiver, Node):
    def connectionMade(self):
        self.initialised = False
        self.greeting = None

    def connectionLost(self, reason=None):
        if self.initialised:
            self.factory.connectionLost(self, reason)

    def stringReceived(self, string):
        if self.initialised:
            self.receivedMessageString(string)
        else:
            if self.factory.checkGreeting(string):
                self.initialised = True
                self.greeting = string
                self.factory.connectionEstablished(self)
            else:
                self.transport.abortConnection()

    def receivedMessageString(self, string):
        kind, body = string[:1], string[1:]
        if kind == CLIENT_REQUEST:
            self.receivedRequestString(body)
        elif kind == CLIENT_CONNECT_AGENT:
            self.receivedConnectAgentString(body)
        elif kind == CLIENT_DISCONNECT_AGENT:
            self.receivedDisconnectAgentString(body)
        else:
            self.factory.gotBadString(self, string)

    def receivedRequestString(self, string):
        agentId, body = string[:2], string[2:]
        try:
            msg = self.factory.messages.buildMessage(body)
        except netmsg.NetworkMessageError:
            self.factory.gotBadString(self, string)
            return
        msg.tracePoint(self, 'receivedRequestString')
        self.hub.sendRequestToGame(self.decodeAgentId(agentId), msg)

    @defer.inlineCallbacks
    def receivedConnectAgentString(self, string):
        reqId, authTag = string[:2], struct.unpack('!Q', string[2:])[0]
        agentId = yield self.hub.connectNewAgent(authTag=authTag)
        self.sendString(
            SERVER_CONNECTED_AGENT + reqId + self.encodeAgentId(agentId))

    def receivedDisconnectAgentString(self, agentId):
        self.hub.disconnectAgent(self.decodeAgentId(agentId))

    def encodeAgentId(self, agentId):
        '''
        Takes an agentId in the form given by our hub and converts it to a form
        the network can understand.
        '''
        return struct.pack('!H', agentId)

    def decodeAgentId(self, agentId):
        '''
        Takes an agentId in the form given by the network and converts it into
        a form our hub will understand.
        '''
        return struct.unpack('!H', agentId)[0]

    def gotServerCommand(self, msg):
        msg.tracePoint(self, 'gotServerCommand')
        self.sendString(SERVER_GENERAL_MESSAGE + msg.pack())

    def gotMessageToAgent(self, agentId, msg):
        msg.tracePoint(self, 'gotMessageToAgent')
        self.sendString(
            SERVER_TARGETED_MESSAGE + struct.pack('!H', agentId) + msg.pack())

    def agentDisconnected(self, agentId):
        self.sendString(SERVER_DISCONNECTED_AGENT + agentId)


class MsgServer(Factory):
    '''
    Base class for servers which receive packed NetworkMessage objects from the
    network.
    '''
    protocol = MsgServerProtocol
    messages = netmsg.MessageCollection()

    def checkGreeting(self, greeting):
        '''
        Must check whether the given greeting string is allowed for this
        server, and return true or false accordingly.
        '''
        return False

    def connectionEstablished(self, protocol):
        '''
        Called after a client has connected and sent an appropriate greeting
        string.
        '''
        pass

    def connectionLost(self, protocol, reason):
        pass

    def gotBadString(self, protocol, string):
        '''
        Called when a client has sent a string that cannot be decoded by our
        known message types.
        '''
        log.warning('Client sent bad message string')
        protocol.transport.abortConnection()
