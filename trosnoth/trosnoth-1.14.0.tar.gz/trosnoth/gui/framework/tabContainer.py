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

from trosnoth.gui.framework.framework import Element, CompoundElement
from trosnoth.gui.framework.hotkey import Hotkey
from trosnoth.gui.framework.tab import Tab
from trosnoth.gui.common import Location, AttachedPoint, ScaledScalar
from trosnoth.utils.event import Event
import pygame

class TabHeader(Element):
    def __init__(self, app, tab, tabContainer, font):
        super(TabHeader, self).__init__(app)
        self.tab = tab
        self.tabContainer = tabContainer
        self.pos = None
        self.font = font

        self._mouseOver = False

    def setDimensions(self, pos, size):
        self.pos = pos
        self.size = size
        self._redraw()

    def _getColour(self):
        if self.hasFocus:
            return self.tabContainer.borderColour
        elif self._mouseOver:
            return (192, 192, 192)
        else:
            return (128, 128, 128)


    def _redraw(self):
        assert self.pos
        self.surface = pygame.surface.Surface(self.size)
        newSurface = self.font.render(self.app, self.tab.caption, True,
                self._getColour())
        newRect = newSurface.get_rect(centerx=self.size[0] / 2)

        x = self.tabContainer._getBorderWidth() + 2
        self.surface.blit(newSurface, (max(x, newRect.left), x))


    def gotFocus(self):
        self._redraw()

    def lostFocus(self):
        self._redraw()

    def processEvent(self, event):
        if (not self.hasFocus and event.type == pygame.MOUSEBUTTONDOWN
                and event.button == 1 and pygame.Rect(self.pos,
                self.size).collidepoint(event.pos)):
            self.tabContainer._tabSelected(self.tab)
        else:
            return event

    def draw(self, screen):
        screen.blit(self.surface, self.pos)
        pygame.draw.rect(screen, self._getColour(), pygame.Rect(self.pos,
                self.size), self.tabContainer._getBorderWidth())

    def tick(self, deltaT):
        if pygame.Rect(self.pos, self.size).collidepoint(
                pygame.mouse.get_pos()):
            if not self._mouseOver:
                self._mouseOver = True
                self._redraw()
        else:
            if self._mouseOver:
                self._mouseOver = False
                self._redraw()

class TabHeaderArrow(Element):
    def __init__(self, app, tabContainer, text, font, onclick, clickable):
        super(TabHeaderArrow, self).__init__(app)
        self.pos = None
        self.tabContainer = tabContainer
        self.font = font
        self.text = text
        self.onclick = onclick
        self.clickable = clickable

        self._mouseOver = False

    def setDimensions(self, pos, size):
        self.pos = pos
        self.size = size
        self._redraw()

    def _getColour(self):
        if not self.clickable():
            return (128, 128, 128)
        if self._mouseOver:
            return (255, 255, 255)
        else:
            return (192, 192, 192)

    def _getSize(self):
        return self.size.getSize(self.app)

    def _getRect(self):
        r = pygame.Rect((0,0), self._getSize())
        if hasattr(self.pos, 'apply'):
            self.pos.apply(self.app, r)
        return r

    def _getPt(self):
        return self._getRect().topleft

    def _redraw(self):
        assert self.pos
        self.surface = pygame.surface.Surface(self._getSize())
        newSurface = self.font.render(self.app, self.text, True,
                self._getColour())
        newRect = newSurface.get_rect(centerx=self._getSize()[0] / 2)

        x = self.tabContainer._getBorderWidth() + 2
        self.surface.blit(newSurface, (max(x, newRect.left), x))

    def gotFocus(self):
        self._redraw()

    def lostFocus(self):
        self._redraw()

    def processEvent(self, event):
        if (self.clickable() and not self.hasFocus and event.type ==
                pygame.MOUSEBUTTONDOWN and
                self._getRect().collidepoint(event.pos)):
            self.onclick()
        else:
            return event

    def draw(self, screen):
        self._redraw()
        screen.blit(self.surface, self._getPt())
        pygame.draw.rect(screen, self._getColour(), self._getRect(),
                self.tabContainer._getBorderWidth())

    def tick(self, deltaT):
        if self._getRect().collidepoint(pygame.mouse.get_pos()):
            if not self._mouseOver:
                self._mouseOver = True
        else:
            if self._mouseOver:
                self._mouseOver = False

