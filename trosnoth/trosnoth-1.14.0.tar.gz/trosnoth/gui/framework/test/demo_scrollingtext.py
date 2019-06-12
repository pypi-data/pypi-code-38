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
from trosnoth.gui.framework import framework, elements, scrollingText
from trosnoth.gui.fonts.font import Font
import pygame
from random import randint, shuffle

class Interface(framework.CompoundElement):
    def __init__(self, app):
        super(Interface, self).__init__(app)
        backdrop = pygame.Surface(app.screenManager.scaledSize)
        backdrop.fill((128,0,128))
        f = open('credits.txt', 'r')
        credPos = (50,50)
        size = (500, 350)
        fonts = {'body': self.app.fonts.creditsFont,
         'h1': self.app.fonts.creditsH1,
         'h2': self.app.fonts.creditsH2}
        cred = scrollingText.ScrollingText(self.app,
                        credPos, size, f.read(), (0,0,0),
                        fonts, bgColour = (255,255,255), autoScroll = False,
                        speed = 100, align = 'middle', border=True,
                        loop = True)
        def doIt():
            print("Done Scrolling")
        cred.onFinishedScrolling.addListener(lambda: doIt())
        
        self.elements = [elements.PictureElement(app, backdrop), cred]

size = (600,450)

if __name__ == '__main__':
    a = Application(size, 0, "Testing", Interface)
    a.run()
