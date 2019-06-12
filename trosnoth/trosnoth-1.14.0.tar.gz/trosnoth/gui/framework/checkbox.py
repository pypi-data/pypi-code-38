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

import logging

import pygame

from .framework import Element
from .elements import TextElement
from trosnoth.utils.event import Event
from trosnoth.gui.common import AttachedPoint, Location, ScaledSize

log = logging.getLogger(__name__)


class CheckBox(Element):
    def __init__(self, app, pos, text, font, colour, initValue=False,
                 hotkey=None, style='circle', fillColour=None):
        super(CheckBox, self).__init__(app)

        self.pos = pos
        self.font = font

        if hasattr(pos, 'apply'):
            self.text = TextElement(app, ' ' + text, font,
                    Location(AttachedPoint(ScaledSize(self._getBoxSize()[0] // 5,
                    2), self._getBoxRect, 'midright'), 'midleft'), colour)
        else:
            self.text = TextElement(app, ' ' + text, font, Location((pos[0] +
                    self._getBoxSize()[0], pos[1] - self._getBoxSize()[0] // 10),
                    'topleft'), colour)

        self.value = initValue
        self.colour = colour
        if fillColour is None:
            self.fillColour = tuple((256*3+i)//4 for i in colour)
        else:
            self.fillColour = fillColour
        self.hotkey = hotkey
        self.style = style
        self.onValueChanged = Event()

    def _getRect(self):
        return self._getBoxRect().union(self.text._getRect())

    def _getBorderWidth(self):
        return max(1, self._getBoxSize()[0] // 8)

    def _getBoxSize(self):
        return (int(self.font.getHeight(self.app) / 1.5),
                int(self.font.getHeight(self.app) / 1.5))

    def _getBoxRect(self):
        if hasattr(self.pos, 'apply'):
            box = pygame.rect.Rect((0,0), self._getBoxSize())
            self.pos.apply(self.app, box)
        else:
            box = pygame.rect.Rect(self.pos, self._getBoxSize())
        return box

    def draw(self, surface):
        box = self._getBoxRect()
        if self.value:
            if self.style == 'fill':
                pygame.draw.rect(surface, self.fillColour, box, 0)
            elif self.style == 'cross':
                pygame.draw.line(surface, self.fillColour, box.topright,
                        box.bottomleft, self._getBorderWidth())
                pygame.draw.line(surface, self.fillColour, box.topleft,
                        box.bottomright, self._getBorderWidth())
            elif self.style == 'circle':
                pygame.draw.circle(surface, self.fillColour, box.center,
                        box.width // 2 - 2)
        pygame.draw.rect(surface, self.colour, box, self._getBorderWidth())

        self.text.draw(surface)

    def setValue(self, val):
        if val != self.value:
            self.value = val
            self.onValueChanged.execute(self)

    def getValue(self):
        return self.value

    def processEvent(self, event):
        box = self._getBoxRect()
        # Active events.
        if (event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and
                box.collidepoint(event.pos)) or (event.type == pygame.KEYDOWN
                and event.key == self.hotkey):
            self.setValue(not self.value)
            self.onValueChanged.execute(self)
        else:
            return event
        return None
