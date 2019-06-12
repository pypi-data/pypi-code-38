import logging

import pygame

from trosnoth.gui.common import Location
from trosnoth.gui.framework import elements, framework
from trosnoth.utils.utils import wrapline

log = logging.getLogger(__name__)


class CollapseBox(framework.CompoundElement):
    ACCELERATION = 500  # pix/s/s

    def __init__(
            self, app, region, titleFont, font, titleColour, hvrColour, colour,
            backColour, title='Note', lines=()):
        super(CollapseBox, self).__init__(app)

        self.region = region
        self.titleFont = titleFont
        self.font = font
        self.titleColour = titleColour
        self.hvrColour = hvrColour
        self.colour = colour
        self.backColour = backColour
        self.title = title
        self.lines = lines
        self.rect = None
        self.targetRect = None
        self.background = None
        self.hidden = False
        self.velocity = 0
        self.updateElements()

        app.screenManager.onResize.addListener(self.appResized)

    def appResized(self):
        self.updateElements()

    def setInfo(self, lines, title=None):
        if lines == self.lines and (title is None or title == self.title):
            return

        if title is not None:
            self.title = title
        self.lines = lines

        self.updateElements()

    def recalculateTarget(self):
        targetRect = self.region.getRect(self.app)
        titleBtn = self.makeTitleButton(targetRect)
        results = [titleBtn]

        y = targetRect.top + titleBtn.stdImage.get_height() + 4
        maxWidth = targetRect.width - 4
        font = self.font._getFont(self.app)
        if not self.hidden:
            x = targetRect.left + 2
            for line in self.lines:
                for subline in wrapline(line, font, maxWidth):
                    element = elements.TextElement(
                        app=self.app, text=subline, font=self.font,
                        pos=Location((x, y), 'topleft'),
                        colour=self.colour)
                    results.append(element)
                    y += element.image.getImage(self.app).get_height() + 2
        targetRect.height = y - targetRect.top
        return targetRect, results

    def updateElements(self):
        self.targetRect, elements = self.recalculateTarget()
        if self.rect is None:
            self.rect = self.targetRect
        else:
            self.rect.topleft = self.targetRect.topleft
            self.rect.width = self.targetRect.width

        self.background = pygame.Surface(self.rect.size, pygame.SRCALPHA)
        self.background.fill(self.backColour)

        if self.hidden or self.rect.size != self.targetRect.size:
            elements[1:] = []

        self.elements = elements

    def makeTitleButton(self, rect):
        if self.hidden:
            text = '\u25b8 ' + self.title
        else:
            text = '\u25be ' + self.title
        img = self.titleFont.render(self.app, text, True, self.titleColour)
        hvr = self.titleFont.render(self.app, text, True, self.hvrColour)

        btn = elements.HoverButton(
            app=self.app,
            pos=Location((rect.left + 2, rect.top + 2), 'topleft'),
            stdImage=img, hvrImage=hvr,
            onClick=self.toggle,
        )
        return btn

    def draw(self, screen):
        if not (self.title or self.lines):
            return
        screen.blit(self.background, self.rect)
        super(CollapseBox, self).draw(screen)

    def toggle(self, element):
        self.hidden = not self.hidden
        self.updateElements()

    def tick(self, deltaT):
        super(CollapseBox, self).tick(deltaT)

        diff = self.targetRect.height - self.rect.height
        if diff == 0:
            return

        sgn = diff / abs(diff)
        diff = abs(diff)
        self.velocity = sgn * min(
            abs(self.velocity) + deltaT * self.ACCELERATION,
            (2.0 * self.ACCELERATION * diff) ** 0.5)
        self.rect.height += sgn * min(abs(self.velocity) * deltaT + 1, diff)
        self.updateElements()
