import logging
from twisted.internet import defer

from trosnoth.bots.base import makeAIAgent
from trosnoth.const import (
    TICK_PERIOD, LAG_BUFFER, LAG_THRESHOLD, INITIAL_ASSUMED_LATENCY,
)
from trosnoth.gamerecording.achievements import AchievementManager
from trosnoth.gamerecording.gamerecorder import GameRecorder
from trosnoth.levels.standard import StandardRandomLevel
from trosnoth.messages import (
    RemovePlayerMsg, ConnectionLostMsg, DelayUpdatedMsg, TICK_LIMIT,
    ResyncAcknowledgedMsg, UpdateGameInfoMsg,
)
from trosnoth.model.hub import Node
from trosnoth.model.universe import Universe, ServerUniverse
from trosnoth.utils import globaldebug
from trosnoth.utils.event import Event
from trosnoth.utils.twist import WeakLoopingCall

log = logging.getLogger(__name__)

VERIFY_PLAYER_CONSISTENCY = False


class Game(object):
    '''
    The most important interface in the Trosnoth code base is the Game/Agent
    interface. A Game represents either a locally running server or a game that
    is running on a remote server. In both of these cases, the game will
    provide the same interface for agents to connect to for receiving orders
    from the game, sending requests, and examining the state of the Universe.
    '''

    def __init__(
            self, world, botProcess=False, botProcessLogPrefix=None,
            *args, **kwargs):
        super(Game, self).__init__(*args, **kwargs)
        self.world = world

        self.onServerCommand = Event()      # (msg)

        world.onPlayerRemoved.addListener(self.playerRemoved)

        if botProcess:
            from trosnoth.botprocess import ServerSideBotProcessManager
            self.botProcessManager = ServerSideBotProcessManager(
                self, botProcessLogPrefix)
        else:
            self.botProcessManager = None

    def addAgent(self, agent, user=None, authTag=0):
        '''
        Connects an agent to this game. An agent may be a user interface,
        an AI player, or anything that wants to receive events from the game
        and potentially send actions to it.
        Every player in Trosnoth must be controlled by an agent and no agent
        can control more than one player.
        May return a deferred which will fire once the agent is successfully
        added.
        '''
        raise NotImplementedError('%s.addAgent' % (self.__class__.__name__,))

    @defer.inlineCallbacks
    def addBot(
            self, aiName, team=None, fromLevel=False, nick='',
            forceLocal=False, authTag=0):

        # Note: forceLocal should eventually be removed, but not until the
        # bot process has a way to control bots from the arena process.
        if forceLocal or not self.botProcessManager:
            ai = makeAIAgent(self, aiName, fromLevel=fromLevel, nick=nick)
            yield self.addAgent(ai, authTag=authTag)

            ai.start(team)
        else:
            ai = yield defer.ensureDeferred(self.botProcessManager.startBot(
                aiName, fromLevel=fromLevel, nick=nick, team=team))
        defer.returnValue(ai)

    def detachAgent(self, agent):
        raise NotImplementedError('%s.detachAgent' % (
            self.__class__.__name__,))

    def agentRequest(self, agent, msg):
        '''
        Called by an agent with an AgentRequest message that it wants to
        request.
        '''
        raise NotImplementedError('%s.agentRequest' % (
            self.__class__.__name__,))

    def stop(self):
        self.world.stop()
        if self.botProcessManager:
            self.botProcessManager.stop()

    def joinSuccessful(self, agent, playerId):
        '''
        Called when a join request succeeds.
        '''
        player = self.world.getPlayer(playerId)
        assert player.agent is None
        assert agent.player is None
        assert player is not None

        player.agent = agent
        agent.setPlayer(player)
        player.joinComplete = True
        player.onJoinComplete()

    def playerRemoved(self, player, playerId):
        '''
        Called when a player is removed from the game.
        '''
        if player.agent:
            player.agent.setPlayer(None)


