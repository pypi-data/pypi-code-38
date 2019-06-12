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

import pygame

from trosnoth.utils.event import Event
from trosnoth.gui.common import (uniqueColour, AttachedPoint, Location,
        TextImage)
from .framework import Element
from .elements import HoverButton

class ListBox(Element):
    def __init__(self, app, area, items, font, colour, hlColour=None,
                 showBtns=True):
        super(ListBox, self).__init__(app)
        self.area = area
        self.items = items
        self.font = font
        self.showBtns = showBtns
        self.onValueChanged = Event()

        self.setColour(colour, hlColour)

        self.offset = 0
        self.index = -1


        # Create up and down buttons.
        if showBtns:
            img1 = TextImage('up', font, colour)
            img2 = TextImage('up', font, self.hlColour)
            self.upBtn = HoverButton(self.app, Location(AttachedPoint((0,0),
                    self._getRect, 'topright'), 'topright'), img1, img2)
            self.upBtn.onClick.addListener(self.upClick)
            img1 = TextImage('down', font, colour)
            img2 = TextImage('down', font, self.hlColour)
            self.dnBtn = HoverButton(self.app, Location(AttachedPoint((0,0),
                self._getRect, 'bottomright'), 'bottomright'), img1, img2)
            self.dnBtn.onClick.addListener(self.dnClick)

    def _getRect(self):
        return self.area.getRect(self.app)

    def _getMaxInView(self):
        return int((self._getSize()[1] - 1) / self._getItemHeight()) + 1

    def _getItemHeight(self):
        return int(self.font.getLineSize(self.app))

    def setColour(self, colour, hlColour=None):
        self.colour = colour
        if hlColour:
            self.hlColour = hlColour
        else:
            self.hlColour = tuple((255 + i) / 2 for i in colour)

        self.bgColour = uniqueColour([self.hlColour, self.colour])

    def setItems(self, items):
        self.items = items
        if self.index >= len(self.items):
            self.index = -1

    def getItem(self, index=None):
        if index == None:
            index = self.index
        if index >= 0 and index < len(self.items):
            return self.items[index]
        raise ValueError("Listbox doesn't have that many items")

    def getNumItems(self):
        return len(self.items)

    def setIndex(self, index):
        if index >= self.getNumItems():
            raise ValueError("Listbox doesn't have that many items")
        self.index = index

    def getIndex(self):
        return self.index

    def _getSize(self):
        return self._getRect().size

    def _getPt(self):
        rect = self._getRect()
        return rect.topleft


    def draw(self, screen):
        rect = self._getRect()
        pos = rect.topleft


        self.offset = min(self.offset, max(0, len(self.items) -
                                           self._getMaxInView() + 1))

        # Draw the items.
        y = pos[1]
        for i in range(self.offset, min(self.offset + self._getMaxInView(),
                len(self.items))):
            text = self.font.render(self.app, self.items[i], True, self.colour)
            self._blitTextToScreen(screen, text, (pos[0], y))

            # Highlight selected one.
            if i == self.index:
                text = self.font.render(self.app, self.items[i], True,
                        self.hlColour)
                hlOffset = int(self._getItemHeight() / 30. + .5)
                self._blitTextToScreen(screen, text,
                        (pos[0] + hlOffset, y + hlOffset))


            y = y + self._getItemHeight()


        if self.showBtns:
            self.upBtn.draw(screen)
            self.dnBtn.draw(screen)

    def _blitTextToScreen(self, screen, textImage, placement):
        rect = self._getRect()
        textRect = textImage.get_rect()
        textRect.topleft = placement
        clippedRect = textRect.clip(rect)
        clippedRect.topleft = (0,0)

        screen.blit(textImage, placement, clippedRect)

    def processEvent(self, event):
        if self.showBtns:
            event = self.upBtn.processEvent(event)
            if not event: return
            event = self.dnBtn.processEvent(event)
            if not event: return

        # Click on element selects it.
        if (event.type == pygame.MOUSEBUTTONDOWN and
                self._getRect().collidepoint(event.pos)):
            # Left-click
            if event.button == 1:
                rect = self._getRect()
                pos = rect.topleft
                index = int((event.pos[1] - pos[1]) / self._getItemHeight() +
                        self.offset)
                if index < len(self.items):
                    self.index = index
                    self.onValueChanged.execute(index)
                else:
                    return event
            # Scroll up
            elif event.button == 4:
                self._changeSelection(max(self.index - 1, 0))
            # Scroll down
            elif event.button == 5:
                self._changeSelection(min(self.index + 1, len(self.items) - 1))
            else:
                return event

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self._changeSelection(max(self.index - 1, 0))
            elif event.key == pygame.K_DOWN:
                self._changeSelection(min(self.index + 1, len(self.items) - 1))
            elif event.key == pygame.K_PAGEUP:
                self._changeSelection(max(self.index - self._getMaxInView(), 0))
            elif event.key == pygame.K_PAGEDOWN:
                self._changeSelection(min(self.index + self._getMaxInView(),
                        len(self.items) - 1))
            elif event.key == pygame.K_HOME:
                self._changeSelection(0)
            elif event.key == pygame.K_END:
                self._changeSelection(len(self.items) - 1)
            else:
                return event
        else:
            return event
        return None

    def _changeSelection(self, newIndex):
        self.setIndex(newIndex)
        self._putSelectedInView()
        self.onValueChanged.execute(self.index)

    def _putSelectedInView(self):
        if self.offset+ self._getMaxInView() <= self.index:
            self.offset = (min(self.index + 3, len(self.items)) -
                    self._getMaxInView())
        elif self.offset > self.index:
            self.offset = max(self.index - 2, 0)

    def tick(self, deltaT):
        if not self.showBtns: return

        self.upBtn.tick(deltaT)
        self.dnBtn.tick(deltaT)

    def upClick(self, btn):
        self.offset = max(self.offset - 1, 0)

    def dnClick(self, btn):
        self.offset = self.offset + 1

