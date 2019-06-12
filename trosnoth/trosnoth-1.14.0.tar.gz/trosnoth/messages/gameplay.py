import logging

from trosnoth.const import (
    PRIVATE_CHAT, TEAM_CHAT, OPEN_CHAT, RESYNC_IN_PROGRESS_REASON,
    GAME_NOT_STARTED_REASON, ALREADY_ALIVE_REASON, BE_PATIENT_REASON,
    ENEMY_ZONE_REASON, FROZEN_ZONE_REASON, DEFAULT_RESYNC_MESSAGE,
    DEFAULT_COIN_VALUE, PHANTOM_STATE, MAX_EMOTE,
)
from trosnoth.messages.base import (
    AgentRequest, ServerCommand, ServerResponse, ClientCommand,
)
from trosnoth.model.universe_base import NO_PLAYER, NO_SHOT
from trosnoth.utils import globaldebug

log = logging.getLogger(__name__)


class TickMsg(ServerCommand):
    idString = b'tick'
    fields = ('tickId',)
    packspec = 'H'


class TaggingZoneMsg(ServerCommand):
    idString = b'Tag!'
    fields = 'zoneId', 'playerId', 'teamId'
    packspec = 'Icc'


class CreateCollectableCoinMsg(ServerCommand):
    idString = b'StCr'
    fields = 'coinId', 'xPos', 'yPos', 'xVel', 'yVel', 'value'
    packspec = 'cffffI'
    value = DEFAULT_COIN_VALUE


class RemoveCollectableCoinMsg(ServerCommand):
    idString = b'StCo'
    fields = 'coinId'
    packspec = 'c'


class BasePlayerUpdate(ServerCommand):
    '''
    attached may be:
        'f' - falling
        'g' - on ground
        'l' - on wall to left of player
        'r' - on wall to right of player
    '''
    fields = (
        'playerId', 'xPos', 'yPos', 'xVel', 'yVel', 'angle', 'ghostThrust',
        'jumpTime', 'gunReload', 'respawn', 'coins', 'health',
        'resync', 'leftKey', 'rightKey', 'jumpKey', 'downKey',
        'ignoreLeft', 'ignoreRight', 'ignoreJump', 'ignoreDown',
        'gripCountDown', 'grabbedSurfaceAngle', 'emoteId', 'emoteTicks',
        'grapplingHookState',
    )
    packspec = 'cfffffffffIB?????????ffII*'


class PlayerUpdateMsg(BasePlayerUpdate):
    idString = b'PlUp'

    def applyOrderToWorld(self, world):
        player = world.getPlayer(self.playerId)
        player.applyPlayerUpdate(self)


class ResyncPlayerMsg(BasePlayerUpdate):
    '''
    Carries the same information as PlayerUpdateMsg, but is sent only to the
    player in question to tell them to reposition their player and acknowledge
    the resync.
    '''
    idString = b'Sync'
    isControl = True


class DelayUpdatedMsg(ServerResponse):
    idString = b'Dlay'
    fields = 'delay'
    packspec = 'f'

    def applyOrderToLocalState(self, localState, world):
        localState.serverDelay = self.delay


class CheckSyncMsg(AgentRequest):
    '''
    Sent periodically by the client to confirm that it's idea of where its
    player is matches the server's idea.
    '''
    idString = b'syn?'
    fields = 'tickId', 'xPos', 'yPos', 'yVel'
    packspec = 'Hfff'
    timestampedPlayerRequest = True

    def serverApply(self, game, agent):
        if agent.player is None or agent.player.resyncing:
            return

        x, y = agent.player.pos
        if (
                abs(x - self.xPos) >= 1
                or abs(y - self.yPos) >= 1
                or abs(agent.player.yVel - self.yVel) >= 1):
            log.info('Player out of sync: %s', agent.player)
            agent.player.sendResync()


