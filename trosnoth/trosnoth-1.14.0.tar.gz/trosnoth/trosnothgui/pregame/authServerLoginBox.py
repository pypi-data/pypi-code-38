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
from twisted.internet import defer

from trosnoth.gui.framework.dialogbox import DialogBox
from trosnoth.gui.framework.tab import Tab
from trosnoth.gui.framework.tabContainer import TabContainer
from trosnoth.gui.common import Region, Canvas, Location
from trosnoth.gui.framework.elements import TextElement, TextButton
from trosnoth.gui.framework import prompt, framework
from trosnoth.utils.twist import WeakCallLater


class PasswordGUIError(Exception):
    pass


class PasswordGUI(DialogBox):
    def __init__(self, app):
        size = Canvas(512, 384)
        DialogBox.__init__(self, app, size, 'Please authenticate')
        self._deferred = None
        self._host = None

        font = app.screenManager.fonts.defaultTextBoxFont
        btnColour = app.theme.colours.dialogButtonColour
        highlightColour = app.theme.colours.black
        errorTextColour = app.theme.colours.errorColour

        self.tabContainer = TabContainer(app,
                Region(topleft=self.Relative(0, 0),
                size=self.Relative(1, 0.75)), font,
                app.theme.colours.tabContainerColour)
        self.tabContainer.addTab(LoginTab(app))
        self.tabContainer.addTab(CreateAccountTab(app))

        self.errorText = TextElement(app, '', font,
            Location(self.Relative(0.5, 0.8), 'center'), errorTextColour)

        font = app.screenManager.fonts.bigMenuFont
        self.elements = [
            self.tabContainer,
            self.errorText,
            TextButton(app,
                Location(self.Relative(0.3, 0.9), 'center'),
                'Ok', font, btnColour, highlightColour,
                onClick=self.okClicked),
            TextButton(app,
                Location(self.Relative(0.7, 0.9), 'center'),
                'Cancel', font, btnColour, highlightColour,
                onClick=self.cancelClicked),
        ]
        self.cancelled = False

    def setCancelled(self, cancelled):
        self.cancelled = cancelled

    def processEvent(self, event):
        if event.type == pygame.KEYDOWN and event.key in (pygame.K_KP_ENTER,
                pygame.K_RETURN):
            self.okClicked()
            return None
        else:
            return DialogBox.processEvent(self, event)

    def cancelClicked(self, element=None):
        self.close()
        self._deferred.callback(None)

    def okClicked(self, element=None):
        if self.tabContainer.selectedIndex == 1:
            create = True
            # Check that passwords match.
            tab = self.tabContainer.tabs[1]
            if tab.passwordField.value != tab.passwordField2.value:
                self.setErrorText('Passwords do not match!')
                return
        else:
            create = False
            tab = self.tabContainer.tabs[0]

        username = tab.usernameField.value
        password = tab.passwordField.value

        if len(username) == 0:
            self.setErrorText('You must give a username!')
            return
        if len(password) == 0:
            self.setErrorText('Password cannot be blank!')
            return

        self.close()
        self.app.identitySettings.usernames[self._host] = username
        self._deferred.callback((create, username, password))

    def getPassword(self, host, errorMsg=''):
        if self.showing:
            raise PasswordGUIError('PasswordGUI already showing')
        if self.cancelled:
            self.cancelled = False
            result = self._deferred = defer.Deferred()
            WeakCallLater(0.1, result, 'callback', None)
            return result
        self.setCaption(host)
        self.tabContainer.tabs[0].reset(host)
        self.tabContainer.tabs[1].reset()
        self.setErrorText(errorMsg)
        self.show()
        self._host = host
        result = self._deferred = defer.Deferred()
        return result

    def setErrorText(self, text):
        self.errorText.setText(text)


class LoginTab(Tab, framework.TabFriendlyCompoundElement):
    def __init__(self, app):
        Tab.__init__(self, app, 'Sign in')
        framework.TabFriendlyCompoundElement.__init__(self, app)
        font = app.screenManager.fonts.defaultTextBoxFont
        labelColour = app.theme.colours.dialogBoxTextColour
        inputColour = app.theme.colours.grey

        self.usernameField = prompt.InputBox(app,
            Region(topleft=self.Relative(0.1, 0.16),
                bottomright=self.Relative(0.9, 0.32)),
                font=font, colour=inputColour,
                validator=usernameValidator,
                onClick=self.setFocus, onTab=self.tabNext)

        self.passwordField = prompt.PasswordBox(app,
            Region(topleft=self.Relative(0.1, 0.48),
                bottomright=self.Relative(0.9, 0.64)),
                font=font, colour=inputColour,
                onClick=self.setFocus, onTab=self.tabNext)

        self.elements = [
            TextElement(app, 'Username', font,
                Location(self.Relative(0.1, 0.11), 'midleft'),
                labelColour),
            self.usernameField,
            TextElement(app, 'Password', font,
                Location(self.Relative(0.1, 0.43), 'midleft'),
                labelColour),
            self.passwordField,
        ]
        self.tabOrder = [self.usernameField, self.passwordField]

    def reset(self, host):
        self.passwordField.setValue('')
        self.setFocus(self.passwordField)

        if self.usernameField.value == '':
            username = self.app.identitySettings.usernames.get(host)
            if username is None:
                self.setFocus(self.usernameField)
            else:
                self.usernameField.setValue(username)


class CreateAccountTab(Tab, framework.TabFriendlyCompoundElement):
    def __init__(self, app):
        Tab.__init__(self, app, 'New account')
        framework.TabFriendlyCompoundElement.__init__(self, app)
        font = app.screenManager.fonts.defaultTextBoxFont
        labelColour = app.theme.colours.dialogBoxTextColour
        inputColour = app.theme.colours.grey

        self.usernameField = prompt.InputBox(app,
            Region(topleft=self.Relative(0.1, 0.16),
                bottomright=self.Relative(0.9, 0.32)),
                font=font, colour=inputColour,
                validator=usernameValidator,
                onClick=self.setFocus, onTab=self.tabNext)

        self.passwordField = prompt.PasswordBox(app,
            Region(topleft=self.Relative(0.1, 0.48),
                bottomright=self.Relative(0.9, 0.64)),
                font=font, colour=inputColour,
                onClick=self.setFocus, onTab=self.tabNext)

        self.passwordField2 = prompt.PasswordBox(app,
            Region(topleft=self.Relative(0.1, 0.8),
                bottomright=self.Relative(0.9, 0.96)),
                font=font, colour=inputColour,
                onClick=self.setFocus, onTab=self.tabNext)

        self.elements = [
            TextElement(app, 'Username', font,
                Location(self.Relative(0.1, 0.11), 'midleft'),
                labelColour),
            self.usernameField,
            TextElement(app, 'Password', font,
                Location(self.Relative(0.1, 0.43), 'midleft'),
                labelColour),
            self.passwordField,
            TextElement(app, 'Retype password', font,
                Location(self.Relative(0.1, 0.75), 'midleft'),
                labelColour),
            self.passwordField2,
        ]
        self.tabOrder = [self.usernameField, self.passwordField,
                self.passwordField2]

    def reset(self):
        self.passwordField.setValue('')
        self.passwordField2.setValue('')
        self.setFocus(self.usernameField)


USERNAME_CHARS = set(
        'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_0123456789-')


def usernameValidator(char):
    return char in USERNAME_CHARS
