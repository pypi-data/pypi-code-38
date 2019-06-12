#!/usr/bin/env python3

if __name__ == '__main__':
    # Make sure that this version of trosnoth is run.
    import os
    import sys
    sys.path.insert(0, os.path.join(
        os.path.abspath(os.path.dirname(__file__)), '..', '..'))

    # Install the asyncio reactor as early as possible
    import asyncio
    from twisted.internet import asyncioreactor
    asyncioreactor.install(asyncio.get_event_loop())

    # Init django environment for database use
    import django
    os.environ.setdefault(
        'DJANGO_SETTINGS_MODULE', 'trosnoth.server.settings')
    django.setup()


import argparse
import logging
import os
import time

import simplejson
from twisted.internet import defer, reactor, task
from twisted.internet.error import ConnectionClosed
from twisted.internet.protocol import ClientCreator
from twisted.protocols import amp

from trosnoth import data
from trosnoth import dbqueue
from trosnoth.djangoapp.models import (
    TrosnothArena, User, TrosnothUser, TrosnothServerSettings,
)
from trosnoth.game import LocalGame
from trosnoth.gamerecording.stats import ServerGameStats
from trosnoth.levels.base import StandardLobbyLevel, ServerLobbySettings
from trosnoth.levels.catpigeon import CatPigeonLevel
from trosnoth.levels.defencedrill import DefenceDrillLevel
from trosnoth.levels.elephantking import ElephantKingLevel
from trosnoth.levels.freeforall import FreeForAllLevel
from trosnoth.levels.hunted import HuntedLevel
from trosnoth.levels.orbchase import OrbChaseLevel
from trosnoth.levels.positioningdrill import PositioningDrillLevel
from trosnoth.levels.standard import StandardRandomLevel
from trosnoth.levels.trosball import RandomTrosballLevel
from trosnoth.manholehelper import AuthServerManholeHelper
from trosnoth.model.mapLayout import LayoutDatabase
from trosnoth.network.server import TrosnothServerFactory
from trosnoth.server import arenaamp
from trosnoth.utils import twistdebug
from trosnoth.utils.event import Event
from trosnoth.utils.utils import initLogging

log = logging.getLogger(__name__)

REPLAY_SUB_PATH = os.path.join(
    'authserver', 'public', 'trosnoth', 'replays')
INITIAL_LOBBY_SIZE = (2, 1)


def startManhole(*args, **kwargs):
    # 2018-01-30 Twisted for Python 3 doesn't yet have manhole support
    try:
        from trosnoth.network.manhole import startManhole as realStart
    except ImportError as e:
        log.warning('Error starting manhole: %s', e)
        return
    realStart(*args, **kwargs)


def startArena(arenaId, ampPort, token, manholePassword=None):
    manager = ArenaManager(arenaId)
    record = manager.getArenaRecord()
    if not record.enabled:
        raise RuntimeError('This arena is disabled')

    if record.profileSlowCalls:
        log.info('Initialising profiling of slow calls.')
        twistdebug.start(profiling=True)

    namespace = {
        'manager': manager,
        'helper': AuthServerManholeHelper(manager),
    }
    startManhole(0, namespace, manholePassword)

    reactor.callWhenRunning(manager.start, ampPort, token)
    reactor.run()


class AuthTagTracker(object):
    lifetime = 5

    def __init__(self):
        self.tags = {}      # auth tag -> timestamp, username

    def addTag(self, tag, username):
        self.tags[tag] = (time.time(), username)

    def getUsername(self, tag):
        created, username = self.tags.get(tag, (None, None))
        if username is None:
            return None
        if  created + self.lifetime < time.time():
            del self.tags[tag]
            return None
        return username

    def clean(self):
        threshold = time.time() - self.lifetime
        for tag, (created, username) in list(self.tags.items()):
            if created < threshold:
                del self.tags[tag]


