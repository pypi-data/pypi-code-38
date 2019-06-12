'''
themes.py
This module defines the interface to the various different themes.
'''

import functools
import logging
import os

from direct.gui.OnscreenImage import OnscreenImage
from panda3d.core import Filename, Texture, TransparencyAttrib

import trosnoth.data.themes
from trosnoth import data
from trosnoth.client3d.base.fonts.font import Font
from trosnoth.utils.unrepr import unrepr

log = logging.getLogger(__name__)


def teamColour(colourId):
    def colourFunction(self, team):
        return self.getTeamColour(team, colourId)
    return colourFunction


class ThemeColours(object):
    def getTeamColour(self, team, colourId):
        if team is None:
            teamNum = 0
        else:
            teamNum = ord(team.id) - 64
        return getattr(
            self, 'team%d%s' % (teamNum, colourId),
            getattr(self, 'team0%s' % (colourId,)))

    chatColour = teamColour('chat')
    miniMapTrosballTargetColour = teamColour('Mn_trosball')
    miniMapDarkZoneColour = teamColour('Mn_zone')
    miniMapLightZoneColour = teamColour('Mn_mk')
    miniMapPlayerColour = teamColour('Mn_pl')
    miniMapGhostColour = teamColour('Mn_gh')
    miniMapColour = teamColour('Mn')
    miniMapZoneHighlight = teamColour('Mn_highlight')
    leaderboard = teamColour('Leaderboard')


def cached(fn):
    @functools.wraps(fn)
    def spriteFunction(self, *args):
        try:
            return self._store[fn, args]
        except KeyError:
            self._store[fn, args] = fn(self, *args)
            return self._store[fn, args]
    return spriteFunction


class ThemeSprites(object):
    def __init__(self, theme):
        self.theme = theme
        self._store = {}

    def clearCache(self):
        self._store = {}

    def loadPandaTexture(self, path):
        filepath = self.theme.getPandaPath('sprites', path)
        result = self.theme.app.panda.loader.loadTexture(filepath)
        result.setWrapU(Texture.WM_clamp)
        result.setWrapV(Texture.WM_clamp)
        return result

    @cached
    def orbTexture(self, team):
        if team:
            if team.id == b'A':
                return self.loadPandaTexture('blueOrb.png')
            if team.id == b'B':
                return self.loadPandaTexture('redOrb.png')
        return self.loadPandaTexture('greyOrb.png')

    @cached
    def ghostTexture(self, team):
        if team and team.id == b'B':
            return self.loadPandaTexture('ghost1b.png')
        return self.loadPandaTexture('ghost1.png')


class Theme(object):
    def __init__(self, app):
        self.app = app
        self.paths = []
        self.colours = ThemeColours()
        self.sprites = ThemeSprites(self)
        self.setTheme('default')
#        self.setTheme(app.displaySettings.theme)

        app.displaySettings.onDetailLevelChanged.addListener(
            self.detailChanged)

    def detailChanged(self):
        self.sprites.clearCache()

    def setTheme(self, themeName):
        '''
        Sets the theme to the theme with the given name.
        '''
        self.name = themeName
        self.paths = [data.getPath(data.user), data.getPath(data)]

        def insertPath(p):
            if os.path.exists(p):
                self.paths.insert(0, p)
        insertPath(data.getPath(data.themes, themeName))
        insertPath(data.getPath(data.user, 'themes', themeName))
        self.initFonts()
        self.initSounds()
        self.initColours()

    def initColours(self):
        colourPath = self.getPath('config', 'colours3d.cfg')
        colourData = self._getColourData(colourPath)
        defaultColours = self._getColourData(
            data.getPath(data, 'config', 'colours3d.cfg'))

        for colourName, colour in defaultColours.items():
            if colourName in colourData:
                colour = colourData[colourName]
            setattr(self.colours, colourName, colour)

    def initSounds(self):
        self.app.soundPlayer.addSound('buyUpgrade.ogg', 'buyUpgrade')
        self.app.soundPlayer.addSound('gameLose.ogg', 'gameLose', key=True)
        self.app.soundPlayer.addSound('startGame.ogg', 'startGame', key=True)
        self.app.soundPlayer.addSound('shoot.ogg', 'shoot', n=3)
        self.app.soundPlayer.addSound('explodeGrenade.ogg', 'explodeGrenade')
        self.app.soundPlayer.addSound('goal.ogg', 'goal', key=True)
        self.app.soundPlayer.addSound('ownGoal.ogg', 'ownGoal', key=True)
        self.app.soundPlayer.addSound('bell.ogg', 'gotCoin', n=2)

    def initFonts(self):
        fontData = self._getFontData()

        for fontName, defaultDetails in DEFAULT_FONTS.items():
            if fontName in fontData:
                fontFile, size, bold = fontData[fontName]
            else:
                fontFile, size, bold = defaultDetails.unpack()

            font = Font(fontFile, size, bold)
            self.app.fonts.addFont(fontName, font)

    def _getFontData(self):
        try:
            fontLines = open(self.getPath('config', 'fonts.cfg')).readlines()
        except IOError:
            return {}

        result = {}
        for line in fontLines:
            bits = line.split('=')
            bits[2] = bits[2].strip()
            # Perform basic checks
            if len(bits) != 3 or not bits[2].isdigit():
                log.warning('Invalid font config line: %r', line)
            else:
                result[bits[0]] = (bits[1], int(bits[2]))
        return result

    def _getColourData(self, filepath):
        try:
            lines = open(filepath).readlines()
        except IOError:
            return {}

        result = {}
        for line in lines:
            line = line.strip()
            if line == '' or line.startswith('#'):
                continue
            bits = line.split('=', 1)
            # Perform basic checks
            invalid = False
            if len(bits) != 2:
                invalid = True
            else:
                try:
                    colour = unrepr(bits[1])
                    if type(colour) is str:
                        colour = colour.strip("'")
                except:
                    invalid = True
                else:
                    if colour in list(result.keys()):
                        colour = result[colour]
                    else:
                        if (not isinstance(colour, tuple) or len(colour) < 3 or
                                len(colour) > 4):
                            invalid = True
            if invalid:
                log.warning('Invalid colour config line: %r', line)
            else:
                result[bits[0].strip()] = colour
        return result

    def getPath(self, *pathBits):
        '''
        Returns a path to the given themed file, looking in the following
        locations:
         1. User theme files for the current theme.
         2. Built-in theme files for the current theme.
         3. Default files.
        '''
        for path in self.paths:
            path = os.path.join(path, *pathBits)
            if os.path.isfile(path):
                return path
        raise IOError('file not found: %s' % (os.path.join(*pathBits),))

    def getPandaPath(self, *pathBits):
        '''
        Performs the same function as getPath, but returns a path that is usable in
        calls to Panda functions.
        '''
        path = self.getPath(*pathBits)
        pandaPath = Filename.fromOsSpecific(path)
        pandaPath.makeTrueCase()
        return pandaPath.getFullpath()

    def loadPandaImage(self, *pathBits):
        '''
        Returns a Panda3D OnscreenImage object that has the same aspect ratio
        as the original image.
        '''
        filepath = self.getPandaPath(*pathBits)
        texture = self.app.panda.loader.loadTexture(filepath)
        texture.setWrapU(Texture.WM_clamp)
        texture.setWrapV(Texture.WM_clamp)

        result = OnscreenImage(image=texture, scale=(
            texture.get_orig_file_x_size() / 1600.,
            1.0,
            texture.get_orig_file_y_size() / 1600.))
        result.setTransparency(TransparencyAttrib.MAlpha)

        return result