class TabHeaderRow(CompoundElement):
    def __init__(self, app, tabContainer):
        super(CompoundElement, self).__init__(app)

        self.firstVisible = 0
        self.skipOnMove = 3
        self.numToDisplay = 0
        self.arrowWidth = arrowWidth = 30

        self.elements = []
        self.headers = []
        self.selectedIndex = -1

        onLeft = lambda: self._moveDirection(True)
        onRight = lambda: self._moveDirection(False)
        canClickLeft = lambda: self.firstVisible > 0
        canClickRight = lambda: (self.firstVisible + self.numToDisplay <
                len(self.headers))
        self.tabContainer = tabContainer

        self._getHeight = _getHeight = tabContainer._getHeaderHeight

        class ArrowSize(object):
            def __init__(self, text):
                self.text = text

            def getSize(self, app):
                return (arrowWidth, _getHeight())

            def __repr__(self):
                return 'Arrow Size'

        self.leftArrow = TabHeaderArrow(app, tabContainer, '<',
                tabContainer.font, onLeft, canClickLeft)
        leftLocation = Location(AttachedPoint((0,0), tabContainer._getRect,
                'topleft'), 'topleft')
        leftSize = ArrowSize('<')
        self.leftArrow.setDimensions(leftLocation, leftSize)

        self.rightArrow = TabHeaderArrow(app, tabContainer, '>',
                tabContainer.font, onRight, canClickRight)
        rightLocation = Location(AttachedPoint((0,0), tabContainer._getRect,
                'topright'), 'topright')
        rightSize = ArrowSize('>')
        self.rightArrow.setDimensions(rightLocation, rightSize)

        self._getPt = self.tabContainer._getPt

    def _getMaxHeaderWidth(self):
        return max(self._getHeight() * 5, self._getWidth() / 3)

    def _getMinHeaderWidth(self):
        return self._getHeight()

    def _getWidth(self):
        return self.tabContainer._getSize()[0]


    def __len__(self):
        return len(self.headers)

    def _moveDirection(self, left):
        if left:
            self.firstVisible = max(self.firstVisible - self.skipOnMove, 0)
        else:
            self.firstVisible = min(self.firstVisible + self.skipOnMove,
                    len(self.headers)-self.numToDisplay)

        self._update()

    def newTabHeader(self, header):
        self.headers.append(header)
        self._update()
        self._orderElements()

    def delTabHeader(self, index):
        # Handling the selectedIndex is done in the tabContainer itself
        del self.headers[index]
        if self.selectedIndex == index:
            self.selectedIndex = -1
        self._update()

    def tabSelected(self, index):
        if self.selectedIndex > -1 and self.selectedIndex < len(self.headers):
            self.headers[self.selectedIndex].lostFocus()
            self.headers[self.selectedIndex].hasFocus = False
        self.selectedIndex = index
        self._setFirstVisible()
        self._update()
        self.setFocus(self.headers[self.selectedIndex])

    def _orderElements(self):
        if self.firstVisible + self.numToDisplay > len(self.headers):
            self.firstVisible = len(self.headers) - self.numToDisplay
        if self.selectedIndex == -1:
            self.elements = []
        elif (self.firstVisible <= self.selectedIndex < self.firstVisible +
                self.numToDisplay):
            self.elements = (
                self.headers[self.firstVisible:self.selectedIndex] +
                self.headers[self.selectedIndex + 1:
                    self.firstVisible + self.numToDisplay] +
                [self.headers[self.selectedIndex]])
        else:
            self.elements = self.headers[self.firstVisible:
                    self.firstVisible + self.numToDisplay]
        if self.numToDisplay != len(self.headers):
            self.elements.append(self.leftArrow)
            self.elements.append(self.rightArrow)

    def _setFirstVisible(self):
        if (self.firstVisible <= self.selectedIndex < self.firstVisible +
                self.numToDisplay):
            pass
        elif self.selectedIndex < self.firstVisible:
            self.firstVisible = self.selectedIndex
        elif self.selectedIndex >= self.firstVisible + self.numToDisplay:
            self.firstVisible = self.selectedIndex - self.numToDisplay + 1
        self._orderElements()

    def tick(self, deltaT):
        self._update()
        self._orderElements()
        super(TabHeaderRow, self).tick(deltaT)


    def _update(self):
        if len(self.headers) > 0:
            # m is the size that each tab header would be
            # if we were to fit them all in
            m = self._getWidth() / len(self.headers)

            # Too many headers, so use arrows to navigate
            if m < self._getMinHeaderWidth():
                availableWidth = self._getWidth() - 2 * self.arrowWidth
                self.numToDisplay = availableWidth / self._getMinHeaderWidth()
                width = availableWidth / self.numToDisplay
                remainder = availableWidth % self.numToDisplay
                self._orderElements()
                currentX = self._getPt()[0] + self.arrowWidth

            # Headers all fit, but will be compressed
            elif m < self._getMaxHeaderWidth():
                width = m
                remainder = self._getWidth() % len(self.headers)
                self.numToDisplay = len(self.headers)
                self.firstVisible = 0
                currentX = self._getPt()[0]

            # There are less headers than can stretch across the tab header area
            else:
                width = self._getMaxHeaderWidth()
                remainder = 0
                self.numToDisplay = len(self.headers)
                self.firstVisible = 0
                currentX = self._getPt()[0]

            for x in range (self.firstVisible,
                    self.firstVisible+self.numToDisplay):
                header = self.headers[x]
                thisWidth = width
                # Do a bit of balancing for tab header widths
                if x - self.firstVisible < remainder:
                    thisWidth += 1
                header.setDimensions((currentX, self._getPt()[1]), (thisWidth,
                        self._getHeight()))
                currentX += thisWidth

