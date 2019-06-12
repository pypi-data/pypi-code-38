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
from trosnoth.gui.framework import framework, elements, hotkey, tabContainer, tab, statList, prompt
from trosnoth.gui.fonts.font import Font
from trosnoth.gui.common import *
import pygame

class Interface(framework.CompoundElement):
    def __init__(self, app):
        super(Interface, self).__init__(app)
        bg = pygame.surface.Surface((1024,768))
        bg.fill((255,255,0))
                                                                     
        font = Font("KLEPTOCR.TTF", 30)
        tc = tabContainer.TabContainer(app, ScaledArea(10,10, 1004, 748), font, (0,128,0))
        background = SizedImage('Awesome Leaders.jpg', tabContainer.TabSize(tc))
        for x in range(0,1):
            t1 = tab.Tab(app, "Hellooooooooo")
            t1.elements = [elements.PictureElement(app, background, Location(AttachedPoint((0,0),tc._getTabRect,'topleft'),'topleft'))]
            t2 = NewTab(app, tc)
            t3 = EpilepticTab(app, tc)
            tc.addTab(t1)
            tc.addTab(t2)
            tc.addTab(t3)
        #tc._setTabHeaderDimensions(3,36,24,200)
        self.elements = [elements.Backdrop(app, bg), tc]

class NewTab(tab.Tab):
    def __init__(self, app, tabContainer):
        super(NewTab, self).__init__(app, "New Tab")
        h = prompt.InputBox(app, Area(AttachedPoint((10,10), tabContainer._getTabRect), ScaledSize(400,100)), "Press Enter", font = app.screenManager.fonts.bigMenuFont)
        h.onEnter.addListener(lambda sender:self.app.screenManager.setScreenProperties((1024,768), 0, "Testing"))
        h.onClick.addListener(self.setFocus)
        self.elements = [h]

import pygame
from random import randint, shuffle


class EpilepticTab(tab.Tab):
    def __init__(self, app, tabContainer):
        super(EpilepticTab, self).__init__(app, str(randint(0,1000)))
        self.val = 4
        self.l = ['hello', self.val]
        getColour = lambda item: ((255,0,0), (0,255,255))['4' in str(item)]
        font = Font("KLEPTOCR.TTF", 50)
        self.s = statList.StatList(app,
                              Location(AttachedPoint((10,100), tabContainer._getTabRect)),
                              self.l,
                              font,
                              colourFunction = getColour)
        self.s.setVisible()
        addTabFunction = lambda sender: tabContainer.addTab(EpilepticTab(app, tabContainer))
        closeTabFunction = lambda sender: tabContainer.removeTab(self)
        button = elements.TextButton(app, Location(AttachedPoint((200,50), tabContainer._getTabRect)), "Click for new Tab", font, (0,128,0), (0,255,0))
        button.onClick.addListener(addTabFunction)
        otherButton = elements.TextButton(app, Location(AttachedPoint((200,90), tabContainer._getTabRect)), "Close This Tab", font, (128,0,0), (255,0,0))
        otherButton.onClick.addListener(closeTabFunction)

        f = lambda: self.s.setVisible(not self.s.getVisibility())

        h = hotkey.Hotkey(app, pygame.K_s, 0)
        h.onTriggered.addListener(f)
        # TODO: add a backdrop
        self.elements += [self.s, button, otherButton, h]
    def tick(self, deltaT):
        super(EpilepticTab, self).tick(deltaT)
        if randint(0,100) == 1:
            shuffle(self.l)
        if randint(0,30000) == 42:
            self.l.append("What's going on here?! %d" % randint(0,100000))
        if randint(0,1000) == 100:
            i = self.l.index(self.val)
            self.val = randint(0, 1000)
            self.l[i] = self.val
size = (600,450)
if __name__ == '__main__':
    a = Application(size, 0, "Testing", Interface)
    a.run()
