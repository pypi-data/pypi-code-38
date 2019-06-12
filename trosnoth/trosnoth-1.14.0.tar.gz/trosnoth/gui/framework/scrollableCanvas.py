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

from trosnoth.gui.framework.framework import Element, CompoundElement
from trosnoth.gui.common import Location, AttachedPoint

log = logging.getLogger(__name__)

class ScrollBar(Element):
    defaultWidth = 15
    defaultButtonChange = 20  # number of pixels moved when button is pressed
    defaultColour = (0, 192, 0)
    defaultBackColour = (128, 128, 128)
    def __init__(self, app, parent, pos, horizontal=False):
        Element.__init__(self, app)
        self.width = self.defaultWidth
        self.buttonChange = self.defaultButtonChange
        self.colour = self.defaultColour
        self.backColour = self.defaultBackColour
        self.parent = parent
        self.pos = pos
        self.horizontal = horizontal
        if horizontal:
            self.index = 0
        else:
            self.index = 1

        self.originalPosition = 0
        self.position = 0
        self.beingDraggedFrom = None

    def _getWidth(self):
        return self.width

    # This should be checked before ever being used
    def __checkThisIsValid(self):
        if self.__getDrawableSize() >= self.__getCanvasSize():
            log.error(('Vertical', 'Horizontal')[self.horizontal])
            log.error('Drawable Area: %d', self.__getDrawableSize())
            log.error('Canvas Size: %d', self.__getCanvasSize())
            assert False, ('For there to be a scroll bar, the displaying '
                    'size must be less than the full size')

    def _getTopLeftPt(self):
        self.__checkThisIsValid()
        return self._getFullRect().topleft

    def _getBarLength(self):
        self.__checkThisIsValid()
        return self.__getDrawableSize() ** 2 / self.__getCanvasSize()

    def _getBarRect(self):
        self.__checkThisIsValid()
        if self.horizontal:
            size = (self._getBarLength(), self._getWidth())
            pos = (self._getTopLeftPt()[0] + self.getPosition(),
                    self._getTopLeftPt()[1])
        else:
            size = (self._getWidth(), self._getBarLength())
            pos = (self._getTopLeftPt()[0], self._getTopLeftPt()[1] +
                    self.getPosition())
        return pygame.rect.Rect(pos, size)

    def __getDrawableSize(self):
        return self.parent._getDrawableSize()[self.index]

    def __getCanvasSize(self):
        return self.parent._getCanvasSize()[self.index]

    def _getSize(self):
        self.__checkThisIsValid()
        if self.horizontal:
            x = self.__getDrawableSize()
            y = self._getWidth()
        else:
            x = self._getWidth()
            y = self.__getDrawableSize()
        return (x,y)

    def _getFullRect(self):
        self.__checkThisIsValid()
        r = pygame.rect.Rect((0,0), self._getSize())
        self.pos.apply(self.app, r)
        return r

    def _movedTo(self, pos):
        self.__checkThisIsValid()
        if self.horizontal:
            self.setPosition(self.originalPosition + (pos[0] -
                    self.beingDraggedFrom[0]))
        else:
            self.setPosition(self.originalPosition + (pos[1] -
                    self.beingDraggedFrom[1]))

        newScrollingPos = (self.getPosition() * self.__getCanvasSize() /
                self.__getDrawableSize())
        newScrollingPos = min(newScrollingPos, self.__getCanvasSize() -
                self.__getDrawableSize())
        if self.horizontal:
            self.parent.setHorizontalPos(newScrollingPos)
        else:
            self.parent.setVerticalPos(newScrollingPos)

    def getPosition(self):
        # This line is useful in the event of a screen resize
        self.setPosition(self.position)
        return self.position

    def setPosition(self, pos):
        self.position = min(max(pos, 0), self.__getDrawableSize() -
                self._getBarLength())

    def processEvent(self, event):
        self.__checkThisIsValid()
        if (event.type == pygame.MOUSEBUTTONDOWN and event.button == 1
                and self._getBarRect().collidepoint(event.pos) and
                self.beingDraggedFrom == None):
            self.beingDraggedFrom = event.pos
            return None
        elif (event.type == pygame.MOUSEMOTION and self.beingDraggedFrom
                != None):
            self._movedTo(event.pos)
            return None
        elif (event.type == pygame.MOUSEBUTTONUP and event.button == 1
                and self.beingDraggedFrom != None):
            self.beingDraggedFrom = None
            self.originalPosition = self.getPosition()
            return None
        return event

    def draw(self, screen):
        self.__checkThisIsValid()
        pygame.draw.rect(screen, self.backColour, self._getFullRect(), 0)
        pygame.draw.rect(screen, self.colour, self._getBarRect(), 0)


