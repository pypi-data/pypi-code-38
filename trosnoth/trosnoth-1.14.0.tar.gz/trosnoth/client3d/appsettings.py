import copy
import logging
import os
from twisted.internet import reactor

from direct.showbase.DirectObject import DirectObject
from direct.showbase.MessengerGlobal import messenger

import trosnoth.version
from trosnoth.client3d.base.keyboard import pygameToPandaKey, keyUpEvent, keyDownEvent
from trosnoth.client3d.base.screenManager.screenManager import (
    WINDOWED, FULL_SCREEN,
)
from trosnoth.const import (
    MAP_TO_SCREEN_SCALE, ACTION_LEFT, ACTION_DOWN, ACTION_RIGHT, ACTION_JUMP,
    ACTION_FOLLOW, ACTION_MAIN_MENU, ACTION_UPGRADE_MENU, ACTION_USE_UPGRADE,
    ACTION_EDIT_PLAYER_INFO, ACTION_MORE_MENU, ACTION_RESPAWN, ACTION_READY,
    ACTION_CLEAR_UPGRADE, ACTION_ABANDON_UPGRADE, ACTION_CHAT,
    ACTION_LEADERBOARD_TOGGLE, ACTION_HUD_TOGGLE, ACTION_TERMINAL_TOGGLE,
    ACTION_PAUSE_GAME, ACTION_EMOTE,
)
from trosnoth.data import getPath, user
from trosnoth.model.upgrades import allUpgrades
from trosnoth.utils import unrepr
from trosnoth.utils.event import Event

log = logging.getLogger(__name__)


class SettingsObject(object):
    '''
    Base class for defining settings objects. Defines some functionality for
    loading and saving settings.

    Subclasses should, at a minimum, define the `attributes` member to be a
    sequence of (attrname, key, default) tuples. Attributes then become
    accessible directly on the settings object as python attributes.
    '''

    def __init__(self, app):
        self.app = app
        self.reset()

    def reset(self):
        '''
        Resets all attributes in self.attributes to the values stored on disk.
        '''
        data = self._loadSettingsFile()

        for attr, key, default in self.attributes:
            setattr(self, attr, data.get(key, copy.deepcopy(default)))

    def apply(self):
        '''
        Should be overridden by subclasses to perform actions needed to put
        settings changes into effect.
        '''
        pass

    def save(self):
        '''
        Writes the settings to file in a JSON-like format.
        '''
        # Write to file
        fn = getPath(user, self.dataFileName)
        f = open(fn, 'w')
        data = {}
        for attr, key, default in self.attributes:
            data[key] = getattr(self, attr)
        f.write(repr(data))
        f.close()

    def _getSettingsFilename(self):
        '''
        Returns the path to the file that should be used to save and load these
        settings. May be overridden by subclasses.
        '''
        return getPath(user, self.dataFileName)

    def _loadSettingsFile(self):
        '''
        Loads the data from the settings file and returns it in a dict.
        '''
        filename = self._getSettingsFilename()
        try:
            f = open(filename, 'rU')
            d = unrepr.unrepr(f.read())
            if not isinstance(d, dict):
                d = {}
        except IOError:
            d = {}
        return d


