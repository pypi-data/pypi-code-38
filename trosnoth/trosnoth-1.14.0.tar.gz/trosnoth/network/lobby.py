# Trosnoth (UberTweak Platform Game)
# Copyright (C) 2006-2012 Joshua D Bartlett
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# version 2 as published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301, USA.

import getpass
import logging
import socket

import simplejson

from trosnoth import rsa
from trosnoth.const import MULTICAST_PROTOCOL_NAME
from trosnoth.network import authcommands
from trosnoth.network.client import TrosnothClientProtocol
from trosnoth.network.networkDefines import (
    validServerVersions, multicastPort, multicastGroup,
)
from trosnoth.settings import getPolicySettings
from trosnoth.utils.unrepr import unrepr
from twisted.internet.error import CannotListenError
from twisted.internet import reactor, defer
from twisted.internet.protocol import ClientCreator, DatagramProtocol
from twisted.protocols import amp
from trosnoth.utils.twist import WeakCallLater

log = logging.getLogger(__name__)


class PasswordGetter(object):
    '''
    Interface for password getters, which must be used as a parameter to
    lobby.Game.join() below.
    '''
    def getPassword(self, host, errorText=''):
        '''
        Returns a deferred whose callback will be executed with (create,
        username, password), where create is a boolean indicating whether the
        account should be created. If the user cancels the getPassword(), the
        deferred's callback will be executed with an argument of None.

        @errorText: Should be provided if the previous password was invalid or
                the host refused to create a user.
        '''


class Game(object):
    '''
    Base class for lobby.Game objects.
    '''
    name = 'Unnamed game'

    def join(self, passwordGetter):
        '''
        Connects to the game and returns a deferred whose callback will be
        executed with (trosnothClient, authTag).
        @param passwordGetter: an object satisfying the PasswordGetter
            interface, used if authentication is needed to join this game.
        '''

    @defer.inlineCallbacks
    def connectToGameServer(self, host, port, timeout=5):
        cc = ClientCreator(reactor, TrosnothClientProtocol)

        trosnothClient = yield cc.connectTCP(host, port, timeout=timeout)
        settings = yield trosnothClient.getSettings()

        defer.returnValue((trosnothClient, settings))


class AuthenticationCancelled(Exception):
    '''
    Raised in Game.join() if authentication was required and the user cancelled
    the password dialogue box.
    '''


class AuthGame(Game):
    def __init__(self, lobby, server, game_id, name):
        self.lobby = lobby
        self.server = server
        self.id = game_id
        self.name = name

    @defer.inlineCallbacks
    def join(self, passwordGetter):
        '''
        Attempts to connect to this game. Returns a deferred whose
        callback will be executed with (trosnothClient, authTag).
        '''
        log.info('Attempting to join game on %r', self.server)
        host, port = self.server
        p = yield ClientCreator(reactor, amp.AMP).connectTCP(host, port)
        log.info('Connection established')

        try:
            if getPolicySettings().get(
                    'privacy', 'sendusername', fallback=False):
                yield p.callRemote(
                    authcommands.LocalUsername, username=getpass.getuser())

            result = yield p.callRemote(authcommands.ConnectToGame, id=self.id)
        except authcommands.NotAuthenticated:
            log.info('Not authenticated')
            yield authenticate(p, host, passwordGetter)

            log.info('Retrying')
            result = yield p.callRemote(authcommands.ConnectToGame, id=self.id)
        finally:
            if p.transport.connected:
                p.transport.loseConnection()

        log.info('Done')

        trosnothClient, settings = (
            yield self.connectToGameServer(host, result['port']))
        log.info('Got trosnothClient')
        self.lobby.app.identitySettings.setNick(result['nick'])
        defer.returnValue((trosnothClient, settings, result['authTag']))


class NonAuthGame(Game):
    def __init__(self, lobby, ipAddr, port):
        self.lobby = lobby
        self.ip = ipAddr
        self.port = port

    @defer.inlineCallbacks
    def join(self, passwordGetter):
        '''
        Attempts to connect to the given lobby.Game. Returns a deferred whose
        callback will be executed with (trosnothClient, authTag).
        '''
        trosnothClient, settings = (
            yield self.connectToGameServer(self.ip, self.port))
        defer.returnValue((trosnothClient, settings, 0))


