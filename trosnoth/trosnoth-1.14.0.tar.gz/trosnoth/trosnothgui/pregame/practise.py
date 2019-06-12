from trosnoth.utils.event import Event
from trosnoth.gui.common import (Region, Canvas, Location)
from trosnoth.gui.framework import framework
from trosnoth.gui.framework.elements import (SolidRect, TextButton)
from trosnoth.model import mapLayout
from trosnoth.game import LocalGame

SIZE = (3, 1)
AICOUNT = 5

class PractiseScreen(framework.CompoundElement):
    def __init__(self, app, onClose=None, onStart=None):
        super(PractiseScreen, self).__init__(app)

        self.onClose = Event()
        if onClose is not None:
            self.onClose.addListener(onClose)
        self.onStart = Event()
        if onStart is not None:
            self.onStart.addListener(onStart)

        if app.displaySettings.alphaOverlays:
            alpha = 192
        else:
            alpha = None
        bg = SolidRect(app, app.theme.colours.playMenu, alpha,
                Region(centre=Canvas(512, 384), size=Canvas(924, 500)))

        #colour = app.theme.colours.mainMenuColour
        #font = app.screenManager.fonts.consoleFont

        font = app.screenManager.fonts.bigMenuFont
        cancel = TextButton(app, Location(Canvas(512, 624), 'midbottom'),
                'Cancel', font, app.theme.colours.secondMenuColour,
                app.theme.colours.white, onClick=self.cancel)
        self.elements = [bg, cancel]

    def cancel(self, element):
        self.onClose.execute()

    def startGame(self):
        db = self.app.layoutDatabase
        game = LocalGame(db, SIZE[0], SIZE[1],
                onceOnly=True)

        for i in range(AICOUNT):
            game.addBot('ranger')

        self.onStart.execute(game)
