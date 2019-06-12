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

from trosnoth.gui.framework import framework, elements
from trosnoth.gui.common import Location, translateEvent
from trosnoth.gui import keyboard

class MenuDisplay(framework.CompoundElement):
    '''
    Represents the UI side of a menu. To use this kind of element, you should
    first create a trosnoth.ui.menu.menu.MenuManager object with appropriate
    menus.

    Note that a menu manager will show the hotkeys of actions, but will not
    actually cause the actions to be executed. For this, you should construct
    a gui.hotkey.Hotkeys() object.

    For example:

    menuMan = MenuManager()
    menu1 = Menu(name='file',
                 items=[MenuItem('action1', ...),
                        MenuItem('action2', ...),
                        MenuItem('cancel', menuMan.cancel)])
    menu2 = Menu(name='main',
                 items=[MenuItem('file', lambda: menuMan.show(menu1)),
                        ...])
    menuMan.setDefaultMenu(menu2)

    menuDisp = MenuDisplay(..., menuMan, ...)

    @param  location    should always be an instance of
                        trosnoth.ui.common.Location, but the current
                        implementation accounts for the possibility of it being
                        a point for the top-left.
    '''
    ACCELERATION = 500  # pix/s/s

    def __init__(self, app, location, size, font, manager, titleColour,
                 stdColour, hvrColour, disabledColour=None, backColour=None,
                 autosize=False, hidable=False, keymapping=None):
        super(MenuDisplay, self).__init__(app)

        self.screenSize = app.screenManager.size
        self.location = location
        self.size = size
        self.rect = pygame.Rect(0, 0, 0, 0)
        self.font = font
        self.manager = manager

        self.titleColour = titleColour
        self.stdColour = stdColour
        self.hvrColour = hvrColour
        self.disabledColour = disabledColour or stdColour

        self.autosize = autosize
        self.hidable = hidable
        self.hidden = False
        self.image = None

        self.keymapping = keymapping

        if backColour is None:
            self.backColour = (0, 0, 1)
            self.transparent = True
        else:
            self.backColour = backColour
            self.transparent = False

        if hasattr(size, 'getSize'):
            size = size.getSize(app)
        if not autosize:
            self.image = pygame.Surface(size)
            if self.transparent:
                self.image.set_colorkey(self.backColour)
        self.rect.size = size
        self.velocity = 0

        # When the menu changes we need to be told.
        manager.onShowMenu.addListener(self.refresh)
        self.refresh(manager.menu)

    def _refreshRect(self):
        if hasattr(self.location, 'apply'):
            self.location.apply(self.app, self.rect)
        else:
            self.rect.topleft = self.location

    def drawChildren(self):
        self.image.fill(self.backColour)
        super(MenuDisplay, self).draw(self.image)

    def resizeIfNeeded(self):
        if self.app.screenManager.size == self.screenSize:
            return
        self.screenSize = self.app.screenManager.size

        size = self.size
        if hasattr(size, 'getSize'):
            size = size.getSize(self.app)
        if not self.autosize:
            self.image = pygame.Surface(size)
            if self.transparent:
                self.image.set_colorkey(self.backColour)
        self.rect.size = size
        self.refresh(self.manager.menu)

    def tick(self, deltaT):
        self.resizeIfNeeded()
        diff = self.image.get_rect().height - self.rect.height
        if diff != 0:
            sgn = diff/abs(diff)
            diff = abs(diff)
            self.velocity = sgn * min(abs(self.velocity) +
                                         deltaT*self.ACCELERATION,
                                      (2.0 * self.ACCELERATION * diff)**0.5)
            self.rect.height += sgn * min(abs(self.velocity)*deltaT+1, diff)

        self._refreshRect()
        super(MenuDisplay, self).tick(deltaT)

    def draw(self, screen):
        self.drawChildren()
        if not self.transparent:
            screen.fill(self.backColour, self.rect)
        if self.rect.height < self.image.get_rect().height:
            screen.blit(self.image,
                        self.rect,
                        pygame.Rect((0, 0), self.rect.size))
        else:
            screen.blit(self.image, self.rect)

    def hide(self, btn=None):
        if self.hidden:
            self.hidden = False
            if self.autosize:
                itemSpacing = self.font.getLineSize(self.app)
                size = (self.rect.width,
                        itemSpacing * (1 + len(self.manager.menu.items)))
            else:
                size = self.size
            self.image = pygame.Surface(size)
        else:
            self.hidden = True
            itemSpacing = self.font.getLineSize(self.app)
            self.image = pygame.Surface((self.rect.width, itemSpacing))

        if self.transparent:
            self.image.set_colorkey(self.backColour)
        self.refresh(self.manager.menu)

    def refresh(self, menu=None):
        '''Updates the display of this menu to reflect the currently-showing
        menu of the manager.'''

        if menu is None:
            menu = self.manager.menu
        if menu is None:
            menuItemCount = 0
        else:
            menuItemCount = len(menu.items)

        if self.hidable and self.hidden:
            # Display the menu title only.
            itemSpacing = self.font.getLineSize(self.app)
        elif self.autosize:
            # Make a canvas for the new menu.
            itemSpacing = self.font.getLineSize(self.app)
            size = (self.rect.width, itemSpacing * (1 + menuItemCount))
            self.image = pygame.Surface(size)
            if self.transparent:
                self.image.set_colorkey(self.backColour)

        rect = self.image.get_rect()

        if not (self.autosize or (self.hidable and self.hidden)):
            # Calculate the item spacing.
            itemSpacing = rect.height / (1 + menuItemCount)

        self.elements = []

        if menu is None:
            return

        x = rect.width // 2

        # Menu title.
        if self.hidable:
            stdImage = pygame.Surface((self.rect.width, itemSpacing))
            stdImage.fill(self.backColour)
            img = self.font.render(self.app, menu.name, True, self.titleColour)
            r = img.get_rect()
            r.center = (self.rect.width // 2, itemSpacing // 2)
            stdImage.blit(img, r)

            hvrImage = pygame.Surface((self.rect.width, itemSpacing))
            hvrImage.fill(self.backColour)
            img = self.font.render(self.app, menu.name, True, self.hvrColour)
            hvrImage.blit(img, r)

            btn = elements.HoverButton(app=self.app,
                                     pos=Location((x, itemSpacing/2), 'center'),
                                     stdImage=stdImage,
                                     hvrImage=hvrImage)
            btn.onClick.addListener(self.hide)
            self.elements.append(btn)
            if self.hidden:
                return
        else:
            self.elements.append(
                elements.TextElement(app=self.app, text=menu.name,
                                     font=self.font,
                                     pos=Location((x, itemSpacing / 2),
                                                  'center'),
                                     colour=self.titleColour))

        # Menu items.
        y = itemSpacing * 3 / 2
        for item in menu.items:
            self.addMenuItem(item, x, y, rect.width, itemSpacing)
            y += itemSpacing

    def processEvent(self, event):
        event0 = event
        if event.type in (pygame.MOUSEMOTION, pygame.MOUSEBUTTONDOWN,
                pygame.MOUSEBUTTONUP):
            event = translateEvent(event, self.rect.topleft)
        event1 = super(MenuDisplay, self).processEvent(event)

        # This bit is just so that our event translations are restricted to
        # this menu.

        if event1 is event:
            return event0
        return event1

    def addMenuItem(self, item, x, y, width, itemHeight):
        stdImage = pygame.Surface((self.rect.width, itemHeight))
        hvrImage = pygame.Surface((self.rect.width, itemHeight))
        stdImage.set_colorkey((0,0,0))
        hvrImage.set_colorkey((0,0,0))

        if item.enabled:
            stdColour = self.stdColour
            hvrColour = self.hvrColour
        else:
            stdColour = hvrColour = self.disabledColour

        if item.name == '---':
            # Separator.
            pygame.draw.line(stdImage, stdColour, (0, itemHeight//2),
                             (self.rect.width, itemHeight//2))
            pygame.draw.line(hvrImage, hvrColour, (0, itemHeight//2),
                             (self.rect.width, itemHeight//2))
        else:
            # Put caption on standard canvas.
            img = self.font.render(self.app, item.name, True, stdColour)
            r = img.get_rect()
            r.midleft = (2, itemHeight // 2)
            stdImage.blit(img, r)

            # Put caption on hover canvas.
            img = self.font.render(self.app, item.name, True, hvrColour)
            hvrImage.blit(img, r)

        if item.action is not None and self.keymapping is not None:
            try:
                hkStr = keyboard.shortcutName(self.keymapping.getkey(
                        item.action))
            except KeyError:
                pass
            else:

                # Put hotkey on standard canvas.
                img = self.font.render(self.app, hkStr, True, stdColour)
                r = img.get_rect()
                r.midright = (width-2, itemHeight // 2)
                stdImage.blit(img, r)

                # Put hotkey on hover canvas.
                img = self.font.render(self.app, hkStr, True, hvrColour)
                hvrImage.blit(img, r)

        btn = elements.HoverButton(self.app, Location((x, y), 'center'),
                                   stdImage, hvrImage)
        if item.enabled:
            btn.onClick.addListener(lambda btn: item.execute())
        self.elements.append(btn)
