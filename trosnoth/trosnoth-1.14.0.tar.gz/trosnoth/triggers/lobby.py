import logging
import random

from twisted.internet import defer

from trosnoth.messages import SetPlayerTeamMsg
from trosnoth.model.universe_base import NEUTRAL_TEAM_ID
from trosnoth.triggers.base import Trigger
from trosnoth.utils.twist import WeakLoopingCall

log = logging.getLogger(__name__)


class MakeNewPlayersNeutralTrigger(Trigger):
    def doActivate(self):
        self.world.onPlayerAdded.addListener(self.newPlayerAdded)

    def doDeactivate(self):
        self.world.onPlayerAdded.removeListener(self.newPlayerAdded)

    def newPlayerAdded(self, player):
        if player.team is not None:
            self.world.sendServerCommand(
                SetPlayerTeamMsg(player.id, NEUTRAL_TEAM_ID))


class AddBotsForLobbyTrigger(Trigger):
    '''
    Adds a number of bots so even a single player can mess around in the
    lobby until others arrive.

    Keeps the total number of bots at least up to a particular minimum,
    adding and removing bots as necessary.
    '''

    def __init__(self, level, playerCount=6):
        from trosnoth.bots.base import listAIs

        super(AddBotsForLobbyTrigger, self).__init__(level)
        self.playerCount = playerCount
        self.loop = WeakLoopingCall(self, 'recheck')
        self.agents = []
        self.newAgents = set()
        self.aiNames = listAIs()

    def doActivate(self):
        if not self.loop.running:
            self.loop.start(3, False)

    def doDeactivate(self):
        if self.loop.running:
            self.loop.stop()
        self._stopAllAgents()

    @defer.inlineCallbacks
    def recheck(self):
        self._graduateNewAgents()
        yield self._adjustAgentsToTarget()

    def _graduateNewAgents(self):
        for agent in list(self.newAgents):
            if agent.player is not None:
                self.agents.append(agent)
                self.newAgents.remove(agent)

    def _stopAllAgents(self):
        if len(self.agents) != 0:
            log.info('AIInjector: Stopping all agents')
        for agent in self.agents:
            agent.stop()
            self.world.game.detachAgent(agent)
        self.agents = []

    @defer.inlineCallbacks
    def _adjustAgentsToTarget(self):
        worldPlayers = len(self.world.game.world.players)
        newAgents = len(self.newAgents)
        if self.playerCount > worldPlayers + newAgents:
            yield self._addAgents(self.playerCount - worldPlayers - newAgents)
        else:
            self._removeAgents(worldPlayers + newAgents - self.playerCount)

    @defer.inlineCallbacks
    def _addAgents(self, count):
        log.info('AIInjector: Adding %d agents', count)
        for i in range(count):
            agent = yield self.world.game.addBot(random.choice(self.aiNames))
            self.newAgents.add(agent)

    def _removeAgents(self, count):
        if count != 0:
            log.info('AIInjector: Removing %d agents', count)
        for i in range(count):
            if len(self.agents) == 0:
                break
            agent = self.agents.pop(0)
            agent.stop()
            self.world.game.detachAgent(agent)


class StartGameWhenReadyTrigger(Trigger):
    def __init__(self, level):
        super(StartGameWhenReadyTrigger, self).__init__(level)
        self.loop = WeakLoopingCall(self, 'check')

    def doActivate(self):
        if not self.loop.running:
            self.loop.start(3, False)

    def doDeactivate(self):
        if self.loop.running:
            self.loop.stop()

    def check(self):
        try:
            self.world.voteArbiter.startNewGameIfReady()
        except Exception:
            log.exception('Error trying to start new game')