class LocalGame(Game):
    def __init__(
            self, layoutDatabase,
            halfMapWidth=None, mapHeight=None, blockRatio=0.5,
            duration=0, maxPerTeam=100, maxTotal=500, serverInterface=None,
            onceOnly=False, saveReplay=False,
            gamePrefix=None, replayPath=None, level=None, gameType=None,
            lobbySettings=None, *args, **kwargs):

        self._serverCommandStack = []
        self._waitingForEmptyCommandQueue = []
        self.maxPerTeam = maxPerTeam
        self.maxTotalPlayers = min(2 * maxPerTeam, maxTotal)
        self.serverInterface = serverInterface
        self.lobbySettings = lobbySettings

        self.agents = set()
        self.agentInfos = {}
        self.layoutDatabase = layoutDatabase

        if level is None:
            level = StandardRandomLevel(
                halfMapWidth, mapHeight, blockRatio=blockRatio,
                duration=duration)
        world = ServerUniverse(
            self, layoutDatabase,
            onceOnly=onceOnly, level=level, gameType=gameType)

        self.idManager = world.idManager

        self.gameRecorder = GameRecorder(
            self, world, saveReplay=saveReplay, gamePrefix=gamePrefix,
            replayPath=replayPath)

        super(LocalGame, self).__init__(world, *args, **kwargs)

        world.onServerTickComplete.addListener(self.worldTickDone)
        self.gameRecorder.start()

        self.updateDelayLoop = WeakLoopingCall(self, 'updateDelays')
        self.updateDelayLoop.start(10, False)

        self.achievementManager = AchievementManager(self)
        self.achievementManager.start()

        if VERIFY_PLAYER_CONSISTENCY:
            self.playerConsistencyVerifier = PlayerConsistencyVerifier(self)

    def updateDelays(self):
        for info in self.agentInfos.values():
            info.updateDelays()

    def addAgent(self, agent, user=None, authTag=0):
        agent.user = user
        info = AgentInfo(self, agent)
        self.agentInfos[agent] = info
        self.agents.add(agent)

    def detachAgent(self, agent):
        if agent not in self.agents:
            return
        self.agents.remove(agent)
        if agent.player:
            self.kickPlayer(agent.player.id)
            self.agentInfos[agent].takePlayer()
        del self.agentInfos[agent]
        agent.detached()

    def kickPlayer(self, playerId):
        '''
        Removes the player with the specified ID from the game.
        '''
        self.sendServerCommand(RemovePlayerMsg(playerId))

    def agentRequest(self, agent, msg):
        '''
        Some messages need to be delayed until the correct time comes.
        '''
        msg.tracePoint(self, 'agentRequest')
        if agent not in self.agents:
            # Probably just because it's a delayed call
            log.debug('LocalGame got message %s from unconnected agent', msg)
            return
        info = self.agentInfos[agent]
        info.requestFromAgent(msg)

    def dispatchDelayedRequest(self, agent, msg):
        '''
        Called by an AgentInfo when the correct time comes for a request to be
        dispatched.
        '''
        msg.tracePoint(self, 'dispatchDelayedRequest')
        msg.serverApply(self, agent)

    def setPlayerLimits(self, maxPerTeam, maxTotal=40):
        '''
        Changes the player limits in the current game. Note that this does not
        affect players who are already in the game.

        @param maxPerTeam: Maximum number of players per team at once
        @param maxTotal: Maximum number of players in the game at once
        '''
        self.maxPerTeam = maxPerTeam
        self.maxTotalPlayers = min(2 * maxPerTeam, maxTotal)

    def stop(self):
        super(LocalGame, self).stop()
        self.gameRecorder.stop()
        self.achievementManager.stop()
        self.updateDelayLoop.stop()
        self.idManager.stop()

    def worldTickDone(self):
        '''
        Called when the universe has ticked.
        '''
        self.checkCollisionsWithCollectables()
        for info in self.agentInfos.values():
            info.tick()

    def checkCollisionsWithCollectables(self):
        '''
        When a player runs into a collectable unit (e.g. a coin or the
        trosball), we pay attention not to where we think the collectable units
        are, but where the player's client thinks they are. To do this, we need
        to project the collectable units back in time based on the player's
        current delay.
        '''
        greatestDelay = 0
        for info in self.agentInfos.values():
            if not info.player or info.player.dead:
                continue
            greatestDelay = max(greatestDelay, info.currentDelay)

            for unit in self.world.getCollectableUnits():
                if unit.checkCollision(info.player, info.currentDelay):
                    unit.collidedWithPlayer(info.player)

        for unit in self.world.getCollectableUnits():
            unit.clearOldHistory(greatestDelay)

    def joinSuccessful(self, agent, playerId):
        super(LocalGame, self).joinSuccessful(agent, playerId)
        if agent in self.agentInfos:
            self.agentInfos[agent].givePlayer(self.world.getPlayer(playerId))

    def playerRemoved(self, player, playerId):
        super(LocalGame, self).playerRemoved(player, playerId)
        info = self.agentInfos.get(player.agent)
        if info:
            info.takePlayer()

    def sendServerCommand(self, msg):
        '''
        Sends a command to the universe and all attached agents. Typically
        called by message classes in serverApply().
        '''
        self._serverCommandStack.append(msg)
        if len(self._serverCommandStack) > 1:
            # Sometimes one of the calls below (e.g. self.world.consumeMsg())
            # triggers another sendServerCommand() call, so to make sure
            # that all the messages arrive at the clients in the same order
            # as the server, we queue them and release them as soon as the
            # first message is completely sent.
            msg.tracePoint(self, '(sendServerCommand: deferred)')
            return

        while self._serverCommandStack:
            cmd = self._serverCommandStack[0]
            cmd.tracePoint(self, 'sendServerCommand')
            if VERIFY_PLAYER_CONSISTENCY:
                self.playerConsistencyVerifier.preMessage(cmd)
            self.world.consumeMsg(cmd)
            self.gameRecorder.consumeMsg(cmd)
            if VERIFY_PLAYER_CONSISTENCY:
                self.playerConsistencyVerifier.postMessage(cmd)
            self.onServerCommand(cmd)
            cmd.tracePoint(self, 'done sendServerCommand')
            self._serverCommandStack.pop(0)

        # Release things that are waiting for the command stack to empty
        while not self._serverCommandStack and self._waitingForEmptyCommandQueue:
            d = self._waitingForEmptyCommandQueue.pop(0)
            try:
                d.callback(None)
            except Exception:
                log.exception('Error in queued callback')

    def waitForEmptyCommandQueue(self):
        '''
        :return: a Deferred which will callback when the queue of server
            commands to send is empty. This is useful to be sure that the
            world is in a consistent state (all messages have been
            processed).
        '''
        if not self._serverCommandStack:
            return defer.succeed(None)

        d = defer.Deferred()
        self._waitingForEmptyCommandQueue.append(d)
        return d

    def sendResync(
            self, playerId,
            reason='Your computer was out of sync with the server!'):
        '''
        Resyncs the position of the player with the given id. Typically called
        by message classes in serverApply().
        '''
        player = self.world.getPlayer(playerId)
        player.sendResync(reason)


