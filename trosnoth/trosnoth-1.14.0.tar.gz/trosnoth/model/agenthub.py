import logging

from twisted.internet import defer

from trosnoth.messages import (
    SetAgentPlayerMsg, ConnectionLostMsg, AgentDetachedMsg,
)
from trosnoth.model.agent import Agent
from trosnoth.model.hub import Hub, MAX_AGENT_ID, UnableToConnect, Unauthorised
from trosnoth.model.universe_base import NO_PLAYER

log = logging.getLogger(__name__)


class LocalHub(Hub):
    '''
    A Hub that connects to a local game by creating agents (rather than
    connecting to a remote game over the network).

    (In theory, this hub can even connect to a RemoteGame, but that is unlikely
    to be a useful state of affairs, since that RemoteGame will require another
    hub to connect to the network.)
    '''

    def __init__(
            self, game, noAuth=False, agentCallback=None, *args, **kwargs):
        super(LocalHub, self).__init__(*args, **kwargs)
        self.game = game
        self.noAuth = noAuth
        self.agentCallback = agentCallback
        self.agents = {}
        self.nextId = 0
        self.game.onServerCommand.addListener(self.gotServerCommand)

    def gotServerCommand(self, msg):
        msg.tracePoint(self, 'gotServerCommand')
        if self.node:
            self.node.gotServerCommand(msg)

    def disconnectNode(self):
        super(LocalHub, self).disconnectNode()
        for agentId in list(self.agents.keys()):
            self.disconnectAgent(agentId)

    @defer.inlineCallbacks
    def connectNewAgent(self, authTag=0):
        if self.game.serverInterface and not self.noAuth:
            user = self.game.serverInterface.getUserFromAuthTag(authTag)
            if user is None:
                raise Unauthorised()
        else:
            user = None

        result = self.nextId
        if len(self.agents) >= MAX_AGENT_ID:
            raise UnableToConnect('No spare agent IDs')
        while result in self.agents:
            result = (result + 1) % (MAX_AGENT_ID + 1)

        agent = LocalHubAgent(self, result)
        yield self.game.addAgent(agent, user=user)

        self.agents[result] = agent
        self.nextId = (result + 1) % (MAX_AGENT_ID + 1)
        if self.agentCallback:
            self.agentCallback(agent, authTag)
        defer.returnValue(result)

    def disconnectAgent(self, agentId):
        agent = self.agents[agentId]
        self.game.detachAgent(agent)
        self.agentDisconnected(agent)

    def sendRequestToGame(self, agentId, msg):
        msg.tracePoint(self, 'sendRequestToGame')
        self.game.agentRequest(self.agents[agentId], msg)

    def agentDisconnected(self, agent):
        '''
        Called when the game indicates that the connection to this agent is
        lost.
        '''
        if agent.agentId not in self.agents:
            # It may be possible for this to be triggered twice for the same
            # agent, but we only want it to run once.
            return

        if self.node:
            self.node.agentDisconnected(agent.agentId)
        agent.stop()
        del self.agents[agent.agentId]


class LocalHubAgent(Agent):

    def __init__(self, hub, agentId, *args, **kwargs):
        super(LocalHubAgent, self).__init__(game=hub.game, *args, **kwargs)
        self.hub = hub
        self.agentId = agentId

    def messageToAgent(self, msg):
        msg.tracePoint(self, 'messageToAgent')
        if self.hub.node:
            if isinstance(msg, ConnectionLostMsg):
                self.hub.agentDisconnected(self)
            else:
                self.hub.node.gotMessageToAgent(self.agentId, msg)

    def detached(self):
        super().detached()
        self.messageToAgent(AgentDetachedMsg())

    def setPlayer(self, player):
        super(LocalHubAgent, self).setPlayer(player)

        # To get this across the hub/node interface it must be encoded as a
        # message.
        playerId = player.id if player else NO_PLAYER
        self.messageToAgent(SetAgentPlayerMsg(playerId))
