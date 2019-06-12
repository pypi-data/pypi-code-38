import logging

from trosnoth.client3d.base import app
from trosnoth.client3d.ingame.gameInterface import PandaUIAgent
from trosnoth.client3d.pregame.startup import StartupScene
from trosnoth.game import LocalGame, RemoteGame
from trosnoth.gamerecording import replays
from trosnoth.model.mapLayout import LayoutDatabase
from trosnoth.model.uithrottler import UIMsgThrottler, LocalGameTweener
from trosnoth.network.lobby import UDPMulticaster
from trosnoth.network.networkDefines import serverVersion
from trosnoth.network.server import TrosnothServerFactory
from trosnoth.utils.event import Event


log = logging.getLogger(__name__)

GAME_TITLE = 'Trosnoth'


class Main(app.Application):
    '''Instantiating the Main class will set up the game. Calling the run()
    method will run the reactor. This class handles the three steps of joining
    a game: (1) get list of clients; (2) connect to a server; (3) join the
    game.'''


    def __init__(self, serverDetails=None, showReplay=None):
        '''Initialise the game.'''

        super(Main, self).__init__(GAME_TITLE)

        self.hoster = Hoster(self)
        self.connector = Connector(self)

        self.connector.onReplayOpened.addListener(self._setupReplay)
        self.connector.onGameOpened.addListener(self._setupGame)

        self._showStartupScreens()
        if serverDetails is not None:
            # TODO: make this work
            log.error('--auth-server flag does not currently work')
        elif showReplay:
            self.connector.openReplay(showReplay)

    def __str__(self):
        return 'Trosnoth Main Object'

    def getConsoleLocals(self):
        result = super(Main, self).getConsoleLocals()
        result['server'] = self.hoster.server
        return result

    def stopping(self):
        self.hoster.stop()
        super(Main, self).stopping()

    def initialise(self):
        super(Main, self).initialise()

        self.layoutDatabase = LayoutDatabase(pathGetter=self.theme.getPath)

    def _showStartupScreens(self):
        self.elements = []
        self.setPandaScene(StartupScene(self))

    def _setupGame(self, game, authTag):
        # Create a game interface.
        self.agent = PandaUIAgent(
            self, game,
            onDisconnectRequest=self.connector.closeGame,
            authTag=authTag)
        self.agent.show()

    def _setupReplay(self, game):
        self.agent = PandaUIAgent(
            self, game, onDisconnectRequest=self._userQuitReplay,
            replay=True, onConnectionLost=self._replayOver)
        self.agent.show()

    def _userQuitReplay(self):
        # TODO: make sure the replay actually stops playing
        self._replayOver()

    def _replayOver(self):
        self._showStartupScreens()



class Hoster(object):
    '''
    If this Trosnoth instance is hosting any games, takes care of keeping the
    game running even if you leave the game but keep Trosnoth open.
    '''

    def __init__(self, app):
        self.app = app
        self.server = None
        self.multicaster = None

    def startServer(self, halfMapWidth=3, mapHeight=2, gameDuration=0):
        if self.server is not None and self.server.running:
            log.warning('Refusing to start local game: one is already running')
            return

        game = LocalGame(
            self.app.layoutDatabase, halfMapWidth, mapHeight,
            duration=gameDuration * 60,
            saveReplay=True, gamePrefix='LAN')

        self.server = TrosnothServerFactory(game)
        self.server.onShutdown.addListener(self._serverShutdown)
        self.server.startListening()

        # Start listening for game requests on the lan.
        self.multicaster = UDPMulticaster(self._getGames)

    def stop(self):
        # Shut down the server if one's running.
        if self.server is not None:
            self.server.shutdown()

        if self.multicaster is not None:
            self.multicaster.stop()
            self.multicaster = None

    def getGameObject(self):
        if self.server is None:
            return None
        return self.server.game

    def _serverShutdown(self):
        self.server.stopListening()
        self.server = None

    def _getGames(self):
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


class Connector(object):
    '''
    Maintains the state of whether the Trosnoth app is currently connected to
    (viewing) a game or replay, or is on the main menu.
    '''

    def __init__(self, app):
        self.app = app
        self.game = None
        self.trosnothClient = None

        self.onGameOpened = Event()     # (game, authTag)
        self.onReplayOpened = Event()   # (game)
        self.onGameClosed = Event()

    def openGameObject(self, game):
        if self.game is not None:
            raise RuntimeError('Already displaying a game')

        self.game = game
        self.app.tweener = LocalGameTweener(game)

        self.onGameOpened(game, 0)

    def openReplay(self, filename):
        if self.game is not None:
            raise RuntimeError('Already displaying a game')

        self.trosnothClient = replayer = replays.ReplayPlayer(filename)

        self.game = game = RemoteGame(self.app.layoutDatabase)
        self.app.tweener = UIMsgThrottler()

        replayer.connectNode(self.app.tweener)
        self.app.tweener.connectNode(game)

        game.connected(replayer.popSettings())
        replayer.start()

        self.onReplayOpened(game)

    def connectedToGame(self, trosnothClient, settings, authTag):
        self.trosnothClient = trosnothClient
        trosnothClient.onConnectionLost.addListener(self._connectionLost)

        self.game = game = RemoteGame(self.app.layoutDatabase)
        self.app.tweener = UIMsgThrottler()
        self.trosnothClient.connectNode(self.app.tweener)
        self.app.tweener.connectNode(game)

        game.connected(settings)
        self.onGameOpened(game, authTag)

    def _connectionLost(self, reason=None):
        self.onGameClosed(self.game)
        if self.game is not None:
            if self.game is not self.app.hoster.getGameObject():
                self.game.stop()
            self.game = None

    def closeGame(self):
        '''
        Disconnect from the game or replay.
        '''
        if self.trosnothClient is not None:
            self.trosnothClient.disconnect()
            self.trosnothClient.disconnectNode()
            self.trosnothClient = None
        else:
            self._connectionLost()
