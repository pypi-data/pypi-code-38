import logging

from trosnoth.const import (
    GAME_FULL_REASON, UNAUTHORISED_REASON, NICK_USED_REASON, BAD_NICK_REASON,
    USER_IN_GAME_REASON, ALREADY_JOINED_REASON, HEAD_LOCATIONS, HEAD_CUEBALL,
    HEAD_BOT,
)
from trosnoth.messages.base import (
    AgentRequest, ServerCommand, ServerResponse, ClientCommand,
)
from trosnoth.messages.special import PlayerHasElephantMsg
from trosnoth.model.universe_base import NEUTRAL_TEAM_ID, NO_PLAYER
from trosnoth.utils.netmsg import NetworkMessage

log = logging.getLogger(__name__)


####################
# Setup
####################

class InitClientMsg(NetworkMessage):
    idString = b'wlcm'
    fields = 'settings'
    packspec = '*'


class ConnectionLostMsg(ServerCommand):
    # Doesn't really originate on the server.
    fields = ()
    isControl = True
    packspec = ''

    def applyOrderToWorld(self, world):
        pass


class WorldResetMsg(ServerCommand):
    idString = b'rset'
    fields = 'settings'
    packspec = '*'
    pumpAllEvents = True


class ZoneStateMsg(ServerCommand):
    idString = b'ZnSt'
    fields = 'zoneId', 'teamId', 'dark'
    packspec = 'Icb'


class WorldLoadingMsg(ServerCommand):
    idString = b'wait'
    fields = 'loading'
    packspec = 'b'
    isControl = True

    def applyOrderToWorld(self, world):
        world.loading = self.loading


####################
# Game
####################

class ChangeNicknameMsg(ClientCommand):
    idString = b'Nick'
    fields = 'playerId', 'nickname'
    packspec = 'c*'

    def serverApply(self, game, agent):
        if not game.world.abilities.renaming:
            return
        p = game.world.getPlayer(self.playerId)
        if not p:
            return

        nick = self.nickname.decode()
        if not game.world.isValidNick(nick):
            return

        for player in game.world.players:
            if p != player and player.nick.lower() == nick.lower():
                # Nick in use.
                return

        if game.serverInterface:
            if game.serverInterface.checkUsername(nick) and (
                    p.user is None or nick.lower() != p.user.username):
                # Nick is someone else's username.
                return

        game.sendServerCommand(self)
        if p.user:
            p.user.setNick(nick)

    def applyOrderToWorld(self, world):
        player = world.getPlayer(self.playerId)
        if player:
            player.nick = self.nickname.decode()

    def applyOrderToLocalState(self, localState, world):
        player = localState.player
        if player and player.id == self.playerId:
            player.nick = self.nickname.decode()


class ChangeHeadMsg(ClientCommand):
    idString = b'Head'
    fields = 'playerId', 'head'
    packspec = 'cB'

    def serverApply(self, game, agent):
        if not game.world.abilities.renaming:
            return
        p = game.world.getPlayer(self.playerId)
        if not p:
            return

        if self.head not in HEAD_LOCATIONS:
            return
        if self.head == HEAD_BOT and not p.bot:
            return
        game.sendServerCommand(self)

    def applyOrderToWorld(self, world):
        player = world.getPlayer(self.playerId)
        if player:
            player.head = self.head

    def applyOrderToLocalState(self, localState, world):
        player = localState.player
        if player and player.id == self.playerId:
            player.head = self.head


class PlayerIsReadyMsg(ClientCommand):
    idString = b'Redy'
    fields = 'playerId', 'ready'
    packspec = 'c?'

    def serverApply(self, game, agent):
        game.sendServerCommand(self)

    def applyOrderToWorld(self, world):
        self.applyToPlayer(world.getPlayer(self.playerId))

    def applyOrderToLocalState(self, localState, world):
        player = localState.player
        if player and player.id == self.playerId:
            self.applyToPlayer(player)

    def applyToPlayer(self, player):
        player.readyToStart = self.ready


class SetPreferredTeamMsg(AgentRequest):
    idString = b'TmNm'
    fields = 'name'
    packspec = '*'

    MAX_TEAM_NAME_LENGTH = 30

    def serverApply(self, game, agent):
        if agent.player is None:
            return
        teamName = self.name.decode('utf-8')[:self.MAX_TEAM_NAME_LENGTH]
        game.sendServerCommand(PreferredTeamSelectedMsg(
            agent.player.id,
            teamName.encode()))


class PreferredTeamSelectedMsg(ServerCommand):
    idString = b'TmNm'
    fields = 'playerId', 'name'
    packspec = 'c*'

    def applyOrderToWorld(self, world):
        self.applyToPlayer(world.getPlayer(self.playerId))

    def applyOrderToLocalState(self, localState, world):
        player = localState.player
        if player and player.id == self.playerId:
            self.applyToPlayer(player)

    def applyToPlayer(self, player):
        player.preferredTeam = self.name.decode()


