import logging
import pygame

from trosnoth.gui.framework import clock
from trosnoth.gui.common import (
    Area, FullScreenAttachedPoint, Location, ScaledSize,
)
import trosnoth.gui.framework.framework as framework

log = logging.getLogger(__name__)


class GameTimer(framework.CompoundElement):
    def __init__(self, app, game):
        super(GameTimer, self).__init__(app)
        self.world = game.world
        self.app = app

        # Change these constants to say where the box goes
        self.area = Area(
            FullScreenAttachedPoint(ScaledSize(0, -3), 'midtop'),
            ScaledSize(110, 35),
            'midtop')

        self.lineWidth = max(int(3*self.app.screenManager.scaleFactor), 1)
        # Anything more than width 2 looks way too thick
        if self.lineWidth > 2:
            self.lineWidth = 2

        self.gameClock = clock.Clock(
            self.app,
            self.getTimeString,
            Location(FullScreenAttachedPoint(
                ScaledSize(0, 0), 'midtop'), 'midtop'),
            self.app.screenManager.fonts.timerFont,
            self.app.theme.colours.timerFontColour)
        self.elements = [self.gameClock]
        self.running = False

        # Seconds for half a flash
        self.flashCycle = 0.5
        # Value the countdown has to get to before it starts to flash
        self.flashValue = 30

    def getTimeString(self):
        return self.world.clock.getTimeString()

    def _flash(self, flashState):
        if flashState == 0:
            self.gameClock.setColours(self.app.theme.colours.timerFlashColour)
        else:
            self.gameClock.setColours(self.app.theme.colours.timerFontColour)

    def _getRect(self):
        return self.area.getRect(self.app)

    def tick(self, deltaT):
        super(GameTimer, self).tick(deltaT)

        if self.world.clock.shouldFlash():
            self._flash(int((self.world.clock.value / self.flashCycle) % 2))
        else:
            self._flash(1)

    def draw(self, surface):
        timerBox = self._getRect()
        # Box background
        surface.fill(self.app.theme.colours.timerBackground, timerBox)

        # Box border
        pygame.draw.rect(
            surface, self.app.theme.colours.black, timerBox, self.lineWidth)

        super(GameTimer, self).draw(surface)
