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

from trosnoth.gui.app import Application
from trosnoth.gui.framework import framework, statList, elements, hotkey
from trosnoth.gui.common import Location
from trosnoth.gui.fonts.font import Font
import pygame
from random import randint, shuffle

class Interface(framework.CompoundElement):
    def __init__(self, app):
        super(Interface, self).__init__(app)
        backdrop = pygame.Surface(app.screenManager.scaledSize)
        backdrop.fill((128,0,128))
        self.val = 4
        self.l = ['hello', self.val]
        getColour = lambda item: ((255,0,0), (0,255,255))[str(item).startswith('h')]
        font = Font("KLEPTOCR.TTF", 30)
        self.s = statList.StatList(app,
                              Location((550,400), 'bottomright'),
                              self.l,
                              font,
                              colourFunction = getColour,
                                   align='right')
    
        self.s.setVisible()

        f = lambda: self.s.setVisible(not self.s.getVisibility())

        h = hotkey.Hotkey(app, pygame.K_s, 0)
        h.onTriggered.addListener(f)
        self.elements = [elements.PictureElement(app, backdrop),
                         self.s,
                         h]
    def tick(self, deltaT):
        super(Interface, self).tick(deltaT)
        if randint(0,100) == 1:
            shuffle(self.l)
        if randint(0,30000) == 42:
            self.l.append("What's going on here?!")
        if randint(0,1000) == 100:
            i = self.l.index(self.val)
            self.val = randint(0, 1000)
            self.l[i] = self.val

size = (600,450)

if __name__ == '__main__':
    a = Application(size, 0, "Testing", Interface)
    a.run()
