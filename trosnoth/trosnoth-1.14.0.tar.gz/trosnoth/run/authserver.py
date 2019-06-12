if __name__ == '__main__':
    # Install the asyncio reactor as early as possible
    import asyncio
    from twisted.internet import asyncioreactor
    asyncioreactor.install(asyncio.get_event_loop())

import datetime
import functools
from hashlib import sha1
import logging
import os
import pickle
import random
import sys
import uuid
import webbrowser

from django.contrib.auth import authenticate
from django.core import management
import simplejson
from twisted.internet import reactor, defer
from twisted.internet.error import CannotListenError
from twisted.internet.protocol import (
    Factory, ProcessProtocol, DatagramProtocol,
)
from twisted.protocols import amp
from twisted.python.failure import Failure

from trosnoth import data, dbqueue, rsa
from trosnoth.const import MULTICAST_PROTOCOL_NAME
from trosnoth.data import getPath, makeDirs
from trosnoth.djangoapp.models import (
    User, TrosnothUser, TrosnothArena, TrosnothServerSettings,
)
from trosnoth.network import authcommands
from trosnoth.network.networkDefines import (
    serverVersion, multicastGroup, multicastPort,
)
from trosnoth.server import arenaamp
from trosnoth.settings import AuthServerSettings
from trosnoth.utils.event import Event
from trosnoth.utils.utils import initLogging
from trosnoth.web.server import startWebServer

log = logging.getLogger(__name__)

MAX_GAMES = 1
GAME_KIND = 'Trosnoth1'


def startManhole(*args, **kwargs):
    # Manhole is non-essential so don't explode if we're using a Twisted version that doesn't have it
    try:
        from trosnoth.network.manhole import startManhole as realStart
    except ImportError as e:
        log.warning('Error starting manhole: %s', e)
        return
    realStart(*args, **kwargs)


class AuthenticationProtocol(amp.AMP):
    '''
    Trosnoth authentication server which is used when running a game server
    which keeps track of users.
    '''

    def connectionMade(self):
        super(AuthenticationProtocol, self).connectionMade()
        self.user = None
        self.token = None
        log.info('New connection.')

    def connectionLost(self, reason):
        log.info('Connection lost.')

    @authcommands.GetPublicKey.responder
    def getPublicKey(self):
        return {
            'e': self.factory.pubKey['e'],
            'n': self.factory.pubKey['n'],
        }

    @authcommands.ListGames.responder
    def listGames(self):
        result = {
            'games': [{
                'id': arena.id,
                'game': GAME_KIND,
                'version': serverVersion,
                'name': arena.name,
            } for arena in TrosnothArena.objects.all() if arena.enabled]
        }
        return result

    @authcommands.ListOtherGames.responder
    def listOtherGames(self):
        # Older version of Trosnoth used this command
        return {'games': []}

    @authcommands.RegisterGame.responder
    def registerGame(self, game, version, port):
        # Older version of Trosnoth used this command
        return {}

    @authcommands.CreateGame.responder
    def createGame(self, game):
        raise authcommands.CannotCreateGame()

    @authcommands.ConnectToGame.responder
    @defer.inlineCallbacks
    def connectToGame(self, id):
        if self.user is None:
            raise authcommands.NotAuthenticated()

        try:
            arenaProxy = yield self.factory.getArena(id, start=True)
        except (TrosnothArena.DoesNotExist, GameIsDisabled):
            raise authcommands.GameDoesNotExist()

        authTag = random.randrange(2**64)
        yield arenaProxy.amp.callRemote(
            arenaamp.RegisterAuthTag,
            username=self.user.username, authTag=authTag)
        nick = self.user.getNick()

        defer.returnValue({
            'port': arenaProxy.port,
            'authTag': authTag,
            'nick': nick,
        })

    @authcommands.GetSupportedSettings.responder
    def getSupportedSettings(self):
        settings = ['password']
        return {
            'result': settings,
        }

    @authcommands.SetPassword.responder
    def setUserPassword(self, password):
        if self.user is None:
            raise authcommands.NotAuthenticated()
        password = self._decodePassword(password)
        self.user.setPassword(password)
        return {}

    @authcommands.GetAuthToken.responder
    def getAuthToken(self):
        self.token = b''.join(bytes([random.randrange(256)]) for i in range(16))
        return {
            'token': self.token
        }

    @authcommands.PasswordAuthenticate.responder
    def passwordAuthenticate(self, username, password):
        username = username.lower()
        password = self._decodePassword(password)
        if password is None:
            return {'result': False}    # Bad auth token used.

        d = self.factory.authManager.authenticateUser(username, password)

        @d.addCallback
        def authSucceeded(user):
            self.user = user
            return {'result': True}

        @d.addErrback
        def authFailed(failure):
            return {'result': False}

        return d

    @authcommands.LocalUsername.responder
    def gotClientUsername(self, username):
        user = self.factory.authManager.noteClientUsername(username)
        if user:
            self.user = user
        return {}

    @authcommands.CreateUserWithPassword.responder
    def createUserWithPassword(self, username, password):
        if self.factory.settings.allowNewUsers:
            nick = username
            username = username.lower()
            password = self._decodePassword(password)
            if password is None:
                return {'result': 'Authentication token failure.'}

            authMan = self.factory.authManager
            if authMan.checkUsername(username):
                return {'result': 'That username is taken.'}
            self.user = authMan.createUser(username, password, nick)
        else:
            return {'result': self.factory.settings.privateMsg}
        return {'result': ''}

    def _decodePassword(self, passwordFromWire):
        if self.token is None:
            return None
        token, self.token = self.token, None
        passwordData = rsa.decrypt(passwordFromWire, self.factory.privKey)
        if passwordData[:len(token)] != token:
            return None
        return passwordData[len(token):].decode('utf-8')

