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

from trosnoth.gui.app import Application
from trosnoth.gui.framework.framework import CompoundElement
from trosnoth.gui.framework.elements import SizedPicture
from trosnoth.gui.common import Location
from trosnoth.utils import datafile

from trosnoth.gui.framework.menu import MenuDisplay
from trosnoth.gui.menu.menu import MenuManager, Menu, MenuItem

class Interface(CompoundElement):
    backdropLocator = datafile.Locator('startupMenu')

    def __init__(self, app):
        super(Interface, self).__init__(app)
        
        self.menu = None
        self.elements = []
        self.makeElements()

    def makeElements(self):
        backdrop = pygame.image.load(self.backdropLocator \
                                     .getPath('backdrop.png')).convert()
        backdrop = SizedPicture(self.app, backdrop, Location((0,0), 'topleft'),
                                 FullScreenSize())

        menuMan = MenuManager()
        menu1 = Menu(name='File',
                     items=[MenuItem('New'),
                            MenuItem('Open'),
                            MenuItem('Save'),
                            MenuItem('Save As'),
                            MenuItem('Exit', self.app.stop),
                            MenuItem('---'),
                            MenuItem('Cancel', menuMan.cancel)]
                     )
        menu0 = Menu(name='Main',
                     items=[MenuItem('File', lambda: menuMan.showMenu(menu1)),
                            MenuItem('Blah')]
                     )
        menuMan.setDefaultMenu(menu0)
        
        self.menu = MenuDisplay(self.app,
                                location=Location((300, 400), 'bottomleft'),
                                size=(200, 200),
                                font=pygame.font.Font(None, 28),
                                manager=menuMan, titleColour=(255, 255, 0),
                                stdColour=(255, 255, 128),
                                hvrColour=(128, 255, 255),
                                backColour=(0, 64, 192), autosize=True,
                                hidable=True)
        
        self.elements = [backdrop, self.menu]



if __name__ == '__main__':
    screenSize = (920, 690)
    graphicsOptions = 0
    caption = 'Trosnoth Menu Test Program'
    
    app = Application(screenSize, graphicsOptions, caption, Interface)
    app.run()
