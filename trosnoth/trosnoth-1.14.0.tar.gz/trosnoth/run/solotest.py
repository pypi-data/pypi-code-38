import logging
import sys

import pygame
from twisted.internet import defer, reactor

from trosnoth.game import LocalGame, RemoteGame
from trosnoth.gui import app
from trosnoth.settings import DisplaySettings, SoundSettings, IdentitySettings
from trosnoth.themes import Theme
from trosnoth.trosnothgui.ingame.gameInterface import GameInterface
from trosnoth.gui.framework import framework
from trosnoth.manholehelper import LocalManholeHelper
from trosnoth.model import mapLayout
from trosnoth.model.agenthub import LocalHub
from trosnoth.model.hub import Hub, Node
from trosnoth.model.uithrottler import UIMsgThrottler, LocalGameTweener

log = logging.getLogger(__name__)

GAME_TITLE = 'Trosnoth Solo Mode'


class Main(app.MultiWindowApplication):
    def __init__(
            self, isolate=False, size=(1, 1), aiCount=0, aiClass='ranger',
            mapBlocks=(), testMode=False, stackTeams=False,
            delay=None, blockRatio=0.5, duration=0,
            level=None):
        '''Initialise the game.'''
        pygame.init()
        self.size = size
        self.aiCount = aiCount
        self.isolate = isolate
        self.mapBlocks = mapBlocks
        self.testMode = testMode
        self.stackTeams = stackTeams
        self.aiClass = aiClass
        self.delay = delay
        self.blockRatio = blockRatio
        self.duration = duration

        self.displaySettings = DisplaySettings(self)
        self.soundSettings = SoundSettings(self)
        self.identitySettings = IdentitySettings(self)
        self.ais = []

        pygame.font.init()
        super(Main, self).__init__(
            self.displaySettings.getSize(),
            self.displaySettings.fullScreen,
            GAME_TITLE,
            SoloInterface)

        # Set the master sound volume.
        self.soundSettings.apply()

        self.game = None
        self.startGame(level=level)

    def getConsoleLocals(self):
        result = {
            'game': self.game,
            'ais': self.ais,
            'helper': LocalManholeHelper(lambda: self.game),
        }
        return result

    def initialise(self):
        super(Main, self).initialise()

        # Loading the theme loads the fonts.
        self.theme = Theme(self)

    def getFontFilename(self, fontName):
        '''
        Tells the UI framework where to find the given font.
        '''
        return self.theme.getPath('fonts', fontName)

    def changeScreenSize(self, size, fullScreen):
        self.screenManager.setScreenProperties(size, fullScreen, GAME_TITLE)

    def startGame(self, level=None):
        db = mapLayout.LayoutDatabase(
            pathGetter=self.theme.getPath,
            blocks=self.mapBlocks)
        gameType = 'solo'
        self.game = game = LocalGame(
            db, self.size[0], self.size[1], onceOnly=True,
            blockRatio=self.blockRatio,
            duration=self.duration*60,
            level=level,
            gameType=gameType,
            botProcess=True,
        )
        if self.testMode:
            game.world.setTestMode()

        self.ais[:] = []

        try:
            for i in range(self.aiCount):
                if self.stackTeams:
                    ai = game.addBot(self.aiClass, team=game.world.teams[0])
                else:
                    ai = game.addBot(self.aiClass)
                self.ais.append(ai)
        except ImportError:
            print('AI module not found: %s' % (self.aiClass,), file=sys.stderr)
            sys.exit(1)
        except AttributeError:
            print((
                'AI module does not define BotClass: %s' % (self.aiClass,)), file=sys.stderr)
            sys.exit(1)

        # Create a client and an interface.
        if self.isolate:
            rgame = RemoteGame(db)
            hub = LocalHub(game)
            self.tweener = UIMsgThrottler()
            if self.delay:
                delayer = DelayNodeHub(self.delay)
                hub.connectNode(delayer)
                delayer.connectNode(self.tweener)
            else:
                hub.connectNode(self.tweener)
            self.tweener.connectNode(rgame)
            self.rgame = rgame
            self.gi = gi = GameInterface(self, rgame)
            rgame.connected(game.world.dumpEverything())
        else:
            self.tweener = LocalGameTweener(game)
            self.gi = gi = GameInterface(self, game)
        gi.onDisconnectRequest.addListener(self.stop)
        gi.onConnectionLost.addListener(self.stop)
        self.interface.elements.append(gi)

    def stop(self):
        self.game.stop()
        super(Main, self).stop()


class DelayNodeHub(Hub, Node):
    def __init__(self, delay, *args, **kwargs):
        super(DelayNodeHub, self).__init__(*args, **kwargs)
        self.delay = delay

    @defer.inlineCallbacks
    def connectNewAgent(self, authTag=0):
        result = yield self.hub.connectNewAgent(authTag=authTag)

        d = defer.Deferred()
        reactor.callLater(self.delay, d.callback, None)
        yield d

        defer.returnValue(result)

    def disconnectAgent(self, agentId):
        reactor.callLater(self.delay, self.hub.disconnectAgent, agentId)

    def sendRequestToGame(self, agentId, msg):
        msg.tracePoint(self, 'sendRequestToGame')
        reactor.callLater(self.delay, self.hub.sendRequestToGame, agentId, msg)

    def gotServerCommand(self, msg):
        msg.tracePoint(self, 'gotServerCommand')
        reactor.callLater(self.delay, self.node.gotServerCommand, msg)

    def gotMessageToAgent(self, agentId, msg):
        msg.tracePoint(self, 'gotMessageToAgent')
        reactor.callLater(
            self.delay, self.node.gotMessageToAgent, agentId, msg)

    def agentDisconnected(self, agentId):
        reactor.callLater(self.delay, self.node.agentDisconnected, agentId)


class SoloInterface(framework.CompoundElement):
    def __init__(self, app):
        super(SoloInterface, self).__init__(app)
        self.elements = []
