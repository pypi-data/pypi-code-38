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
from trosnoth.gui.framework import slider, elements
from trosnoth.gui.fonts.font import Font
from trosnoth.gui.common import *
from trosnoth.gui.framework import framework
import pygame

class Interface(framework.CompoundElement):
    def __init__(self, app):
        super(Interface, self).__init__(app)
        backdrop = pygame.Surface(app.screenManager.scaledSize)
        backdrop.fill((128,0,128))
        s1 = slider.Slider(app, ScaledArea(100,100,400,60))
        #s1.setRange(50,150)
        t1 = elements.TextElement(app, "100", Font(None, 60), ScaledLocation(100, 200))
        t2 = elements.TextElement(app, "100", Font(None, 60), ScaledLocation(550, 100))
        onSlide = lambda x: t1.setText("%.1f" % x)
        onChange = lambda x: t2.setText("%.1f" % x)
        s1.onSlide.addListener(onSlide)
        s1.onValueChanged.addListener(onChange)
        self.elements = [elements.PictureElement(app, backdrop), s1, t1, t2]

size = (600,450)

if __name__ == '__main__':
    a = Application(size, 0, "Testing", Interface)
    a.run()