class ActivityMonitor(object):
    def __init__(self, server, timeout=60):
        self.server = server
        self.timeout = timeout
        self.onInactive = Event([])

        server.onConnectionEstablished.addListener(
            self.gotConnectionEstablished)
        server.onConnectionLost.addListener(self.gotConnectionLost)
        self.timer = None

    def gotConnectionLost(self, protocol):
        self.cancelTimer()
        if not self.server.connectedClients:
            self.timer = reactor.callLater(self.timeout, self.onInactive)

    def gotConnectionEstablished(self, protocol):
        self.cancelTimer()

    def cancelTimer(self):
        if self.timer:
            self.timer.cancel()
            self.timer = None



class ArenaManager(object):
    def __init__(self, arenaId):
        self.arenaId = arenaId
        self.game = None
        self.server = None
        self.lobbySettings = None
        self.gameStats = None
        self.amp = None
        self.activityMonitor = None
        self.tagTracker = AuthTagTracker()

    def getArenaRecord(self):
        return TrosnothArena.objects.get(id=self.arenaId)

    @defer.inlineCallbacks
    def start(self, ampPort, token):
        task.LoopingCall(self.tagTracker.clean).start(5)

        gamePort = self.getArenaRecord().gamePort

        self.lobbySettings = ServerLobbySettings(self)
        self.game = LocalGame(
            layoutDatabase=LayoutDatabase(),
            saveReplay=True,
            gamePrefix='Server',
            replayPath=REPLAY_SUB_PATH,
            level=StandardLobbyLevel(INITIAL_LOBBY_SIZE, self.lobbySettings),
            lobbySettings=self.lobbySettings,
            serverInterface=ServerInterface(self),
            botProcess=True,
            botProcessLogPrefix=self.arenaId,
        )
        self.server = TrosnothServerFactory(self.game)
        self.server.startListening(gamePort)
        self.activityMonitor = ActivityMonitor(self.server)
        self.activityMonitor.onInactive.addListener(self.gotServerInactive)

        self.game.world.onSwitchStats.addListener(self._switchGameStats)

        yield self._startAMPConnection(ampPort, token)

        self.game.world.uiOptions.onDefaultUserInfoChange.addListener(
            self.gotUserLevelInfoChange)
        self.game.world.onPlayerAdded.addListener(self.gotPlayerAdded)
        self.game.world.onPlayerRemoved.addListener(self.gotPlayerRemoved)
        self.game.world.onPauseStateChanged.addListener(self.gotPauseChange)
        self.game.world.onStartMatch.addListener(self.gotStartMatch)

        log.info('Arena initialised')
        self.sendArenaInfo()

    @defer.inlineCallbacks
    def sendArenaInfo(self):
        # TODO: subscribe to events when these change
        args = {}
        args['status'] = self.game.world.getLevelStatus()
        args['players'] = sum(not p.bot for p in self.game.world.players)
        args['paused'] = self.game.world.paused
        try:
            yield self.amp.callRemote(arenaamp.ArenaInfoChanged, **args)
        except ConnectionClosed:
            pass

    def gotServerInactive(self):
        log.error('Shutting down due to inactivity')
        if reactor.running:
            reactor.stop()

    def gotUserLevelInfoChange(self, *args, **kwargs):
        self.sendArenaInfo()

    def gotPlayerAdded(self, *args, **kwargs):
        self.sendArenaInfo()

    def gotPlayerRemoved(self, *args, **kwargs):
        self.sendArenaInfo()

    def gotPauseChange(self, *args, **kwargs):
        self.sendArenaInfo()

    def gotStartMatch(self, *args, **kwargs):
        self.sendArenaInfo()

    def _switchGameStats(self, enabled, finished):
        if self.gameStats:
            if enabled:
                self.gameStats.resume()
            elif finished:
                # Stopping game
                self.gameStats.stopAndSave()
                self.gameStats = None
            else:
                self.gameStats.pause()

        elif self.game.world.scenarioManager.level is None:
            log.error('onSwitchStats called with no level set!!!')
        elif enabled:
            # Starting game
            self.gameStats = ServerGameStats(self.game, self.arenaId)

    @defer.inlineCallbacks
    def _startAMPConnection(self, ampPort, token, host='127.0.0.1'):
        self.amp = yield ClientCreator(
            reactor, AuthAMPProtocol, self).connectTCP(
            host, ampPort, timeout=5)
        yield self.amp.callRemote(arenaamp.ArenaListening, token=token)


