from functools import partial
import logging
import random
import pygame

from trosnoth.const import (
    TROSBALL_DEATH_HIT, OFF_MAP_DEATH_HIT, OPEN_CHAT, PRIVATE_CHAT, TEAM_CHAT,
    NOT_ENOUGH_COINS_REASON, PLAYER_DEAD_REASON, CANNOT_REACTIVATE_REASON,
    GAME_NOT_STARTED_REASON, TOO_CLOSE_TO_EDGE_REASON,
    TOO_CLOSE_TO_ORB_REASON, NOT_IN_DARK_ZONE_REASON, INVALID_UPGRADE_REASON,
    DISABLED_UPGRADE_REASON, ALREADY_ALIVE_REASON, BE_PATIENT_REASON,
    ENEMY_ZONE_REASON, FROZEN_ZONE_REASON, TICK_PERIOD, BOMBER_DEATH_HIT,
    ACTION_CLEAR_UPGRADE,
)
from trosnoth.gui.framework import framework, hotkey, console
from trosnoth.gui.framework.elements import (
    TextElement, SolidRect,
)
from trosnoth.gui.framework.collapsebox import CollapseBox
from trosnoth.gui import keyboard
from trosnoth.gui.common import (
    Region, Screen, Location, Canvas, PaddedRegion, ScaledScalar,
)

from trosnoth.gamerecording.achievementlist import availableAchievements

from trosnoth.model.agent import ConcreteAgent
from trosnoth.model.universe_base import NEUTRAL_TEAM_ID, NO_PLAYER

from trosnoth.trosnothgui.ingame import viewManager
from trosnoth.trosnothgui.ingame.replayInterface import ViewControlInterface
from trosnoth.trosnothgui.ingame.joincontroller import JoinGameController
from trosnoth.trosnothgui.ingame.detailsInterface import DetailsInterface
from trosnoth.trosnothgui.ingame.playerInterface import PlayerInterface

from trosnoth import keymap

from trosnoth.data import user, getPath

from trosnoth.utils import globaldebug
from trosnoth.utils.math import distance
from trosnoth.utils.event import Event
from trosnoth.utils.twist import WeakCallLater, WeakLoopingCall

from trosnoth.messages import (
    TaggingZoneMsg, ChatFromServerMsg, ChatMsg, PingMsg,
    ShotFiredMsg, RespawnMsg, CannotRespawnMsg, TickMsg,
    CannotJoinMsg, AddPlayerMsg, PlayerHasUpgradeMsg, RemovePlayerMsg,
    PlayerCoinsSpentMsg, CannotBuyUpgradeMsg, ConnectionLostMsg,
    AchievementUnlockedMsg, SetPlayerTeamMsg, PlaySoundMsg,
    PlayerHasElephantMsg, FireShoxwaveMsg, AwardPlayerCoinMsg,
    PlayerHasTrosballMsg, UpgradeChangedMsg,
)

from twisted.internet import defer

log = logging.getLogger(__name__)


