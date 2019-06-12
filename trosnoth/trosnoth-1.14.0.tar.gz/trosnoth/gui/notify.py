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

from trosnoth.utils.event import Event
from trosnoth.gui import browser
from trosnoth.gui.framework.framework import CompoundElement
from trosnoth.gui.framework.elements import (SizedPicture, TextElement,
        TextButton)

class NotificationBar(CompoundElement):
    '''
    Displays a bar notifying the user of some information.
    '''

    def __init__(self, app, message, font, area, buttonPos, textPos, url=None,
            textColour=(0,0,0), closeColour=(0,0,0), hoverColour=(255,255,255),
            backColour=(255,150,150), textAnchor='center'):
        super(NotificationBar, self).__init__(app)
        self.area = area
        self.url = url
        self.backColour = backColour

        self.rect = pygame.Rect(0,0,0,0)
        self.background = pygame.Surface(self.rect.size)
        self.visible = False

        self.onClick = Event()
        self.onClose = Event()

        self.elements = [
            # A blank rectangle.
            SizedPicture(app, self.background, area, area.size),

            # The text.
            TextElement(app, message, font, textPos, textColour,
                anchor=textAnchor
            ),

            # A button to dismiss it.
            TextButton(app,
                pos=buttonPos,
                text='[close]',
                font=font,
                stdColour=closeColour,
                hvrColour=hoverColour,
                onClick=self._doHide
            )
        ]

    #####################
    # Main interface
    #####################

    def show(self, message=None):
        if message is not None:
            self.elements[1].setText(message)
        self._showMessage()

    def hide(self):
        self._hideMessage()

    #####################
    # Element behaviour
    #####################

    def processEvent(self, event):
        '''Processes the specified event and returns the event if it should
        be passed on, or None if it has been caught.'''
        if not self.visible:
            return event

        event = CompoundElement.processEvent(self, event)
        if (event is not None and event.type == pygame.MOUSEBUTTONDOWN and
                self.rect.collidepoint(event.pos)):
            # User has clicked somewhere on the component.
            self.onClick()
            if self.url is not None:
                browser.openPage(self.app, self.url)
            return

        return event

    def draw(self, screen):
        if not self.visible:
            return
        CompoundElement.draw(self, screen)

    def _showMessage(self):
        self.visible = True
        self.area.apply(self.app, self.rect)

        # Show the components.
        self.background = pygame.Surface(self.rect.size)
        self.background.fill(self.backColour)
        self.elements[0].setImage(self.background)

    def _hideMessage(self):
        self.visible = False
        self.onClose()

    def _doHide(self, component):
        self.hide()
