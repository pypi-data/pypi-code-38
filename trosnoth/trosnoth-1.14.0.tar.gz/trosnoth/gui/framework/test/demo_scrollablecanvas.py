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
from trosnoth.gui.framework import framework, elements, scrollableCanvas
from trosnoth.gui.common import *
from trosnoth.gui.fonts.font import Font
import pygame

class Interface(framework.CompoundElement):
    def __init__(self, app):
        super(Interface, self).__init__(app)
        backdrop = pygame.image.load('Awesome Leaders.jpg').convert()
        x, y = backdrop.get_size()
        size = Size(x, y)
        sc1 = scrollableCanvas.ScrollableCanvas(app, ScaledLocation(20,20), size, ScaledSize(200,200))
        sc2 = scrollableCanvas.ScrollableCanvas(app, ScaledLocation(230,20), size, ScaledSize(200,y+scrollableCanvas.ScrollBar.defaultWidth))
        sc3 = scrollableCanvas.ScrollableCanvas(app, ScaledLocation(440,20), size, ScaledSize(x,y))
        sc4 = scrollableCanvas.ScrollableCanvas(app, ScaledLocation(20,530), size, ScaledSize(x+scrollableCanvas.ScrollBar.defaultWidth, 200))
        #sc5 = scrollableCanvas.ScrollableCanvas(app, ScaledLocation(20,530), size, ScaledSize(x+scrollableCanvas.ScrollBar.defaultWidth, y))
        self.elements = [sc1, sc2, sc3, sc4]#, sc5]
        font = Font("KLEPTOCR.TTF", 30)
        onclick = lambda sender: self.app.screenManager.setScreenProperties((1680, 1050), 0, "Testing")
        for sc in self.elements:
            sc.elements = [elements.PictureElement(app, backdrop, Location(scrollableCanvas.ScrollableCanvasAttachedPoint(sc, (0,0)), 'topleft')),
                           elements.TextButton(app, Location(scrollableCanvas.ScrollableCanvasAttachedPoint(sc, (20,20))), "Hello", font, (0,128,0), (0,0,128), onClick = onclick)]

    def draw(self, screen):
        screen.fill((0,0,0))
        super(Interface, self).draw(screen)

size = (1200,768)

if __name__ == "__main__":
    a = Application(size, 0, "Testing", Interface)
    a.run()