class ResyncAcknowledgedMsg(ClientCommand):
    idString = b'Synd'
    fields = (
        'tickId', 'xPos', 'yPos', 'yVel', 'angle', 'ghostThrust',
        'health', 'playerId',
    )
    packspec = 'HfffffBc'
    timestampedPlayerRequest = True
    playerId = NO_PLAYER

    def serverApply(self, game, agent):
        if agent.player is None:
            return
        if not agent.player.resyncing:
            log.warning(
                'Received unexpected resync acknowledgement from %s',
                agent.player)
            # If we get a resync acknowledgement when we're not resyncing
            # something is up and we need to resync again.
            agent.player.sendResync()
            return

        if not agent.player.checkResyncAcknowledgement(self):
            # If the values the client is acknowledging don't match up to where
            # we think the client is at, it's probably because another resync /
            # a game reset has happened, so we need to wait for the second
            # acknowledgement.
            return

        self.playerId = agent.player.id
        game.sendServerCommand(self)

    def applyRequestToLocalState(self, localState):
        localState.player.resyncing = False

    def applyOrderToWorld(self, world):
        player = world.getPlayer(self.playerId)
        player.resyncing = False


class RespawnMsg(ServerCommand):
    idString = b'Resp'
    fields = 'playerId', 'zoneId'
    packspec = 'cI'


class RespawnRequestMsg(AgentRequest):
    idString = b'Resp'
    fields = 'tickId'
    packspec = 'H'
    timestampedPlayerRequest = True

    def clientValidate(self, localState, world, sendResponse):
        if localState.player is None:
            return False
        code = self.getInvalidCode(localState.player, world)
        if code is None:
            return True

        sendResponse(CannotRespawnMsg(code))
        return False

    def applyRequestToLocalState(self, localState):
        localState.player.respawn()

    def serverApply(self, game, agent):
        # Since the client has already applied the respawn before the message
        # gets to the server, any invalid respawn necessitates a resync.
        if not agent.player or agent.player.resyncing:
            return
        code = self.getInvalidCode(agent.player, game.world)
        if code is None:
            game.sendServerCommand(
                RespawnMsg(agent.player.id, agent.player.getZone().id))
        else:
            if code == ENEMY_ZONE_REASON:
                reason = 'You no longer own the zone.'
                error = True
            else:
                reason = DEFAULT_RESYNC_MESSAGE
                error = False
            agent.player.sendResync(reason=reason, error=error)

    def getInvalidCode(self, player, world):
        '''
        Returns None if this respawn request seems valid, a reason code
        otherwise.
        '''
        if player.resyncing:
            return RESYNC_IN_PROGRESS_REASON
        if not world.abilities.respawn:
            return GAME_NOT_STARTED_REASON
        if not player.dead:
            return ALREADY_ALIVE_REASON
        if player.timeTillRespawn > 0:
            return BE_PATIENT_REASON
        if not player.inRespawnableZone():
            return ENEMY_ZONE_REASON
        if player.getZone().frozen:
            return FROZEN_ZONE_REASON
        return None


class CannotRespawnMsg(ServerResponse):
    '''
    reasonId may be:
        P: game hasn't started
        A: Already Alive
        T: Can't respawn yet
        E: In enemy zone
        F: Frozen Zone

    Note that this message actually always originates on the client rather than
    the server, so it never needs to travel on the network.
    '''
    idString = b'NoRs'
    fields = 'reasonId'
    packspec = 'c'


class UpdatePlayerStateMsg(ClientCommand):
    idString = b'Pres'
    fields = 'value', 'tickId', 'playerId', 'stateKey'
    packspec = 'bHc*'
    timestampedPlayerRequest = True
    playerId = NO_PLAYER

    def clientValidate(self, localState, world, sendResponse):
        if not localState.player:
            return False
        return True

    def applyRequestToLocalState(self, localState):
        localState.player.updateState(self.stateKey, self.value)

    def serverApply(self, game, agent):
        if not agent.player or agent.player.resyncing:
            return
        self.playerId = agent.player.id
        game.sendServerCommand(self)

    def applyOrderToWorld(self, world):
        player = world.getPlayer(self.playerId)
        if player:
            player.updateState(self.stateKey, self.value)