class ExpectedPlayerToNoticeDeath(object):
    def __init__(self, agentInfo):
        self.agentInfo = agentInfo
        self.canceled = False

    def cancel(self):
        self.canceled = True

    def __call__(self):
        if self.canceled:
            return
        player = self.agentInfo.player
        if player and not player.allDead:
            log.warning('Player %r did not notice death', player.nick)
            player.sendResync()


class AgentInfo(object):
    '''
    Used by a local game to keep track of information about a connected Agent.
    '''

    def __init__(self, game, agent):
        self.game = game
        self.agent = agent
        self.world = game.world
        self.player = None
        self.pendingExpectedNotice = None
        self.expectedNotice = None

        self.currentDelay = INITIAL_ASSUMED_LATENCY
        self.recentDelay = -1
        self.idealDelay = int(0.5 * INITIAL_ASSUMED_LATENCY)
        self.delayedCallQueue = []

    def requestFromAgent(self, msg):
        '''
        When we receive a request from an agent, we first check to see if this
        request is supposed to occur at a specific time. If so, we delay the
        message until that time.
        '''
        msg.tracePoint(self, 'requestFromAgent')
        if msg.timestampedPlayerRequest:
            measuredDelay = (self.world.lastTickId - msg.tickId) % TICK_LIMIT
            if measuredDelay > LAG_THRESHOLD:
                adjustedDelay = measuredDelay + LAG_BUFFER
            else:
                adjustedDelay = measuredDelay

            forceUpdate = False
            if __debug__ and globaldebug.enabled:
                adjustedDelay = max(adjustedDelay, globaldebug.forceDelay)
                if globaldebug.forceDelay > self.currentDelay:
                    forceUpdate = True
            self.recentDelay = max(self.recentDelay, adjustedDelay)

            if measuredDelay > self.currentDelay or forceUpdate:
                self.currentDelay = adjustedDelay
                if isinstance(msg, ResyncAcknowledgedMsg):
                    self.passRequestToGame(
                        msg, delay=(adjustedDelay - measuredDelay))
                elif self.player:
                    self.player.sendResync(
                        reason='Your latency just spiked to %.2f s RTT' % (
                            measuredDelay * TICK_PERIOD), error=True)
                self.agent.messageToAgent(DelayUpdatedMsg(self.currentDelay))
            else:
                self.passRequestToGame(
                    msg, delay=(self.currentDelay - measuredDelay))
        else:
            self.passRequestToGame(msg)

    def passRequestToGame(self, msg, delay=0):
        msg.tracePoint(self, 'passRequestToGame')
        self.addCallbackAfterDelay(
            delay, self.game.dispatchDelayedRequest, [self.agent, msg])

    def addCallbackAfterDelay(self, delay, function, args=()):
        if delay == 0:
            function(*args)
        else:
            while len(self.delayedCallQueue) < delay:
                self.delayedCallQueue.append([])
            self.delayedCallQueue[delay - 1].append((function, args))

    def updateDelays(self):
        self.idealDelay, self.recentDelay = self.recentDelay, -1

    def tick(self):
        if self.player:
            if __debug__ and globaldebug.enabled:
                if globaldebug.localPlayerId == self.player.id:
                    globaldebug.localPlayerDelay = self.currentDelay
            static = self.player.willNotChangeOnNextTick()
        else:
            static = False

        if self.idealDelay < 0 and self.recentDelay < 0:
            # We have not seen any recent timed requests so we don't know how
            # much this agent is really lagging by.
            return

        idealDelay = max(self.idealDelay, self.recentDelay, 0)
        if static:
            changed = False
            while idealDelay < self.currentDelay:
                if self.delayedCallQueue and self.delayedCallQueue[0]:
                    break
                log.debug(
                    'Catching up one frame of player lag (%s)',
                    self.player.nick if self.player else '-')
                if self.delayedCallQueue:
                    self.delayedCallQueue.pop(0)
                changed = True
                self.currentDelay -= 1
            if changed:
                self.agent.messageToAgent(DelayUpdatedMsg(self.currentDelay))

        if self.delayedCallQueue:
            for function, args in self.delayedCallQueue.pop(0):
                function(*args)

        if self.pendingExpectedNotice:
            self.expectedNotice = self.pendingExpectedNotice
            self.pendingExpectedNotice = None
            self.addCallbackAfterDelay(
                self.currentDelay + 1, self.expectedNotice)

    def givePlayer(self, player):
        '''
        Called when this agent is being given control of the specified player.
        '''
        assert self.player is None
        self.player = player
        player.onDied.addListener(self.playerDied)
        player.onAllDead.addListener(self.playerAllDead)

        userTitle = self.world.uiOptions.defaultUserTitle
        userInfo = self.world.uiOptions.defaultUserInfo
        botGoal = self.world.uiOptions.defaultBotGoal
        self.agent.messageToAgent(
            UpdateGameInfoMsg.build(userTitle, userInfo, botGoal))

    def takePlayer(self):
        if not self.player:
            return
        self.player.onDied.removeListener(self.playerDied)
        self.player.onAllDead.removeListener(self.playerAllDead)
        self.player = None

    def playerDied(self, *args, **kwargs):
        if self.expectedNotice:
            self.expectedNotice.cancel()
            self.expectedNotice = None
        self.pendingExpectedNotice = ExpectedPlayerToNoticeDeath(self)

    def playerAllDead(self):
        if self.expectedNotice:
            self.expectedNotice.cancel()
            self.expectedNotice = None


