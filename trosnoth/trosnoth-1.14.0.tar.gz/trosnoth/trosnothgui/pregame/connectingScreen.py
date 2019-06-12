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

from trosnoth.gui.framework.elements import TextElement, TextButton
from trosnoth.gui.framework import framework
from trosnoth.gui.common import ScaledLocation
from trosnoth.gui.common import (Location, ScaledScreenAttachedPoint,
        ScaledSize)

class ConnectingScreen(framework.CompoundElement):
    def __init__(self, app, serverName='server', onCancel=None):
        super(ConnectingScreen, self).__init__(app)
        colours = app.theme.colours

        self.text = TextElement(self.app, 'Connecting to %s...' % serverName,
                self.app.screenManager.fonts.bigMenuFont,
                ScaledLocation(512, 384, 'center'),
                colour = colours.connectingColour)

        button = TextButton(
            self.app,
            Location(ScaledScreenAttachedPoint(ScaledSize(0, 300),
                    'center'), 'center'),
            'cancel',
            self.app.screenManager.fonts.bigMenuFont,
            colours.mainMenuColour,
            colours.white,
            onClick=onCancel
        )
        self.onCancel = button.onClick

        self.elements = [button, self.text]

    def setServer(self, serverName):
        self.text.setText('Connecting to %s...' % serverName)
        self.text.setFont(self.app.screenManager.fonts.bigMenuFont)