class GameInterface(framework.CompoundElement, ConcreteAgent):
    '''Interface for when we are connected to a game.'''

    achievementDefs = availableAchievements

    def __init__(
            self, app, game, onDisconnectRequest=None,
            onConnectionLost=None, replay=False, authTag=0):
        super(GameInterface, self).__init__(app, game=game)
        self.localState.onShoxwave.addListener(self.localShoxwaveFired)
        self.localState.onGameInfoChanged.addListener(self.gameInfoChanged)
        self.world.onOpenChatReceived.addListener(self.openChat)
        self.world.onTeamChatReceived.addListener(self.teamChat)
        self.world.onReset.addListener(self.worldReset)
        self.world.onGrenadeExplosion.addListener(self.grenadeExploded)
        self.world.onTrosballExplosion.addListener(self.trosballExploded)
        self.world.onBomberExplosion.addListener(self.trosballExploded)
        self.world.uiOptions.onChange.addListener(self.uiOptionsChanged)
        self.timingsLoop = WeakLoopingCall(self, '_sendPing')
        self.timingsLoop.start(1, now=False)

        self.subscribedPlayers = set()

        self.onDisconnectRequest = Event()
        if onDisconnectRequest is not None:
            self.onDisconnectRequest.addListener(onDisconnectRequest)

        self.onConnectionLost = Event()
        if onConnectionLost is not None:
            self.onConnectionLost.addListener(onConnectionLost)
        self.game = game

        self.joinDialogReason = None

        self.keyMapping = keyboard.KeyboardMapping(keymap.default_game_keys)
        self.runningPlayerInterface = None
        self.updateKeyMapping()
        self.gameViewer = viewManager.GameViewer(self.app, self, game, replay)
        if replay:
            self.joinController = None
        else:
            self.joinController = JoinGameController(self.app, self, self.game)
        self.detailsInterface = DetailsInterface(self.app, self)
        self.winnerMsg = WinnerMsg(app)
        self.timingInfo = TimingInfo(
            app, self, Location(Canvas(307, 768), 'midbottom'),
            app.screenManager.fonts.timingsFont,
            )
        self.gameInfoDisplay = GameInfoDisplay(
            app, self,
            Region(topleft=Screen(0.01, 0.05), size=Canvas(330, 200)))
        self.hotkeys = hotkey.Hotkeys(
            self.app, self.keyMapping, self.detailsInterface.doAction)
        self.terminal = None

        self.joinInProgress = False

        self.vcInterface = None
        if replay:
            self.vcInterface = ViewControlInterface(self.app, self)

        self.ready = False
        defer.maybeDeferred(
            game.addAgent, self, authTag=authTag).addCallback(self.addedAgent)

        self.setElements()

    def _sendPing(self):
        for i in range(3):
            data = bytes([random.randrange(256)])
            if data not in self.localState.pings:
                self.sendRequest(PingMsg(data))
                return

    def gameInfoChanged(self):
        self.gameInfoDisplay.refreshInfo()

    def addedAgent(self, result):
        self.ready = True
        if self.joinController:
            self.joinDialogReason = 'automatic'
            self.joinController.start()

    def spectatorWantsToJoin(self):
        if self.runningPlayerInterface or not self.joinController:
            return
        self.joinDialogReason = 'from menu'
        self.joinController.maybeShowJoinDialog(autoJoin=True)

    def sendRequest(self, msg):
        if not self.ready:
            # Not yet completely connected to game
            return
        super(GameInterface, self).sendRequest(msg)

    def worldReset(self, *args, **kwarsg):
        self.winnerMsg.hide()
        if self.ready and self.joinController:
            self.joinController.gotWorldReset()
        self.gameViewer.reset()

    def updateKeyMapping(self):
        # Set up the keyboard mapping.
        try:
            # Try to load keyboard mappings from the user's personal settings.
            with open(getPath(user, 'keymap'), 'r') as f:
                config = f.read()
            self.keyMapping.load(config)
            if self.runningPlayerInterface:
                self.runningPlayerInterface.keyMappingUpdated()
        except IOError:
            pass

    @ConnectionLostMsg.handler
    def connectionLost(self, msg):
        self.cleanUp()
        if self.joinController:
            self.joinController.hide()
        self.onConnectionLost.execute()

    def joined(self, player):
        '''Called when joining of game is successful.'''
        pygame.key.set_repeat()
        self.gameViewer.worldgui.overridePlayer(self.localState.player)
        self.runningPlayerInterface = pi = PlayerInterface(self.app, self)
        self.detailsInterface.setPlayer(pi.player)
        self.setElements()

        self.joinController.hide()
        self.gameViewer.leaderboard.update()

    def spectate(self):
        '''
        Called by join controller if user selects to only spectate.
        '''
        self.vcInterface = ViewControlInterface(self.app, self)
        self.setElements()
        self.joinController.hide()

    def joinDialogCancelled(self):
        if self.joinDialogReason == 'automatic':
            self.disconnect()
        else:
            self.spectate()

    def stop(self):
        super(GameInterface, self).stop()
        self.localState.onShoxwave.removeListener(self.localShoxwaveFired)
        self.localState.onGameInfoChanged.removeListener(self.gameInfoChanged)
        self.world.onOpenChatReceived.removeListener(self.openChat)
        self.world.onTeamChatReceived.removeListener(self.teamChat)
        self.world.onReset.removeListener(self.worldReset)
        self.world.onGrenadeExplosion.removeListener(self.grenadeExploded)
        self.world.onTrosballExplosion.removeListener(self.trosballExploded)
        self.world.onBomberExplosion.removeListener(self.trosballExploded)
        self.world.uiOptions.onChange.removeListener(self.uiOptionsChanged)
        self.timingsLoop.stop()
        self.gameViewer.stop()
        if self.runningPlayerInterface is not None:
            self.runningPlayerInterface.stop()

    def setElements(self):
        spectate = replay = False
        if self.runningPlayerInterface:
            self.elements = [
                self.gameViewer, self.runningPlayerInterface,
                self.gameInfoDisplay, self.hotkeys, self.detailsInterface,
                self.winnerMsg, self.timingInfo]
        else:
            self.elements = [
                self.gameViewer, self.gameInfoDisplay,
                self.hotkeys, self.detailsInterface,
                self.winnerMsg, self.timingInfo]
            if self.vcInterface is not None:
                self.elements.insert(2, self.vcInterface)

            if self.joinController:
                spectate = True
            else:
                replay = True
        self.detailsInterface.menuManager.setMode(
            spectate=spectate, replay=replay)

    def toggleTerminal(self):
        if self.terminal is None:
            locs = {'app': self.app}
            if hasattr(self.app, 'getConsoleLocals'):
                locs.update(self.app.getConsoleLocals())
            self.terminal = console.TrosnothInteractiveConsole(
                self.app,
                self.app.screenManager.fonts.consoleFont,
                Region(size=Screen(1, 0.4), bottomright=Screen(1, 1)),
                locals=locs)
            self.terminal.interact().addCallback(self._terminalQuit)

        from trosnoth.utils.utils import timeNow
        if self.terminal in self.elements:
            if timeNow() > self._termWaitTime:
                self.elements.remove(self.terminal)
        else:
            self._termWaitTime = timeNow() + 0.1
            self.elements.append(self.terminal)
            self.setFocus(self.terminal)

    def _terminalQuit(self, result):
        if self.terminal in self.elements:
            self.elements.remove(self.terminal)
        self.terminal = None

    def disconnect(self):
        self.cleanUp()
        self.onDisconnectRequest.execute()

    def joinGame(self, nick, head, team, timeout=10):
        if self.joinInProgress:
            return

        if team is None:
            teamId = NEUTRAL_TEAM_ID
        else:
            teamId = team.id

        self.joinInProgress = True
        self.sendJoinRequest(teamId, nick, head)
        WeakCallLater(timeout, self, '_joinTimedOut')

    def setPlayer(self, player):
        if not player:
            self.gameViewer.worldgui.removeOverride()
            self.lostPlayer()

        super(GameInterface, self).setPlayer(player)

        if player:
            if __debug__ and globaldebug.enabled:
                globaldebug.localPlayerId = player.id

            self.joinInProgress = False
            self.joined(player)

    @CannotJoinMsg.handler
    def joinFailed(self, msg):
        self.joinInProgress = False
        self.joinController.joinFailed(msg.reasonId)

    def _joinTimedOut(self):
        if self.player or not self.joinInProgress:
            return
        self.joinInProgress = False
        self.joinController.joinFailed('timeout')

    def cleanUp(self):
        if self.gameViewer.timerBar is not None:
            self.gameViewer.timerBar = None
        pygame.key.set_repeat(300, 30)

    def uiOptionsChanged(self):
        if self.world.uiOptions.showGameOver:
            winner = self.world.uiOptions.winningTeam
            if winner:
                self.winnerMsg.show(
                    '{} win'.format(winner),
                    self.app.theme.colours.chatColour(winner),
                )
            else:
                self.winnerMsg.show('Game drawn', (128, 128, 128))
        else:
            self.winnerMsg.hide()

    @PlayerCoinsSpentMsg.handler
    def discard(self, msg):
        pass

    @AwardPlayerCoinMsg.handler
    def playerAwardedCoin(self, msg):
        if not self.localState.player:
            return
        if msg.sound and msg.playerId == self.localState.player.id:
            self.playSound('gotCoin')

    @PlayerHasElephantMsg.handler
    def gotElephant(self, msg, _lastElephantPlayer=[None]):
        player = self.world.getPlayer(msg.playerId)
        if player and player != _lastElephantPlayer[0]:
            message = '%s now has %s!' % (
                player.nick, player.world.uiOptions.elephantName)
            self.detailsInterface.newMessage(message)
            _lastElephantPlayer[0] = player

    @PlayerHasTrosballMsg.handler
    def gotTrosball(self, msg, _lastTrosballPlayer=[None]):
        player = self.world.playerWithId.get(msg.playerId)

        if player != _lastTrosballPlayer[0]:
            _lastTrosballPlayer[0] = player
            if player is None:
                message = 'The ball has been dropped!'
            else:
                message = '%s has the ball!' % (player.nick,)
            self.detailsInterface.newMessage(message)

    @AddPlayerMsg.handler
    def addPlayer(self, msg):
        player = self.world.getPlayer(msg.playerId)
        if player and player not in self.subscribedPlayers:
            self.subscribedPlayers.add(player)
            team = player.team if player.team else self.world.rogueTeamName
            message = '%s has joined %s' % (player.nick, team)
            self.detailsInterface.newMessage(message)
            player.onDied.addListener(partial(self.playerDied, player))

    @SetPlayerTeamMsg.handler
    def changeTeam(self, msg):
        self.defaultHandler(msg)    # Make sure the local player changes team
        player = self.world.getPlayer(msg.playerId)
        if player:
            message = '%s has joined %s' % (
                player.nick, self.world.getTeamName(msg.teamId))
            self.detailsInterface.newMessage(message)

    @RemovePlayerMsg.handler
    def handle_RemovePlayerMsg(self, msg):
        player = self.world.getPlayer(msg.playerId)
        if player:
            message = '%s has left the game' % (player.nick,)
            self.detailsInterface.newMessage(message)
            self.subscribedPlayers.discard(player)

    def lostPlayer(self):
        self.runningPlayerInterface.stop()
        self.runningPlayerInterface = None
        self.setElements()

    @CannotBuyUpgradeMsg.handler
    def notEnoughCoins(self, msg):
        if msg.reasonId == NOT_ENOUGH_COINS_REASON:
            text = 'Your team does not have enough coins.'
        elif msg.reasonId == CANNOT_REACTIVATE_REASON:
            text = 'You already have that item.'
        elif msg.reasonId == PLAYER_DEAD_REASON:
            text = 'You cannot buy an upgrade while dead.'
        elif msg.reasonId == GAME_NOT_STARTED_REASON:
            text = 'Upgrades can''t be bought at this time.'
        elif msg.reasonId == TOO_CLOSE_TO_EDGE_REASON:
            text = 'You are too close to the zone edge.'
        elif msg.reasonId == TOO_CLOSE_TO_ORB_REASON:
            text = 'You are too close to the orb.'
        elif msg.reasonId == NOT_IN_DARK_ZONE_REASON:
            text = 'You are not in a dark friendly zone.'
        elif msg.reasonId == INVALID_UPGRADE_REASON:
            text = 'Upgrade not recognised by server.'
        elif msg.reasonId == DISABLED_UPGRADE_REASON:
            text = 'That upgrade is currently disabled.'
        else:
            text = 'You cannot buy that item at this time.'
        self.detailsInterface.newMessage(text)
        self.defaultHandler(msg)

    @PlayerHasUpgradeMsg.handler
    def gotUpgrade(self, msg):
        player = self.world.getPlayer(msg.playerId)
        if player:
            self.detailsInterface.upgradeUsed(player, msg.upgradeType)
            upgradeClass = self.world.getUpgradeType(msg.upgradeType)
            existing = player.items.get(upgradeClass)
            if not existing:
                if (self.detailsInterface.player is None or
                        self.detailsInterface.player.isFriendsWith(player)):
                    self.playSound('buyUpgrade')

        self.defaultHandler(msg)

    @ChatFromServerMsg.handler
    def gotChatFromServer(self, msg):
        self.detailsInterface.newMessage(
            msg.text.decode('utf-8'), error=msg.error)

    @TaggingZoneMsg.handler
    def zoneTagged(self, msg):
        try:
            zone = self.world.zoneWithId[msg.zoneId]
            zoneLabel = zone.defn.label
        except KeyError:
            zoneLabel = '<?>'

        if msg.playerId != NO_PLAYER:
            try:
                player = self.world.playerWithId[msg.playerId]
            except KeyError:
                nick = '<?>'
            else:
                nick = player.nick
            message = '%s tagged zone %s' % (nick, zoneLabel)

            self.detailsInterface.newMessage(message)

    def playerDied(self, target, killer, deathType):
        if deathType == OFF_MAP_DEATH_HIT:
            messages = [
                'fell into the void', 'looked into the abyss',
                'dug too greedily and too deep']
            message = '%s %s' % (target.nick, random.choice(messages))
        elif deathType == TROSBALL_DEATH_HIT:
            message = '%s was killed by the Trosball' % (target.nick,)
        elif deathType == BOMBER_DEATH_HIT:
            message = '%s head asplode' % (target.nick,)
            thisPlayer = self.detailsInterface.player
            if thisPlayer and target.id == thisPlayer.id:
                self.detailsInterface.doAction(ACTION_CLEAR_UPGRADE)
        else:
            if killer is None:
                message = '%s was killed' % (target.nick,)
                self.detailsInterface.newMessage(message)
            else:
                message = '%s killed %s' % (killer.nick, target.nick)

        self.detailsInterface.newMessage(message)

    @RespawnMsg.handler
    def playerRespawn(self, msg):
        player = self.world.getPlayer(msg.playerId)
        if player:
            message = '%s is back in the game' % (player.nick,)
            self.detailsInterface.newMessage(message)

    @CannotRespawnMsg.handler
    def respawnFailed(self, msg):
        if msg.reasonId == GAME_NOT_STARTED_REASON:
            message = 'The game has not started yet.'
        elif msg.reasonId == ALREADY_ALIVE_REASON:
            message = 'You are already alive.'
        elif msg.reasonId == BE_PATIENT_REASON:
            message = 'You cannot respawn yet.'
        elif msg.reasonId == ENEMY_ZONE_REASON:
            message = 'Cannot respawn outside friendly zone.'
        elif msg.reasonId == FROZEN_ZONE_REASON:
            message = 'That zone has been frozen!'
        else:
            message = 'You cannot respawn here.'
        self.detailsInterface.newMessage(
            message, self.app.theme.colours.errorMessageColour)

    def sendPrivateChat(self, player, targetId, text):
        self.sendRequest(ChatMsg(PRIVATE_CHAT, targetId, text=text.encode()))

    def sendTeamChat(self, player, text):
        self.sendRequest(
            ChatMsg(TEAM_CHAT, player.teamId, text=text.encode()))

    def sendPublicChat(self, player, text):
        self.sendRequest(ChatMsg(OPEN_CHAT, text=text.encode()))

    def openChat(self, text, sender):
        text = ': ' + text
        self.detailsInterface.newChat(text, sender)

    def teamChat(self, team, text, sender):
        player = self.detailsInterface.player
        if player and player.isFriendsWithTeam(team):
            text = ' (team): ' + text
            self.detailsInterface.newChat(text, sender)

    @AchievementUnlockedMsg.handler
    def achievementUnlocked(self, msg):
        player = self.world.getPlayer(msg.playerId)
        if not player:
            return

        achievementName = self.achievementDefs.getAchievementDetails(
            msg.achievementId)[0]
        self.detailsInterface.newMessage(
            '%s has unlocked "%s"!' % (player.nick, achievementName),
            self.app.theme.colours.achievementMessageColour)

        focusPlayer = self.detailsInterface.player
        if (focusPlayer is not None and focusPlayer.id == msg.playerId):
            self.detailsInterface.localAchievement(msg.achievementId)

    @ShotFiredMsg.handler
    def shotFired(self, msg):
        self.defaultHandler(msg)
        try:
            shot = self.world.getShot(msg.shotId)
        except KeyError:
            return

        pos = shot.pos
        dist = self.distance(pos)
        self.playSound('shoot', self.getSoundVolume(dist))

    def grenadeExploded(self, pos, radius):
        self.gameViewer.worldgui.addExplosion(pos)
        dist = self.distance(pos)
        self.playSound('explodeGrenade', self.getSoundVolume(dist))

    def trosballExploded(self, player):
        self.gameViewer.worldgui.addTrosballExplosion(player.pos)
        dist = self.distance(player.pos)
        self.playSound('explodeGrenade', self.getSoundVolume(dist))

    @FireShoxwaveMsg.handler
    def shoxwaveExplosion(self, msg):
        localPlayer = self.localState.player
        if localPlayer and msg.playerId == localPlayer.id:
            return
        self.gameViewer.worldgui.addShoxwaveExplosion((msg.xpos, msg.ypos))

    def localShoxwaveFired(self):
        localPlayer = self.localState.player
        self.gameViewer.worldgui.addShoxwaveExplosion(localPlayer.pos)

    @UpgradeChangedMsg.handler
    def upgradeChanged(self, msg):
        self.detailsInterface.upgradeDisplay.refresh()

    def distance(self, pos):
        return distance(self.gameViewer.viewManager.getTargetPoint(), pos)

    def getSoundVolume(self, distance):
        'The volume for something that far away from the player'
        # Up to 500px away is within the "full sound zone" - full sound
        distFromScreen = max(0, distance - 500)
        # 1000px away from "full sound zone" is 0 volume:
        return 1 - min(1, (distFromScreen / 1000.))

    def playSound(self, action, volume=1):
        self.app.soundPlayer.play(action, volume)

    @PlaySoundMsg.handler
    def playSoundFromServerCommand(self, msg):
        self.app.soundPlayer.playFromServerCommand(
            msg.filename.decode('utf-8'))

    @TickMsg.handler
    def handle_TickMsg(self, msg):
        super(GameInterface, self).handle_TickMsg(msg)
        self.timingInfo.ticksSeen += 1