class RemoteGame(Game, Node):
    '''
    Represents a game that is running on a remote server. This game object
    maintains the current state of the Universe based on messages from the
    server.
    '''

    def __init__(self, layoutDatabase, *args, **kwargs):
        world = Universe(layoutDatabase)
        super(RemoteGame, self).__init__(world, *args, **kwargs)
        self.agentIds = {}
        self.agentById = {}

    def connected(self, settings):
        self.world.restoreEverything(settings)

    @defer.inlineCallbacks
    def addAgent(self, agent, user=None, authTag=0):
        assert agent not in self.agentIds
        agentId = yield self.hub.connectNewAgent(authTag=authTag)
        self.agentIds[agent] = agentId
        self.agentById[agentId] = agent

    def detachAgent(self, agent):
        if agent in self.agentIds:
            self.hub.disconnectAgent(self.agentIds[agent])

    def agentRequest(self, agent, msg):
        '''
        Called by an agent with an AgentRequest message that it wants to
        request.
        '''
        msg.tracePoint(self, 'agentRequest')
        if agent not in self.agentIds:
            log.warning('%r: got agentRequest for unconnected agent', self)
            return
        self.hub.sendRequestToGame(self.agentIds[agent], msg)

    def gotServerCommand(self, msg):
        '''
        Called when a server command is received from the network.
        '''
        msg.tracePoint(self, 'gotServerCommand')
        self.world.consumeMsg(msg)
        self.onServerCommand(msg)

    def gotMessageToAgent(self, agentId, msg):
        msg.tracePoint(self, 'gotMessageToAgent')
        agent = self.agentById[agentId]
        agent.messageToAgent(msg)

    def agentDisconnected(self, agentId):
        agent = self.agentById[agentId]
        del self.agentIds[agent]
        del self.agentById[agentId]
        agent.messageToAgent(ConnectionLostMsg())


