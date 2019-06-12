'''interface.py - defines the Interface class which deals with drawing the
game to the screen, including menus and other doodads.'''

import logging

import pygame
from twisted.internet import defer, reactor
from twisted.internet.protocol import ClientCreator

from trosnoth.const import JOIN_LAN_GAME, JOIN_LOCAL_GAME
from trosnoth.network.client import TrosnothClientProtocol, ConnectionFailed
from trosnoth.game import RemoteGame
from trosnoth.gamerecording import replays

from trosnoth.gui.framework import framework
from trosnoth.model.uithrottler import UIMsgThrottler, LocalGameTweener

from trosnoth.trosnothgui.pregame.startup import StartupInterface
from trosnoth.trosnothgui.pregame.connectingScreen import ConnectingScreen
from trosnoth.trosnothgui.pregame.backdrop import TrosnothBackdrop
from trosnoth.trosnothgui.pregame.playscreen import PlayAuthScreen

from trosnoth.trosnothgui.pregame.connectionFailedDialog import (
    ConnectionFailedDialog)
from trosnoth.trosnothgui.ingame.gameInterface import GameInterface
from trosnoth.trosnothgui.pregame.savedGameMenu import SavedGameMenu
from trosnoth.trosnothgui.settings.settings import SettingsMenu
import trosnoth.version

log = logging.getLogger(__name__)


class Interface(framework.CompoundElement):
    def __init__(self, app):
        super(Interface, self).__init__(app)

        # Create an interfaces for pre- and post-connection.
        self.backdrop = TrosnothBackdrop(app)

        self.gi = None
        self.game = None
        self.gameIsLocal = False
        self.currentDeferred = None
        self.trosnothClient = None
        self.startupInterface = self._makeStartupInterface()

        self.elements = [self.backdrop, self.startupInterface]

    def _makeStartupInterface(self):
        result = StartupInterface(self.app, self)
        result.start()
        return result

    def processEvent(self, event):
        # Capture the quit event.
        if event.type == pygame.QUIT:
            self.app.stop()
            return
        return super(Interface, self).processEvent(event)

    @defer.inlineCallbacks
    def connectToServer(self, host, port, timeout=7):
        self.elements = [
            self.backdrop,
            ConnectingScreen(
                self.app, '%s:%s' % (host, port),
                onCancel=self.cancelConnecting)
        ]

        try:
            cc = ClientCreator(reactor, TrosnothClientProtocol)
            self.currentDeferred = cc.connectTCP(host, port, timeout=timeout)
            trosnothClient = yield self.currentDeferred
            self.trosnothClient = trosnothClient
            self.currentDeferred = trosnothClient.getSettings()
            settings = yield self.currentDeferred
            self.currentDeferred = None
            self.connectionEstablished(settings)

        except Exception as e:
            self.currentDeferred = None
            self.trosnothClient = None
            self.elements = [self.backdrop, self.startupInterface]
            if not isinstance(e, defer.CancelledError):
                if isinstance(e, ConnectionFailed):
                    text = str(e.reason)
                else:
                    text = 'Internal Error'
                    log.exception('Unexpected failure in deferred')
                d = ConnectionFailedDialog(self.app, text)
                d.show()

    def cancelConnecting(self, source):
        if self.currentDeferred:
            self.currentDeferred.cancel()

    def connectedToGame(self, trosnothClient, settings, authTag):
        self.trosnothClient = trosnothClient
        self.connectionEstablished(settings, authTag)

    def connectToLocalServer(self):
        '''
        Requries app.server is not None. Connects to the locally-hosted server.
        '''
        self.connectToGameObject(self.app.server.game)

    def connectToGameObject(self, game):
        self.game = game
        self.app.tweener = LocalGameTweener(game)
        self.setupGame(game, 0, local=True)

        self.elements = [self.gi]

    def connectionEstablished(self, settings, authTag=0):
        'Called when this client establishes a connection to a server.'
        self.trosnothClient.onConnectionLost.addListener(self.connectionLost)

        game = RemoteGame(self.app.layoutDatabase)
        self.app.tweener = UIMsgThrottler()
        self.trosnothClient.connectNode(self.app.tweener)
        self.app.tweener.connectNode(game)

        game.connected(settings)
        self.setupGame(game, authTag, local=False)

        self.game = game
        self.elements = [self.gi]

    def setupGame(self, game, authTag, local):
        # Create a game interface.
        self.gi = GameInterface(
            self.app, game,
            onDisconnectRequest=self._disconnectGame,
            onConnectionLost=self.connectionLost, authTag=authTag)
        self.gameIsLocal = local

    def setupReplay(self, game):
        self.gi = GameInterface(
            self.app, game, onDisconnectRequest=self.userQuitReplay,
            replay=True, onConnectionLost=self.replayOver)

    def userQuitReplay(self):
        self.trosnothClient.stop()
        self.replayOver()

    def replayOver(self):
        self.elements = [self.backdrop, self.startupInterface]

    def _disconnectGame(self):
        '''
        Requested to disconnect from the game.
        '''
        if self.trosnothClient is not None:
            self.trosnothClient.disconnect()
            self.trosnothClient.disconnectNode()
            self.trosnothClient = None
        else:
            self.connectionLost()

    def connectionLost(self, reason=None):
        self.elements = [self.backdrop, self.startupInterface]
        if self.game is not None:
            if self.gi:
                self.game.detachAgent(self.gi)
            if not self.gameIsLocal:
                # Do not stop a local server, in case other people are still
                # playing.
                self.game.stop()
            self.game = None
        if self.gi is not None:
            self.gi.stop()
            self.gi = None

        if reason is not None:
            d = ConnectionFailedDialog(self.app, reason)
            d.show()

    def connectToReplay(self, filename):
        self.trosnothClient = player = replays.ReplayPlayer(filename)

        game = RemoteGame(self.app.layoutDatabase)
        self.app.tweener = UIMsgThrottler()

        player.connectNode(self.app.tweener)
        self.app.tweener.connectNode(game)

        game.connected(player.popSettings())
        self.setupReplay(game)
        player.start()

        self.game = game
        self.elements = [self.gi]


class SingleAuthInterface(Interface):
    connectScreenFactory = PlayAuthScreen

    def __init__(self, app):
        Interface.__init__(self, app)

        if self.app.serverDetails:
            self.startupInterface.begin(
                [self.app.serverDetails], canHost=False)
        else:
            settings = app.connectionSettings
            servers = list(settings.servers)
            if not trosnoth.version.release:
                # Check that developers aren't accidentally connecting to
                # play.trosnoth.org.
                servers = [
                    s[:2] for s in servers if s[0] != 'play.trosnoth.org']
            if settings.lanGames == 'afterInet':
                servers.append(JOIN_LAN_GAME)
            elif settings.lanGames == 'beforeInet':
                servers.insert(0, JOIN_LAN_GAME)
            servers.insert(0, JOIN_LOCAL_GAME)
            self.startupInterface.begin(servers, canHost=True)

    def _makeStartupInterface(self):
        return self.connectScreenFactory(self.app, onFail=self.app.stop)

    def connectionLost(self, reason=None):
        Interface.connectionLost(self, reason)
        self.app.stop()


class KeySettingsInterface(Interface):
    def _makeStartupInterface(self):
        return SettingsMenu(
            self.app, onClose=self.app.stop, showSound=False,
            showDisplay=False)


class ArchivesInterface(Interface):
    def _makeStartupInterface(self):
        return SavedGameMenu(
            self.app, onCancel=self.app.stop, onReplay=self.connectToReplay)
