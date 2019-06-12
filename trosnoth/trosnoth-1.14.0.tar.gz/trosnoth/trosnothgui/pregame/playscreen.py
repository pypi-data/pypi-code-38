import logging

import pygame
from twisted.internet import defer
from twisted.internet.error import ConnectError, ConnectionRefusedError
from twisted.protocols import amp

from trosnoth.const import JOIN_LAN_GAME, JOIN_LOCAL_GAME, JOIN_AUTH_LAN_GAME
from trosnoth.gui.common import (Region, Canvas, Location, ScaledSize)
from trosnoth.gui.framework import framework
from trosnoth.gui.framework.dialogbox import DialogBox, OkBox
from trosnoth.gui.framework.elements import (TextElement, SolidRect, TextButton)
from trosnoth.gui.framework.listbox import ListBox
from trosnoth.network.lobby import (
    Lobby, AuthenticationCancelled, get_multicast_server,
)
from trosnoth.network import authcommands
from trosnoth.network.client import ConnectionFailed
from trosnoth.utils.event import Event
from trosnoth.trosnothgui.pregame.authServerLoginBox import (
    PasswordGUI, PasswordGUIError)


log = logging.getLogger(__name__)


class PlayAuthScreen(framework.CompoundElement):
    passwordGUIFactory = PasswordGUI

    def __init__(self, app, onSucceed=None, onFail=None):
        super(PlayAuthScreen, self).__init__(app)
        self.onSucceed = Event(listener=onSucceed)
        self.onFail = Event(listener=onFail)
        self.lobby = None
        self.badServers = set()

        if app.displaySettings.alphaOverlays:
            alpha = 192
        else:
            alpha = None
        bg = SolidRect(app, app.theme.colours.playMenu, alpha,
                Region(centre=Canvas(512, 384), size=Canvas(924, 500)))

        colour = app.theme.colours.mainMenuColour
        font = app.screenManager.fonts.consoleFont
        self.logBox = LogBox(app, Region(size=Canvas(900, 425),
                midtop=Canvas(512, 146)), colour, font)

        font = app.screenManager.fonts.bigMenuFont
        cancel = TextButton(app, Location(Canvas(512, 624), 'midbottom'),
                'Cancel', font, app.theme.colours.secondMenuColour,
                app.theme.colours.white, onClick=self.cancel)
        self.cancelled = False
        self.elements = [bg, self.logBox, cancel]
        self._passwordGetter = None
        self._gameSelectionBox = None

    @property
    def passwordGetter(self):
        if self._passwordGetter is None:
            self._passwordGetter = self.passwordGUIFactory(self.app)
        return self._passwordGetter

    @defer.inlineCallbacks
    def begin(self, servers, canHost=True):
        self.cancelled = False
        self.passwordGetter.setCancelled(False)
        self.badServers = set()
        if self.lobby is None:
            self.lobby = Lobby(self.app)

        # Removes the third item (http) from the tuple since we don't care about
        # it.
        servers = [ (server[:2] if isinstance(server, tuple) else server)
                for server in servers ]

        for server in servers:
            if self.cancelled:
                break

            if server == JOIN_LOCAL_GAME:
                if self.app.server is not None:
                    self.onSucceed.execute()
                    self.app.interface.connectToLocalServer()
                    return

            elif isinstance(server, tuple):
                if server in self.badServers:
                    continue

                self.logBox.log('Requesting games from %s:%d...' % server)
                connected = yield self.attemptServerConnect(
                        self.lobby.getGames, server)
                if connected:
                    return

            elif server == JOIN_LAN_GAME:
                self.logBox.log('Asking local network for other games...')
                games = yield self.lobby.get_adhoc_lan_games()
                for game in games:
                    joinSuccessful = yield self.attemptJoinGame(game)
                    if joinSuccessful:
                        return

            elif server == JOIN_AUTH_LAN_GAME:
                self.logBox.log('Searching for servers on local network...')
                server = yield get_multicast_server()
                if server:
                    self.logBox.log(
                        'Server found. Requesting games from %s:%d...' % server)
                    connected = yield self.attemptServerConnect(
                        self.lobby.getGames, server)
                    if connected:
                        return

        if canHost:
            if not self.cancelled:
                result = yield HostGameQuery(self.app).run()

                if not result:
                    self.onFail.execute()
                    return

                self.app.startListenServer(2, 1)

                self.onSucceed.execute()
                self.app.interface.connectToLocalServer()
        else:
            if not self.cancelled:
                box = OkBox(self.app, ScaledSize(450, 150), 'Trosnoth',
                        'Connection unsuccessful.')
                box.onClose.addListener(self.onFail.execute)
                box.show()

    @defer.inlineCallbacks
    def attemptServerConnect(self, getGamesList, server):
        '''
        Attempts to connect to a game on the server, returned by
        getGamesList(server).
        '''
        try:
           games = yield getGamesList(server)
        except ConnectError:
            self.logBox.log('Unable to connect.')
            self.badServers.add(server)
        except amp.UnknownRemoteError:
            self.logBox.log('Error on remote server.')
        except amp.RemoteAmpError as e:
            self.logBox.log('Error on remote server.')
            log.error('Remote error getting games list: %s', e)
        except IOError as e:
            self.logBox.log('Error connecting to remote server.')
            log.error('Error connecting to auth server: %s', e)
            self.badServers.add(server)
        except Exception:
            self.logBox.log('Error retrieving games list.')
            log.exception('Error retrieving games list')
        else:
            if len(games) == 0:
                self.logBox.log('No running games.')
            elif len(games) == 1:
                joinSuccessful = yield self.attemptJoinGame(games[0])
                defer.returnValue(joinSuccessful)
            else:
                game = yield self.selectGame(server, games)
                if game:
                    joinSuccessful = yield self.attemptJoinGame(game)
                    defer.returnValue(joinSuccessful)
                self.logBox.log('No game selected.')

        defer.returnValue(False)

    def selectGame(self, server, games):
        host, port = server
        if self._gameSelectionBox is None:
            self._gameSelectionBox = GameSelectionBox(self.app)
        return self._gameSelectionBox.selectGame(host, games)

    @defer.inlineCallbacks
    def attemptJoinGame(self, game):
        '''
        Attempts to join the given game.
        '''
        try:
            self.logBox.log('Found game: joining.')
            result = yield game.join(self.passwordGetter)
        except authcommands.GameDoesNotExist:
            pass
        except AuthenticationCancelled:
            pass
        except authcommands.NotAuthenticated:
            self.logBox.log('Authentication failure.')
        except amp.UnknownRemoteError:
            self.logBox.log('Error on remote server.')
        except amp.RemoteAmpError as e:
            self.logBox.log('Error on remote server.')
            log.error('Remote error joining game: %s', e)
        except ConnectionFailed:
            self.logBox.log('Could not connect.')
        except ConnectionRefusedError:
            self.logBox.log('Connection refused.')
        except IOError as e:
            self.logBox.log('Error connecting to remote server.')
            log.error('Error attempting to join game: %s', e)
        except Exception:
            self.logBox.log('Error connecting to remote server.')
            log.exception('Error joining game.')
        else:
            self._joined(result)
            defer.returnValue(True)
            return

        defer.returnValue(False)

    def _joined(self, result):
        self.onSucceed.execute()
        self.app.interface.connectedToGame(*result)

    def cancel(self, element):
        self.cancelled = True
        self.passwordGetter.setCancelled(True)
        self.onFail.execute()

    def processEvent(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.onFail.execute()
        else:
            return super(PlayAuthScreen, self).processEvent(event)

class LogBox(framework.Element):
    '''
    Draws a canvas and adds text to the bottom of it, scrolling the canvas
    upwards.
    '''
    def __init__(self, app, region, colour, font):
        super(LogBox, self).__init__(app)
        self.image = None
        self.region = region
        self.colour = colour
        self.font = font

    def draw(self, screen):
        r = self.region.getRect(self.app)
        if self.image is not None:
            screen.blit(self.image, r.topleft)

    def log(self, text):
        t = self.font.render(self.app, text, False, self.colour,
                (255, 255, 255))
        t.set_colorkey((255, 255, 255))
        r = self.region.getRect(self.app)
        img = pygame.Surface(r.size)
        img.fill((255, 255, 255))
        img.set_colorkey((255, 255, 255))
        h = t.get_rect().height
        r.topleft = (0, h)
        if self.image is not None:
            img.blit(self.image, (0, 0), r)
        img.blit(t, (0, r.height - h))
        self.image = img


class HostGameQuery(DialogBox):
    def __init__(self, app):
        size = Canvas(384, 150)
        DialogBox.__init__(self, app, size, 'Host game?')
        self._deferred = None

        font = app.screenManager.fonts.defaultTextBoxFont
        btnColour = app.theme.colours.dialogButtonColour
        highlightColour = app.theme.colours.black
        labelColour = app.theme.colours.dialogBoxTextColour
        btnFont = app.screenManager.fonts.bigMenuFont

        self.elements = [
            TextElement(app, 'No games found. Host a game?', font,
                Location(self.Relative(0.5, 0.4), 'center'), labelColour),

            TextButton(app,
                Location(self.Relative(0.3, 0.85), 'center'),
                'Yes', btnFont, btnColour, highlightColour,
                onClick=self.yesClicked),
            TextButton(app,
                Location(self.Relative(0.7, 0.85), 'center'),
                'No', btnFont, btnColour, highlightColour,
                onClick=self.noClicked),
        ]

    def processEvent(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_KP_ENTER, pygame.K_RETURN):
                self.yesClicked()
                return None
            elif event.key == pygame.K_ESCAPE:
                self.noClicked()
                return None
        else:
            return DialogBox.processEvent(self, event)

    def yesClicked(self, element=None):
        self.close()
        self._deferred.callback(True)

    def noClicked(self, element=None):
        self.close()
        self._deferred.callback(False)

    def run(self):
        if self.showing:
            raise PasswordGUIError('HostGameQuery already showing')
        self.show()
        result = self._deferred = defer.Deferred()
        return result


class GameSelectionBox(DialogBox):
    def __init__(self, app):
        size = Canvas(512, 384)
        DialogBox.__init__(self, app, size, 'Select arena')
        self._deferred = None
        self._games = None

        font = app.screenManager.fonts.defaultTextBoxFont
        btnColour = app.theme.colours.dialogButtonColour
        highlightColour = app.theme.colours.black
        labelColour = app.theme.colours.dialogBoxTextColour
        btnFont = app.screenManager.fonts.bigMenuFont
        listboxFont = app.screenManager.fonts.serverListFont
        listboxColour = app.theme.colours.mainMenuColour
        listboxHighlight = app.theme.colours.mainMenuHighlight

        self.gameList = ListBox(
            self.app,
            Region(
                topleft=self.Relative(0.05, 0.15),
                size=self.Relative(0.9, 0.65)),
            [],
            listboxFont, listboxColour, listboxHighlight,
        )

        self.elements = [
            TextElement(app, 'Please select:', font,
                Location(self.Relative(0.05, 0.05), 'topleft'), labelColour),

            self.gameList,

            TextButton(app,
                Location(self.Relative(0.3, 0.9), 'center'),
                'Ok', btnFont, btnColour, highlightColour,
                onClick=self.okClicked),
            TextButton(app,
                Location(self.Relative(0.7, 0.9), 'center'),
                'Cancel', btnFont, btnColour, highlightColour,
                onClick=self.cancelClicked),
        ]

    def selectGame(self, host, games):
        if self.showing:
            raise RuntimeError('GameSelectionBox already showing')

        self.setCaption(host)
        self._games = list(games)
        self.gameList.setItems([g.name for g in games])
        self.gameList.setIndex(-1)

        self.show()
        self._deferred = defer.Deferred()
        return self._deferred

    def cancelClicked(self, element):
        self._sendResult(None)

    def okClicked(self, element):
        index = self.gameList.getIndex()
        if index >= 0:
            self._sendResult(self._games[index])

    def _sendResult(self, result):
        self.close()
        d, self._deferred = self._deferred, None
        d.callback(result)