class IncorrectServerVersion(Exception):
    '''
    The server created a game of the wrong version.
    '''


class AuthServerConnection(object):
    def __init__(self, server, timeout=5):
        self.host, self.port = server
        self.timeout = timeout
        self.protocol = None

    def __enter__(self):
        d = ClientCreator(reactor, amp.AMP).connectTCP(
            self.host, self.port, timeout=self.timeout)
        d.addCallback(self.connectionEstablished)
        return d

    def connectionEstablished(self, protocol):
        self.protocol = protocol
        return protocol

    def __exit__(self, exc_type, exc_value, exc_tb):
        if self.protocol and self.protocol.transport.connected:
            self.protocol.transport.loseConnection()


class Lobby(object):
    '''
    Performs tasks related to finding games and joining them.
    '''
    def __init__(self, app):
        self.app = app

    @defer.inlineCallbacks
    def getGames(self, server, timeout=2):
        '''
        Connects to an authentication server and asks it for the
        available games on that server. Returns a deferred whose
        callback will be executed with a list of lobby.Game objects.

        :param server: A tuple of (host, port)
        :param timeout: seconds before attempt is canceled
        '''
        with AuthServerConnection(server, timeout) as deferred:
            p = yield deferred

            result = yield p.callRemote(authcommands.ListGames)
            games = []
            for item in result['games']:
                if (item['game'] == 'Trosnoth1' and item['version'] in
                        validServerVersions):
                    games.append(
                        AuthGame(self, server, item['id'], item['name']))

            defer.returnValue(games)

    @defer.inlineCallbacks
    def get_adhoc_lan_games(self):
        '''
        Returns a deferred which will be called back with a sequence of Game
        objects representing the games which could be found on the LAN by
        multicasting a game request.
        '''
        games = yield getMulticastGames()

        result = []
        for (ip, port), gameInfo in games:
            result.append(NonAuthGame(self, ip, port))
        defer.returnValue(result)


@defer.inlineCallbacks
def authenticate(p, host, passwordGetter):
    errorMsg = ''
    for i in range(15):
        if host in AUTHENTICATION_CACHE:
            log.info('Got cached auth info')
            create = False
            username, password = AUTHENTICATION_CACHE[host]
        else:
            log.info('Checking with password getter')
            result = yield passwordGetter.getPassword(host, errorMsg)
            if result is None:
                raise AuthenticationCancelled()
            create, username, password = result

        data = yield encryptPassword(p, password)

        if create:
            log.info('Creating user')
            result = yield p.callRemote(
                    authcommands.CreateUserWithPassword,
                    username=str(username), password=data)
            result = result['result']
            if result == '':
                log.info('Auth successful')
                return  # Authentication successful.
            errorMsg = result
        else:
            log.info('Attempting to auth')
            result = yield p.callRemote(
                authcommands.PasswordAuthenticate,
                username=str(username), password=data)
            result = result['result']
            if result:
                log.info('Auth successful')
                return  # Authentication successful.
            errorMsg = 'Bad username/password'

    # If we can't get the authentication right in 15 tries, something is
    # wrong.
    raise AuthenticationCancelled()


@defer.inlineCallbacks
def encryptPassword(p, password):
    log.info('Getting auth token')
    token = yield p.callRemote(authcommands.GetAuthToken)
    token = token['token']

    log.info('Getting server public key')
    pubkey = yield p.callRemote(authcommands.GetPublicKey)
    pubkey = makePublicKey(pubkey)

    defer.returnValue(rsa.encrypt(token + password.encode('utf-8'), pubkey))


AUTHENTICATION_CACHE = {}   # host -> (username, password)


def makePublicKey(result):
    '''
    Takes the result of the GetPublicKey amp call and converts it into a public
    key which the rsa module can handle.
    '''
    return result


class UDPMulticaster(object):
    def __init__(self, gameGetter):
        self.stopped = False
        self.port = None
        self.listener = UDPMulticastListener(gameGetter)
        self.tryListening()

    def stop(self):
        if self.port is not None:
            self.port.stopListening()
        self.stopped = True

    def tryListening(self):
        if self.stopped:
            return
        try:
            self.port = reactor.listenMulticast(multicastPort, self.listener)
        except CannotListenError:
            # Cannot listen to the multicast, possibly because another
            # instance is running on this computer.

            # Try listening again in 5 seconds.
            WeakCallLater(5, self, 'tryListening')


