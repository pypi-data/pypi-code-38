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

'''prompt.py - contains the definition for a prompt that could be used for
any type of input.'''

import logging

import pygame
import trosnoth.gui.framework.framework as framework
from trosnoth.utils.event import Event
from trosnoth.gui import keyboard

log = logging.getLogger(__name__)

def intValidator(char):
    return char >= '0' and char <= '9'

class InputBox(framework.Element):
    pxFromLeft = 2
    pxFromRight = 5
    pxToSkipWhenCursorGoesToTheRight = 90
    cursorFlashTime = 0.6
    def __init__(self, app, area, initValue='', validator=None, font=None,
            colour=(255,255,255), maxLength=None, onClick=None, onEnter=None,
            onTab=None, onEsc=None, onEdit=None):
        super(InputBox, self).__init__(app)

        self.area = area
        self.onClick = Event()
        if onClick is not None:
            self.onClick.addListener(onClick)
        self.onEnter = Event()
        if onEnter is not None:
            self.onEnter.addListener(onEnter)
        self.onTab = Event()
        if onTab is not None:
            self.onTab.addListener(onTab)
        self.onEsc = Event()
        if onEsc is not None:
            self.onEsc.addListener(onEsc)
        self.onEdit = Event()
        if onEdit is not None:
            self.onEdit.addListener(onEdit)

        if validator:
            self.validator = validator
        else:
            self.validator = lambda x: True


        if font:
            self.font = font
        else:
            self.font = self.app.screenManager.fonts.defaultTextBoxFont

        self.value = initValue
        self.maxLength = maxLength
        self.fontColour = (0,0,0)
        self.backColour = colour
        self.cursorColour = (255, 0, 0)
        self._cursorVisible = True
        self._timeToFlash = self.cursorFlashTime

        # Calculate the white part of the input area
        self.cursorIndex = len(self.value)
        self.offset = 0

    def clear(self):
        self.setValue('')

    def setValue(self, value):
        self.value = value
        self.offset = 0
        self.cursorIndex = len(self.value)

    def getValue(self):
        return self.value

    def setFont(self, font):
        self.font = font

    def setValidator(self, validator):
        self.validator = validator

    def setMaxLength(self, length):
        self.maxLength = length

    def _getSize(self):
        return self._getRect().size

    def _getCursorImage(self):
        s = pygame.Surface((2, min(int(self.font.getHeight(self.app)),
                self._getSize()[1] * 0.8)))
        s.fill(self.cursorColour)
        return s

    def _getRect(self):
        return self.area.getRect(self.app)

    def _getPt(self):
        return self._getRect().topleft

    def setFontColour(self, fontColour):
        self.fontColour = fontColour

    def setBackColour(self, backColour):
        self.backColour = backColour

    def setCursorColour(self, cursorColour):
        self.cursorColour = cursorColour

    def gotFocus(self):
        self._cursorVisible = True
        self._timeToFlash = self.cursorFlashTime

    def _renderText(self):
        '''
        Provided so that PasswordBox can override it.
        '''
        return self.font.render(self.app, self.value, True, self.fontColour,
                self.backColour)

    def draw(self, surface):
        rect = self._getRect()
        size = rect.size
        pos = rect.topleft
        # Fill the input area with the specified colour
        surface.fill(self.backColour, rect)

        # Put what's currently inputted into the input area
        inputText = self._renderText()

        # Adjust offset
        cursorPos = self._getCursorPos()
        if cursorPos < self.offset:
            self.offset = max(0, self.offset -
                    self.pxToSkipWhenCursorGoesToTheRight)
        else:
            minOffset = cursorPos - size[0] + self.pxFromRight + self.pxFromLeft
            if self.offset < minOffset:
                self.offset = minOffset

        text_rect = inputText.get_rect()
        text_rect.centery = rect.centery
        diff = (text_rect.height - rect.height) / 2
        # Find the currently-displaying text (based on where the cursor is):
        area = pygame.Rect(self.offset, diff, size[0] - self.pxFromRight,
                rect.height)

        # Put the text on the screen
        surface.blit(inputText, (pos[0] + self.pxFromLeft, rect.top), area)

        # Add the cursor where it is.
        if self.hasFocus and self._cursorVisible:
            cs = self._getCursorImage()
            cursor_rect = cs.get_rect()
            cursor_rect.centery = rect.centery
            surface.blit(cs, (pos[0] + self._getCursorPos() - self.offset,
                    cursor_rect.top))

    def _getCursorPos(self):
        return self._getFontSize(self.value[:self.cursorIndex])[0] + 1

    def _getFontSize(self, text):
        '''
        Provided so that PasswordBox can override it.
        '''
        return self.font.size(self.app, text)

    # Get the index of the position clicked
    def __getCursorIndex(self, clickOffset):
        totalOffset = clickOffset + self.offset + self.pxFromLeft
        i = 1
        fontOffset = 0
        last = 0
        while fontOffset < totalOffset and i <= len(self.value):
            last = fontOffset
            fontOffset = self._getFontSize(self.value[:i])[0]
            i += 1
        if (fontOffset - totalOffset) <= (totalOffset - last):
            return i - 1
        else:
            return i - 2
        return i

    def processEvent(self, event):
        '''Processes the key press. If we use the event, return nothing.
        If we do not use it,
        return the event so something else can use it.'''

        if self.hasFocus and event.type == pygame.KEYDOWN:
            self._cursorVisible = True
            self._timeToFlash = self.cursorFlashTime
            if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                self.onEnter.execute(self)
                return None
            if event.key == pygame.K_ESCAPE:
                self.onEsc.execute(self)
                return None
            if event.key == pygame.K_TAB:
                self.onTab.execute(self)
                return None

            # Delete the letter behind the cursor
            if event.key == pygame.K_BACKSPACE:
                # Make sure there's something in the string behind the cursor
                # first, don't want to kill what's not there
                if self.cursorIndex > 0:
                    self.value = (self.value[:self.cursorIndex - 1] +
                            self.value[self.cursorIndex:])
                    self.cursorIndex -= 1
                    self.onEdit.execute(self)

            elif event.key == pygame.K_DELETE:
                # Make sure there's something in the string in front of the
                # cursor first, don't want to kill what's not there
                if self.cursorIndex < len(self.value):
                    self.value = (self.value[:self.cursorIndex] +
                            self.value[self.cursorIndex + 1:])
                    self.onEdit.execute(self)

            elif event.key == pygame.K_LEFT:
                if self.cursorIndex > 0:
                    self.cursorIndex -= 1

            elif event.key == pygame.K_RIGHT:
                if self.cursorIndex < len(self.value):
                    self.cursorIndex += 1

            elif event.key == pygame.K_END:
                self.cursorIndex = len(self.value)

            elif event.key == pygame.K_HOME:
                self.cursorIndex = 0
                self.offset = 0

            # Add the character to our string
            elif event.unicode == '':
                return event
            else:
                # Validate the input.
                if not self.validator(event.unicode):
                    return event

                # Check the maxLength
                if self.maxLength is not None:
                    if len(self.value) >= self.maxLength:
                        return event

                # Add the typed letter to the string
                self.value = (self.value[:self.cursorIndex] + event.unicode +
                        self.value[self.cursorIndex:])
                self.cursorIndex += len(event.unicode)
                self.onEdit.execute(self)

        else:
            rect = self._getRect()

            if (event.type == pygame.MOUSEBUTTONDOWN and
                    rect.collidepoint(event.pos) and event.button == 1):

                self.onClick.execute(self)
                xOffset = event.pos[0] - rect.left
                self.cursorIndex = self.__getCursorIndex(xOffset)
                self._timeToFlash = self.cursorFlashTime
                self._cursorVisible = True
            else:
                # It's not a keydown event. Pass it on.
                return event

    def tick(self, deltaT):
        self._timeToFlash -= deltaT
        while self._timeToFlash < 0:
            self._timeToFlash += self.cursorFlashTime
            self._cursorVisible = not self._cursorVisible

