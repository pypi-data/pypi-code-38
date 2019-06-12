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

'''
Demo of the console component.
'''

from trosnoth.gui.app import Application
from trosnoth.gui.framework import (framework, elements,
        console)
from trosnoth.gui.fonts.font import Font
from trosnoth.gui.common import Area
import pygame

class Interface(framework.CompoundElement):
    def __init__(self, app):
        super(Interface, self).__init__(app)
        backdrop = pygame.Surface(app.screenManager.scaledSize)
        backdrop.fill((128,0,128))

        con = console.TrosnothInteractiveConsole(app, Font(None, 18),
                Area((0, 200), (500, 200)))
        con.interact().addCallback(self.done)
                        
        self.elements = [elements.PictureElement(app, backdrop), con]
        self.setFocus(con)

    def done(self, component):
        print('Done!!!')
        self.app.stop()


size = (600,450)

if __name__ == '__main__':
    a = Application(size, 0, "Testing", Interface)
    a.run_twisted()