class TimingInfo(framework.Element):
    def __init__(self, app, gameInterface, location, font, *args, **kwargs):
        super(TimingInfo, self).__init__(app, *args, **kwargs)
        self.interface = gameInterface
        self.location = location
        self.font = font
        self.framesSeen = 0
        self.ticksSeen = 0
        self.timePassed = 0.
        self.lastDelay = None
        self.lastPing = 0
        self.make_image()

    def make_image(self):
        bits = []
        if self.timePassed > 0:
            bits.append(self.font.render(
                self.app,
                'FPS: %.1f' % (self.framesSeen / self.timePassed),
                True, (0, 0, 0),
            ))
            bits.append(self.font.render(
                self.app,
                'TPS: %.1f' % (self.ticksSeen / self.timePassed),
                True, (0, 0, 0),
            ))

        self.lastPing = pingTime = self.interface.localState.lastPingTime
        if pingTime is not None:
            bits.append(self.font.render(
                self.app, 'Ping: %d ms' % (1000 * pingTime,), True, (0, 0, 0)))

        self.lastDelay = self.interface.localState.serverDelay
        delay = self.interface.localState.serverDelay * TICK_PERIOD
        bits.append(self.font.render(
            self.app, 'Smooth: %d ms' % (1000 * delay,), True, (0, 0, 0)))

        if self.app.jitterLogger.jitter is not None:
            bits.append(self.font.render(
                self.app, 'LJMax: %d ms' % (
                    1000 * self.app.jitterLogger.jitter,), True, (0, 0, 0)))

        width = max(b.get_width() for b in bits) if bits else 0
        height = sum(b.get_height() for b in bits)
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)

        y = 0
        for bit in bits:
            self.image.blit(bit, (0, y))
            y += bit.get_height()

        self.framesSeen = 0
        self.ticksSeen = 0
        self.timePassed = 0.

    def tick(self, deltaT):
        if not self.app.displaySettings.showTimings:
            return
        self.timePassed += deltaT

    def draw(self, screen):
        if not self.app.displaySettings.showTimings:
            return
        self.framesSeen += 1
        if (
                self.timePassed > 3
                or self.lastDelay != self.interface.localState.serverDelay
                or self.lastPing != self.interface.localState.lastPingTime):
            self.make_image()
        rect = self.image.get_rect()
        self.location.apply(self.app, rect)
        screen.blit(self.image, rect)


