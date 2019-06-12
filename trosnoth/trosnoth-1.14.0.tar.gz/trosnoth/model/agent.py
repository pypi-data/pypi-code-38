import logging

from twisted.internet import reactor

from trosnoth.const import (
    TICK_PERIOD, INITIAL_ASSUMED_LATENCY, BOT_GOAL_NONE, HEAD_CUEBALL,
)
from trosnoth.messages import (
    JoinRequestMsg, TickMsg, ResyncPlayerMsg, UpdatePlayerStateMsg,
    AimPlayerAtMsg, UpgradeApprovedMsg, PlayerHasUpgradeMsg, ShootMsg,
    CheckSyncMsg, WorldResetMsg, BuyUpgradeMsg, GrapplingHookMsg,
    PlayerAllDeadMsg,
)
from trosnoth.model.shot import LocalShot, LocalGrenade
from trosnoth.model.trosball import LocalTrosball
from trosnoth.model.upgrades import Grenade
from trosnoth.utils.event import Event
from trosnoth.utils.message import MessageConsumer

log = logging.getLogger(__name__)

SYNC_CHECK_PERIOD = 3 / TICK_PERIOD


class Agent(object):
    '''
    Base class for things which can be connected to a Game using Game.addAgent.
    This may represent a user interface, an AI player, someone connecting over
    the network, or anything else that wants to receive interact with the game.
    '''

    def __init__(self, game, *args, **kwargs):
        super(Agent, self).__init__(*args, **kwargs)
        self.game = game
        self.user = None
        self.player = None
        self.onPlayerSet = Event([])
        self.stopped = False
        self.botPlayerAllowed = False
        self.botRequestFromLevel = False

    def allowBotPlayer(self, fromLevel):
        self.botPlayerAllowed = True
        self.botRequestFromLevel = fromLevel

    def stop(self):
        '''
        Disconnects this agent from things that it's subscribed to and stops
        any active timed or looping calls.
        '''
        self.stopped = True

    def detached(self):
        '''
        Called after this agent has been detached from a Game.
        '''
        pass

    def setPlayer(self, player):
        '''
        Called by the connected Game object when we are given authority to
        control the specified player. Also called with player=None when we no
        longer have the authority to control any player.
        '''
        self.player = player
        reactor.callLater(0, self.onPlayerSet.execute)

    def messageToAgent(self, msg):
        '''
        Called by the connected Game object when there is a message
        specifically for this Agent (as opposed to a general game message).
        '''
        raise NotImplementedError(
            '%s.messageToAgent' % (self.__class__.__name__,))


