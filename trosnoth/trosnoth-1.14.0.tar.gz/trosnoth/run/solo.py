import logging
import sys
from twisted.conch import manhole_ssh
from twisted.conch.error import ConchError
from twisted.cred import portal, checkers
from twisted.internet import defer, reactor
from twisted.internet.error import CannotListenError

from trosnoth.client3d.base import app
from trosnoth.client3d.ingame.gameInterface import PandaUIAgent
from trosnoth.game import LocalGame, RemoteGame
from trosnoth.model import mapLayout
from trosnoth.model.agenthub import LocalHub
from trosnoth.model.hub import Hub, Node
from trosnoth.model.uithrottler import UIMsgThrottler, LocalGameTweener
from trosnoth.network.manhole import Manhole

log = logging.getLogger(__name__)

GAME_TITLE = 'Trosnoth Solo Mode'
MANHOLE = True


class SoloTrosnothApp(app.Application):
    def __init__(
            self, isolate=False, size=(1, 1), aiCount=0, aiClass='ranger',
            mapBlocks=(), testMode=False, stackTeams=False,
            delay=None, blockRatio=0.5, duration=0,
            level=None):
        '''Initialise the game.'''

        super(SoloTrosnothApp, self).__init__(GAME_TITLE)

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

        self.ais = []
        self.startGame(level=level)
        if MANHOLE:
            self.startSSHManhole()

    def getConsoleLocals(self):
        result = super(SoloTrosnothApp, self).getConsoleLocals()
        result['ais'] = self.ais
        result['app'] = self
        result['panda'] = self.panda
        return result

    def startGame(self, level=None):
        db = mapLayout.LayoutDatabase(
            pathGetter=self.theme.getPath,
            blocks=self.mapBlocks)
        gameType = 'solo'
        self.game = game = LocalGame(
            db, self.size[0], self.size[1], onceOnly=True,
            blockRatio=self.blockRatio,
            duration=self.duration * 60,
            level=level,
            gameType=gameType,
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
            rgame.connected(game.world.dumpEverything())
            self.uiAgent = agent = PandaUIAgent(self, rgame)
        else:
            self.tweener = LocalGameTweener(game)
            self.uiAgent = agent = PandaUIAgent(self, game)
        agent.onDisconnectRequest.addListener(self.stop)
        agent.onConnectionLost.addListener(self.stop)

        agent.show()

    def stop(self):
        self.game.stop()
        super(SoloTrosnothApp, self).stop()

    def startSSHManhole(self):
        namespace = self.getConsoleLocals()
        realm = manhole_ssh.TerminalRealm()

        # If we don't do this, the server will generate an exception when
        # you resize the SSH window
        realm.sessionFactory.windowChanged = lambda *args, **kwargs: None

        def getManhole(_):
            return Manhole(namespace)
        realm.chainedProtocolFactory.protocolFactory = getManhole
        p = portal.Portal(realm)

        # Username/Password authentication
        passwordDB = checkers.InMemoryUsernamePasswordDatabaseDontUse()
        passwordDB.addUser('trosnoth', '')
        p.registerChecker(passwordDB)

        factory = manhole_ssh.ConchFactory(p)

        manholePort = 6799
        try:
            reactor.listenTCP(manholePort, factory)
        except CannotListenError:
            log.error('Error starting manhole on port %d', manholePort)
        except ConchError as e:
            log.error('Error starting manhole on port %d: %s', manholePort,
                e.value)
        else:
            log.warning(
                'SSH manhole started on port %d with password ""', manholePort)


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
