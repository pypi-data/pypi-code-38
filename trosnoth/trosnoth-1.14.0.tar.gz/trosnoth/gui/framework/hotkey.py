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

from .framework import Element
from trosnoth.utils.event import Event
from trosnoth.gui import keyboard
import pygame

class Hotkey(Element):
    def __init__(self, app, key, modifiers):
        super(Hotkey, self).__init__(app)
        self.onTriggered = Event()
        self.key = key
        self.mods = modifiers

    def processEvent(self, event):
        if event.type == pygame.KEYDOWN:
            if self.testEquals(event.key, event.mod):
                self.onTriggered.execute()
                return
        return event

    def __str__(self):
        return keyboard.shortcutName(self.key, self.mods)

    def testEquals(self, key, modifiers, mapping=None):
        'Checks if the key press matches this shortcut.'

        # First test: key equality.
        if key != self.key:
            return False

        # Second test: modifier compatibility.
        for kmod, modName in keyboard.KMOD_NAMES:
            if self.mods & kmod:
                if not (modifiers & kmod):
                    return False
            elif modifiers & kmod:
                return False
        # Testing modifiers as done above ignores left/right status.

        return True

class Hotkeys(Element):
    '''
    Traps any keys which occur in the mapping and carries out some action on
    them. Note that this observes only, but does not stop the keypress events
    from passing through.
    '''
    def __init__(self, app, mapping, onActivated=None):
        super(Hotkeys, self).__init__(app)
        self.mapping = mapping
        self.onActivated = Event()
        if onActivated is not None:
            self.onActivated.addListener(onActivated)

    def processEvent(self, event):
        if event.type == pygame.KEYDOWN:
            try:
                action = self.mapping[event.key]
            except KeyError:
                return event

            # Process this hotkey.
            self.onActivated.execute(action)
        return event

    def __repr__(self):
        if isinstance(self.key, int):
            key = self.key
        else:
            # Calculate the physical key.
            for key, value in self.mapping.items():
                if value == self.key:
                    break
            else:
                return '??'

        return keyboard.shortcutName(key, 0)

class MappingHotkey(Element):
    def __init__(self, app, key, mapping=None):
        '''
        key may be a physical pygame key or a string where
            mapping[pygameKey] = key
        '''
        super(MappingHotkey, self).__init__(app)
        self.key = key
        self.onActivated = Event()

        if mapping is None:
            mapping = {}
        self.mapping = mapping

    def processEvent(self, event):
        if event.type == pygame.KEYDOWN:
            if self.mapping.get(event.key, None) == self.key:
                self.onActivated.execute()
                return None
            if event.key == self.key:
                self.onActivated.execute()
                return None
        return event

    def __repr__(self):
        if isinstance(self.key, int):
            key = self.key
        else:
            # Calculate the physical key.
            for key, value in self.mapping.items():
                if value == self.key:
                    break
            else:
                return '??'

        return keyboard.shortcutName(key, 0)