class ConcreteAgent(Agent, MessageConsumer):
    '''
    Base class for Agents that actually represent the world (rather than
    proxying it through to the Network or some other agent).

    Note that a concrete agent is designed to represent only zero or one
    players.
    '''

    def __init__(self, *args, **kwargs):
        super(ConcreteAgent, self).__init__(*args, **kwargs)
        self.world = self.game.world
        self.localState = LocalState(self)
        self.lastPlayerAimSent = (None, None)
        self.nextSyncCheck = None
        self.alreadySendingRequest = False
        self.sendRequestQueue = []
        self.game.onServerCommand.addListener(self.gotServerCommand)

    def stop(self):
        super().stop()
        self.game.onServerCommand.removeListener(self.gotServerCommand)

    def gotServerCommand(self, msg):
        msg.tracePoint(self, 'gotServerCommand')
        self.consumeMsg(msg)

    def messageToAgent(self, msg):
        msg.tracePoint(self, 'messageToAgent')
        self.consumeMsg(msg)

    def sendRequest(self, msg):
        if self.stopped:
            log.error('Stopped agent trying to send %r: %s', msg, self)
            # log.error(''.join(traceback.format_stack()))
            return
        msg.tracePoint(self, 'sendRequest')

        self.sendRequestQueue.append(msg)
        if self.alreadySendingRequest:
            # The actual sending will be done in the parent's loop
            return

        self.alreadySendingRequest = True
        try:
            while self.sendRequestQueue:
                self.processSendRequestQueue()
        finally:
            self.alreadySendingRequest = False

    def processSendRequestQueue(self):
        msg = self.sendRequestQueue.pop(0)
        msg.tracePoint(self, 'processSendRequestQueue')

        if not msg.clientValidate(
                self.localState, self.world, self._validationResponse):
            msg.tracePoint(self, 'failed clientValidate')
            return
        msg.applyRequestToLocalState(self.localState)
        if isinstance(msg, AimPlayerAtMsg):
            # Special case: apply aim messages to the local state, but don't
            # indiscriminately send them to the server as they are mostly
            # cosmetic.
            return
        if isinstance(msg, (ShootMsg, GrapplingHookMsg)) or (
                isinstance(msg, BuyUpgradeMsg)
                and msg.upgradeType == Grenade.upgradeType):
            # Special case: before shooting make sure the server knows what
            # direction we are facing.
            self.maybeSendAimMsg(self.world.lastTickId)
        reactor.callLater(0, self.game.agentRequest, self, msg)

    def _validationResponse(self, msg):
        self.consumeMsg(msg)

    def defaultHandler(self, msg):
        msg.tracePoint(self, 'defaultHandler')
        msg.applyOrderToLocalState(self.localState, self.world)

    def setPlayer(self, player):
        super(ConcreteAgent, self).setPlayer(player)
        if player:
            self.localState.playerJoined(player)
            self.resyncLocalPlayer({})
        elif self.player:
            self.localState.lostPlayer()

    @WorldResetMsg.handler
    def handle_WorldResetMsg(self, msg):
        if self.player is not None:
            oldKeyState = dict(self.localState.player._state)
            self.localState.refreshPlayer()
            self.resyncLocalPlayer(oldKeyState)

    @TickMsg.handler
    def handle_TickMsg(self, msg):
        self.maybeSendAimMsg(tickId=max(0, msg.tickId - 1))
        self.localState.tick()

        player = self.localState.player
        now = self.world.getMonotonicTick()
        if player and self.nextSyncCheck <= now:
            self.nextSyncCheck = now + SYNC_CHECK_PERIOD
            self.sendRequest(CheckSyncMsg(
                self.world.lastTickId, player.pos[0],
                player.pos[1], player.yVel))

    def maybeSendAimMsg(self, tickId):
        '''
        Tell the server where the local player is facing.
        '''
        player = self.localState.player
        if player:
            lastAngle, lastThrust = self.lastPlayerAimSent
            if (
                    lastAngle != player.angleFacing or
                    lastThrust != player.ghostThrust):
                reactor.callLater(
                    0, self.game.agentRequest, self, AimPlayerAtMsg(
                        player.angleFacing, player.ghostThrust, tickId))
                self.lastPlayerAimSent = (
                    player.angleFacing, player.ghostThrust)

    @ResyncPlayerMsg.handler
    def handle_ResyncPlayerMsg(self, msg):
        oldKeyState = dict(self.localState.player._state)
        self.localState.player.applyPlayerUpdate(msg)
        self.resyncLocalPlayer(oldKeyState)

    def resyncLocalPlayer(self, oldKeyState):
        newKeyState = self.localState.player._state
        self.sendRequest(self.localState.player.buildResyncAcknowledgement())
        self.nextSyncCheck = self.world.getMonotonicTick() + SYNC_CHECK_PERIOD

        for key, value in list(oldKeyState.items()):
            if value != newKeyState[key]:
                self.sendRequest(UpdatePlayerStateMsg(
                    value, self.world.lastTickId, stateKey=key))

    @UpgradeApprovedMsg.handler
    def handle_UpgradeApprovedMsg(self, msg):
        self.sendRequest(PlayerHasUpgradeMsg(
            msg.upgradeType, self.world.lastTickId))

    def sendJoinRequest(
            self, teamId, nick, head=HEAD_CUEBALL, bot=False, fromLevel=False):
        if self.player is not None:
            raise RuntimeError('Already joined.')

        msg = JoinRequestMsg(teamId, nick=nick.encode(), bot=bot, head=head)
        if bot:
            msg.localBotRequest = True
        if fromLevel:
            msg.botRequestFromLevel = True

        self.sendRequest(msg)


