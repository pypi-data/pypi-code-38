from trosnoth.gui.framework import framework
from trosnoth.gui.framework.elements import TextElement, Backdrop
from trosnoth.version import titleVersion

from trosnoth.gui.common import (Location, ScaledSize,
        FullScreenAttachedPoint)

class TrosnothBackdrop(framework.CompoundElement):
    def __init__(self, app):
        super(TrosnothBackdrop, self).__init__(app)

        backdropPath = app.theme.getPath('startupMenu', 'blackdrop.png')
        backdrop = Backdrop(app, backdropPath,
                app.theme.colours.backgroundFiller)

        # Things that will be part of the backdrop of the entire startup menu
        # system.
        verFont = self.app.screenManager.fonts.versionFont
        self.elements = [
            backdrop,
            TextElement(self.app, titleVersion, verFont,
                Location(FullScreenAttachedPoint(ScaledSize(-10,-10),
                'bottomright'), 'bottomright'),
                app.theme.colours.versionColour),
        ]