SALT = b'Trosnoth'


class AuthManager(object):
    '''
    Manages user accounts on the system.
    '''

    def __init__(self, dataPath):
        self.dataPath = dataPath
        self.tags = {}      # auth tag -> user id
        self.settings = AuthServerSettings(dataPath)

    def checkUsername(self, username):
        '''
        Returns True or False, depending on whether the given username is
        already in use.
        '''
        try:
            TrosnothUser.fromUser(username=username)
        except User.DoesNotExist:
            return False
        return True

    def noteClientUsername(self, username):
        '''
        Do nothing, unless the "Trust client usernames" setting is switched on.
        Returns a Trosnoth user, or None.
        '''
        settings = TrosnothServerSettings.get()
        if not settings.trustClientUsernames:
            return None

        username = username.lower()
        try:
            trosnothUser = TrosnothUser.fromUser(username=username)
        except User.DoesNotExist:
            user = self.createUser(username, None)
        else:
            if not trosnothUser.user.is_active:
                return None
            user = AuthenticatedUser(self, username)

        user.seen()
        return user

    def authenticateUser(self, username, password):
        '''
        If a username exists with the given password, returns the user,
        otherwise returns None.
        '''
        username = username.lower()
        try:
            trosnothUser = TrosnothUser.fromUser(username=username)
        except User.DoesNotExist:
            return defer.fail()

        if not trosnothUser.oldPasswordHash:
            # Just use Django auth
            djangoUser = authenticate(username=username, password=password)
            if djangoUser is None:
                return defer.fail(ValueError('Authentication failed'))
            if not djangoUser.is_active:
                return defer.fail(ValueError('User deactivated'))
            user = AuthenticatedUser(self, username)
        else:
            # Old Trosnoth auth, only exists for backward compatibility
            hash1 = sha1(SALT + password.encode('utf-8')).digest()
            hash2 = bytes(trosnothUser.oldPasswordHash)
            if hash1 != hash2:
                return defer.fail(ValueError('Incorrect password'))

            # Put the password into Django
            trosnothUser.user.set_password(password)
            trosnothUser.user.save()
            trosnothUser.oldPasswordHash = b''
            trosnothUser.save()

            user = AuthenticatedUser(self, username)

        user.seen()
        return defer.succeed(user)

    def createUser(self, username, password, nick=None):
        username = username.lower()
        if self.checkUsername(username):
            raise ValueError('user %r already exists' % (username,))
        User.objects.create_user(username, password=password)

        user = AuthenticatedUser(self, username)
        user.setPassword(password)
        user.seen()
        if nick is not None:
            user.setNick(nick)
        return user

    def getNick(self, username):
        return TrosnothUser.fromUser(username=username).nick