class LocalState(object):
    '''
    Stores state information which a client wants to keep which do not need to
    wait for a round trip to the server. e.g. when a player moves, it should
    start moving on the local screen even before the server has received the
    message.
    '''

    LOCAL_ID_CAP = 1 << 16

    def __init__(self, agent):
        self.onGameInfoChanged = Event([])
        self.agent = agent
        self.world = agent.world
        self.player = None
        self.onShoxwave = Event()
        self.onAddLocalShot = Event()
        self.onRemoveLocalShot = Event()
        self.shotById = {}
        self.localShots = {}
        self.localGrenade = None
        self.localTrosball = None
        self.trosballResetCall = None
        self.nextLocalId = 1
        self.serverDelay = INITIAL_ASSUMED_LATENCY
        self.userTitle = ''
        self.userInfo = ()
        self.botGoal = BOT_GOAL_NONE
        self.unverifiedItems = []
        self.world.onShotRemoved.addListener(self.shotRemoved)
        self.pings = {}
        self.lastPingTime = None

    def gotPingTime(self, pingTime):
        self.lastPingTime = pingTime

    @property
    def shots(self):
        for shot in list(self.shotById.values()):
            yield shot
        for shot in list(self.localShots.values()):
            yield shot

    def playerJoined(self, player):
        # Create a shallow copy of the player object, and use it to simulate
        # movement before the server approves it.
        self.player = player.clone()

        player.onCoinsChanged.addListener(self.playerCoinsChanged)
        player.onGotTrosball.addListener(self.gotTrosball)
        self.player.onDied.addListener(self.projectionDied)

    def refreshPlayer(self):
        realPlayer = self.world.playerWithId[self.player.id]
        self.player.restore(realPlayer.dump())

    def playerCoinsChanged(self, oldCoins):
        player = self.world.getPlayer(self.player.id)
        self.player.coins = player.coins

    def gotTrosball(self):
        self.player.items.clear()

    def projectionDied(self, killer, deathType):
        for shot in list(self.localShots.values()):
            self.onRemoveLocalShot(shot)
        self.localShots.clear()
        self.agent.sendRequest(PlayerAllDeadMsg(self.world.lastTickId))

    def lostPlayer(self):
        realPlayer = self.world.getPlayer(self.player.id)
        if realPlayer:
            realPlayer.onCoinsChanged.removeListener(self.playerCoinsChanged)
            realPlayer.onGotTrosball.removeListener(self.gotTrosball)
        self.player.onDied.removeListener(self.projectionDied)
        self.player = None

    def shotFired(self):
        if self.player.shoxwave:
            self.onShoxwave()
            localId = 0
        else:
            localId = self.nextLocalId
            self.nextLocalId = (self.nextLocalId + 1) % self.LOCAL_ID_CAP
            self.localShots[localId] = shot = self.player.createShot(
                shotClass=LocalShot)
            self.onAddLocalShot(shot)
        self.player.weaponDischarged()
        return localId

    def matchShot(self, localId, shotId):
        if localId in self.localShots:
            shot = self.localShots.pop(localId)
            shot.realShotStarted = True
            self.shotById[shotId] = shot

    def shotRemoved(self, shotId, *args, **kwargs):
        if shotId in self.shotById:
            shot = self.shotById[shotId]
            del self.shotById[shotId]
            self.onRemoveLocalShot(shot)

    def grenadeLaunched(self):
        self.localGrenade = LocalGrenade(
            self, self.world, self.player, Grenade.totalTimeLimit)

    def matchGrenade(self):
        for grenade in self.world.grenades:
            if grenade.player.id == self.player.id:
                self.localGrenade.realShotStarted = True
                return

    def grenadeRemoved(self):
        self.localGrenade = None

    def trosballThrown(self):
        self.localTrosball = LocalTrosball(self.world)
        self.localTrosball.onRealShotCaughtUp.addListener(
            self.trosballCaughtUp)
        vel = self.world.trosballManager.getThrowVelocity(self.player)
        self.localTrosball.teleport(self.player.pos, vel)
        if self.trosballResetCall:
            self.trosballResetCall.cancel()
        self.trosballResetCall = self.world.callLater(2, self.revertTrosball)

    def matchTrosball(self):
        self.localTrosball.realShotStarted = True

    def trosballCaughtUp(self, sprite):
        self.revertTrosball()

    def revertTrosball(self):
        self.localTrosball = None
        if self.trosballResetCall:
            self.trosballResetCall.cancel()

    def tick(self):
        if self.player:
            self.player.reset()
            self.player.advance()

            if not self.player.dead:
                for unit in self.world.getCollectableUnits():
                    if unit.hitLocalPlayer:
                        continue
                    if unit.checkCollision(self.player, 0):
                        unit.collidedWithLocalPlayer(self.player)

        for shot in list(self.shotById.values()) + list(self.localShots.values()):
            shot.reset()
            shot.advance()
        if self.localGrenade:
            self.localGrenade.reset()
            self.localGrenade.advance()
        if self.localTrosball:
            self.localTrosball.reset()
            self.localTrosball.advance()

        for shotId, shot in list(self.shotById.items()):
            if shot.expired:
                del self.shotById[shotId]
                self.onRemoveLocalShot(shot)
        for localId, shot in list(self.localShots.items()):
            if shot.expired:
                del self.localShots[localId]
                self.onRemoveLocalShot(shot)

    def addUnverifiedItem(self, item):
        self.unverifiedItems.append(item)

    def discardUnverifiedItem(self, item):
        self.unverifiedItems.remove(item)

    def popUnverifiedItem(self):
        if self.unverifiedItems:
            return self.unverifiedItems.pop(0)
        return None