class SetPreferredSizeMsg(ClientCommand):
    idString = b'Size'
    fields = 'playerId', 'halfMapWidth', 'mapHeight'
    packspec = 'cBB'

    MAX_MAP_HEIGHT = 10
    MAX_HALF_WIDTH = 10

    def serverApply(self, game, agent):
        if game.world.getPlayer(self.playerId):
            halfMapWidth = min(self.halfMapWidth, self.MAX_HALF_WIDTH)
            mapHeight = min(self.mapHeight, self.MAX_MAP_HEIGHT)
            game.sendServerCommand(
                SetPreferredSizeMsg(self.playerId, halfMapWidth, mapHeight))

    def applyOrderToWorld(self, world):
        self.applyToPlayer(world.getPlayer(self.playerId))

    def applyOrderToLocalState(self, localState, world):
        player = localState.player
        if player and player.id == self.playerId:
            self.applyToPlayer(player)

    def applyToPlayer(self, player):
        player.preferredSize = (self.halfMapWidth, self.mapHeight)


class SetPreferredDurationMsg(ClientCommand):
    '''
    duration is in seconds.
    '''
    idString = b'Dr8n'
    fields = 'playerId', 'duration'
    packspec = 'cI'

    MAX_GAME_DURATION = 86400

    def serverApply(self, game, agent):
        if game.world.getPlayer(self.playerId):
            duration = min(self.duration, self.MAX_GAME_DURATION)
            game.sendServerCommand(
                SetPreferredDurationMsg(self.playerId, duration))

    def applyOrderToWorld(self, world):
        self.applyToPlayer(world.getPlayer(self.playerId))

    def applyOrderToLocalState(self, localState, world):
        player = localState.player
        if player and player.id == self.playerId:
            self.applyToPlayer(player)

    def applyToPlayer(self, player):
        player.preferredDuration = self.duration


class SetPreferredLevelMsg(ClientCommand):
    '''
    duration is in seconds.
    '''
    idString = b'Levl'
    fields = 'playerId', 'level'
    packspec = 'c*'

    def serverApply(self, game, agent):
        if game.world.getPlayer(self.playerId):
            try:
                self.getLevelClass(self.level)
            except KeyError:
                pass
            else:
                game.sendServerCommand(self)

    @staticmethod
    def getLevelClass(level):
        if level == b'standard':
            from trosnoth.levels.standard import StandardRandomLevel
            return StandardRandomLevel
        if level == b'trosball':
            from trosnoth.levels.trosball import RandomTrosballLevel
            return RandomTrosballLevel
        if level == b'catpigeon':
            from trosnoth.levels.catpigeon import CatPigeonLevel
            return CatPigeonLevel
        if level == b'free4all':
            from trosnoth.levels.freeforall import FreeForAllLevel
            return FreeForAllLevel
        if level == b'hunted':
            from trosnoth.levels.hunted import HuntedLevel
            return HuntedLevel
        if level == b'orbchase':
            from trosnoth.levels.orbchase import OrbChaseLevel
            return OrbChaseLevel
        if level == b'elephantking':
            from trosnoth.levels.elephantking import ElephantKingLevel
            return ElephantKingLevel
        if level == b'auto':
            return None
        raise KeyError('Unknown level key')

    def applyOrderToWorld(self, world):
        self.applyToPlayer(world.getPlayer(self.playerId))

    def applyOrderToLocalState(self, localState, world):
        player = localState.player
        if player and player.id == self.playerId:
            self.applyToPlayer(player)

    def applyToPlayer(self, player):
        player.preferredLevel = self.level


class SetGameModeMsg(ServerCommand):
    idString = b'Mode'
    fields = 'gameMode'
    packspec = '*'

    def applyOrderToWorld(self, world):
        world.setGameMode(self.gameMode.decode())


class SetGameSpeedMsg(ServerCommand):
    idString = b'Spee'
    fields = 'gameSpeed'
    packspec = 'f'

    def applyOrderToWorld(self, world):
        world.setGameSpeed(self.gameSpeed)


class SetTeamNameMsg(ServerCommand):
    idString = b'Team'
    fields = 'teamId', 'name'
    packspec = 'c*'

    def applyOrderToWorld(self, world):
        if self.teamId == NEUTRAL_TEAM_ID:
            world.rogueTeamName = self.name
        else:
            team = world.getTeam(self.teamId)
            team.teamName = self.name.decode('utf-8')


####################
# Players
####################

class AddPlayerMsg(ServerCommand):
    idString = b'NewP'
    fields = 'playerId', 'teamId', 'zoneId', 'dead', 'bot', 'head', 'nick'
    packspec = 'ccIbbB*'


class SetPlayerTeamMsg(ServerCommand):
    idString = b'PlTm'
    fields = 'playerId', 'teamId'
    packspec = 'cc'

    def applyOrderToWorld(self, world):
        player = world.getPlayer(self.playerId)
        player.team = world.getTeam(self.teamId)
        player.onTeamSet()

    def applyOrderToLocalState(self, localState, world):
        if localState.player and localState.player.id == self.playerId:
            localState.player.team = world.getTeam(self.teamId)
            localState.player.onTeamSet()