class AuthenticationFactory(Factory):
    protocol = AuthenticationProtocol
    authManagerClass = AuthManager
    instance = None

    def __init__(self, dataPath=None, manholePassword=None):
        if dataPath is None:
            dataPath = getPath(data.user, 'authserver')
        makeDirs(dataPath)
        self.dataPath = dataPath
        self.manholePassword=None

        self.authManager = self.authManagerClass(dataPath)
        self.pubKey, self.privKey = self.loadKeys()
        self.arenaProxies = {}
        self.arenaAMPListener = None
        self.adminTokens = set()

        self.onArenaStarting = Event(['proxy'])
        self.onArenaStopped = Event(['proxy'])

        AuthenticationFactory.instance = self

    @property
    def settings(self):
        return self.authManager.settings

    def loadKeys(self):
        '''
        Loads public and private keys from disk or creates them and saves them.
        '''
        keyPath = os.path.join(self.dataPath, 'keys')
        try:
            with open(keyPath, 'rb') as f:
                pub, priv = pickle.load(f)
        except IOError:
            pub, priv = rsa.newkeys(self.settings.keyLength)
            pickle.dump((pub, priv), open(keyPath, 'wb'), 2)

        return pub, priv

    @defer.inlineCallbacks
    def getArena(self, arenaId, start=False):
        if not isinstance(arenaId, int):
            raise TypeError(
                'Expected numeric arenaId, not {!r}'.format(arenaId))
        try:
            result = self.arenaProxies[arenaId]
        except KeyError:
            if not start:
                raise
            result = ArenaProcessProtocol(
                arenaId, token=self.getNewArenaToken(),
            )
            if not result.processDied:
                self.arenaProxies[arenaId] = result
                result.onExit.addListener(self._arenaExited)
                self.onArenaStarting(result)
            log.error('Starting arena #%s', arenaId)
            yield result.start(self.getArenaAMPPort(), self.manholePassword)
        else:
            if not result.ready:
                yield result.onReady.waitOrRaise()
        defer.returnValue(result)

    def _arenaExited(self, proxy, reason):
        log.error('Arena #%s exited', proxy.arenaId)
        if self.arenaProxies.get(proxy.arenaId):
            del self.arenaProxies[proxy.arenaId]
            self.onArenaStopped(proxy)
        proxy.onExit.removeListener(self._arenaExited)

    @defer.inlineCallbacks
    def teardown(self):
        # Give a fraction of a second for the message to get through
        # the the children have ended, then send a kill signal.
        d = defer.Deferred()
        reactor.callLater(0.1, d.callback, None)
        yield d

        yield defer.DeferredList([
            p.killProcess() for p in list(self.arenaProxies.values())])

    def getNewArenaToken(self):
        if self.arenaAMPListener is None or \
                self.arenaAMPListener.disconnecting:
            self.startArenaAMPListener()
        return uuid.uuid4().hex.encode('ascii')

    def matchArenaToken(self, ampProtocol, token):
        for arenaProxy in list(self.arenaProxies.values()):
            if arenaProxy.token and arenaProxy.token == token:
                ampProtocol.arena = arenaProxy
                arenaProxy.matchedToken(ampProtocol)
                if not any(p.token for p in list(self.arenaProxies.values())):
                    self.stopArenaAMPListener()
                return True
        return False

    def getArenaAMPPort(self):
        return self.arenaAMPListener.getHost().port

    def startArenaAMPListener(self, port=0, interface='127.0.0.1'):
        factory = Factory.forProtocol(ArenaAMPProtocol)
        factory.authFactory = self
        self.arenaAMPListener = reactor.listenTCP(
            port, factory, interface=interface)
        factory.stopFactory = functools.partial(
            self._arenaAMPFactoryStopped, self.arenaAMPListener)

    def stopArenaAMPListener(self):
        if self.arenaAMPListener and not self.arenaAMPListener.disconnecting:
            self.arenaAMPListener.stopListening()

    def _arenaAMPFactoryStopped(self, listener):
        if listener == self.arenaAMPListener:
            self.arenaAMPListener = None

    @defer.inlineCallbacks
    def getArenaInfo(self, arenaId):
        try:
            arena = yield self.getArena(arenaId)
        except KeyError:
            arenaRecord = TrosnothArena.objects.get(id=arenaId)
            if not arenaRecord.enabled:
                status = 'DISABLED'
            else:
                status = 'not running'

            defer.returnValue({
                'status': status,
                'paused': False,
                'players': 0,
                'blue': {'shots': True, 'caps': True},
                'red': {'shots': True, 'caps': True},
            })

        defer.returnValue({
            'status': arena.status,
            'paused': arena.paused,
            'players': arena.players,
            'blue': arena.teamInfo[0],
            'red': arena.teamInfo[1],
        })

    @defer.inlineCallbacks
    def setArenaInfo(self, arenaId, info):
        try:
            arena = yield self.getArena(arenaId)
        except KeyError:
            return

        if info.get('action') == 'shutdown':
            yield arena.killProcess()
            return

        yield arena.setInfo(info)

    @defer.inlineCallbacks
    def startLevel(self, arenaId, levelInfo):
        try:
            arena = yield self.getArena(arenaId)
        except KeyError:
            return

        yield arena.amp.callRemote(
            arenaamp.StartLevel,
            infoJSON=simplejson.dumps(levelInfo),
        )

    def getAdminToken(self):
        token = uuid.uuid4().hex
        self.adminTokens.add(token)
        return token

    def revokeAdminToken(self, token):
        self.adminTokens.discard(token)

    def useAdminToken(self, token):
        if token not in self.adminTokens:
            return False
        self.revokeAdminToken(token)
        return True


