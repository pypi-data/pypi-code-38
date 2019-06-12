import pygame
import trosnoth.gui.framework.framework as framework
from trosnoth.utils.event import Event
from trosnoth.gui.common import ScaledArea

class Slider(framework.Element):
    def __init__(self, app, area, bounds=None, snap=False):
        super(Slider, self).__init__(app)
        self.app = app
        self.area = area
        self.beingDragged = False
        self.snap = snap
        if not bounds:
            bounds = 0, 100
        self.lowBound, self.highBound = bounds
        self.unscaledSlider = 20
        self.sliderRectWidth = int(self.unscaledSlider *
                app.screenManager.scaleFactor)
        self.lineColour = (0,192,0)
        self.sliderColour = (0,255,0)
        self.onValueChanged = Event()
        self.onSlide = Event()

        self.largeArea = ScaledArea(self.area.point.val[0] +
                self.unscaledSlider // 2, self.area.point.val[1],
                self.area.size.val[0] - self.unscaledSlider + 1,
                self.area.size.val[1])

        self.area, self.largeArea = self.largeArea, self.area

        self.sliderVal = self.highBound

    def doSnap(self, value):
        if self.snap:
            return int(value + 0.5)
        return value

    def getVal(self):
        return self.sliderVal

    def setVal(self, val):
        old = self.sliderVal
        self.sliderVal = self.doSnap(val)
        if old != self.sliderVal:
            self.onValueChanged.execute(self.sliderVal)

    def setRange(self, low, high):
        self.lowBound = low
        self.highBound = high
        if self.sliderVal > self.highBound:
            self.sliderVal = self.highBound
        elif self.sliderVal < self.lowBound:
            self.sliderVal = self.lowBound

    def setSliderColour(self, colour):
        self.sliderColour = colour

    def setLineColour(self, colour):
        self.lineColour = colour

    def _getRange(self):
        return self.highBound - self.lowBound

    def _getRect(self):
        return self.area.getRect(self.app)

    def _getPt(self):
        return self._getRect().topleft

    def _getSize(self):
        return self._getRect().size

    def _valPerPixel(self):
        return self._getSize()[0] / (self._getRange() + 0.)

    def _pixelPerVal(self):
        return self._getRange() / (self._getSize()[0] + 0.)

    # Number of pixels from 0 to width
    def _relPx(self, x):
        return min(max(0, (x - self._getPt()[0])), self._getSize()[0])

    def _mouseAt(self, x):
        old = self.sliderVal
        self.sliderVal = self.lowBound + self._pixelPerVal() * self._relPx(x)
        if old != self.sliderVal:
            self.onSlide.execute(self.sliderVal)

    def _getSliderRect(self):
        # Ignore pos for now
        sliderRect = pygame.Rect(0,0, self._getSliderRectWidth(),
                self._getSize()[1])
        pt = self._getPt()
        sliderRect.midtop = ((self.sliderVal - self.lowBound) *
                self._valPerPixel() + pt[0], pt[1])
        return sliderRect

    def _getLineWidth(self):
        return max(1, self._getSize()[1] // 8)

    def _getSliderRectWidth(self):
        return int(self.unscaledSlider * self.app.screenManager.scaleFactor)


    def processEvent(self, event):
        if (event.type == pygame.MOUSEBUTTONDOWN and
                self.largeArea.getRect(self.app).collidepoint(event.pos)):
            # Each click of the scroll wheel moves the slider by 5%
            percent = int((self.highBound - self.lowBound) * 0.05)

            if event.button == 1:
                self.beingDragged = True
                self._mouseAt(event.pos[0])
            elif event.button == 4:
                self.setVal(min(self.highBound,
                                self.sliderVal + percent))
            elif event.button == 5:
                self.setVal(max(self.lowBound,
                                self.sliderVal - percent))
            else:
                return event

        elif event.type == pygame.MOUSEMOTION and self.beingDragged:
            self._mouseAt(event.pos[0])

        elif (event.type == pygame.MOUSEBUTTONUP and event.button == 1 and
                self.beingDragged):
            self.beingDragged = False
            self.sliderVal = self.doSnap(self.sliderVal)
            self.onValueChanged.execute(self.sliderVal)
        else:
            return event
        return None

    def draw(self, surface):
        r = self.largeArea.getRect(self.app)
        lineWidth = self._getLineWidth()
        pygame.draw.line(
            surface, self.lineColour, r.midleft, r.midright, lineWidth)

        if self.snap:
            low = r.left
            high = r.right
            count = self.highBound - self.lowBound + 0.
            y0 = r.centery - 0.25 * r.height
            y1 = r.centery + 0.25 * r.height
            for i in range(self.lowBound, self.highBound + 1):
                x = (high * i + low * (count - i)) // count
                pygame.draw.line(
                    surface, self.lineColour, (x, y0), (x, y1), lineWidth)

        surface.fill(self.sliderColour, self._getSliderRect())

