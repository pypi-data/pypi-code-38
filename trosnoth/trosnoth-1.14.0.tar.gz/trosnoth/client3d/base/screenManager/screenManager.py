import logging

from panda3d.core import WindowProperties

from trosnoth.utils.event import Event

log = logging.getLogger(__name__)

WINDOWED = 'Run in a window'
NO_BORDER = 'Windowed (no border)'
FULL_SCREEN = 'Full screen'


class ScreenFonts(object):
    def addFont(self, identifier, font):
        setattr(self, identifier, font)


class ScreenManager(object):
    '''Manages everything to do with the screen, especially any scaling due
    to the size of the screen.'''

    def __init__(self, app, size, displayMode, caption):
        super(ScreenManager, self).__init__()

        self.app = app
        self.onResize = Event()
        self.size = None
        self.displayMode = None
        self.setScreenProperties(size, displayMode, caption)
        self.fonts = ScreenFonts()
        self.pointer = None
        self.elements = []

    def createInterface(self, element):
        self.elements = []
        if self.pointer is not None:
            self.elements.append(self.pointer)

    def setScreenProperties(self, size, displayMode, caption):
        self.displayMode = displayMode

        self.processResize(size)

        properties = WindowProperties()
        properties.setSize(*size)
        properties.setTitle(caption + ' (panda3d)')
        properties.setFullscreen(displayMode == FULL_SCREEN)
        properties.setUndecorated(displayMode == NO_BORDER)
        # -2, -2 places the window in the middle of the screen
        properties.setOrigin(-2, -2)
        self.app.panda.win.requestProperties(properties)

    def processResize(self, size):
        if size != self.size:
            self.size = size
            self.scaleFactor = min(size[0] / 1024.,
                                   size[1] / 768.)

            # Calculate corner offset for strange screen sizes.
            self.scaledSize = self.scale((1024, 768))
            self.offsets = ((size[0] - self.scaledSize[0]) / 2,
                            (size[1] - self.scaledSize[1]) / 2)

            self.onResize()

    def isFullScreen(self):
        return self.displayMode == FULL_SCREEN

    def scale(self, point):
        '''Takes a point on a 1024x768 screen and scales it to this screen.'''
        return (int(point[0] * self.scaleFactor),
                int(point[1] * self.scaleFactor))

    def placePoint(self, point):
        '''Places the point from a 1024x768 screen onto the largest rectangle
        of that ratio that fits within this screen.'''
        return (int(point[0] * self.scaleFactor + self.offsets[0]),
                int(point[1] * self.scaleFactor + self.offsets[1]))
