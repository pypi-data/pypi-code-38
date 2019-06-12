'''
themes.py
This module defines the interface to the various different themes.
'''

import functools
import logging
import os

import pygame
from pygame.surface import Surface
import pygame.transform

from trosnoth import data
import trosnoth.data.themes     # noqa
from trosnoth.const import (
    BODY_BLOCK_SCREEN_SIZE, INTERFACE_BLOCK_SCREEN_SIZE,
    TEAM_1_COLOUR, TEAM_2_COLOUR,
)
from trosnoth.gui.fonts.font import Font, ScaledFont
from trosnoth.gui.framework.basics import SingleImage, Animation
from trosnoth.trosnothgui.common import setAlpha
from trosnoth.utils.unrepr import unrepr
from trosnoth.model.universe_base import NEUTRAL_TEAM_ID
from trosnoth.model.upgrades import Upgrade

BLOCK_BACKGROUND_COLOURKEY = (224, 192, 224)
x1 = INTERFACE_BLOCK_SCREEN_SIZE[0]
x2 = x1 + BODY_BLOCK_SCREEN_SIZE[0]
y = BODY_BLOCK_SCREEN_SIZE[1]
BLOCK_OFFSETS = {
    'top': (-x1, 0),
    'btm': (-x1, -y),
    'fwd': ((-x2, -y), (0, 0)),
    'bck': ((-x2, 0), (0, -y)),
}
del x1, x2, y

log = logging.getLogger(__name__)


def setToRed(surface):
    '''Inverts the colors of a pygame Screen'''
    surface.lock()

    for x in range(surface.get_width()):
        for y in range(surface.get_height()):
            r, g, b, a = surface.get_at((x, y))
            greyscale = r * 0.298 + g * 0.587 + b * 0.114
            surface.set_at((x, y), (greyscale, 0, 0, a))

    surface.unlock()


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
    miniMapZoneHighlight = teamColour('Mn_highlight')
    leaderboard = teamColour('Leaderboard')
    shot = teamColour('shot')


def cachedProperty(fn):
    @functools.wraps(fn)
    def spriteFunction(self):
        try:
            return self._store[fn]
        except KeyError:
            self._store[fn] = fn(self)
            return self._store[fn]
    return property(spriteFunction)


def cached(fn):
    @functools.wraps(fn)
    def spriteFunction(self, *args):
        try:
            return self._store[fn, args]
        except KeyError:
            self._store[fn, args] = fn(self, *args)
            return self._store[fn, args]
    return spriteFunction


def image(path, **kwargs):
    def imageFunction(self):
        return self.theme.loadSprite(path, sprites=self, **kwargs)
    return cachedProperty(imageFunction)


def reversibleImage(filename):
    @cached
    def accessor(self, reversed):
        if reversed:
            regular = accessor(self, False)
            return pygame.transform.flip(regular, True, False)
        return self.theme.loadSprite(filename, sprites=self)
    return accessor