class F(object):

    def __init__(self, fontFile, size, bold=False):
        self.fontFile = fontFile
        self.size = size
        self.bold = bold

    def unpack(self):
        return (self.fontFile, self.size, self.bold)

DEFAULT_FONTS = {
    'default': F('Junction.ttf', 24),
    'defaultTextBoxFont': F('Junction.ttf', 20),
    'chatFont': F('Junction.ttf', 25),
    'newChatFont': F('Vera.ttf', 14, True),

    'winMessageFont': F('Junction.ttf', 32),

    'nameFont': F('Junction.ttf', 20),
    'countdownFont': F('Junction.ttf', 16),

    'hugeMenuFont': F('Junction.ttf', 54),
    'bigMenuFont': F('Junction.ttf', 36),
    'mainMenuFont': F('Junction.ttf', 36),
    'serverListFont': F('Junction.ttf', 24),
    'timerFont': F('Junction.ttf', 32),
    'consoleFont': F('orbitron-light.ttf', 20),
    'ampleMenuFont': F('Junction.ttf', 40),
    'mediumMenuFont': F('Junction.ttf', 36),
    'menuFont': F('Junction.ttf', 30),
    'smallMenuFont': F('Junction.ttf', 20),
    'ingameMenuFont': F('FreeSans.ttf', 12),
    'miniMapLabelFont': F('FreeSans.ttf', 10),
    'gameInfoFont': F('FreeSans.ttf', 14),
    'gameInfoTitleFont': F('FreeSans.ttf', 20),
    'versionFont': F('Junction.ttf', 16),
    'scrollingButtonsFont': F('Junction.ttf', 24),
    'zoneBarFont': F('Junction.ttf', 24),
    'dialogButtonFont': F('KLEPTOCR.TTF', 50),
    'serverSelectionCheckboxesFont': F('Junction.ttf', 28),

    'messageFont': F('Junction.ttf', 20),
    'leaderboardFont': F('FreeSans.ttf', 14),

    'smallNoteFont': F('Junction.ttf', 22),
    'labelFont': F('Junction.ttf', 32),
    'captionFont': F('Junction.ttf', 35),
    'keymapFont': F('Junction.ttf', 20),
    'keymapInputFont': F('Junction.ttf', 20),

    'achievementTitleFont': F('orbitron-light.ttf', 21),
    'achievementNameFont': F('Junction.ttf', 18),

    'connectionFailedFont': F('Junction.ttf', 32),

    'creditsFont': F('Junction.ttf', 32),
    'creditsH2': F('KLEPTOCR.TTF', 55),
    'creditsH1': F('KLEPTOCR.TTF', 70),

    'bigZoneFont': F('VeraBd.ttf', 164),

    'glyphFont': F('FreeSans.ttf', 12),

    'statusBarFont': F('Junction.ttf', 15),
}