class UDPMulticastListener(DatagramProtocol):
    def __init__(self, gameGetter):
        '''
        gameGetter must be callable, and return a sequence of game information
        dicts, each of which must contain:
            ['port'] - the port this game is listening on
            ['version'] - the version string
            ['name'] - the game name
        '''
        self.getGames = gameGetter

    def startProtocol(self):
        # Join the correct multicast group.
        self.transport.joinGroup(multicastGroup)

    def datagramReceived(self, datagram, address):
        '''
        A multicast datagram has been received.
        '''
        if datagram == b'%s:GetGames' % (MULTICAST_PROTOCOL_NAME,):
            for game in self.getGames():
                self.transport.write(
                    b'%s:Game:%s' % (MULTICAST_PROTOCOL_NAME, repr(game),),
                    address)


class UDPMulticastGameGetter(DatagramProtocol):
    def __init__(self):
        self.port = reactor.listenUDP(0, self)
        self._deferred = None
        self._games = []

    def stop(self):
        self.port.stopListening()

    def getGames(self, timeout=1):
        '''
        Returns a deferred which will be called back with a sequence of
        (address, info) where info is a dict which has:
            ['name'] - the name of the game
            ['version'] - the version string of the game
        '''
        d = defer.Deferred()
        try:
            self.transport.write(
                b'%s:GetGames' % MULTICAST_PROTOCOL_NAME,
                (multicastGroup, multicastPort))
        except socket.error as e:
            log.info('Could not request games from multicast: %s', e)
            d.callback([])
            return d

        self._deferred = d
        self._games = []

        WeakCallLater(timeout, self, '_gotGames', d)

        return d

    def _gotGames(self, d):
        d.callback(self._games)
        self._deferred = None
        self._games = []

    def datagramReceived(self, datagram, address):
        '''
        A reply to our query has been received.
        '''
        if self._deferred is None:
            return
        if datagram.startswith(b'%s:Game:' % (MULTICAST_PROTOCOL_NAME,)):
            gameInfo = unrepr(
                datagram[len(b'%s:Game:' % (MULTICAST_PROTOCOL_NAME,)):])
            gameAddress = (address[0], gameInfo.pop('port'))
            self._games.append((gameAddress, gameInfo))


class UDPMulticastServerGetter(DatagramProtocol):
    def __init__(self, timeout=1):
        self.timeout = timeout
        self.port = None
        self._deferred = None

    def stop(self):
        self.port.stopListening()

    def get_server(self):
        '''
        Returns a deferred which will be called back with a (host,
        port) tuple, or None.
        '''
        self.port = reactor.listenUDP(0, self)
        self._deferred = defer.Deferred()
        try:
            self.transport.write(
                b'%s:GetServer' % MULTICAST_PROTOCOL_NAME,
                (multicastGroup, multicastPort))
        except socket.error as e:
            log.info('Could not request games from multicast: %s', e)
            self._deferred.callback(None)
        else:
            WeakCallLater(self.timeout, self, 'timed_out')
        return self._deferred

    def timed_out(self):
        if self._deferred is not None:
            self.finish(None)

    def datagramReceived(self, datagram, address):
        '''
        A reply to our query has been received.
        '''
        if self._deferred is None:
            return

        if not datagram.startswith(b'%s:Server:' % (MULTICAST_PROTOCOL_NAME,)):
            return

        auth_port = simplejson.loads(
            datagram[len(b'%s:Server:' % (MULTICAST_PROTOCOL_NAME,)):])
        if not isinstance(auth_port, int):
            return
        server = (address[0], auth_port)
        self.finish(server)

    def finish(self, result):
        self.stop()
        d, self._deferred = self._deferred, None
        d.callback(result)


def getMulticastGames(timeout=1):
    getter = UDPMulticastGameGetter()
    d = getter.getGames(timeout)
    @d.addCallback
    def gotGames(games):
        getter.stop()
        return games
    return d


def get_multicast_server(timeout=1):
    return UDPMulticastServerGetter(timeout).get_server()
