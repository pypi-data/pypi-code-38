import logging

import pygame

from trosnoth.gui.common import defaultAnchor, addPositions
from trosnoth.gui.framework.framework import Element

log = logging.getLogger(__name__)


class Clock(Element):
    '''
    A graphical clock class; could be used to show a countdown or a count-up
    of the game in progress. Counts to the second.
    '''

    def __init__(self, app, timeFunction, pos, font,
                 colour=(0, 0, 0), bgColour=None):
        super(Clock, self).__init__(app)
        self.setTimeFunction(timeFunction)
        self.pos = pos
        self.size = None
        self.colour = colour
        self.bgColour = bgColour

        self.font = font

    def setTimeFunction(self, timeFunction):
        self.timeFunction = timeFunction

    # Rather than the size of this object changing as the numbers change,
    # set a fixed size.
    # For no fixed size, call with size as None
    def setFixedSize(self, size):
        self.size = size

    # Since 'None' as a bgColour means 'no background', call this function
    # with bgColour = False to set it to None.
    def setColours(self, fontColour=None, bgColour=None):
        if fontColour is not None:
            self.colour = fontColour
        if bgColour is not None:
            if bgColour is False:
                self.bgColour = None
            else:
                self.bgColour = bgColour

    def _getSize(self):
        if self.size is None:
            return addPositions(
                self.font.size(self.app, self.timeFunction()), (2, 0))
        else:
            return self.size.getSize(self.app)

    def _getRect(self):
        rect = pygame.Rect((0, 0), self._getSize())
        if hasattr(self.pos, 'apply'):
            self.pos.apply(self.app, rect)
        else:
            setattr(rect, defaultAnchor, self.pos)
        return rect

    def _getPt(self):
        return self._getRect().topleft

    def draw(self, surface):
        if self.bgColour is not None:
            clockImage = self.font.render(
                self.app, self.timeFunction(),
                True, self.colour, self.bgColour)
            rect = self._getRect()
            surface.fill(self.bgColour, rect)
            clockRect = clockImage.get_rect()
            clockRect.center = rect.center
            surface.blit(clockImage, clockRect.topleft)
        else:
            clockImage = self.font.render(
                self.app, self.timeFunction(),
                True, self.colour)
            surface.blit(clockImage, self._getPt())
