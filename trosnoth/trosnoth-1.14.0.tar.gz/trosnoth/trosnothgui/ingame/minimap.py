'''miniMap.py - defines the MiniMap class which deals with drawing the
miniMap to the screen.'''

import random
import logging
import pygame
from twisted.internet import reactor

from trosnoth.const import MAP_TO_SCREEN_SCALE
from trosnoth.model.map import MapLayout
from trosnoth.model import mapblocks
import trosnoth.gui.framework.framework as framework
from trosnoth.gui.framework.basics import Animation
from trosnoth.trosnothgui.ingame.sprites import PlayerSprite
from trosnoth.trosnothgui.ingame.utils import viewRectToMap
from trosnoth.utils.utils import timeNow

log = logging.getLogger(__name__)

SHADOW_OFFSET = 1, 1


class MiniMap(framework.Element):

    def __init__(self, app, scale, universeGui, viewManager):
        '''Called upon creation of a ViewManager object.  screen is a pygame
        screen object.  universe is the Universe object to draw.  target is
        either a point, a PlayerSprite object, or None.  If target is None, the
        view manager will follow the action, otherwise it will follow the
        specified point or player.'''
        super(MiniMap, self).__init__(app)
        self.universeGui = universeGui
        self.universe = universeGui.universe
        self.viewManager = viewManager
        self.disrupt = False
        # Initialise the graphics in all the mapBlocks
        bodyBlockSize = (
            int(MapLayout.zoneBodyWidth / scale + 0.5),
            int(MapLayout.halfZoneHeight / scale + 0.5))
        self.bodyBlockRect = pygame.Rect((0,0), bodyBlockSize)

        interfaceBlockSize = (
            int(MapLayout.zoneInterfaceWidth / scale + 0.5),
            int(MapLayout.halfZoneHeight / scale + 0.5))
        self.interfaceBlockRect = pygame.Rect((0,0), interfaceBlockSize)

        # Recalculate scale based on integer-sized block rectangles
        self.scale = (
            (MapLayout.zoneBodyWidth + MapLayout.zoneInterfaceWidth + 0.)
            / (bodyBlockSize[0] + interfaceBlockSize[0]))
        self.graphicsScale = self.scale * MAP_TO_SCREEN_SCALE

        self.disruptAnimation = self.createDisrupted()

        # self._focus represents the point where the miniMap is currently
        # looking.
        self._focus = None
        self.updateFocus()

    def getScaledMaximumSize(self):
        # 35% of screen size
        return tuple([self.app.screenManager.scaledSize[i] * 35 / 100
                for i in (0, 1)])

    def getAbsoluteMaximumSize(self):
        # Could be aptly described as the minimum maximum
        return (300,200)

    def getMaximumSize(self):
        size1 = self.getScaledMaximumSize()
        size2 = self.getAbsoluteMaximumSize()
        return tuple([max(size1[i], size2[i]) for i in (0,1)])

    def getUniverseScaledSize(self):
        if not self.universe.zoneBlocks:
            return (1, 1)

        universeSize = (len(self.universe.zoneBlocks[0]),
                len(self.universe.zoneBlocks))

        mapHeight = universeSize[1] * self.bodyBlockRect.height
        mapWidth = ((universeSize[0] / 2) * self.bodyBlockRect.width +
                (universeSize[0] / 2 + 1) * self.interfaceBlockRect.width)

        return (mapWidth, mapHeight)

    def getSize(self):
        size1 = self.getUniverseScaledSize()
        size2 = self.getMaximumSize()
        return tuple([min(size1[i], size2[i]) for i in (0,1)])

    def getOffset(self):
        return self.app.screenManager.size[0] - self.getSize()[0] - 5, 5

    def getRect(self):
        return pygame.Rect(self.getOffset(), self.getSize())

    def createDisrupted(self):
        sRect = self.getRect()
        screens = [pygame.surface.Surface(sRect.size) for i in range(4)]

        # Because the creation of these disruption sprites is very slow, do
        # them a bit at a time so that other events don't get blocked.
        for screen in screens:
            reactor.callLater(0, self.drawSingleDisruption, screen)
        return Animation(0.1, timeNow, *screens)

    def drawSingleDisruption(self, screen, y=0, sRect=None, rect=None):
        if sRect is None:
            sRect = self.getRect()
        if rect is None:
            rect = pygame.rect.Rect(0, 0, 2, 2)
        disruptColours = [
            self.app.theme.colours.minimapDisruptionColour1,
            self.app.theme.colours.minimapDisruptionColour2
        ]

        rows = 0
        while y < sRect.bottom:
            x = 0
            rect.top = y
            while x < sRect.right:
                rect.left = x
                pygame.draw.rect(screen, random.choice(disruptColours),
                        rect, 0)
                x += 2
            y += 2
            rows += 1
            if rows >= 5:
                reactor.callLater(
                    0, self.drawSingleDisruption, screen, y, sRect, rect)
                break

    def drawDisrupted(self, screen):
        screen.blit(self.disruptAnimation.getImage(), self.getOffset())

    def mapPosToMinimap(self, sRect, xxx_todo_changeme):
        (x, y) = xxx_todo_changeme
        fx, fy = self._focus
        cx, cy = sRect.center
        s = self.scale
        return (int((x - fx + 0.5) / s + cx), int((y - fy + 0.5) / s + cy))

    def minimapPosToMap(self, sRect, xxx_todo_changeme1):
        (x, y) = xxx_todo_changeme1
        fx, fy = self._focus
        cx, cy = sRect.center
        s = self.scale
        return ((x - cx) * s + fx, (y - cy) * s + fy)

    def draw(self, screen):
        '''Draws the current state of the universe at the current viewing
        location on the screen.  Does not call pygame.display.flip() .'''
        if not self.universe.map:
            return

        sRect = self.getRect()

        oldClip = screen.get_clip()
        screen.set_clip(sRect)

        colours = self.app.theme.colours
        pygame.draw.rect(screen, colours.black, sRect, 0)

        # If disrupted, draw static 95% of the time
        if self.disrupt and random.random() > 0.05:
            self.drawDisrupted(screen)
        else:
            # Update where we're looking at.
            self.updateFocus()
            frontLine = self.universe.uiOptions.getFrontLine()
            if frontLine is not None:
                self.drawShiftingBg(screen, sRect, frontLine)
            else:
                self.drawZones(screen, sRect)

            def drawCircle(sprite, colour, radius):
                pos = self.mapPosToMinimap(sRect, sprite.pos)
                if sRect.collidepoint(*pos):
                    pygame.draw.circle(screen, colour, pos, radius)

            # Draw the shots
            for shotSprite in self.universeGui.iterShots():
                shot = shotSprite.shot
                if shot and not shot.expired:
                    drawCircle(shotSprite, colours.white, 0)
            # Draw the coins
            for coin in list(self.universe.collectableCoins.values()):
                drawCircle(coin, colours.miniMapCoin, 2)

            # Draw the trosball
            sprite = self.universeGui.getTrosballSprite()
            if sprite:
                drawCircle(sprite, colours.white, 4)

            if self.universe.uiOptions.highlightElephant:
                player = self.universe.playerWithElephant
                if player:
                    sprite = self.universeGui.getPlayerSprite(player.id)
                    drawCircle(sprite, colours.white, 4)

            # Go through and update the positions of the players on the screen.
            for playerSprite in self.universeGui.iterPlayers():
                self.drawPlayer(screen, sRect, playerSprite)

            if self.universe.uiOptions.showNets:
                for team in self.universe.teams:
                    colour = colours.miniMapTrosballTargetColour(team)
                    drawCircle(
                        self.universe.trosballManager.getTargetZoneDefn(team),
                        colour, 3)

            # Draw the box showing where the view is looking
            worldRect = self.viewManager.getMapRect()
            topLeft = self.mapPosToMinimap(sRect, worldRect.topleft)
            bottomRight = self.mapPosToMinimap(sRect, worldRect.bottomright)
            rect = pygame.Rect(topLeft, (
                bottomRight[0] - topLeft[0], bottomRight[1] - topLeft[1]))
            pygame.draw.rect(screen, colours.minimapViewBoxColour, rect, 1)

        # Finally, draw the border
        screen.set_clip(oldClip)
        pygame.draw.rect(screen, colours.minimapBorder, sRect, 2)

    def drawCircle(self, screen, sRect, sprite, colour, radius):
        pos = self.mapPosToMinimap(sRect, sprite.pos)
        if sRect.collidepoint(*pos):
            pygame.draw.circle(screen, colour, pos, radius)

    def drawPlayer(self, screen, sRect, playerSprite):
        player = playerSprite.player
        targetPlayer = self.getTargetPlayer()
        colours = self.app.theme.colours

        if player == targetPlayer:
            # The player being drawn is the one controlled by the user.
            clr = colours.minimapOwnColour
            radius = 3
            self.drawCircle(screen, sRect, playerSprite, clr, radius)
            return

        if player.dead:
            clr = colours.miniMapGhostColour(player.team)
        else:
            clr = colours.miniMapPlayerColour(player.team)

        if not (targetPlayer and player.isFriendsWith(targetPlayer)):
            radius = 2
            self.drawCircle(screen, sRect, playerSprite, clr, radius)
            return

        # Friendly player: write letters instead of a circle
        img = playerSprite.renderMiniMapNameTag()
        rect = img.get_rect()
        rect.center = self.mapPosToMinimap(sRect, playerSprite.pos)
        screen.blit(img, rect)

    def screenToMap(self, pt):
        '''
        Converts the given point to a map position assuming it's inside the
        minimap's area.
        '''
        sRect = self.getRect()
        topCorner = [self._focus[i] - (sRect.size[i] / 2 * self.scale)
                     for i in (0,1)]
        mapOffset = ((pt[0] - sRect.left) * self.scale, (pt[1] - sRect.top) *
                self.scale)
        return (topCorner[0] + mapOffset[0], topCorner[1] + mapOffset[1])

    def drawShiftingBg(self, screen, sRect, frontLine):
        minimapTrosballPosition = self.mapPosToMinimap(
            sRect, (frontLine, 0))[0]
        colours = self.app.theme.colours
        blue = colours.miniMapDarkZoneColour(self.universe.teams[0])
        red = colours.miniMapDarkZoneColour(self.universe.teams[1])
        if minimapTrosballPosition > sRect.right:
            self.drawZones(screen, sRect, forceColour=blue)
        elif minimapTrosballPosition < sRect.left:
            self.drawZones(screen, sRect, forceColour=red)
        else:
            blueWidth = minimapTrosballPosition - sRect.left
            blueRect = pygame.Rect(sRect.left, sRect.top, blueWidth,
                    sRect.height)
            redRect = pygame.Rect(minimapTrosballPosition, sRect.top,
                    sRect.width - blueWidth, sRect.height)
            clip = screen.get_clip()
            try:
                screen.set_clip(blueRect)
                self.drawZones(screen, sRect, forceColour=blue)
                screen.set_clip(redRect)
                self.drawZones(screen, sRect, forceColour=red)
            finally:
                screen.set_clip(clip)

    def drawZones(self, screen, sRect, forceColour=None):
        '''Draws the miniMap graphics onto the screen'''
        topCorner = [self._focus[i] - (sRect.size[i] / 2 * self.scale)
                     for i in (0,1)]
        # Find which map blocks are on the screen.
        i, j = MapLayout.getMapBlockIndices(*topCorner)
        i = max(0, i)
        j = max(0, j)
        firstBlock = self.universe.zoneBlocks[i][j]


        # Set the initial position back to where it should be.
        firstPos = self.mapPosToMinimap(sRect, firstBlock.defn.rect.topleft)
        firstPos = [min(firstPos[a], sRect.topleft[a]) for a in (0, 1)]

        posToDraw = [firstPos[a] for a in (0,1)]
        y, x = i, j
        while posToDraw[1] < sRect.bottom:
            while posToDraw[0] < sRect.right:
                try:
                    block = self.universe.zoneBlocks[y][x]
                except IndexError:
                    break
                zone = None
                if isinstance(block, mapblocks.InterfaceMapBlock):
                    currentRect = self.interfaceBlockRect
                elif isinstance(block, mapblocks.BottomBodyMapBlock):
                    currentRect = self.bodyBlockRect
                    zone = block.zone
                else:
                    currentRect = self.bodyBlockRect
                currentRect.topleft = posToDraw
                area = currentRect.clip(sRect)
                draw = True
                if area.size == currentRect.size:
                    # Nothing has changed.
                    self._drawBlockMiniBg(
                        block, screen, sRect, currentRect,
                        forceColour=forceColour)
                elif area.size == (0,0):
                    # Outside the bounds of the minimap
                    draw = False
                else:
                    self._drawBlockMiniBg(
                        block, screen, sRect, currentRect, area,
                        forceColour=forceColour)

                if draw and zone:
                    self.drawZoneDecoration(
                        zone, screen, sRect, currentRect.midtop)

                posToDraw[0] += currentRect.width
                x += 1
            x = j
            y += 1
            # Next Row
            posToDraw[0] = firstPos[0]
            posToDraw[1] += self.interfaceBlockRect.height

    def drawZoneLetter(self, screen, sRect, zone, centre):
        img = self.renderLetter(zone.defn.label)
        rect = img.get_rect()
        rect.center = centre
        screen.blit(img, rect)

    def getZoneHighlight(self, zone):
        '''
        Determines whether the given zone should be highlighted and if so in
        what colour. Returns None if the zone should not be highlighted on the
        minimap, otherwise returns the highlight colour.
        '''
        if not self.universe.abilities.zoneCaps:
            return None

        sprites = self.app.theme.sprites

        player = self.getTargetPlayer()
        if player is None or player.team is None:
            playerTeam = self.universe.teams[0]
        else:
            playerTeam = player.team
        owner = zone.owner
        if zone.isCapturableBy(playerTeam):
            return sprites.zoneHighlight(playerTeam, self.scale)
        if owner == playerTeam or owner is None:
            teams = zone.teamsAbleToTag()
            teams.discard(playerTeam)
            if teams:
                return sprites.zoneHighlight(teams.pop(), self.scale)
        if zone.isBorderline():
            return sprites.zoneHighlight(None, self.scale)
        return None

    def drawZoneDecoration(self, zone, screen, sRect, centre):
        if not self.universe.uiOptions.showNets:
            highlight = self.getZoneHighlight(zone)
            if highlight:
                rect = highlight.get_rect()
                rect.center = centre
                screen.blit(highlight, rect)
        self.drawZoneLetter(screen, sRect, zone, centre)

    def _drawBlockMiniBg(self, block, surface, sRect, rect, area=None,
            forceColour=None):
        if block.defn.kind == 'fwd':
            self._drawFwdBlockMiniBg(block, surface, rect, area, forceColour)
        elif block.defn.kind == 'bck':
            self._drawBckBlockMiniBg(block, surface, rect, area, forceColour)
        else:
            self._drawBodyBlockMiniBg(block, surface, rect, area, forceColour)
        self._drawBlockMiniArtwork(block, surface, rect, area)

    def _drawBlockMiniArtwork(self, block, surface, rect, area):
        if block.defn.graphics is None:
            return

        if area is not None:
            cropPos = (area.left - rect.left, area.top - rect.top)
            crop = pygame.rect.Rect(cropPos, area.size)
            surface.blit(block.defn.graphics.getMini(
                self.app, self.graphicsScale), area.topleft, crop)
        else:
            surface.blit(block.defn.graphics.getMini(
                self.app, self.graphicsScale), rect.topleft)

    def _drawBodyBlockMiniBg(self, block, surface, rect, area,
            forceColour=None):
        if block.zone:
            clr = (self._getMiniMapColour(block.zone) if forceColour is None
                    else forceColour)
        else:
            clr = (0, 0, 0)
        if area is not None:
            pygame.draw.rect(surface, clr, area)
        else:
            pygame.draw.rect(surface, clr, rect)

    def renderLetter(self, letter):
        if not hasattr(self, 'letters'):
            self.letters = {}
        if letter not in self.letters:
            font = self.app.screenManager.fonts.ingameMenuFont
            shadow = font.render(self.app, letter, False, (0, 0, 0))
            highlight = font.render(self.app, letter, False, (255, 255, 255))
            x, y = highlight.get_size()
            xOff, yOff = SHADOW_OFFSET
            result = pygame.Surface((x + xOff, y + yOff)).convert()
            result.fill((0, 0, 1))
            result.set_colorkey((0, 0, 1))
            result.blit(shadow, SHADOW_OFFSET)
            result.blit(highlight, (0, 0))
            self.letters[letter] = result
        return self.letters[letter]

    def _drawFwdBlockMiniBg(self, block, surface, rect, area, forceColour=None):
        if area:
            tempSurface = pygame.surface.Surface(rect.size)
            tempRect = tempSurface.get_rect()
        if block.zone1:
            clr = (self._getMiniMapColour(block.zone1) if forceColour is None
                    else forceColour)
        else:
            clr = (0, 0, 0)
        if area:
            pts = (tempRect.topleft, tempRect.topright, tempRect.bottomleft)
            pygame.draw.polygon(tempSurface, clr, pts)
        else:
            pts = (rect.topleft, rect.topright, rect.bottomleft)
            pygame.draw.polygon(surface, clr, pts)

        if block.zone2:
            clr = (self._getMiniMapColour(block.zone2) if forceColour is None
                    else forceColour)
        else:
            clr = (0, 0, 0)

        if area:
            pts = (tempRect.bottomright, tempRect.topright, tempRect.bottomleft)
            pygame.draw.polygon(tempSurface, clr, pts)
            # Now put it onto surface
            cropPos = (area.left - rect.left, area.top - rect.top)
            crop = pygame.rect.Rect(cropPos, area.size)
            surface.blit(tempSurface, area.topleft, crop)
        else:
            pts = (rect.bottomright, rect.topright, rect.bottomleft)
            pygame.draw.polygon(surface, clr, pts)

    def _drawBckBlockMiniBg(self, block, surface, rect, area, forceColour=None):
        if area:
            tempSurface = pygame.surface.Surface(rect.size)
            tempRect = tempSurface.get_rect()
        if block.zone1:
            clr = (self._getMiniMapColour(block.zone1) if forceColour is None
                    else forceColour)
        else:
            clr = (0, 0, 0)

        if area:
            pts = (tempRect.topleft, tempRect.bottomright, tempRect.bottomleft)
            pygame.draw.polygon(tempSurface, clr, pts)
        else:
            pts = (rect.topleft, rect.bottomright, rect.bottomleft)
            pygame.draw.polygon(surface, clr, pts)

        if block.zone2:
            clr = (self._getMiniMapColour(block.zone2) if forceColour is None
                    else forceColour)
        else:
            clr = (0, 0, 0)
        if area:
            pts = (tempRect.topleft, tempRect.bottomright, tempRect.topright)
            pygame.draw.polygon(tempSurface, clr, pts)
            # Now put it onto surface
            cropPos = (area.left - rect.left, area.top - rect.top)
            crop = pygame.rect.Rect(cropPos, area.size)
            surface.blit(tempSurface, area.topleft, crop)
        else:
            pts = (rect.topleft, rect.bottomright, rect.topright)
            pygame.draw.polygon(surface, clr, pts)

    def _getMiniMapColour(self, zone):
        colours = self.app.theme.colours
        if zone.dark:
            result = colours.miniMapDarkZoneColour(zone.owner)
        else:
            result = colours.miniMapLightZoneColour(zone.owner)
        return result

    # The right-most and left-most positions at which the minimap can focus
    def getBoundaries(self):
        if not self.universe.zoneBlocks:
            return (0, 0), (1, 1)
        # The edge of the map will always be an interfaceMapBlock
        indices = (len(self.universe.zoneBlocks) - 1,
                   len(self.universe.zoneBlocks[0]) - 1)

        block = self.universe.zoneBlocks[indices[0]][indices[1]]
        pos = block.defn.rect.bottomright
        sRect = self.getRect()
        rightMost = (pos[0] - sRect.size[0] * self.scale / 2,
                             pos[1] - sRect.size[1] * self.scale / 2)

        # The left-most position at which the minimap can focus
        leftMost = (sRect.size[0] * self.scale / 2,
                            sRect.size[1] * self.scale / 2)

        return rightMost, leftMost

    def getTargetPlayer(self):
        if isinstance(self.viewManager.target, PlayerSprite):
            return self.viewManager.target.player
        return None

    def updateFocus(self):
        if isinstance(self.viewManager.target, PlayerSprite):
            self._focus = self.viewManager.target.pos
        elif self.viewManager.target is None:
            self._focus = self.viewManager._focus
        else:
            #assert isinstance(self._focus, tuple)
            self._focus = self.viewManager.target

        rightMost, leftMost = self.getBoundaries()
        self._focus = [max(min(self._focus[i], rightMost[i]), leftMost[i]) for
                i in (0,1)]

    def disrupted(self):
        self.disrupt = True

    def endDisruption(self):
        self.disrupt = False

    def getZoneAtPoint(self, pt):
        if self.getRect().collidepoint(pt):
            x, y = self.screenToMap(pt)
            i, j = MapLayout.getMapBlockIndices(x, y)
            try:
                return self.universe.map.zoneBlocks[i][j].getZoneAtPoint(x, y)
            except IndexError:
                return None
        return None