class KeycodeBox(framework.Element):
    pxFromLeft = 2
    pxFromRight = 5
    def __init__(self, app, area, initValue=None, font=None,
            colour=(255,255,255), focusColour=(192, 192, 255), acceptMouse=False):
        super(KeycodeBox, self).__init__(app)

        self.area = area
        self.onClick = Event()
        self.onChange = Event()

        if font:
            self.font = font
        else:
            self.font = self.app.screenManager.fonts.defaultTextBoxFont

        self.value = initValue
        self.fontColour = (0,0,0)
        self.realBackColour = self._backColour = colour
        self.focusColour = focusColour
        self.acceptMouse = acceptMouse

    def _getBackColour(self):
        return self._backColour
    def _setBackColour(self, colour):
        if self.realBackColour == self._backColour:
            self.realBackColour = colour
        self._backColour = colour
    backColour = property(_getBackColour, _setBackColour)

    def draw(self, surface):
        rect = self._getRect()
        size = rect.size
        pos = rect.topleft

        # Fill the input area with the specified colour
        surface.fill(self.realBackColour, rect)

        # Put what's currently inputted into the input area
        if self.value is None:
            name = ''
        else:
            name = keyboard.shortcutName(self.value)

        inputText = self.font.render(self.app, name, True, self.fontColour,
                        self.realBackColour)

        text_rect = inputText.get_rect()

        diff = (text_rect.height - rect.height) / 2
        area = pygame.Rect(0, diff, size[0] - self.pxFromRight, rect.height)

        # Put the text on the screen
        text_rect.centery = rect.centery
        surface.blit(inputText, (pos[0]+self.pxFromLeft, rect.top), area)

    def processEvent(self, event):
        '''Processes the key press. If we use the event, return nothing.
        If we do not use it,
        return the event so something else can use it.'''

        if self.hasFocus:
            # Catch a single keystroke.
            if event.type == pygame.KEYDOWN:
                self.caughtKey(event.key)
            elif self.acceptMouse and event.type == pygame.MOUSEBUTTONDOWN:
                if event.button != 1:
                    self.caughtKey(keyboard.mouseButton(event.button))
        else:
            rect = self._getRect()

            if (event.type == pygame.MOUSEBUTTONDOWN and
                    rect.collidepoint(event.pos)):
                self.onClick.execute(self)
            else:
                # It's not a keydown event. Pass it on.
                return event

    def caughtKey(self, key):
        self.value = key
        self.hasFocus = False
        self.lostFocus()
        self.onChange.execute(self)

    def _getSize(self):
        return self._getRect().size

    def _getRect(self):
        return self.area.getRect(self.app)

    def _getPt(self):
        return self._getRect().topleft

    def gotFocus(self):
        self.realBackColour = self.focusColour

    def lostFocus(self):
        self.realBackColour = self._backColour

class PasswordBox(InputBox):
    def _renderText(self):
        val = '*' * len(self.value)
        return self.font.render(self.app, val, True, self.fontColour,
                self.backColour)

    def _getFontSize(self, text):
        text = '*' * len(text)
        return self.font.size(self.app, text)

