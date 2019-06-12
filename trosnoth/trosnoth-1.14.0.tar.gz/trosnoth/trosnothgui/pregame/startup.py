import getpass
import logging

from twisted.internet import defer
from twisted.web.client import getPage

from trosnoth.const import JOIN_LAN_GAME, JOIN_LOCAL_GAME, JOIN_AUTH_LAN_GAME
from trosnoth.gui.framework import framework
from trosnoth.gui.framework.elements import TextElement
from trosnoth.settings import getPolicySettings
from trosnoth.trosnothgui.settings.settings import SettingsMenu
from trosnoth.trosnothgui.pregame.savedGameMenu import SavedGameMenu
from trosnoth.trosnothgui.pregame.practise import PractiseScreen
from trosnoth.trosnothgui.pregame.playscreen import PlayAuthScreen
from trosnoth.trosnothgui.pregame.serverSelectionScreen import (
        ServerSelectionScreen)
from trosnoth.trosnothgui.common import mainButton
from trosnoth.trosnothgui.credits import CreditsScreen

from trosnoth.trosnothgui.pregame.firstplaynotify import (
        FirstPlayNotificationBar)
import trosnoth.version

from trosnoth.gui.common import ScaledLocation

log = logging.getLogger(__name__)


class StartupInterface(framework.CompoundElement):
    '''Represents the interface while the game is not connected to a server.'''
    connectScreenFactory = PlayAuthScreen
    serverScreenFactory = ServerSelectionScreen
    practiseScreenFactory = PractiseScreen
    creditsScreenFactory = CreditsScreen

    def __init__(self, app, mainInterface):
        super(StartupInterface, self).__init__(app)
        self.interface = mainInterface

        # Create font.
        self.font = self.app.screenManager.fonts.bigMenuFont

        self.offsets = self.app.screenManager.offsets

        self.extra = []
        y0 = 0
        policies = getPolicySettings()
        if policies.get('privacy', 'sendusername', fallback=False):
            y0 = 75
            self.extra.extend([
                TextElement(
                    self.app,
                    'Logged in as %s' % (getpass.getuser(),),
                    self.font, ScaledLocation(65, 175, 'topleft'),
                    self.app.theme.colours.headingColour),
                TextElement(
                    self.app,
                    'Not you? Log out of this computer and log back in',
                    self.app.screenManager.fonts.smallMenuFont,
                    ScaledLocation(65, 225, 'topleft'),
                    self.app.theme.colours.headingColour),
                TextElement(
                    self.app,
                    'as yourself so you can earn achievements',
                    self.app.screenManager.fonts.smallMenuFont,
                    ScaledLocation(65, 255, 'topleft'),
                    self.app.theme.colours.headingColour)
            ])

        # Create other elements.
        self.buttons = [
            self.button(
                'play', self.playClicked, (65, y0 + 225), hugeFont=True),
            self.button(
                'servers', self.serverSelectionClicked, (85, y0 + 285),
                smallFont=True),
            self.button(
                'practise', self.practiseClicked, (85, y0 + 325),
                smallFont=True),
            self.button('archives', self.savedGamesClicked, (65, y0 + 420)),
            self.button('settings', self.settingsClicked, (65, y0 + 490)),
            self.button('credits', self.creditsClicked, (65, y0 + 560)),
            self.button('exit', self.exitClicked, (939, 700), 'topright')
        ]
        self.firstTimeNotification = FirstPlayNotificationBar(app)
        self.updateNotification = self._makeUpdateNotificationBar()
        self.elements = []

        if app.identitySettings.firstTime:
            self.firstTimeNotification.show()

        # Create sub-menus.
        self.settingsMenu = SettingsMenu(app, onClose=self.mainMenu,
                onRestart=app.restart)
        self.serverSelectionScreen = ServerSelectionScreen(app,
                onClose=self.mainMenu)
        self.savedGameMenu = None
        self.practiseScreen = self.practiseScreenFactory(app,
                onClose=self.mainMenu,
                onStart=self.interface.connectToGameObject)
        self.creditsScreen = self.creditsScreenFactory(self.app,
                self.app.theme.colours.mainMenuColour, self.mainMenu,
                highlight=self.app.theme.colours.mainMenuHighlight)

        self.mainMenu()

    @defer.inlineCallbacks
    def start(self):
        try:
            stable = yield getPage(b'http://trosnoth.org/stable-version.txt')
        except Exception as e:
            log.warning(
                'Failed to check trosnoth.org for stable version: {}'.format(
                    e))
            return
        stable = stable.strip()
        if stable != trosnoth.version.version:
            self.updateNotification.show()

    def _makeUpdateNotificationBar(self):
        from trosnoth.gui.common import Location, Area, ScaledPoint, ScaledSize
        from trosnoth.gui.notify import NotificationBar
        bar = NotificationBar(
            self.app,
            message='This is not the latest stable release. Click for info.',
            url='https://trosnoth.org/download',
            font=self.app.fonts.default,
            area=Area(ScaledPoint(0, 0), ScaledSize(1024, 30), 'topleft'),
            buttonPos=Location(ScaledPoint(1024, 0), 'topright'),
            textPos=Area(
                ScaledPoint(512, 15), ScaledSize(1024, 30), 'centre'),
        )
        bar.onClick.addListener(bar.hide)
        return bar

    def button(self, text, onClick, pos, anchor='topleft', hugeFont=False,
            smallFont=False):
        return mainButton(self.app, text, onClick, pos, anchor, hugeFont,
                smallFont)

    def heading(self, caption):
        return TextElement(self.app, caption, self.font,
                ScaledLocation(1000, 60, 'topright'),
                self.app.theme.colours.headingColour)

    def practiseClicked(self):
        #self.elements = [self.practiseScreen]
        self.practiseScreen.startGame()

    def playClicked(self):
        playAuthScreen = self.connectScreenFactory(self.app,
                onSucceed=self.mainMenu, onFail=self.mainMenu)
        self.elements = [playAuthScreen]

        servers = [JOIN_LOCAL_GAME]
        if self.app.connectionSettings.lanGames != 'never':
            servers.append(JOIN_AUTH_LAN_GAME)
        servers += list(self.app.connectionSettings.servers)
        if self.app.connectionSettings.lanGames != 'never':
            servers.append(JOIN_LAN_GAME)
        playAuthScreen.begin(tuple(servers))

    def serverSelectionClicked(self):
        self.serverSelectionScreen.reload()
        self.elements = [self.serverSelectionScreen]

    def creditsClicked(self):
        self.creditsScreen.restart()
        self.elements = [self.creditsScreen]

    def exitClicked(self):
        # Quit the game.
        self.app.stop()

    def mainMenu(self):
        self.elements = self.buttons + [
            self.firstTimeNotification,
            self.updateNotification,
        ] + self.extra

    def settingsClicked(self):
        self.elements = [self.settingsMenu]

    def savedGamesClicked(self):
        if self.savedGameMenu is None:
            self.savedGameMenu = SavedGameMenu(self.app,
                    onCancel=self.mainMenu, onReplay=self.replayConnect)
        self.savedGameMenu.replayTab.populateList()
        self.elements = [self.savedGameMenu]

    def inetConnect(self, server, port):
        'Called when user selects connect from inet menu.'
        self.mainMenu()

        # Actually connect.
        self.interface.connectToServer(server, port)

    def replayConnect(self, fname):
        self.interface.connectToReplay(fname)