class ScrollableCanvas(CompoundElement):
    '''
    For a scrollable canvas, the displaySize is how big it will actually be
    drawn, while its size is how big the canvas is in memory.  If the size is
    bigger than the displaySize either horizontally or vertically, there will be
    a scroll bar to allow moving around the full area.
    '''
    def __init__(self, app, pos, size, displaySize):
        CompoundElement.__init__(self, app)

        self.pos = pos
        self.size = size
        self.displaySize = displaySize
        self.backgroundColour = (64,64,64)

        self._screenSize = tuple(app.screenManager.size)

        self.__horizontalScrollBar = ScrollBar(app, self,
                Location(AttachedPoint((0,0), self._getRect, 'bottomleft'),
                'bottomleft'), True)
        self.__verticalScrollBar = ScrollBar(app, self,
                Location(AttachedPoint((0,0), self._getRect, 'topright'),
                'topright'), False)

        # internalPos is the position on the full canvas that we are drawing
        # from
        self.internalPos = None
        self.setInternalPos((0,0))

    def getInternalPos(self):
        if self._screenSize != self.app.screenManager.size:
            self._screenSize = tuple(self.app.screenManager.size)
            self.setInternalPos(self.internalPos)

        return self.internalPos

    def setInternalPos(self, pos):
        self.internalPos = tuple([min(pos[i], (self._getCanvasSize()[i] -
                self._getDrawableSize()[i])) for i in (0,1)])

    def _getHorizontalScrollBar(self):
        if self._needsHorizontalScrollBar():
            return self.__horizontalScrollBar
        return None

    def _getVerticalScrollBar(self):
        if self._needsVerticalScrollBar():
            return self.__verticalScrollBar
        return None

    def _calculateIfWeNeedBars(self):
        hScroll = self._getMinimumCanvasSize()[0] > self._getSize()[0]
        if hScroll:
            vScroll = (self._getMinimumCanvasSize()[1] > self._getSize()[1] -
                    self.__horizontalScrollBar._getWidth())
        else:
            vScroll = self._getMinimumCanvasSize()[1] > self._getSize()[1]
        if vScroll and not hScroll:
            # re-calculate now that we know we have a vertical scroll bar
            hScroll = (self._getMinimumCanvasSize()[0] > self._getSize()[0] -
                    self.__verticalScrollBar._getWidth())
        return (hScroll, vScroll)

    def _getDrawableSize(self):
        drawableHeight = self._getSize()[1]

        hScroll, vScroll = self._calculateIfWeNeedBars()

        if hScroll:
            drawableHeight -= ScrollBar.defaultWidth

        drawableWidth = self._getSize()[0]
        if vScroll:
            drawableWidth -= ScrollBar.defaultWidth

        return (drawableWidth, drawableHeight)

    def _needsHorizontalScrollBar(self):
        return self._calculateIfWeNeedBars()[0]

    def _needsVerticalScrollBar(self):
        return self._calculateIfWeNeedBars()[1]

    def _getPt(self):
        return self._getRect().topleft

    def _getSize(self):
        return self.displaySize.getSize(self.app)

    def _getMinimumCanvasSize(self):
        return self.size.getSize(self.app)

    def _getCanvasSize(self):
        canvasSize = self._getMinimumCanvasSize()
        availableSize = self._getDrawableSize()
        x = max(availableSize[0], canvasSize[0])
        y = max(availableSize[1], canvasSize[1])
        return x, y

    def _getRect(self):
        r = pygame.rect.Rect((0,0), self._getSize())
        self.pos.apply(self.app, r)
        return r

    def setVerticalPos(self, verticalPos):
        self.setInternalPos((self.getInternalPos()[0], verticalPos))

    def setHorizontalPos(self, horizontalPos):
        self.setInternalPos((horizontalPos, self.getInternalPos()[1]))

    def _getContentsRect(self):
        return pygame.rect.Rect(self._getPt(), self._getDrawableSize())

    def _getOffsetCanvasRect(self):
        topleft = self._getPt()
        offsetPt = tuple([topleft[i] - self.getInternalPos()[i] for i in (0, 1)])
        return pygame.rect.Rect(offsetPt, self._getCanvasSize())

    def draw(self, screen):
        contentsRect = self._getContentsRect()
        screen.fill(self.backgroundColour, contentsRect)
        if self._needsHorizontalScrollBar():
            self._getHorizontalScrollBar().draw(screen)
        if self._needsVerticalScrollBar():
            self._getVerticalScrollBar().draw(screen)
        oldClipRect = screen.get_clip()

        if oldClipRect is None:
            screen.set_clip(contentsRect)
        else:
            assert isinstance(oldClipRect, pygame.rect.Rect)
            r = oldClipRect.clip(contentsRect)
            screen.set_clip(r)
        try:
            CompoundElement.draw(self, screen)
        finally:
            screen.set_clip(oldClipRect)

    def processEvent(self, event):
        if self._needsHorizontalScrollBar():
            event = self._getHorizontalScrollBar().processEvent(event)
        if self._needsVerticalScrollBar() and event:
            event = self._getVerticalScrollBar().processEvent(event)
        if event:
            if (event.type == pygame.MOUSEBUTTONDOWN or event.type ==
                    pygame.MOUSEBUTTONUP):
                if self._getContentsRect().collidepoint(event.pos):
                    CompoundElement.processEvent(self, event)
                    return None
                elif event.type == pygame.MOUSEMOTION:
                    CompoundElement.processEvent(self, event)
                    return event
                else:
                    return event
            else:
                return CompoundElement.processEvent(self, event)
        else:
            return None

def ScrollableCanvasAttachedPoint(scrollableCanvas, val, anchor='topleft'):
    return AttachedPoint(val, scrollableCanvas._getOffsetCanvasRect, anchor)
