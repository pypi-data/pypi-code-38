import logging

from twisted.internet import defer
from twisted.internet.error import ConnectError, ConnectionRefusedError
from twisted.protocols import amp

from trosnoth.const import JOIN_LAN_GAME, JOIN_LOCAL_GAME
from trosnoth.network.lobby import (
    Lobby, AuthenticationCancelled,
)
from trosnoth.network import authcommands
from trosnoth.network.client import ConnectionFailed
from trosnoth.utils.event import Event


log = logging.getLogger(__name__)


class PlayConnector(object):
    '''
    Connects to the first available game based on the configured server
    settings.

    passwordGetFunction must be a function that satisfies the
    PasswordGetter.getPassword interface from trosnoth.network.lobby.

    hostGameQueryFunction must be a function that returns a deferred which
    prompts the user to decide whether to host a game and returns the user's
    decision.
    '''

    def __init__(
            self, app, onSucceed=None, onFail=None, onLogLine=None,
            passwordGetFunction=None, hostGameQueryFunction=None):
        self.app = app
        self.onSucceed = Event(listener=onSucceed)
        self.onFail = Event(listener=onFail)
        self.onLogLine = Event(listener=onLogLine)
        self.passwordGetFunction = passwordGetFunction
        self.hostGameQueryFunction = hostGameQueryFunction
        self.lobby = None
        self.badServers = set()
        self.cancelled = False
        self.running = False

    def getPassword(self, host, errorText=''):
        if self.passwordGetFunction is not None:
            return self.passwordGetFunction(host, errorText)
        return None

    @defer.inlineCallbacks
    def begin(self, servers, canHost=True):
        '''
        Attempts to connect to the given servers in turn, and if canHost is
        given will prompt the user to host a game if no other games are
        available.

        Calling this function will always trigger either onSucceed or onFail to
        be executed unless the user selects cancel.
        '''
        if self.running:
            raise RuntimeError('Already running')
        self.running = True

        self.cancelled = False
        self.badServers = set()
        if self.lobby is None:
            self.lobby = Lobby(self.app)

        for server in servers:
            if self.cancelled:
                break

            if server == JOIN_LOCAL_GAME:
                localGame = self.app.hoster.getGameObject()
                if localGame is not None:
                    self.onSucceed.execute()
                    self.app.connector.openGameObject(localGame)
                    self.running = False
                    return

            elif isinstance(server, tuple):
                host, port = server[:2]
                if (host, port) in self.badServers:
                    continue

                self.onLogLine(
                    'Requesting games from {}:{}...'.format(host, port))
                connected = yield self.attemptServerConnect(
                        self.lobby.getGames, (host, port))
                if connected:
                    self.running = False
                    return

            elif server == JOIN_LAN_GAME:
                self.onLogLine('Asking local network for other games...')
                games = yield self.lobby.get_adhoc_lan_games()
                for game in games:
                    joinSuccessful = yield self.attemptJoinGame(game)
                    if joinSuccessful:
                        self.running = False
                        return

        if canHost:
            if not self.cancelled:
                result = yield self.hostGameQueryFunction()

                if not result:
                    self.onFail.execute()
                    self.running = False
                    return

                self.app.hoster.startServer(halfMapWidth=2, mapHeight=1)
                self.onSucceed.execute()
                localGame = self.app.hoster.getGameObject()
                self.app.connector.openGameObject(localGame)
        else:
            if not self.cancelled:
                self.onFail.execute()

        self.running = False

    @defer.inlineCallbacks
    def attemptServerConnect(self, getGamesList, server):
        '''
        Attempts to connect to a game on the server, returned by
        getGamesList(server).
        '''
        try:
            games = yield getGamesList(server)
        except ConnectError:
            self.onLogLine('Unable to connect.')
            self.badServers.add(server)
        except amp.UnknownRemoteError:
            self.onLogLine('Error on remote server.')
        except amp.RemoteAmpError as e:
            self.onLogLine('Error on remote server.')
            log.error('Remote error getting games list: %s', e)
        except IOError as e:
            self.onLogLine('Error connecting to remote server.')
            log.error('Error connecting to auth server: %s', e)
            self.badServers.add(server)
        except Exception:
            self.onLogLine('Error retrieving games list.')
            log.exception('Error retrieving games list')
        else:
            if len(games) == 0:
                self.onLogLine('No running games.')
            # TODO: display a dialog for user to select arena

            for game in games:
                joinSuccessful = yield self.attemptJoinGame(game)
                if joinSuccessful:
                    defer.returnValue(True)
                    return

        defer.returnValue(False)

    @defer.inlineCallbacks
    def attemptJoinGame(self, game):
        '''
        Attempts to join the given game.
        '''
        try:
            self.onLogLine('Found game: joining.')
            result = yield game.join(self)
        except authcommands.GameDoesNotExist:
            pass
        except AuthenticationCancelled:
            pass
        except authcommands.NotAuthenticated:
            self.onLogLine('Authentication failure.')
        except amp.UnknownRemoteError:
            self.onLogLine('Error on remote server.')
        except amp.RemoteAmpError as e:
            self.onLogLine('Error on remote server.')
            log.error('Remote error joining game: %s', e)
        except ConnectionFailed:
            self.onLogLine('Could not connect.')
        except ConnectionRefusedError:
            self.onLogLine('Connection refused.')
        except IOError as e:
            self.onLogLine('Error connecting to remote server.')
            log.error('Error attempting to join game: %s', e)
        except Exception:
            self.onLogLine('Error connecting to remote server.')
            log.exception('Error joining game.')
        else:
            self._joined(result)
            defer.returnValue(True)
            return

        defer.returnValue(False)

    def _joined(self, result):
        self.onSucceed.execute()
        self.app.connector.connectedToGame(*result)

    def cancel(self):
        self.cancelled = True
