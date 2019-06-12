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

class StatList(Element):
    '''
    @param items A list of items to retrieve text from
    @param function A callable object which will be run on each item
    '''
    def __init__(self, app, pos, items, font,
            colourFunction=lambda item: ((0,0,0)), function=str, align='left'):
        super(StatList, self).__init__(app)
        self.pos = pos
        self.items = items
        self.font = font
        self.align = align
        self.colourFunction = colourFunction
        self.function = function
        self._visible = False

    def getVisibility(self):
        return self._visible

    def setVisible(self, isVisible = True):
        self._visible = isVisible

    def _moveRect(self, rect):
        if hasattr(self.pos, 'apply'):
            self.pos.apply(self.app, rect)
            return rect.topleft
        else:
            return self.pos

    def draw(self, screen):
        '''Gives the element a chance to draw itself onto the screen.'''
        if self._visible:
            totalHeight = 0
            maxWidth = 0
            surfaces = []
            colours = []
            for i in range(0, len(self.items)):
                item = self.items[i]
                text = self.function(item)
                colour = self.colourFunction(item)
                colours.append(colour)
                s = self.font.render(self.app, text, True, colour)
                maxWidth = max(maxWidth, s.get_width())
                totalHeight += s.get_height()
                surfaces.append(s)

            tempRect = pygame.Rect((0,0),(maxWidth, totalHeight))
            self._moveRect(tempRect)
            currentHeight = tempRect.top
            for s in surfaces:
                r = s.get_rect()
                setattr(r, self.align, getattr(tempRect, self.align))
                r.top = currentHeight
                screen.blit(s, r.topleft)
                currentHeight += s.get_height()