class RemovePlayerMsg(ServerCommand):
    idString = b'DelP'
    fields = 'playerId'
    packspec = 'c'

    def applyOrderToWorld(self, world):
        player = world.getPlayer(self.playerId)
        if player:
            world.delPlayer(player)


class JoinRequestMsg(AgentRequest):
    idString = b'Join'
    fields = 'teamId', 'bot', 'head', 'nick'
    packspec = 'cbB*'
    localBotRequest = False         # Intentionally not sent over wire.
    botRequestFromLevel = False     # Intentionally not sent over wire.

    def serverApply(self, game, agent):
        nick = self.nick.decode('utf-8')
        teamPlayerCounts = game.world.getTeamPlayerCounts()

        if agent.player is not None:
            agent.messageToAgent(CannotJoinMsg(ALREADY_JOINED_REASON))
            return

        if not game.world.isValidNick(nick):
            agent.messageToAgent(CannotJoinMsg(BAD_NICK_REASON))
            return

        allowBot = self.localBotRequest or agent.botPlayerAllowed
        if agent.user and not allowBot:
            if self.bot:
                agent.messageToAgent(CannotJoinMsg(UNAUTHORISED_REASON))
                return

            user = agent.user
            for player in game.world.players:
                if player.user == user:
                    agent.messageToAgent(CannotJoinMsg(USER_IN_GAME_REASON))
                    return
            if nick.lower() != user.username and game.serverInterface:
                if game.serverInterface.checkUsername(nick):
                    agent.messageToAgent(CannotJoinMsg(NICK_USED_REASON))
                    return
        else:
            user = None

        # Only check for duplicate nick after checking for auth-related errors.
        usedNicks = {player.nick.lower() for player in game.world.players}
        levelBot = self.botRequestFromLevel or agent.botRequestFromLevel
        if self.bot and not levelBot:
            if '-' in nick and nick.rsplit('-', 1)[-1].isdigit():
                base, number = nick.rsplit('-', 1)
                number = int(number)
            else:
                base = nick
                number = 1

            if 'Bot' not in base:
                base += 'Bot'

            nick = '{}-{}'.format(base, number)
            while nick.lower() in usedNicks:
                number += 1
                nick = '{}-{}'.format(base, number)
        else:
            if nick.lower() in usedNicks:
                agent.messageToAgent(CannotJoinMsg(NICK_USED_REASON))
                return

        if user:
            user.setNick(nick)

        if levelBot:
            teamId = self.teamId
        elif game.world.scenarioManager.level is None:
            # Delay until the level has been set
            game.world.onStartMatch.wait().addCallback(
                self._tryServerApplyAgain, game, agent)
            return
        else:
            preferredTeam = (
                game.world.getTeam(self.teamId) if self.teamId is not None
                else None)
            team = game.world.scenarioManager.level.getTeamToJoin(
                preferredTeam, user, self.bot)
            teamId = team.id if team is not None else NEUTRAL_TEAM_ID

            reason = game.world.scenarioManager.level.findReasonPlayerCannotJoin(
                game, teamId, user, self.bot)
            if reason is not None:
                agent.messageToAgent(CannotJoinMsg(reason))
                return

        playerId = game.idManager.newPlayerId()
        if playerId is None:
            agent.messageToAgent(CannotJoinMsg(GAME_FULL_REASON))
            return

        head = self.head
        if head not in HEAD_LOCATIONS:
            head = HEAD_CUEBALL
        elif head == HEAD_BOT and not self.bot:
            head = HEAD_CUEBALL

        zoneId = game.world.selectZoneForTeam(teamId).id
        game.sendServerCommand(AddPlayerMsg(
            playerId, teamId, zoneId, True, self.bot, head,
            nick.encode('utf-8')))
        player = game.world.getPlayer(playerId)
        game.joinSuccessful(agent, playerId)
        if player.isElephantOwner():
            game.world.sendServerCommand(PlayerHasElephantMsg(playerId))

        if game.world.botManager:
            game.world.botManager.playerAdded(player)

    def _tryServerApplyAgain(self, eventArgs, game, agent):
        self.serverApply(game, agent)


class CannotJoinMsg(ServerResponse):
    '''
    Valid reasonId options are defined in trosnoth.const.
    '''
    idString = b'NotP'
    fields = 'reasonId'
    packspec = 'c'


class SetAgentPlayerMsg(ServerCommand):
    '''
    Send back to the agent which requested to join if the join has succeeded.

    This is not a control message, because we only want the successful join to
    be delivered after the player has been added to the universe.
    '''
    idString = b'OwnP'
    fields = 'playerId'
    packspec = 'c'

    def applyOrderToLocalState(self, localState, world):
        player = world.getPlayer(self.playerId)
        assert self.playerId == NO_PLAYER or player is not None
        localState.agent.setPlayer(player)


class AgentDetachedMsg(ServerCommand):
    idString = b'loos'
    fields = ()
    packspec = ''

    def applyOrderToLocalState(self, localState, world):
        localState.agent.detached()