class TabContainer(CompoundElement):
    def __init__(self, app, area, font, borderColour=(0, 0, 0)):
        super(TabContainer, self).__init__(app)

        self.onTabSelected = Event()

        # area is that of the entire space including tab headers
        self.area = area
        self.font = font

        self._borderWidth = ScaledScalar(3)
        self.borderColour = borderColour

        nextTab = lambda: self._tabSelected((self.selectedIndex + 1) %
                len(self.tabs))
        lastTab = lambda: self._tabSelected((self.selectedIndex - 1) %
                len(self.tabs))
        self.nextTabKey = Hotkey(app, pygame.K_TAB, pygame.KMOD_CTRL)
        self.nextTabKey.onTriggered.addListener(nextTab)
        self.lastTabKey = Hotkey(app, pygame.K_TAB,
                pygame.KMOD_CTRL|pygame.KMOD_SHIFT)
        self.lastTabKey.onTriggered.addListener(lastTab)

        self.tabs = []
        self.tabHeaders = TabHeaderRow(app, self)
        self.selectedIndex = -1

        self.tabHeaders._update()

        self.elements = [self.tabHeaders, self.lastTabKey, self.nextTabKey]
        self.tabHeaders._update()

    def _getBorderWidth(self):
        if hasattr(self._borderWidth, 'getVal'):
            return int(self._borderWidth.getVal(self.app))
        else:
            return self._borderWidth

    def _getHeaderHeight(self):
        linesize = self.font.getLineSize(self.app)
        return int(linesize * 1.1)


    ##
    # Full rect (including headers)
    def _getRect(self):
        return self.area.getRect(self.app)

    def _getSize(self):
        return self._getRect().size

    def _getPt(self):
        return self._getRect().topleft

    ##
    # For the internal rect (not including headers)
    def _getTabPos(self):
        pos = self._getPt()
        return (pos[0], pos[1]+self._getHeaderHeight())

    def _getTabSize(self):
        size = self._getSize()
        return (size[0], size[1]-self._getHeaderHeight())

    def _getTabRect(self):
        return pygame.Rect(self._getTabPos(), self._getTabSize())

    def _getTabInternalRect(self):
        '''
        Returns the pygame.Rect of area which the tab should draw on. (When the
        tab draws it is relative to the top-left of the tab container.)
        '''
        return pygame.Rect((0, self._getHeaderHeight()), self._getTabSize())

    def selectTab(self, index):
        self._tabSelected(index)

    def _tabSelected(self, tab):
        if self.selectedIndex != -1:
            if not self.tabs[self.selectedIndex].beforeDeactivating():
                return
            self.tabs[self.selectedIndex].deactivated()
        if isinstance(tab, Tab):
            assert tab in self.tabs, 'This tab must be in our list'
            self.selectedIndex = self.tabs.index(tab)
        else:
            # By index
            self.selectedIndex = tab

        # Notify those who care:
        self.tabHeaders.tabSelected(self.selectedIndex)
        self.onTabSelected.execute(self.selectedIndex)
        self.tabs[self.selectedIndex].activated()

    def addTab(self, tab):
        self.tabs.append(tab)
        tab.container = self

        newHeader = TabHeader(self.app, tab, self, self.font)
        self.tabHeaders.newTabHeader(newHeader)

        self.tabHeaders._update()
        # If it's the only tab, select it
        if self.selectedIndex == -1:
            self._tabSelected(tab)

    def renameTab(self, newName, tab):
        tab.caption = newName
        self.tabHeaders._update()

    def removeTabAt(self, index):
        tab = self.tabs.pop(index)
        tab.container = None

        self.tabHeaders.delTabHeader(index)
        assert len(self.tabs) == len(self.tabHeaders)
        assert len(self.tabs) != 0
        if index == self.selectedIndex:
            self.selectedIndex = -1
            self._tabSelected(min(index, len(self.tabs)-1))
        self.tabHeaders._update()

    def removeTab(self, tab):
        tab.container = None
        index = self.tabs.index(tab)
        self.removeTabAt(index)


    def draw(self, screen):
        super(TabContainer, self).draw(screen)
        assert len(self.tabs) > 0, ('Need to have at least one tab before '
                'drawing a tabContainer')
        self.tabs[self.selectedIndex].draw(screen)
        # Draw a border
        pygame.draw.rect(screen, self.borderColour, self._getTabRect(),
                self._getBorderWidth())

    def tick(self, deltaT):
        super(TabContainer, self).tick(deltaT)
        for i in range(0, len(self.tabs)):
            # tick all the tabs
            self.tabs[i].tick(deltaT)

    def processEvent(self, event):
        event = super(TabContainer, self).processEvent(event)
        if event:
            event = self.tabs[self.selectedIndex].processEvent(event)
        return event

class TabSize(object):
    def __init__(self, tc):
        self.fn = tc._getTabSize
    def getSize(self, app):
        return self.fn()
