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

from trosnoth.const import (
    ACTION_DOWN, ACTION_RIGHT, ACTION_HOOK, ACTION_JUMP, ACTION_LEFT,
    ACTION_MAIN_MENU, ACTION_MORE_MENU, ACTION_UPGRADE_MENU, ACTION_EMOTE,
    ACTION_USE_UPGRADE, ACTION_EDIT_PLAYER_INFO, ACTION_READY, ACTION_CHAT,
    ACTION_FOLLOW, ACTION_CLEAR_UPGRADE, ACTION_LEADERBOARD_TOGGLE,
    ACTION_HUD_TOGGLE, ACTION_TERMINAL_TOGGLE, ACTION_SHOW_TRAJECTORY,
)
from trosnoth.model.upgrades import allUpgrades
from trosnoth.trosnothgui.common import button
from trosnoth.gui.framework import prompt
from trosnoth.gui.framework.tab import Tab
from trosnoth.gui.framework.elements import TextElement
from trosnoth.gui.common import ScaledLocation, ScaledArea
from trosnoth.gui import keyboard
from trosnoth import keymap
from trosnoth.data import getPath, user
from trosnoth.utils.event import Event


class KeymapTab(Tab):

    def __init__(self, app, onClose=None):
        super(KeymapTab, self).__init__(app, 'Controls')
        self.font = app.screenManager.fonts.bigMenuFont

        self.onClose = Event()
        if onClose is not None:
            self.onClose.addListener(onClose)

        # Break things up into categories
        movement = [
            ACTION_JUMP, ACTION_DOWN, ACTION_LEFT, ACTION_RIGHT, ACTION_HOOK]
        menus = [ACTION_MAIN_MENU, ACTION_MORE_MENU]
        actions = [ACTION_UPGRADE_MENU, ACTION_USE_UPGRADE,
                   ACTION_EDIT_PLAYER_INFO, ACTION_READY, ACTION_SHOW_TRAJECTORY,
                   ACTION_EMOTE]
        misc = [ACTION_CHAT, ACTION_FOLLOW]
        upgrades = [upgradeClass.action for upgradeClass in sorted(allUpgrades,
                key=lambda upgradeClass: upgradeClass.order)]
        upgrades.append(ACTION_CLEAR_UPGRADE)

        display = [
            ACTION_LEADERBOARD_TOGGLE, ACTION_HUD_TOGGLE,
            ACTION_TERMINAL_TOGGLE]

        actionNames = {
            ACTION_EDIT_PLAYER_INFO: 'Change nick / hat',
            ACTION_CHAT: 'Chat',
            ACTION_CLEAR_UPGRADE: 'Deselect upgrade',
            ACTION_DOWN: 'Drop down',
            ACTION_FOLLOW: 'Auto pan (replay)',
            ACTION_HOOK: 'Grappling hook',
            ACTION_HUD_TOGGLE: 'Toggle HUD',
            ACTION_JUMP: 'Jump',
            ACTION_LEADERBOARD_TOGGLE: 'Show leaderboard',
            ACTION_LEFT: 'Move left',
            ACTION_MAIN_MENU: 'Main menu',
            ACTION_MORE_MENU: 'Advanced',
            ACTION_READY: 'Toggle ready',
            ACTION_RIGHT: 'Move right',
            ACTION_TERMINAL_TOGGLE: 'Toggle terminal',
            ACTION_UPGRADE_MENU: 'Select upgrade',
            ACTION_USE_UPGRADE: 'Activate upgrade',
            ACTION_SHOW_TRAJECTORY: 'Show trajectory',
            ACTION_EMOTE: 'Emote',
        }
        actionNames.update((upgradeClass.action, upgradeClass.name) for
                upgradeClass in allUpgrades)

        # Organise the categories by column
        self.layout = [
            [movement, menus],
            [actions, display],
            [upgrades, misc],
        ]

        self.errorInfo = TextElement(self.app, '', self.font,
                                 ScaledLocation(512, 580, 'center'))
        self.text = [self.errorInfo]
        self.inputLookup = {}
        xPos = 210

        # Lay everything out automatically.
        keymapFont = self.app.screenManager.fonts.keymapFont
        keymapInputFont = self.app.screenManager.fonts.keymapInputFont
        for column in self.layout:               # Each column
            yPos = 200
            for category in column:         # Each category
                for action in category:     # Each action
                    # Draw action name (eg. Respawn)
                    self.text.append(TextElement(self.app, actionNames[action],
                                    keymapFont,
                                    ScaledLocation(xPos, yPos+6, 'topright'),
                                    self.app.theme.colours.headingColour
                                    ))

                    # Create input box
                    box = prompt.KeycodeBox(
                        self.app, ScaledArea(xPos+10, yPos, 100, 30),
                        font=keymapInputFont, acceptMouse=True)
                    box.onClick.addListener(self.setFocus)
                    box.onChange.addListener(self.inputChanged)
                    box.__action = action
                    self.inputLookup[action] = box

                    yPos += 35  # Between items
                yPos += 35      # Between categories
            xPos += 310         # Between columns

        self.elements = self.text + list(self.inputLookup.values()) + [
            button(app, 'restore default controls', self.restoreDefaults, (0,
                -125), 'midbottom', secondColour=app.theme.colours.white),
            button(app, 'save', self.saveSettings, (-100, -75), 'midbottom',
                secondColour=app.theme.colours.white),
            button(app, 'cancel', self.cancel, (100, -75), 'midbottom',
                secondColour=app.theme.colours.white),
        ]

        self.populateInputs()

    def inputChanged(self, box):
        # Remove the old key.
        try:
            oldKey = self.keyMapping.getkey(box.__action)
        except KeyError:
            pass
        else:
            del self.keyMapping[oldKey]

        # Set the new key.
        self.keyMapping[box.value] = box.__action

        # Refresh the display.
        self.refreshInputs()

    def populateInputs(self):
        # Set up the keyboard mapping.
        self.keyMapping = keyboard.KeyboardMapping(keymap.default_game_keys)

        try:
            # Try to load keyboard mappings from the user's personal settings.
            with open(getPath(user, 'keymap'), 'r') as f:
                config = f.read()
            self.keyMapping.load(config)
        except IOError:
            pass

        # Refresh the display.
        self.refreshInputs()

    def refreshInputs(self):
        for column in self.layout:
            for category in column:
                for action in category:
                    # Get the current key and put it in the box.
                    try:
                        key = self.keyMapping.getkey(action)
                    except KeyError:
                        key = None
                    self.inputLookup[action].value = key

                    # Make the box white
                    self.inputLookup[action].backColour = (255, 255, 255)

    def restoreDefaults(self):
        self.keyMapping = keyboard.KeyboardMapping(keymap.default_game_keys)
        self.refreshInputs()

        self.showMessage("Default controls restored: press 'save' to "
                "confirm", (0, 128, 0))

    def clearBackgrounds(self):
        for action in self.inputLookup:
            self.inputLookup[action].backColour = (255, 255, 255)
        self.setFocus(None)

    def saveSettings(self):
        # Perform the save.
        open(getPath(user, 'keymap'), 'w').write(self.keyMapping.save())
        self.mainMenu()

    def showMessage(self, string, colour):
        self.errorInfo.setColour(colour)
        self.errorInfo.setText(string)
        self.errorInfo.setFont(self.font)

    def cancel(self):
        self.populateInputs()
        self.mainMenu()

    def mainMenu(self):
        self.showMessage('', (0, 0, 0))
        self.clearBackgrounds()
        self.onClose.execute()