class GameInfoDisplay(CollapseBox):
    def __init__(self, app, gameInterface, region):
        colours = app.theme.colours
        fonts = app.screenManager.fonts
        self.interface = gameInterface
        super(GameInfoDisplay, self).__init__(
            app,
            region=region,
            titleFont=fonts.gameInfoTitleFont,
            font=fonts.gameInfoFont,
            titleColour=colours.gameInfoTitle,
            hvrColour=colours.gameInfoHover,
            colour=colours.gameInfoColour,
            backColour=colours.gameInfoBackColour,
            title='',
        )
        self.refreshInfo()

    def refreshInfo(self):
        localState = self.interface.localState
        self.setInfo(localState.userInfo, localState.userTitle)


class WinnerMsg(framework.CompoundElement):
    def __init__(self, app):
        super(WinnerMsg, self).__init__(app)
        self.winnerMsg = TextElement(
            app, '', app.screenManager.fonts.winMessageFont,
            Location(Screen(0.5, 0.05), 'midtop'), (64, 64, 64))
        self.background = SolidRect(
            app, (128, 128, 128), 150,
            PaddedRegion(self.winnerMsg, ScaledScalar(15)))
        self.elements = []

    def show(self, text, colour):
        self.winnerMsg.setText(text)
        self.background.colour = colour
        self.background.border = colour
        self.background.refresh()
        self.elements = [self.background, self.winnerMsg]

    def hide(self):
        self.elements = []