class DisplaySettings(SettingsObject):
    '''
    Stores the Trosnoth display settings.
    '''
    DEFAULT_THEME = 'default'
    dataFileName = 'display'
    attributes = (
        ('size', 'size', (800, 600)),
        ('displayMode', 'displayMode', None),
        ('_old_fullScreen', 'fullscreen', False),
        ('_old_useAlpha', 'usealpha', True),
        ('_old_windowsTranslucent', 'windowsTranslucent', False),
        ('detailLevel', 'detailLevel', None),
        ('theme', 'theme', DEFAULT_THEME),
        ('showTimings', 'showTimings', False),
        ('_old_cursor', 'cursor', 0),
    )

    DETAIL_LEVELS = ['lowest', 'shrunk', 'low', 'default', 'full']

    def __init__(self, *args, **kwargs):
        super(DisplaySettings, self).__init__(*args, **kwargs)
        self.onDetailLevelChanged = Event()
        self.pendingScreenResize = None

        reactor.callLater(0, self.subscribeToScreenResize)

    def subscribeToScreenResize(self):
        # This cannot be done directly during the __init__, because we need to
        # be able to load the display settings in order to initialise the
        # ScreenManager.
        self.app.screenManager.onResize.addListener(self.screenResized)

    def screenResized(self):
        if self.pendingScreenResize:
            self.pendingScreenResize.cancel()
        self.pendingScreenResize = reactor.callLater(
            1, self.processScreenResize)

    def processScreenResize(self):
        self.pendingScreenResize = None
        if self.app.screenManager.isFullScreen():
            return
        self.size = self.app.screenManager.size
        self.save()

    def reset(self):
        SettingsObject.reset(self)

        if self.detailLevel is None:
            if self._old_useAlpha and self._old_windowsTranslucent:
                self.detailLevel = 'full'
            elif self._old_useAlpha or self._old_windowsTranslucent:
                self.detailLevel = 'default'
            else:
                self.detailLevel = 'lowest'
        if self.displayMode is None:
            self.displayMode = FULL_SCREEN if self._old_fullScreen else WINDOWED

        self.lastDetailLevel = self.detailLevel
        self.applyDetailLevel()

    def applyTimings(self):
        self.app.panda.setFrameRateMeter(self.showTimings)

    def applyDetailLevel(self):
        self.orbSparkles = True
        self.shader = True
        self.maxViewportWidth = int(1536 * MAP_TO_SCREEN_SCALE + 0.5)
        self.maxViewportHeight = int(960 * MAP_TO_SCREEN_SCALE + 0.5)
        if self.detailLevel == 'full':
            return

        if self.detailLevel == 'default':
            return

        self.orbSparkles = False
        if self.detailLevel == 'low':
            return

        self.maxViewportWidth = 1024
        self.maxViewportHeight = 768
        if self.detailLevel == 'shrunk':
            return

        # If we're going this low, we really want performance
        self.shader = False
        self.maxViewportWidth = 800
        self.maxViewportHeight = 600

    def apply(self):
        '''
        Apply the current settings.
        '''

        # Don't bother changing the screen if the settings that matter haven't
        # changed
        if (self.size != self.app.screenManager.size) or (
                self.displayMode != self.app.screenManager.displayMode):
            # Tell the main program to change its screen size.
            self.app.changeScreenSize(self.size, self.displayMode)

        if self.lastDetailLevel != self.detailLevel:
            self.lastDetailLevel = self.detailLevel
            self.applyDetailLevel()
            self.onDetailLevelChanged()

        self.applyTimings()


class SoundSettings(SettingsObject):
    dataFileName = 'sound'
    attributes = (
        ('soundEnabled', 'playSound', False),
        ('musicEnabled', 'playMusic', True),
        ('musicVolume', 'musicVolume', 100),
        ('soundVolume', 'soundVolume', 100),
    )

    def apply(self):
        '''
        Apply the current settings.
        '''

        if self.musicEnabled != self.app.musicManager.isMusicPlaying():
            if self.musicEnabled:
                self.app.musicManager.playMusic()
            else:
                self.app.musicManager.stopMusic()

        self.app.musicManager.setVolume(self.musicVolume)

        if self.soundEnabled:
            self.app.soundPlayer.setMasterVolume(self.soundVolume / 100.)
        else:
            self.app.soundPlayer.setMasterVolume(0)


class IdentitySettings(SettingsObject):
    dataFileName = 'identity'
    attributes = (
        ('nick', 'nick', None),
        ('usernames', 'usernames', None),
        ('firstTime', 'firstTime', True),
    )

    def __init__(self, app):
        self.app = app
        self.reset()

    def reset(self):
        SettingsObject.reset(self)
        if self.usernames is None:
            self.usernames = {}

    def setNick(self, nick):
        self.nick = nick
        self.save()

    def notFirstTime(self):
        self.firstTime = False
        self.save()


class ConnectionSettings(SettingsObject):
    dataFileName = 'connection'
    attributes = (
        ('servers', 'servers', None),
        ('lanGames', 'lanGames', 'afterInet'),
    )

    def __init__(self, app):
        SettingsObject.__init__(self, app)
        if self.servers is None:
            self.servers = [('localhost', 6787)]
            if trosnoth.version.release:
                self.servers.append(('play.trosnoth.org', 6787))
        else:
            # Previous version used to store web address too
            self.servers = [s[:2] for s in self.servers]
            # For developers who have saved settings.


