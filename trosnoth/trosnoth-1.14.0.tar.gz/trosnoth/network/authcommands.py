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

import pickle
from twisted.protocols import amp


class AuthServerError(Exception):
    pass


class NotAuthenticated(AuthServerError):
    pass


class PortUnreachable(AuthServerError):
    '''
    Raised by the server during an attempt to register a game if the specified
    port cannot be reached.
    '''


class CannotCreateGame(AuthServerError):
    '''
    Raised by the server during an attempt to create a game if the game is not
    allowed, perhaps because there are already the maximum number of games
    running on this server.
    '''


class GameDoesNotExist(AuthServerError):
    '''
    Cannot join the given game because it does not exist.
    '''


class ListGames(amp.Command):
    '''
    Returns a list of the Trosnoth games available on this server.
    '''
    arguments = []
    response = [
        (b'games', amp.AmpList([
            (b'id', amp.Integer()),
            (b'game', amp.Unicode()),
            (b'version', amp.Unicode()),
            (b'name', amp.Unicode(optional=True)),
        ]))
    ]


class ListOtherGames(amp.Command):
    '''
    Returns a list of Trosnoth games this server knows about which are not
    hosted on this server.
    '''
    arguments = []
    response = [
        (b'games', amp.AmpList([
            (b'ip', amp.String()),
            (b'port', amp.Integer()),
            (b'game', amp.Unicode()),
            (b'version', amp.Unicode()),
        ]))
    ]


class RegisterGame(amp.Command):
    '''
    Registers a game running on the client with the server.
    '''
    arguments = [
        (b'game', amp.Unicode()),
        (b'version', amp.Unicode()),
        (b'port', amp.Integer())
    ]
    response = []
    errors = {
        NotAuthenticated: b'NO_AUTH',
        PortUnreachable: b'BAD_PORT',
    }


class CreateGame(amp.Command):
    '''
    Instructs the server to start a new game.
    '''
    arguments = [
        (b'game', amp.Unicode()),
    ]
    response = [
        (b'id', amp.Integer()),
        (b'version', amp.Unicode()),
    ]
    errors = {
        NotAuthenticated: b'NO_AUTH',
        CannotCreateGame: b'WONT',
    }


class ConnectToGame(amp.Command):
    '''
    Requests details with which to join a particular game on the server.
    nick is the preferred nick of the authenticated player.
    '''
    arguments = [(b'id', amp.Integer())]
    response = [(b'port', amp.Integer()),
                (b'authTag', amp.Integer()),
                (b'nick', amp.Unicode())]
    errors = {
        NotAuthenticated: b'NO_AUTH',
        GameDoesNotExist: b'NO_GAME',
    }


class GetAuthToken(amp.Command):
    '''
    Requests the server send a random string to be used during authentication
    or creation of a user. The authentication token which is returned is valid
    until GetAuthToken is called again.
    '''
    arguments = []
    response = [(b'token', amp.String())]


class PasswordAuthenticate(amp.Command):
    '''
    Authenticates with the server using a password. The password value which is
    sent is created by prepending an authentication token obtained from
    GetAuthToken to the password, then encrypting using the server's public RSA
    key.
    '''
    arguments = [
        (b'username', amp.Unicode()),
        (b'password', amp.String()),
    ]
    response = [(b'result', amp.Boolean())]


class LocalUsername(amp.Command):
    '''
    Tell the server what the local username is. Usually this is ignored,
    but on camp we often set the server up to just trust this and create
    accounts based on the user's local username.
    '''
    arguments = [
        (b'username', amp.Unicode()),
    ]
    response = []


class SetPassword(amp.Command):
    arguments = [
        (b'password', amp.String()),
    ]
    response = []
    errors = {
        NotAuthenticated: b'NO_AUTH',
    }


class GetSupportedSettings(amp.Command):
    '''
    Returns a list of strings which indicate which account settings the
    client should display to the user.
    Possible values are 'password'
    '''
    arguments = []
    response = [
        (b'result', amp.ListOf(amp.Unicode())),
    ]


class CreateUserWithPassword(amp.Command):
    '''
    Requests to create a user on the server using the given username and
    password. The password value which is sent is created by prepending an
    authentication token obtained from GetAuthToken to the password, then
    encrypting using the server's public RSA key.
    If successful, the result string will be empty, otherwise it will be a
    human-readable reason why the server is not allowing new users to be
    created.
    '''
    arguments = [
        (b'username', amp.Unicode()),
        (b'password', amp.String()),
    ]
    response = [(b'result', amp.Unicode())]


class PythonLong(amp.Argument):
    """
    Convert to and from 'long'.
    """
    def toString(self, inObject):
        return pickle.encode_long(inObject)

    def fromString(self, inString):
        return pickle.decode_long(inString)


class GetPublicKey(amp.Command):
    '''
    Requests that the server send its public key for authentication. The public
    key values e and n are encoded using pickle.encode_long() before being sent
    as strings.
    '''
    arguments = []
    response = [
        (b'e', PythonLong()),
        (b'n', PythonLong()),
    ]
