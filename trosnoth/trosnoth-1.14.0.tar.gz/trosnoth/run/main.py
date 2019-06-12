import logging

import pygame
from twisted.internet import reactor

from trosnoth.game import LocalGame
from trosnoth.levels.base import StandardLobbyLevel
from trosnoth.settings import (
    DisplaySettings, SoundSettings, IdentitySettings, ConnectionSettings,
)
from trosnoth.trosnothgui import interface
from trosnoth.themes import Theme
from trosnoth.manholehelper import LocalManholeHelper
from trosnoth.model.mapLayout import LayoutDatabase
from trosnoth.network.lobby import UDPMulticaster
from trosnoth.network.networkDefines import serverVersion
from trosnoth.network.server import TrosnothServerFactory

from trosnoth.gui import app

log = logging.getLogger(__name__)

GAME_TITLE = 'Trosnoth'


class Main(app.MultiWindowApplication):
    '''Instantiating the Main class will set up the game. Calling the run()
    method will run the reactor. This class handles the three steps of joining
    a game: (1) get list of clients; (2) connect to a server; (3) join the
    game.'''

    standardInterfaceFactory = interface.Interface
    singleInterfaceFactory = interface.SingleAuthInterface

    def __init__(self, serverDetails=None, showReplay=None):
        '''Initialise the game.'''
        pygame.init()

        self.serverDetails = serverDetails
        self.server = None

        self.displaySettings = DisplaySettings(self)
        self.soundSettings = SoundSettings(self)
        self.identitySettings = IdentitySettings(self)
        self.connectionSettings = ConnectionSettings(self)

        pygame.font.init()
        if self.serverDetails is not None:
            iface = self.singleInterfaceFactory
        else:
            iface = self.standardInterfaceFactory
            if showReplay:
                reactor.callWhenRunning(self.loadReplay, showReplay)

        super(Main, self).__init__(
            self.displaySettings.getSize(),
            self.displaySettings.fullScreen,
            GAME_TITLE, iface)

        # Set the master sound volume.
        self.soundSettings.apply()

        # Start listening for game requests on the lan.
        self.multicaster = UDPMulticaster(self.getGames)

    def __str__(self):
        return 'Trosnoth Main Object'

    def getConsoleLocals(self):
        result = {
            'server': self.server,
            'helper': LocalManholeHelper(
                lambda: getattr(self, 'interface', None).game),
        }
        try:
            result['game'] = self.interface.game
        except AttributeError:
            pass
        return result

    def stopping(self):
        # Shut down the server if one's running.
        if self.server is not None:
            self.server.shutdown()

        self.multicaster.stop()
        super(Main, self).stopping()

    def initialise(self):
        super(Main, self).initialise()

        # Loading the theme loads the fonts.
        self.theme = Theme(self)
        self.layoutDatabase = LayoutDatabase(pathGetter=self.theme.getPath)

    def loadReplay(self, filename):
        self.screenManager.interface.connectToReplay(filename)

    def getFontFilename(self, fontName):
        '''
        Tells the UI framework where to find the given font.
        '''
        return self.theme.getPath('fonts', fontName)

    def changeScreenSize(self, size, fullScreen):
        self.screenManager.setScreenProperties(size, fullScreen, GAME_TITLE)

    def startListenServer(
            self, halfMapWidth=3, mapHeight=2):
        if self.server is not None and self.server.running:
            return
        game = LocalGame(
            self.layoutDatabase,
            saveReplay=True, gamePrefix='LAN',
            level=StandardLobbyLevel(
                (halfMapWidth, mapHeight), lobbySettings=None))
        self.server = TrosnothServerFactory(game)

        self.server.onShutdown.addListener(self._serverShutdown)
        self.server.startListening()

    def getGames(self):
        '''
        Called by multicast listener when a game request comes in.
        '''
        if self.server:
            gameInfo = {
                'version': serverVersion,
                'port': self.server.getTCPPort(),
            }
            return [gameInfo]
        return []

    def _serverShutdown(self):
        self.server.stopListening()
        self.server = None
