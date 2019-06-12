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

from trosnoth.gui.framework.dialogbox import DialogBox, DialogBoxAttachedPoint
from trosnoth.gui.framework.elements import TextElement, TextButton
from trosnoth.gui.framework.utils import wrapWords
from trosnoth.utils.event import Event
from trosnoth.gui.common import Location, ScaledSize

absoluteWidth = 420
class ConnectionFailedDialog(DialogBox):
    def __init__(self, app, reason):
        width = app.screenManager.scaleFactor * absoluteWidth

        font = app.fonts.connectionFailedFont
        boundary = app.screenManager.scaleFactor * 20
        lines = wrapWords(app, reason, font, width - 2 * boundary)

        x = boundary
        elements = []
        colours = app.theme.colours
        for text in lines:
            elements.append(TextElement(app, text, font, Location(
                    DialogBoxAttachedPoint(self, (0, x), 'midtop'), 'midtop'),
                    colour=colours.errorColour))
            x += font.getHeight(app)

        # Boundary * 3 for top, bottom, and middle
        height = boundary * 3 + font.getHeight(app) * (len(lines) + 1)
        size = ScaledSize(absoluteWidth, height)
        super(ConnectionFailedDialog, self).__init__(
            app, size, 'Connection Failed')

        self.elements = elements
        self.elements.append(TextButton(app, Location(DialogBoxAttachedPoint(
            self, (0, -boundary), 'midbottom'), 'midbottom'), 'OK', font,
            colours.dialogButtonColour, colours.radioMouseover,
            onClick=lambda sender: self.close()))
        self.onEnter = Event()
        self.onEnter.addListener(self.close)

    def processEvent(self, event):
        if event.type == pygame.KEYDOWN and event.key in (pygame.K_KP_ENTER,
                pygame.K_RETURN):
            self.onEnter.execute()
            return None
        else:
            return super(ConnectionFailedDialog, self).processEvent(event)

