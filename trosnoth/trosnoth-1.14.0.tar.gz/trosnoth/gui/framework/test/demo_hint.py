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
from trosnoth.gui.framework import framework, prompt, hint, elements
from trosnoth.gui.fonts.font import Font
from trosnoth.gui.common import Area
import pygame
from random import randint, shuffle

class Interface(framework.CompoundElement):
    def __init__(self, app):
        super(Interface, self).__init__(app)
        backdrop = pygame.Surface(app.screenManager.scaledSize)
        backdrop.fill((128,0,128))
        i1 = prompt.InputBox(self.app, Area((40,40),(300,50)), 'Mouse Over', font = Font("KLEPTOCR.TTF", 36))
        i1.onClick.addListener(self.setFocus)
        i2 = prompt.InputBox(self.app, Area((340,140),(200,50)), 'Mouse Over', font = Font("KLEPTOCR.TTF", 36))
        i2.onClick.addListener(self.setFocus)
        h1 = hint.Hint(self.app, "You absolutely\nRULE!", i1, Font("KLEPTOCR.TTF", 24))
        h2 = hint.Hint(self.app, "Like, amazingly so!! TROSNOTH!@!!@!", i2, Font("KLEPTOCR.TTF", 24))
        h3 = hint.Hint(self.app, "A secret!\nWell done, you have found a magical land of wonder and amazement!! \nYou win absolutely nothing, but at least you have a good story to tell now.", pygame.Rect(500, 400, 100, 50), Font("KLEPTOCR.TTF", 24))
        self.elements = [elements.PictureElement(app, backdrop),
                         i1, h1,
                         i2, h2, h3
                         ]

size = (600,450)

if __name__ == '__main__':
    a = Application(size, 0, "Testing", Interface)
    a.run()