class GrapplingHookMsg(ClientCommand):
    idString = b'Hook'
    fields = 'active', 'tickId', 'playerId'
    packspec = 'bHc'
    timestampedPlayerRequest = True
    playerId = NO_PLAYER

    def clientValidate(self, localState, world, sendResponse):
        return self.validate(localState.player)

    def validate(self, player):
        if not player:
            return False
        if player.dead or not player.canMove:
            return False
        hook = player.getGrapplingHook()
        if self.active and hook.isActive():
            return False
        if not self.active and not hook.isActive():
            return False
        return True

    def applyRequestToLocalState(self, localState):
        localState.player.getGrapplingHook().setState(self.active)

    def serverApply(self, game, agent):
        if not agent.player or agent.player.resyncing:
            return
        if agent.player.allDead or not agent.player.canMove:
            agent.player.sendResync()
            return
        if not self.validate(agent.player):
            return

        self.playerId = agent.player.id
        game.sendServerCommand(self)

    def applyOrderToWorld(self, world):
        player = world.getPlayer(self.playerId)
        if player and not player.allDead:
            player.getGrapplingHook().setState(self.active)


class AimPlayerAtMsg(ClientCommand):
    idString = b'Aim@'
    fields = 'angle', 'thrust', 'tickId', 'playerId'
    packspec = 'ffHc'
    timestampedPlayerRequest = True
    playerId = NO_PLAYER

    def applyRequestToLocalState(self, localState):
        localState.player.lookAt(self.angle, self.thrust)

    def serverApply(self, game, agent):
        if agent.player is None or agent.player.resyncing:
            return
        self.playerId = agent.player.id
        game.sendServerCommand(self)

    def applyOrderToWorld(self, world):
        player = world.getPlayer(self.playerId)
        if player:
            player.lookAt(self.angle, self.thrust)


class ShootMsg(AgentRequest):
    idString = b'shot'
    fields = 'tickId', 'localId'
    packspec = 'HH'
    localId = 0
    timestampedPlayerRequest = True

    def clientValidate(self, localState, world, sendResponse):
        if not world.canShoot():
            return False
        if not localState.player.canShoot():
            return False
        return True

    def applyRequestToLocalState(self, localState):
        self.localId = localState.shotFired()

    def serverApply(self, game, agent):
        if not game.world.canShoot():
            return
        if agent.player is None or agent.player.resyncing:
            return
        if not agent.player.canShoot():
            return
        if __debug__ and globaldebug.enabled:
            if (
                    globaldebug.shotLimit and
                    len(game.world.shotWithId) >= globaldebug.shotLimit):
                # When debugging shot physics, limit number of shots
                return

        xpos, ypos = agent.player.pos
        if agent.player.shoxwave:
            game.sendServerCommand(
                FireShoxwaveMsg(agent.player.id, xpos, ypos))
        else:
            shotId = game.idManager.newShotId()
            if shotId is not None:
                game.sendServerCommand(
                    ShotFiredMsg(agent.player.id, shotId, self.localId))


class ShotFiredMsg(ServerCommand):
    '''
    id manager -> agents
    '''
    idString = b'SHOT'
    fields = 'playerId', 'shotId', 'localId'
    packspec = 'cIH'

    def applyOrderToLocalState(self, localState, world):
        if localState.player and self.playerId == localState.player.id:
            localState.matchShot(self.localId, self.shotId)


class FireShoxwaveMsg(ServerCommand):
    '''
    id manager -> agents
    '''
    idString = b'Shox'
    fields = 'playerId', 'xpos', 'ypos'
    packspec = 'cff'


class PlayerHitMsg(ServerCommand):
    '''
    To be perfectly consistent, even in events involving randomness,
    all hits to players are mediated by the server.
    '''
    idString = b'HitP'
    fields = 'playerId', 'hitKind', 'hitpoints', 'hitterId', 'shotId'
    packspec = 'ccBcI'
    hitpoints = 1
    hitterId = NO_PLAYER
    shotId = NO_SHOT

    def applyOrderToWorld(self, world):
        player = world.getPlayer(self.playerId)
        if not player:
            return

        hitter = world.getPlayer(self.hitterId)
        player.hit(self.hitpoints, hitter, self.hitKind)

        if self.shotId:
            shot = world.getShot(self.shotId)
            shot.hitPlayer(player, self.hitpoints)

    def applyOrderToLocalState(self, localState, world):
        player = localState.player
        if player and self.playerId == player.id:
            hitter = world.getPlayer(self.hitterId)
            player.hit(self.hitpoints, hitter, self.hitKind)


