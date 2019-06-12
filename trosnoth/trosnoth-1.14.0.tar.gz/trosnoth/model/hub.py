'''
The hub/node interface exists primarily for sending and receiving network
messages, but it is also used when Trosnoth is run in isolated mode (for
testing).
This interface provides a channel for messages to be passed between agents and
a game. A hub sits on the game side of this interface, while a node sits on the
agent side. The interface may be used to pass messages for zero or more agents.
'''

MAX_AGENT_ID = 1 << 16 - 1


class Hub(object):
    '''
    Sits on the game side of the hub/node message passing interface.
    '''

    def __init__(self, *args, **kwargs):
        super(Hub, self).__init__(*args, **kwargs)
        self.node = None

    def connectNode(self, node):
        assert self.node is None
        assert node.hub is None
        self.node = node
        node.hub = self

    def disconnectNode(self):
        self.node.hub = None
        self.node = None

    def connectNewAgent(self, authTag=0):
        '''
        Requests that a new agent be connected to the game that this hub
        represents. If successful, this method will return an agentId for the
        new agent (or a deferred that results in the agentId).
        May raise UnableToConnect or Unauthorised.
        '''
        raise NotImplementedError(
            '%s.connectNewAgent' % (self.__class__.__name__,))

    def disconnectAgent(self, agentId):
        '''
        Requests that the agent with the given id be disconnected from the
        game. May return a deferred that will not complete until the agent is
        disconnected.
        Note that the onAgentDisconnected event will fire whenever an agent is
        disconnected, regardless of whether it is triggered by this function or
        some other reason (e.g. lost network connection).
        '''
        raise NotImplementedError(
            '%s.disconnectAgent' % (self.__class__.__name__,))

    def sendRequestToGame(self, agentId, msg):
        raise NotImplementedError(
            '%s.sendRequestToGame' % (self.__class__.__name__,))


class UnableToConnect(Exception):
    '''
    Raised by connectNewAgent if the connection could not be established.
    '''

class Unauthorised(Exception):
    '''
    Raised by connectNewAgent if the user is not allowed to connect.
    '''


class Node(object):
    '''
    Sits on the agent side of the hub/node message passing interface.
    '''

    def __init__(self, *args, **kwargs):
        super(Node, self).__init__(*args, **kwargs)
        self.hub = None

    def gotServerCommand(self, msg):
        '''
        Called by the connected hub for every message from the server.
        '''
        raise NotImplementedError(
            '%s.gotServerCommand' % (self.__class__.__name__,))

    def gotMessageToAgent(self, agentId, msg):
        '''
        Called when the game sends a message targetted at a specific agent.
        '''
        raise NotImplementedError(
            '%s.gotMessageToAgent' % (self.__class__.__name__,))

    def agentDisconnected(self, agentId):
        '''
        Called when one of this node's agents has been disconnected from the
        game for any reason.
        '''
        raise NotImplementedError(
            '%s.agentDisconnected' % (self.__class__.__name__,))
