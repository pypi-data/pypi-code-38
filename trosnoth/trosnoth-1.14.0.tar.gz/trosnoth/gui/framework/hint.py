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

from .framework import Element
import pygame

class Hint(Element):
    reqTimeOver = 0.8
    disappearTime = 8

    def __init__(self, app, text, elementOver, font, align='left'):
        super(Hint, self).__init__(app)

        self.lines = text.split('\n')
        self.font = font
        self.align = align

        self.elementOver = elementOver

        # Check that it's valid at constructor time
        self._getOverRect()

        # Value for storing how long the mouse has been over our rect:
        self.timeOver = 0

        self.visible = False
        self.beenOff = True
        self.pos = (0,0)

    def _getOverRect(self):
        # Try to get a rect argument from elementOver
        if isinstance(self.elementOver, pygame.Rect):
            return self.elementOver
        # Try to get it from an element:
        elif hasattr(self.elementOver, '_getRect'):
            return self.elementOver._getRect()
        else:
            raise ValueError('Not a valid elementOver argument')

    def __getSurface(self):
        bgColour = (204, 204, 0)
        rendered = []
        for line in self.lines:
            rendered.append(self.font.render(self.app, line, True, (0,0,0),
                    bgColour))
        width = 0
        height = 0
        for r in rendered:
            width = max(width, r.get_width())
            height += r.get_height()

        # Create our own image now:
        border = (3,3)
        surface = pygame.Surface((width + 2 * border[0],
                height + 2 * border[1]))
        surface.fill(bgColour)
        yPos = border[1]
        for r in rendered:
            if self.align == 'left':
                xPos = border[0]
            elif self.align == 'right':
                xPos = width - r.get_width() + border[0]
            elif self.align == 'middle':
                xPos = (width - r.get_width()) / 2 + border[0]
            else:
                raise ValueError('Not a valid alignment argument')

            surface.blit(r, (xPos, yPos))
            yPos += r.get_height()
        pygame.draw.rect(surface, (0,0,0), surface.get_rect(), 3)
        return surface

    def processEvent(self, event):
        '''Processes the specified event and returns the event if it should
        be passed on, or None if it has been caught.'''
        # All events will make our hint invisible, unless it's a
        # mouse motion that stays within our rect, without touching
        # the hint image
        if (event.type == pygame.MOUSEMOTION and (self.visible or not
                self.beenOff)):
            rect = self.__getSurface().get_rect()
            rect.topleft = self.pos
            if (not self._getOverRect().collidepoint(event.pos)):
                # It's no longer over our rect.
                self.visible = False
                self.timeOver = 0
                self.beenOff = True

            elif rect.collidepoint(event.pos):
                    # It's on our hint! Quick! Disappear!
                    self.visible = False
                    self.timeOver = 0
        else:
            self.visible = False
            self.timeOver = 0
        return event

    def tick(self, deltaT):
        '''Gives the element a chance to update itself. deltaT is the time
        in seconds since the last tick cycle.'''
        pos = pygame.mouse.get_pos()
        if self._getOverRect().collidepoint(pos):
            self.timeOver += deltaT
            if self.timeOver > self.disappearTime:
                self.visible = False
            elif (not self.visible and self.beenOff and self.timeOver >
                    self.reqTimeOver):
                self.visible = True
                # Remember the position, and provide a little offset
                self.pos = (pos[0] + 2, pos[1] + 2)
                self.beenOff = False

    def draw(self, screen):
        '''Gives the element a chance to draw itself onto the screen.'''
        if self.visible:
            # Let's check that pos is a good position to place it - when it was
            # set in the tick method, we had no idea about the size of the
            # screen.
            surface = self.__getSurface()
            x, y = self.pos
            xChange = yChange = False
            width, height = surface.get_rect().size
            screenWidth, screenHeight = screen.get_rect().size
            if screenWidth - self.pos[0] < width:
                x = screenWidth - width
                xChange = True
            if screenHeight - self.pos[1] < height:
                y = screenHeight - height
                yChange = True
            if xChange and yChange:
                # It is extremely likely that the mouse is over
                # the hint - not convenient.
                # Let's try putting it on another side - may not be
                # successful though (i.e. if the hint is too big)
                if x > width:
                    x = x - width
                elif y > width:
                    y = y - width

            # Put the start of the text on screen
            if x < 0:
                x = 0
            if y < 0:
                y = 0

            self.pos = x, y
            screen.blit(self.__getSurface(), self.pos)