class PlayerAllDeadMsg(ClientCommand):
    '''
    After a player dies, but before its client realises it, the ghost still
    moves like a live player. When the client first realises that its player is
    dead, it sends PlayerAllDeadMsg to the server, which checks it, then
    braodcasts to all clients so that the ghost can start moving like a normal
    ghost.
    '''

    idString = b'PDed'
    fields = 'tickId', 'playerId'
    packspec = 'Hc'
    timestampedPlayerRequest = True

    playerId = NO_PLAYER

    def applyRequestToLocalState(self, localState):
        localState.player.makeAllDead()

    def serverApply(self, game, agent):
        player = agent.player
        if not player or player.resyncing:
            return

        if player.lifeState != PHANTOM_STATE:
            agent.player.sendResync()
            return

        self.playerId = agent.player.id
        game.sendServerCommand(self)

    def applyOrderToWorld(self, world):
        player = world.getPlayer(self.playerId)
        if player:
            player.makeAllDead()


####################
# Communication
####################

class ChatFromServerMsg(ServerCommand):
    idString = b'ahoy'
    fields = 'error', 'text'
    packspec = '?*'


class ChatMsg(ClientCommand):
    '''
    Valid values for kind are defined in trosnoth.const.
    '''
    idString = b'chat'
    fields = 'kind', 'targetId', 'playerId', 'text'
    packspec = 'ccc*'
    playerId = NO_PLAYER
    targetId = NO_PLAYER

    def serverApply(self, game, agent):
        if agent.player is None:
            return

        if self.kind == TEAM_CHAT:
            if not agent.player.isFriendsWithTeam(
                    game.world.getTeam(self.targetId)):
                # Cannot send to opposing team.
                return
        elif self.kind == PRIVATE_CHAT:
            if game.world.getPlayer(self.targetId) is None:
                return
        elif self.kind != OPEN_CHAT:
            log.warning('unknown chat kind: %r', self.kind)
            return

        self.playerId = agent.player.id
        game.sendServerCommand(self)

    def applyOrderToWorld(self, world):
        sender = world.getPlayer(self.playerId)
        text = self.text.decode()
        if self.kind == OPEN_CHAT:
            world.onOpenChatReceived(text, sender)
        elif self.kind == PRIVATE_CHAT:
            target = world.getPlayer(self.targetId)
            target.onPrivateChatReceived(text, sender)
        elif self.kind == TEAM_CHAT:
            team = world.getTeam(self.targetId)
            world.onTeamChatReceived(team, text, sender)

    def applyOrderToLocalState(self, localState, world):
        if self.kind == PRIVATE_CHAT:
            player = localState.player
            if player and player.id == self.targetId:
                sender = world.getPlayer(self.playerId)
                text = self.text.decode()
                player.onPrivateChatReceived(text, sender)


class EmoteMsg(ServerCommand):
    idString = b'Emot'
    fields = 'playerId', 'emoteId'
    packspec = 'cI'

    def applyOrderToWorld(self, world):
        player = world.getPlayer(self.playerId)
        player.doEmote(self.emoteId)


class EmoteRequestMsg(AgentRequest):
    idString = b'NaNa'
    fields = 'tickId', 'emoteId'
    packspec = 'HI'
    timestampedPlayerRequest = True

    def clientValidate(self, localState, world, sendResponse):
        return self.isValid(localState.player, world)

    def isValid(self, player, world):
        if player is None or player.resyncing:
            return False

        if player.allDead or not player.canMove:
            return False

        if self.emoteId < 0 or self.emoteId > MAX_EMOTE:
            return False

        return True

    def serverApply(self, game, agent):
        if agent.player is None or agent.player.resyncing:
            return False

        if not self.isValid(agent.player, game.world):
            agent.player.sendResync(reason='Invalid emote request')
            return

        game.sendServerCommand(EmoteMsg(agent.player.id, self.emoteId))

    def applyRequestToLocalState(self, localState):
        localState.player.doEmote(self.emoteId)