class GameIsDisabled(Exception):
    pass


class ArenaProcessProtocol(ProcessProtocol):
    def __init__(self, arenaId, token):
        self.arenaId = arenaId
        self.token = token
        self.amp = None
        self.port = None
        self.processDied = False
        self.startCalled = False
        self.ready = False
        self.onReady = Event(['result'])
        self.onExit = Event(['protocol', 'reason'])
        self.onInfoChanged = Event(['proxy'])

        self.status = 'starting up...'
        self.players = 0
        self.paused = False
        self.teamInfo = [
            {'shots': True, 'caps': True},
            {'shots': True, 'caps': True},
        ]

    def start(self, ampPort, manholePassword=None):
        if self.startCalled:
            raise RuntimeError('Cannot start ArenaProcessProtocol twice')
        self.startCalled = True
        result = self.onReady.waitOrRaise()

        arenaRecord = TrosnothArena.objects.get(id=self.arenaId)
        if not arenaRecord.enabled:
            raise GameIsDisabled('This arena is disabled')
        self.port = arenaRecord.gamePort

        cmd = self.getArenaCommand() + [str(self.arenaId), str(ampPort)]
        if manholePassword:
            cmd.extend(['--password', manholePassword])
        reactor.spawnProcess(
            self, cmd[0], cmd, env=None,
            childFDs=None if os.name == 'nt' else {0: 'w', 1: 1, 2: 2})
        return result

    def recordInfoChange(self, status=None, players=None, paused=None):
        if status is not None:
            self.status = status
        if players is not None:
            self.players = players
        if paused is not None:
            self.paused = paused
        self.onInfoChanged(self)

    @defer.inlineCallbacks
    def setInfo(self, info):
        teams = {'blue': 0, 'red': 1}
        teamAbilities = {}
        for team, abilities in info['teamAbilities'].items():
            teamIndex = teams[team]
            teamAbilities[teamIndex] = abilities
            self.teamInfo[teamIndex].update(abilities)
        yield self.amp.callRemote(
            arenaamp.SetArenaInfo,
            paused=info['paused'],
            teamAbilityJSON=simplejson.dumps(teamAbilities),
            action=info['action'],
        )

    @staticmethod
    def getArenaCommand():
        if getattr(sys, 'frozen', False):
            # Bundled by PyInstaller
            path = os.path.dirname(sys.executable)
            ext = '.exe' if os.name == 'nt' else ''
            return [os.path.join(path, 'support' + ext), 'arena']

        import trosnoth.server
        path = os.path.dirname(trosnoth.server.__file__)
        return [sys.executable, os.path.join(path, 'arena.py')]

    def matchedToken(self, ampProtocol):
        if self.processDied:
            return
        self.token = None
        self.amp = ampProtocol
        self.ready = True
        self.onReady(None)

    @defer.inlineCallbacks
    def connectionMade(self):
        self.processDied = False
        self.ready = False
        self.transport.write(self.token + b'\n')

        for i in range(30):
            d = defer.Deferred()
            reactor.callLater(0.5, d.callback, None)
            yield d

            if self.ready:
                return
            if self.processDied:
                break

        self.killProcess()

        self.onReady(Failure(
            RuntimeError('Child process did not complete initialisation')))

    @defer.inlineCallbacks
    def killProcess(self):
        try:
            if self.processDied:
                return

            self.transport.signalProcess('TERM')

            for i in range(3):
                d = defer.Deferred()
                reactor.callLater(1, d.callback, None)
                yield d
                if self.processDied:
                    return

            self.transport.signalProcess('KILL')
        except Exception:
            log.exception('Error while killing child process')

    def ampConnectionLost(self):
        if not self.processDied:
            log.warning('Lost AMP connection to arena #%s', self.arenaId)
            self.killProcess()

    def processExited(self, reason):
        self.processDied = True
        self.onExit(self, reason)