class PlayerConsistencyVerifier(object):
    '''
    This class exists entirely for debugging. When VERIFY_PLAYER_CONSISTENCY is
    true this class is used much like a ReplayRecorder, but it checks that
    player states in the "replay" match in the real world.
    '''
    dumpStates = True

    def __init__(self, localGame):
        self.realGame = localGame
        self.world = localGame.world

        self.replayGame = RemoteGame(localGame.layoutDatabase)
        self.replayGame.connected(self.world.dumpEverything())

        self.waitingMsg = None
        self.preRealState = None
        self.preReplayState = None
        self.prevInconsistent = False

    def preMessage(self, msg):
        self.resolveWaiting(None)

        self.waitingMsg = msg
        self.preRealState, self.preReplayState = self.getStates()

    def postMessage(self, msg):
        self.replayGame.gotServerCommand(msg)
        self.resolveWaiting(msg)

    def getStates(self):
        real = {p.id: p.dump() for p in self.realGame.world.players}
        replay = {p.id: p.dump() for p in self.replayGame.world.players}
        return real, replay

    def resolveWaiting(self, msg):
        if self.waitingMsg is None:
            if msg is not None:
                log.error(
                    'RECEIVED .postMessage() WITHOUT .preMessage: %s', msg)
            return

        waitingMsg, self.waitingMsg = self.waitingMsg, None
        preRealState, self.preRealState = self.preRealState, None
        preReplayState, self.preReplayState = self.preReplayState, None

        if waitingMsg is not msg:
            if preRealState != preReplayState:
                log.error('INCONSISTENCY BEFORE %s', waitingMsg)
                if self.dumpStates:
                    self.dumpInconsistency(preRealState, preReplayState)
            log.error(
                'DID NOT SEE MATCHING .postMessage() CALL for %s', waitingMsg)

            if msg is not None:
                log.error(
                    'RECEIVED .postMessage() WITHOUT .preMessage: %s', msg)
            return

        postRealState, postReplayState = self.getStates()
        inconsistentPre = (preRealState != preReplayState)
        inconsistentPost = (postRealState != postReplayState)

        if not inconsistentPre:
            if not inconsistentPost:
                if self.prevInconsistent:
                    log.error('INCONSISTENCY RESOLVED BEFORE %s', msg)
            else:
                log.error('INCONSISTENCY INTRODUCED IN %s', msg)
                if self.dumpStates:
                    self.dumpInconsistency(postRealState, postReplayState)
        elif inconsistentPost:
            if not self.prevInconsistent:
                log.error('INCONSISTENCY INTRODUCED BEFORE %s', msg)
                if self.dumpStates:
                    self.dumpInconsistency(preRealState, preReplayState)
        else:
            log.error('INCONSISTENCY RESOLVED IN %s', msg)
            if self.dumpStates:
                self.dumpInconsistency(preRealState, preReplayState)

        self.prevInconsistent = inconsistentPost

    def dumpInconsistency(self, realState, replayState):
        import pprint

        missingInReal = set(replayState) - set(realState)
        missingInReplay = set(realState) - set(replayState)
        if missingInReal:
            log.error('  not present on server: %r', missingInReal)
        if missingInReplay:
            log.error('  not present in replay: %r', missingInReplay)

        for playerId in realState:
            if playerId not in replayState:
                continue
            realPlayerState = realState[playerId]
            replayPlayerState = replayState[playerId]
            if realPlayerState != replayPlayerState:
                log.error('   === server ===')
                log.error(pprint.pformat(realPlayerState))
                log.error('   === replay ===')
                log.error(pprint.pformat(replayPlayerState))
                log.error('   ==============')