def reversibleTeamColouredImage(filename):
    @cached
    def accessor(self, colour, reversed):
        if reversed:
            regular = accessor(self, colour, False)
            surface = pygame.transform.flip(regular, True, False)
            return surface

        if filename not in self._store:
            self._store[filename] = s = self.theme.loadSprite(
                filename, sprites=self)
        surface = self._store[filename].copy()
        solid = pygame.Surface(surface.get_rect().size)
        r, g, b = colour
        solid.fill((127 - r // 2, 127 - g // 2, 127 - b // 2))
        surface.blit(solid, (0, 0), special_flags=pygame.BLEND_SUB)
        surface.blit(surface, (0, 0), special_flags=pygame.BLEND_ADD)
        return surface

    return accessor


def images(paths, **kwargs):
    def imageFunction(self):
        return self.theme.loadSprites(paths, sprites=self, **kwargs)
    return cachedProperty(imageFunction)


def wrappedImage(path, **kwargs):
    def imageFunction(self):
        return SingleImage(self.theme.loadSprite(path, sprites=self, **kwargs))
    return cachedProperty(imageFunction)


def getTeamId(team):
    if team is None:
        return NEUTRAL_TEAM_ID
    return team.id


class TeamColouredImage:
    def __init__(self, prefix):
        self.theme = None
        self.prefix = prefix
        self.baseImg = None
        self.teamImg = None
        self.cached = {}

    def init(self, theme):
        self.theme = theme
        self.baseImg = self.theme.loadSprite(self.prefix + '.png')
        self.teamImg = self.theme.loadSprite(self.prefix + '-team.png')

    def get(self, colour):
        if colour not in self.cached:
            self.loadImage(colour)
        return self.cached[colour]

    def loadImage(self, colour):
        result = Surface(self.baseImg.get_size(), pygame.SRCALPHA)
        result.fill((0, 0, 0, 0))
        result.blit(self.baseImg, (0, 0))

        temp = Surface(self.baseImg.get_size(), pygame.SRCALPHA)
        temp.fill(colour + (255,))
        temp.blit(self.teamImg, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        result.blit(temp, (0, 0))

        self.cached[colour] = result


class ThemeSprites(object):
    def __init__(self, theme):
        self.theme = theme
        self._store = {}
        self.orbs = TeamColouredImage('orbs')

    def init(self):
        self.orbs.init(self.theme)

    def clearCache(self):
        self._store = {}

    smallCoin = image('smallstar.png')
    coin = image('star0.png')
    coinImages = images([
        'star0.png', 'star1.png', 'star2.png', 'star3.png',
        'star4.png', 'star3.png', 'star2.png', 'star1.png',
    ])
    bigCoinImages = images([
        'bigCoin0.png', 'bigCoin1.png', 'bigCoin2.png', 'bigCoin3.png',
        'bigCoin4.png', 'bigCoin3.png', 'bigCoin2.png', 'bigCoin1.png',
    ])
    grenade = image('grenade.png')
    scenery = image('scenery.png', colourkey=None)

    gunIcon = wrappedImage('gun.png')

    shieldImages = images([
        'shieldImage1.png', 'shieldImage2.png', 'shieldImage3.png',
        'shieldImage2.png'])

    playerSpriteSheet = reversibleImage('player.png')
    playerHeadSheet = reversibleTeamColouredImage('heads.png')

    def coinAnimation(self, timer):
        return Animation(0.07, timer, *self.coinImages)

    def bigCoinAnimation(self, timer):
        return Animation(0.07, timer, *self.bigCoinImages)

    @cached
    def head_pic(self, head):
        from trosnoth.trosnothgui.ingame.sprites import (
            PlayerDrawer, PlayerSprite)
        w, h = PlayerSprite.canvasSize
        h += 6  # Add some breathing space
        result = pygame.Surface((w, h), pygame.SRCALPHA)
        drawer = PlayerDrawer(self.theme.app, head=head)
        drawer.render(result)
        return result

    @cached
    def zoneHighlight(self, team, scale):
        colour = self.theme.colours.miniMapZoneHighlight(team)
        size = int(300. / scale + 0.5)
        result = pygame.Surface((2 * size, 2 * size))
        result.fill((0, 0, 0))
        result.set_colorkey((0, 0, 0))
        pygame.draw.circle(result, colour, (size, size), size)
        result.set_alpha(64)
        return result

    @cached
    def bigZoneLetter(self, letter):
        font = self.theme.app.screenManager.fonts.bigZoneFont
        result = font.render(
            self.theme.app, letter, True, self.theme.colours.bigZoneLetter)
        setAlpha(result, 128)
        return result

    @cached
    def ghostAnimation(self, timer, team):
        if team is not None:
            frames = self.theme.loadTeamSprites([
                'ghost1', 'ghost2', 'ghost3', 'ghost4', 'ghost3',
                'ghost2'], team.id, self)
        else:
            lts = functools.partial(self.theme.loadTeamSprite, sprites=self)
            frames = [
                lts('ghost1', b'A'), lts('ghost2', b'B'),
                lts('ghost3', b'A'), lts('ghost4', b'B'),
                lts('ghost3', b'A'), lts('ghost2', b'B')]
        return [Animation(0.25, timer, *frames)]

    @cached
    def ghostIcon(self, team):
        return SingleImage(self.theme.loadTeamSprite(
            'ghost1', getTeamId(team), self))

    @cached
    def trosballAnimation(self, timer):
        frame0 = self.theme.loadSprite('trosball.png', sprites=self)
        scale = 25. / max(frame0.get_size())
        frames = []
        for theta in range(0, 360, 15):
            frames.append(pygame.transform.rotozoom(frame0, -theta, scale))
        return Animation(0.05, timer, *frames)

    @cached
    def trosballWarningAnimation(self, timer):
        frame0 = self.theme.loadSprite('trosball.png', sprites=self)
        scale = 25. / max(frame0.get_size())
        frames = []
        for theta in range(0, 360, 15):
            surface = pygame.transform.rotozoom(frame0, -theta, scale)
            # Every 90 degrees, invert the colours
            if (theta / 45) % 2 < 1:
                setToRed(surface)
            frames.append(surface)
        return Animation(0.05, timer, *frames)

    def explosion(self, timer):
        return Animation(
            0.07, timer, *(self.explosionFrame(i) for i in range(4)))

    def shoxwaveExplosion(self, timer):
        return Animation(
            0.05, timer, *(self.shoxwaveFrame(i) for i in range(3)))

    def trosballExplosion(self, timer):
        return Animation(0.07, timer, self.explosionFrame(0))

    @cached
    def explosionFrame(self, frame):
        return self.theme.loadSprite(
            'explosion%d.png' % (frame + 1,), sprites=self)

    @cached
    def shoxwaveFrame(self, frame):
        return self.theme.loadSprite(
            'shoxwave%d.png' % (frame + 1,), sprites=self)

    def teamGrenade(self, team):
        teamId = getTeamId(team)
        if teamId == b'A':
            path = 'blueGrenade.png'
        elif teamId == b'B':
            path = 'redGrenade.png'
        else:
            return self.grenade
        return self.theme.loadSprite(path, sprites=self)

    @cached
    def zoneBackground(self, team):
        if team is None:
            path = 'greyzone.png'
        elif team.id == b'A':
            path = 'bluezone.png'
        elif team.id == b'B':
            path = 'redzone.png'
        else:
            return self.zoneBackground(None)
        return self.theme.loadSprite(path, sprites=self)

    @cached
    def upgradeImage(self, upgradeType):
        assert issubclass(upgradeType, Upgrade)
        path = upgradeType.iconPath
        if path is None:
            path = 'upgrade-unknown.png'
        return self.theme.loadSprite(
            path, colourkey=upgradeType.iconColourKey, sprites=self)

    def blockBackground(self, block):
        bd = block.defn

        def zoneOwnerId(zone):
            if zone.owner and zone.dark:
                return zone.owner.id
            else:
                return NEUTRAL_TEAM_ID

        if bd.kind in ('top', 'btm'):
            if bd.zone is None:
                return None
            owners = (zoneOwnerId(block.zone),)
        else:
            if bd.zone1 is None:
                owner1 = None
            else:
                owner1 = zoneOwnerId(block.zone1)
            if bd.zone2 is None:
                owner2 = None
            else:
                owner2 = zoneOwnerId(block.zone2)
            owners = (owner1, owner2)
        result = self._getBlockFromStoreOrBuild(bd.kind, owners)
        return result

    def _getBlockFromStoreOrBuild(self, kind, owners):
        try:
            return self._store['blockBackground', kind, owners]
        except KeyError:
            self._buildBlockBackgrounds()
            return self._store['blockBackground', kind, owners]

    def getFilledBlockBackground(self, block, owner):
        ownerId = owner.id if owner is not None else NEUTRAL_TEAM_ID
        if block.defn.kind in ('top', 'btm'):
            if block.defn.zone is None:
                return None
            else:
                owners = (ownerId,)
        else:
            owner1 = ownerId if block.zone1 is not None else None
            owner2 = ownerId if block.zone2 is not None else None
            owners = (owner1, owner2)
        return self._getBlockFromStoreOrBuild(block.defn.kind, owners)

    def _buildBlockBackgrounds(self):
        '''
        Loads and caches zone backgrounds for all combinations of block owners.
        '''

        filename = 'zone.png'
        flags = pygame.SRCALPHA

        zonePics = self.getZonePics(filename)

        def storePic(kind, owners, pic):
            self._store['blockBackground', kind, owners] = pic

        if self.theme.app.displaySettings.paralaxBackgrounds:
            fillColour = (0, 0, 0, 0)
        else:
            fillColour = BLOCK_BACKGROUND_COLOURKEY

        for kind in ('top', 'btm'):
            for ownerId, zonePic in zonePics.items():
                pic = pygame.Surface(BODY_BLOCK_SCREEN_SIZE, flags)
                pic.fill(fillColour)
                pic.blit(zonePic, BLOCK_OFFSETS[kind])
                storePic(kind, (ownerId,), pic)
        for kind in ('fwd', 'bck'):
            for oid1 in (None, NEUTRAL_TEAM_ID, b'A', b'B'):
                for oid2 in (None, NEUTRAL_TEAM_ID, b'A', b'B'):
                    pic = pygame.Surface(
                        INTERFACE_BLOCK_SCREEN_SIZE, flags)
                    pic.fill(fillColour)
                    if oid1 is not None:
                        pic.blit(
                            zonePics[oid1], BLOCK_OFFSETS[kind][0])
                    if oid2 is not None:
                        pic.blit(
                            zonePics[oid2], BLOCK_OFFSETS[kind][1])
                    storePic(kind, (oid1, oid2), pic)

    def getZonePics(self, filename):
        return {
            NEUTRAL_TEAM_ID: self.theme.loadSprite(
                'grey%s' % (filename,), sprites=self),
            b'A': self.theme.loadSprite('blue%s' % (filename,), sprites=self),
            b'B': self.theme.loadSprite('red%s' % (filename,), sprites=self),
        }

    @cached
    def netOrb(self):
        return self.theme.loadSprite('netOrb.png', sprites=self)

    @cached
    def orbIndicator(self, kind, team):
        teamId = team.id.decode('ascii') if team else '0'
        return self.theme.loadSprite('indicator{}{}.png'.format(kind, teamId))


class Theme(object):
    def __init__(self, app):
        self.app = app
        self.paths = []
        self.colours = ThemeColours()
        self.sprites = ThemeSprites(self)
        self.setTheme('default')
#        self.setTheme(app.displaySettings.theme)

        # Building the different zone backgrounds takes time, so do it once on
        # startup.
        self.sprites._buildBlockBackgrounds()

        app.displaySettings.onDetailLevelChanged.addListener(
            self.detailChanged)

    def detailChanged(self):
        self.sprites.clearCache()
        self.sprites._buildBlockBackgrounds()

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
        self.sprites.init()

    def initColours(self):
        colourPath = self.getPath('config', 'colours.cfg')
        colourData = self._getColourData(colourPath)
        defaultColours = self._getColourData(
            data.getPath(data, 'config', 'colours.cfg'))

        for colourName, colour in defaultColours.items():
            if colourName in colourData:
                colour = colourData[colourName]
            setattr(self.colours, colourName, colour)

    def initSounds(self):
        self.app.soundPlayer.addSound('buyUpgrade.ogg', 'buyUpgrade')
        self.app.soundPlayer.addSound('gameLose.ogg', 'gameLose', channel=0)
        self.app.soundPlayer.addSound('startGame.ogg', 'startGame', channel=0)
        self.app.soundPlayer.addSound('shoot.ogg', 'shoot')
        self.app.soundPlayer.addSound('explodeGrenade.ogg', 'explodeGrenade')
        self.app.soundPlayer.addSound('goal.ogg', 'goal', channel=0)
        self.app.soundPlayer.addSound('ownGoal.ogg', 'ownGoal', channel=0)
        self.app.soundPlayer.addSound('bell.ogg', 'gotCoin')

    def initFonts(self):
        fontData = self._getFontData()

        for fontName, defaultDetails in DEFAULT_FONTS.items():
            if fontName in fontData:
                fontFile, size, bold = fontData[fontName]
            else:
                fontFile, size, bold = defaultDetails.unpack()

            if fontName in UNSCALED_FONTS:
                font = Font(fontFile, size, bold)
            else:
                font = ScaledFont(fontFile, size, bold)
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
            with open(filepath) as f:
                lines = f.readlines()
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

    def loadSprite(
            self, filename, colourkey=None, sprites=None,
            borders=(127, 127, 127)):
        '''
        Loads the sprite with the given name. A colour key of None may be given
        to disable colourkey transparency.
        '''
        filepath = self.getPath('sprites', filename)
        image = pygame.image.load(filepath)

        alpha = (colourkey is None)
        if alpha:
            image = image.convert_alpha()
        else:
            image = image.convert()
            image.set_colorkey(colourkey)

        return image

    def loadSprites(self, filenames, sprites, **kwargs):
        images = []
        for filename in filenames:
            images.append(self.loadSprite(filename, sprites=sprites, **kwargs))
        return images

    def loadTeamSprite(self, filename, teamId, sprites, **kwargs):
        '''
        teamId must be 'A' or 'B'.
        If teamId is 'A', grabs <filename>.png
        If teamId is 'B', grabs <filename>b.png if it exists, or <filename>.png
            otherwise.
        '''
        if teamId == b'B':
            fullFilename = '%sb.png' % (filename,)
            try:
                filepath = self.getPath('sprites', fullFilename)
                if not os.path.isfile(filepath):
                    fullFilename = '%s.png' % (filename,)
            except IOError:
                fullFilename = '%s.png' % (filename,)
        else:
            fullFilename = '%s.png' % (filename,)

        return self.loadSprite(fullFilename, sprites=sprites, **kwargs)

    def loadTeamSprites(self, filenames, teamId, sprites, **kwargs):
        images = []
        for filename in filenames:
            images.append(self.loadTeamSprite(
                filename, teamId, sprites, **kwargs))
        return images


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
    'unobtrusivePromptFont': F('Junction.ttf', 28),
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
    'timingsFont': F('Junction.ttf', 10),
    'ampleMenuFont': F('Junction.ttf', 40),
    'mediumMenuFont': F('Junction.ttf', 36),
    'menuFont': F('Junction.ttf', 30),
    'smallMenuFont': F('Junction.ttf', 20),
    'ingameMenuFont': F('FreeSans.ttf', 12),
    'miniMapLabelFont': F('FreeSans.ttf', 10),
    'gameInfoFont': F('FreeSans.ttf', 14),
    'gameInfoTitleFont': F('FreeSans.ttf', 20),
    'coinsDisplayFont': F('FreeSans.ttf', 20),
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

    'creditsFont': F('Junction.ttf', 24),
    'creditsH2': F('KLEPTOCR.TTF', 48),
    'creditsH1': F('KLEPTOCR.TTF', 60),

    'bigZoneFont': F('VeraBd.ttf', 164),
}

UNSCALED_FONTS = {
    'nameFont',
    'ingameMenuFont',
    'miniMapLabelFont',
    'gameInfoFont',
    'gameInfoTitleFont',
    'leaderboardFont',
    'newChatFont',
    'winMessageFont',
    'bigZoneFont',
}