class ArenaAMPProtocol(amp.AMP):
    '''
    Local AMP connection from Arena process.
    '''
    arena = None

    def connectionMade(self):
        super(ArenaAMPProtocol, self).connectionMade()
        self.authFactory = self.factory.authFactory

    def connectionLost(self, reason):
        if self.arena:
            self.arena.ampConnectionLost()

    def locateResponder(self, name):
        '''
        Overriden to refuse all commands that arrive before ArenaListening.
        '''
        if self.arena is not None:
            # Pass through to super from now on.
            self.locateResponder = super(ArenaAMPProtocol, self).locateResponder
            return self.locateResponder(name)
        if name == b'ArenaListening':
            return super(ArenaAMPProtocol, self).locateResponder(name)
        return self.notYetListening

    def notYetListening(self, *args, **kwargs):
        raise arenaamp.NotYetListening()

    @arenaamp.ArenaListening.responder
    def arenaListening(self, token):
        if self.arena:
            raise arenaamp.AlreadyCalled()
        if not self.authFactory.matchArenaToken(self, token):
            self.transport.loseConnection()
        return {}

    @arenaamp.ArenaInfoChanged.responder
    def arenaInfoChanged(self, status=None, players=None, paused=None):
        self.arena.recordInfoChange(status, players, paused)
        return {}


class AuthenticatedUser(object):
    '''
    Represents a user which has been authenticated on the system.
    '''

    def __init__(self, authManager, username):
        self.authManager = authManager
        self.username = username = username.lower()

    def __eq__(self, other):
        if (isinstance(other, AuthenticatedUser) and other.username ==
                self.username):
            return True
        return False

    def __hash__(self):
        return hash(self.username)

    def getNick(self):
        return TrosnothUser.fromUser(username=self.username).nick

    def setNick(self, nick):
        @dbqueue.add
        def writeNickToDB():
            user = TrosnothUser.fromUser(username=self.username)
            if nick != user.nick:
                user.nick = nick
                user.save()

    def setPassword(self, password):
        # Don't put DB write in a queue as user will expect it to take place
        # immediately.
        user = User.objects.get(username=self.username)
        user.set_password(password)
        user.save()
        trosnothUser = TrosnothUser.fromUser(pk=user.pk)
        trosnothUser.oldPasswordHash = b''
        trosnothUser.save()

    def seen(self):
        now = datetime.datetime.now()
        @dbqueue.add
        def writeSeenTimeToDB():
            user = TrosnothUser.fromUser(username=self.username)
            user.lastSeen = now
            user.save()