class AuthServerSettings(SettingsObject):
    '''
    Stores general settings for the authentication server.
    '''
    attributes = (
        ('keyLength', 'keyLength', 512),
        ('lobbySize', 'lobbySize', (2, 1)),
        ('maxPerTeam', 'playersPerTeam', 100),
        ('allowNewUsers', 'allowNewUsers', True),
        ('privateMsg', 'privateMsg', None),
        ('elephantOwners', 'elephantOwners', ()),
        ('serverName', 'serverName', 'Trosnoth server'),
        ('homeUrl', 'homeUrl', None),
        ('hostName', 'hostName', None),
    )

    def __init__(self, dataPath):
        self.dataFileName = os.path.join(dataPath, 'settings')
        self.reset()

    def _getSettingsFilename(self):
        return self.dataFileName

    def reset(self):
        SettingsObject.reset(self)
        self.elephantOwners = set(p.lower() for p in self.elephantOwners)
        if self.privateMsg is None or len(self.privateMsg) == 0:
            self.privateMsg = 'This is a private server.'


class KeyboardMapping(SettingsObject):
    '''
    Stores the user's configured keyboard map.
    '''

    dataFileName = 'keys'
    attributes = (
        ('actions', 'actions', None),
    )

    def __init__(self, app):
        self.do = DirectObject()
        super(KeyboardMapping, self).__init__(app)

    def reset(self):
        super(KeyboardMapping, self).reset()

        if self.actions is None:
            self.revertToDefault()
        self.installMapping()

    def revertToDefault(self):
        self.actions = {}

        # Load the old file if it exists
        oldFilePath = getPath(user, 'keymap')
        try:
            with open(oldFilePath, 'rU') as f:
                lines = f.read().splitlines()
            for line in lines:
                bits = line.split(':', 1)
                if len(bits) == 2 and bits[0].isdigit():
                    key = pygameToPandaKey(int(bits[0]))
                    self.actions.setdefault(key, bits[1])
        except IOError:
            pass

        for key, action in self.getDefaultKeyMap():
            self.actions.setdefault(key, action)

    def getDefaultKeyMap(self):
        defaults = []

        # Default WASD in the current keyboard layout
        layout = self.app.panda.win.get_keyboard_map()
        defaults.append((str(layout.get_mapped_button('a')), ACTION_LEFT))
        defaults.append((str(layout.get_mapped_button('s')), ACTION_DOWN))
        defaults.append((str(layout.get_mapped_button('d')), ACTION_RIGHT))
        defaults.append((str(layout.get_mapped_button('w')), ACTION_JUMP))

        defaults.extend([
            # Used in replay mode.
            ('=', ACTION_FOLLOW),

            # Menu keys.
            ('escape', ACTION_MAIN_MENU),

            ('b', ACTION_UPGRADE_MENU),
            ('space', ACTION_USE_UPGRADE),
            ('f12', ACTION_EDIT_PLAYER_INFO),
            ('v', ACTION_MORE_MENU),
            ('r', ACTION_RESPAWN),
            ('t', ACTION_EMOTE),
            ('y', ACTION_READY),
            ('pause', ACTION_PAUSE_GAME),

            ('0', ACTION_CLEAR_UPGRADE),

            ('m', ACTION_ABANDON_UPGRADE),
            ('enter', ACTION_CHAT),
            ('p', ACTION_LEADERBOARD_TOGGLE),
            ('delete', ACTION_HUD_TOGGLE),

            ('scroll_lock', ACTION_TERMINAL_TOGGLE),
        ])

        for upgradeClass in allUpgrades:
            if upgradeClass.defaultKey is not None:
                defaults.append((upgradeClass.defaultKey, upgradeClass.action))

        return defaults

    def apply(self):
        self.installMapping()

    def installMapping(self):
        self.do.ignoreAll()     # Clear previous mapping
        for k, action in self.actions.items():
            self.do.accept(k, messenger.send, [keyDownEvent(action)])
            self.do.accept(k + '-up', messenger.send, [keyUpEvent(action)])
