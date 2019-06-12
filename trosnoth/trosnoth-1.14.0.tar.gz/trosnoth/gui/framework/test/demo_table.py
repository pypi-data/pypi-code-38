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
from trosnoth.gui.framework import table
from trosnoth.gui.fonts.font import Font
from trosnoth.gui.common import *
from trosnoth.gui.framework import framework
import pygame

class Interface(framework.CompoundElement):
    def __init__(self, app):
        super(Interface, self).__init__(app)
        backdrop = pygame.Surface(app.screenManager.scaledSize)
        backdrop.fill((128,0,128))
        t1 = table.Table(app, Location(FullScreenAttachedPoint((-10,-10), 'bottomright'), 'bottomright'),
                         rows = 4, columns = 2)

        t1[0][0].setText("Hello")
        t1[0][0].style.font = Font('FreeSans.ttf', 16)
        t1[1][1].setText("There")
        t1[1][1].style.foreColour = (0,232, 0)
        t1[1][1].style.textAlign = 'center'
        t1[1][1].style.hasShadow = True
        t1[1][1].style.shadowColour = (0,0,255)
        t1[1][2].style.backColour = (232,0,0)
        t1[1][2].style.font = Font('FreeSans.ttf', 50)
        t1[1][2].setText("TOO BIG!!")
        t1[1][2].style.foreColour = (255,255,255)
        t1.getRow(1).setHeight(100)
        t1.getRow(3).setHeight(ScaledScalar(60))
        t1.setBorderWidth(7)
        self.elements = [t1]

size = (600,450)

if __name__ == '__main__':
    a = Application(size, 0, "Testing", Interface)
    a.run()