def startServer(dataPath=None, browser=False, safemode=False):

    # Ensure that any database migrations have happened
    management.call_command('migrate')

    # Load settings from database
    settings = TrosnothServerSettings.get()
    if safemode:
        authPort = 0
        manholePort = None
        webPort = 0
    else:
        authPort = settings.serverPort
        manholePort = settings.manholePort
        webPort = settings.webPort
    manholePassword = settings.manholePassword

    dbqueue.init()

    pf = AuthenticationFactory(dataPath, manholePassword)

    if manholePort is not None:
        namespace = {}
        namespace['authFactory'] = pf
        startManhole(manholePort, namespace, manholePassword)

    listeningPort = startWebServer(pf, webPort)
    log.warning('Started web server on port %d', listeningPort.getHost().port)
    if browser:
        reactor.callWhenRunning(openBrowser, pf, listeningPort)

    try:
        listeningPort = reactor.listenTCP(authPort, pf)
    except CannotListenError:
        log.error('Error listening on port %d.', authPort)
    else:
        log.warning(
            'Started Trosnoth authentication server on port %d.',
            listeningPort.getHost().port)

        start_multicast_listener(listeningPort.getHost().port)
        reactor.addSystemEventTrigger('before', 'shutdown', pf.teardown)
        reactor.run()


def start_multicast_listener(auth_port):
    listener = MulticastListener(auth_port)
    try:
        port = reactor.listenMulticast(multicastPort, listener)
    except CannotListenError:
        log.error(
            'Could not listen on multicast port to publicise server on LAN.')
        return

    log.warning('Started multicast listener.')
    reactor.addSystemEventTrigger('before', 'shutdown', port.stopListening)


class MulticastListener(DatagramProtocol):
    def __init__(self, auth_port):
        self.auth_port = auth_port

    def startProtocol(self):
        # Join the correct multicast group.
        self.transport.joinGroup(multicastGroup)

    def datagramReceived(self, datagram, address):
        if datagram == b'%s:GetServer' % (MULTICAST_PROTOCOL_NAME,):
            self.transport.write(b'%s:Server:%s' % (
                MULTICAST_PROTOCOL_NAME,
                simplejson.dumps(self.auth_port).encode(),
            ), address)


def openBrowser(authFactory, listeningPort):
    log.warning('Opening web browser...')
    token = authFactory.getAdminToken()
    if not webbrowser.open('http://127.0.0.1:{}/tokenauth?token={}'.format(
            listeningPort.getHost().port, token)):
        log.error('Could not open web browser!')
        authFactory.revokeAdminToken(token)


def main():
    from argparse import ArgumentParser
    parser = ArgumentParser(description='Trosnoth server')
    parser.add_argument(
        '-D', '--datapath', action='store', dest='dataPath', default=None,
        help='path to authentication server data and settings')
    parser.add_argument(
        '-d', '--debug', action='store_true', dest='debug',
        help='show debug-level messages on console')
    parser.add_argument(
        '-l', '--log-file', action='store', dest='logFile',
        help='file to write logs to')
    parser.add_argument(
        '--profile', action='store_true', dest='profile',
        help='dump kcachegrind profiling data to trosnoth.log')
    parser.add_argument(
        '--no-browser', action='store_false', dest='browser',
        help='do not attempt to launch a web browser for the UI')
    parser.add_argument(
        '--safemode', action='store_true',
        help='use safe values for all start-up settings')

    options = parser.parse_args()

    initLogging(options.debug, options.logFile)

    kwargs = dict(
        dataPath=options.dataPath,
        browser=options.browser,
        safemode=options.safemode,
    )

    if options.profile:
        runWithProfiling(**kwargs)
    else:
        startServer(**kwargs)


def runWithProfiling(**kwargs):
    import cProfile
    from trosnoth.utils.profiling import KCacheGrindOutputter
    prof = cProfile.Profile()

    try:
        prof.runcall(startServer, **kwargs)
    except SystemExit:
        pass
    finally:
        kg = KCacheGrindOutputter(prof)
        with open('server.log', 'wb') as f:
            kg.output(f)



if __name__ == '__main__':
    main()
