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

from trosnoth.gui.framework import framework, elements, scrollingText
from trosnoth.gui.common import (ScaledArea, Location, ScaledSize,
        ScaledScreenAttachedPoint)
from trosnoth.utils.event import Event

from trosnoth.data import getPath
import trosnoth.data.startupMenu as startupMenu

class ScalingSpeed(object):
    def __init__(self, baseSpeed):
        self.baseSpeed = baseSpeed

    def getSpeed(self, app):
        return self.baseSpeed * app.screenManager.scaleFactor

class CreditsScreen(framework.CompoundElement):
    def __init__(self, app, colour, onCancel=None, speed=None, loop=True,
            startOff=False, backText='back to main menu',
            highlight=(255, 255, 255)):
        super(CreditsScreen, self).__init__(app)
        self.colour = colour
        self.highlight = highlight

        self.onCancel = Event()
        if onCancel is not None:
            self.onCancel.addListener(onCancel)

        f = open(getPath(startupMenu, 'credits.txt'), 'rU', encoding='utf-8')
        area = ScaledArea(50,130,900, 540)
        fonts = {'body': self.app.fonts.creditsFont,
         'h1': self.app.fonts.creditsH1,
         'h2': self.app.fonts.creditsH2}
        text = f.read()
        if not startOff:
            # Make at least some room on top and bottom
            text = '\n' * 3 + text + '\n' * 2
        self.credits = scrollingText.ScrollingText(self.app,
                        area, text, self.colour,
                        fonts, textAlign='middle', loop=loop,
                        startOff=startOff)
        self.credits.setShadowColour((192, 192, 192))

        self.credits.setAutoscroll(True)
        if speed is None:
            speed = 80
        self.credits.setSpeed(ScalingSpeed(speed))
        self.credits.setBorder(False)

        self.backText = backText
        cancelButton = self.button(backText, self.onCancel.execute,
                (-50, -30), 'bottomright')

        self.elements = [self.credits, cancelButton]

    @property
    def finished(self):
        return self.credits.reachedEnd

    def setColour(self, colour):
        self.colour = colour
        self.elements[-1] = self.button(self.backText,
                self.onCancel.execute, (-50, -30), 'bottomright')
        self.credits.setColour(colour)

    def button(self, text, onClick, pos, anchor='topleft', hugeFont=False):
        pos = Location(ScaledScreenAttachedPoint(ScaledSize(pos[0], pos[1]),
                                                 anchor), anchor)
        if hugeFont:
            font = self.app.screenManager.fonts.hugeMenuFont
        else:
            font = self.app.screenManager.fonts.bigMenuFont
        result = elements.TextButton(self.app, pos, text, font, self.colour,
                                     self.highlight)
        result.onClick.addListener(lambda sender: onClick())
        return result

    def restart(self):
        self.credits.returnToTop()