class ServerInterface(object):
    def __init__(self, arenaManager):
        self._arenaManager = arenaManager

    def getUserFromAuthTag(self, authTag):
        username = self._arenaManager.tagTracker.getUsername(authTag)
        if username:
            return TrosnothUser.fromUser(username=username)
        return None

    def checkUsername(self, username):
        try:
            TrosnothUser.fromUser(username=username)
        except User.DoesNotExist:
            return False
        return True

    def getElephantName(self):
        settings = TrosnothServerSettings.get()
        return settings.elephantName


class AuthAMPProtocol(amp.AMP):
    '''
    Connects to authserver.ArenaAMPProtocol.
    '''

    def __init__(self, arenaManager, *args, **kwargs):
        super(AuthAMPProtocol, self).__init__(*args, **kwargs)
        self.arenaManager = arenaManager

    @arenaamp.RegisterAuthTag.responder
    def registerAuthTag(self, username, authTag):
        self.arenaManager.tagTracker.addTag(authTag, username)
        return {}

    @arenaamp.SetArenaInfo.responder
    def setArenaInfo(self, paused=None, teamAbilityJSON=None, action=None):
        world = self.arenaManager.game.world
        if paused is not None:
            if paused ^ world.paused:
                world.pauseOrResumeGame()
        if teamAbilityJSON is not None:
            for teamIndex, abilities in simplejson.loads(
                    teamAbilityJSON).items():
                team = world.teams[int(teamIndex)]
                if 'caps' in abilities:
                    team.abilities.set(zoneCaps=abilities['caps'])
                if 'shots' in abilities:
                    team.abilities.set(aggression=abilities['shots'])

        if action == 'lobby':
            world = self.arenaManager.game.world
            world.returnToLobby()

        return {}

    @arenaamp.StartLevel.responder
    def startLevel(self, infoJSON):
        levelInfo = simplejson.loads(infoJSON)

        levelClass, fullyConfigurable = LEVELS[levelInfo['scenario']]
        if fullyConfigurable:
            level = levelClass(
                halfMapWidth=levelInfo['half_width'],
                mapHeight=levelInfo['height'],
                duration=levelInfo['duration'],
            )
        else:
            level = levelClass(duration=levelInfo['duration'])

        world = self.arenaManager.game.world
        world.voteArbiter.startHumansVsMachinesGame(level)
        return {}


LEVELS = {
    'standard': (StandardRandomLevel, True),
    'trosball': (RandomTrosballLevel, True),
    'catpigeon': (CatPigeonLevel, False),
    'freeforall': (FreeForAllLevel, False),
    'hunted': (HuntedLevel, False),
    'orbchase': (OrbChaseLevel, False),
    'elephantking': (ElephantKingLevel, False),
    'defencedrill': (DefenceDrillLevel, True),
    'positioningdrill': (PositioningDrillLevel, True),
}


def getParser():
    parser = argparse.ArgumentParser()
    parser.add_argument('arenaId')
    parser.add_argument('ampPort', type=int)
    parser.add_argument(
        '--profile', action='store_true',
        help='dump kcachegrind profiling data to arena?.log')
    parser.add_argument(
        '--password', action='store', dest='manholePassword', default=None,
        help='the password to use for the manhole')
    return parser


def main():
    parser = getParser()
    args = parser.parse_args()
    token = input().encode('ascii')

    if os.name == 'nt':
        logpath = data.getPath(data.user, 'authserver', 'logs')
        data.makeDirs(logpath)
        initLogging(logFile=os.path.join(
            logpath, 'arenalog{}.txt'.format(args.arenaId)))
    else:
        initLogging(prefix='[{}] '.format(args.arenaId))

    dbqueue.init()

    if args.profile:
        from trosnoth.utils.profiling import profilingOutput
        with profilingOutput('arena{}.log'.format(args.arenaId)):
            startArena(args.arenaId, args.ampPort, token, args.manholePassword)
    else:
        startArena(args.arenaId, args.ampPort, token, args.manholePassword)


if __name__ == '__main__':
    main()
