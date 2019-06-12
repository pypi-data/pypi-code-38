import logging
from collections import OrderedDict

from direct.gui.DirectGui import (
    DirectLabel, DirectOptionMenu, DirectCheckButton, DirectButton, DirectFrame,
    DGG, DirectSlider)
from direct.showbase.DirectObject import DirectObject
from panda3d.core import NodePath, TextNode

from trosnoth.client3d.base.screenManager.screenManager import (
    FULL_SCREEN, NO_BORDER, WINDOWED)
from trosnoth.const import (
    ACTION_LEFT, ACTION_DOWN, ACTION_RIGHT, ACTION_JUMP, ACTION_FOLLOW,
    ACTION_MAIN_MENU, ACTION_UPGRADE_MENU, ACTION_MORE_MENU, ACTION_EMOTE,
    ACTION_USE_UPGRADE, ACTION_ABANDON_UPGRADE, ACTION_CLEAR_UPGRADE,
    ACTION_EDIT_PLAYER_INFO, ACTION_READY, ACTION_CHAT, ACTION_LEADERBOARD_TOGGLE,
    ACTION_HUD_TOGGLE, ACTION_TERMINAL_TOGGLE, ACTION_PAUSE_GAME,
)
from trosnoth.model.upgrades import allUpgrades
from trosnoth.utils.gui import align

log = logging.getLogger(__name__)


class SettingsScreen(object):
    def __init__(self, app, scene, onClose=None):
        self.app = app
        self.scene = scene
        self.node = None
        self.onClose = onClose

        self.displaySettingsScreen = DisplaySettingsScreenHelper(
            app, scene, self)
        self.audioSettingsScreen = AudioSettingsScreenHelper(
            app, scene, self)
        self.controlSettingsScreen = ControlSettingsScreenHelper(
            app, scene, self)

        self.visibleNode = None
        self.mainNode = None
        self.displayNode = None
        self.audioNode = None
        self.controlNode = None

    def showNode(self, node):
        if self.visibleNode is not None:
            self.visibleNode.hide()
        self.visibleNode = node
        node.show()

    def showMainButtons(self):
        self.showNode(self.mainNode)

    def showDisplaySettings(self):
        self.showNode(self.displayNode)
        self.displaySettingsScreen.show()

    def showAudioSettings(self):
        self.showNode(self.audioNode)
        self.audioSettingsScreen.show()

    def showControlSettings(self):
        self.showNode(self.controlNode)
        self.controlSettingsScreen.show()

    def show(self):
        self.showMainButtons()

    def close(self):
        self.node.hide()
        if self.onClose is not None:
            self.onClose()

    def setup(self, node):
        self.node = node

        colours = self.app.theme.colours
        DirectFrame(
            parent=self.node,
            pos=(0, 0, 0),
            frameSize=(-0.9, 0.9, -0.55, 0.37),
            frameColor=colours.playMenu,
            relief=DGG.GROOVE,
            borderWidth=(0.02, 0.02),
        )

        self.mainNode = self.scene.reparent(
            NodePath('settingsMain'), self.node)
        self.mainNode.hide()

        self.displayNode = self.scene.reparent(
            NodePath('displaySettings'), self.node)
        self.displayNode.hide()
        self.displaySettingsScreen.setup(self.displayNode)

        self.audioNode = self.scene.reparent(
            NodePath('audioSettings'), self.node)
        self.audioNode.hide()
        self.audioSettingsScreen.setup(self.audioNode)

        self.controlNode = self.scene.reparent(
            NodePath('controlSettings'), self.node)
        self.controlNode.hide()
        self.controlSettingsScreen.setup(self.controlNode)

        BUTTON_PROPERTIES = {
            'scale': 0.04,
            'frameSize': (-7.0, 7.0, -1.0, 1.5),
            'parent': self.mainNode,
        }

        button = DirectButton(
            text='Display',
            command=self.showDisplaySettings,
            **BUTTON_PROPERTIES
        )
        align(button, midX=0, midZ=2.5*0.04)

        button = DirectButton(
            text='Audio',
            command=self.showAudioSettings,
            **BUTTON_PROPERTIES
        )
        align(button, midX=0, midZ=0)

        button = DirectButton(
            text='Controls',
            command=self.showControlSettings,
            **BUTTON_PROPERTIES
        )
        align(button, midX=0, midZ=-2.5*0.04)

        button = DirectButton(
            text='Back',
            command=self.close,
            **BUTTON_PROPERTIES
        )
        align(button, midX=0, midZ=-6*0.04)


class DisplaySettingsScreenHelper(object):

    DISPLAY_MODE_OPTIONS = [WINDOWED, NO_BORDER, FULL_SCREEN]
    DETAIL_LEVEL_OPTIONS = OrderedDict([
        ('Ultra', 'full'),
        ('High', 'default'),
        ('Medium', 'low'),
        ('Low', 'shrunk'),
        ('Toaster', 'lowest')
    ])

    def __init__(self, app, scene, parent):
        self.app = app
        self.scene = scene
        self.settings = app.displaySettings
        self.parent = parent

        self.pendingChanges = False
        self.saveButton = None
        self.finishButton = None

        self.resolutionMenu = None
        self.displayModeMenu = None
        self.detailMenu = None
        self.showFPS = None

    def show(self):
        # Fetch the list of available resolutions.
        resolutions = set()
        displayInfo = self.app.panda.pipe.getDisplayInformation()
        for index in range(displayInfo.getTotalDisplayModes()):
            mode = displayInfo.getDisplayMode(index)
            resolutions.add((mode.width, mode.height))

        resolutions = ['%d x %d' % (r[0], r[1]) for r in sorted(resolutions)]

        currentSize = '%d x %d' % self.settings.size
        if currentSize not in resolutions:
            resolutions.append(currentSize)
        self.resolutionMenu['items'] = resolutions
        self.resolutionMenu['extraArgs'] = [currentSize]
        self.resolutionMenu.set(currentSize)

        self.displayModeMenu['extraArgs'] = [self.settings.displayMode]
        self.displayModeMenu.set(self.settings.displayMode)

        # This finds the key in the detail dict from the value
        d = self.DETAIL_LEVEL_OPTIONS
        currentDetail = list(d.keys())[list(d.values()).index(self.settings.detailLevel)]
        self.detailMenu['extraArgs'] = [currentDetail]
        self.detailMenu.set(currentDetail)

        self.showFPS['extraArgs'] = [self.settings.showTimings]
        self.showFPS['indicatorValue'] = self.settings.showTimings
        self.showFPS.setIndicatorValue()

    def setup(self, node):
        colours = self.app.theme.colours
        TEXT_PROPERTIES = {
            'parent': node,
            'text_scale': 0.08,
            'text_fg': colours.listboxButtons,
            'text_align': TextNode.A_left,
            'relief': None,
        }

        DROPDOWN_PROPERTIES = {
            'parent': node,
            'scale': 0.06,
            'textMayChange': True,
            'frameSize': (-0.5, 12, -0.7, 1.05),
            'command': self.optionChanged,
        }

        label = DirectLabel(
            text='Screen resolution',
            **TEXT_PROPERTIES
        )
        align(label, left=-0.85, midZ=0.25)

        self.resolutionMenu = DirectOptionMenu(
            # If there isn't at least one item by default, the text alignment
            # will be all messed up when adding the resolutions.
            items=[''],
            **DROPDOWN_PROPERTIES
        )
        align(self.resolutionMenu, left=0, midZ=0.25)

        label = DirectLabel(
            text='Display mode',
            **TEXT_PROPERTIES
        )
        align(label, left=-0.85, midZ=0.10)

        self.displayModeMenu = DirectOptionMenu(
            items=self.DISPLAY_MODE_OPTIONS,
            **DROPDOWN_PROPERTIES
        )
        align(self.displayModeMenu, left=0, midZ=0.10)

        label = DirectLabel(
            text='Detail level',
            **TEXT_PROPERTIES
        )
        align(label, left=-0.85, midZ=-0.05)

        self.detailMenu = DirectOptionMenu(
            items=list(self.DETAIL_LEVEL_OPTIONS.keys()),
            **DROPDOWN_PROPERTIES
        )
        align(self.detailMenu, left=0, midZ=-0.05)

        label = DirectLabel(
            text='Show FPS',
            **TEXT_PROPERTIES
        )
        align(label, left=-0.85, midZ=-0.20)

        self.showFPS = DirectCheckButton(
            scale=0.06,
            parent=node,
            pos=(0, 0, -0.20),
            command=self.optionChanged
        )
        align(self.showFPS, left=0, midZ=-0.20)

        BUTTON_PROPERTIES = {
            'scale': 0.04,
            'frameSize': (-5.0, 5.0, -1.0, 1.5),
            'parent': node,
        }

        self.saveButton = DirectButton(
            text='Save',
            command=self.saveSettings,
            **BUTTON_PROPERTIES
        )
        align(self.saveButton, left=-0.87, z=-0.63)
        self.saveButton.hide()

        self.finishButton = DirectButton(
            text='Back',
            command=self.cancelPressed,
            **BUTTON_PROPERTIES
        )
        align(self.finishButton, right=0.87, z=-0.63)

    def saveSettings(self):
        resolution = self.resolutionMenu.get()
        width, height = resolution.split(' x ')

        s = self.settings
        s.size = (int(width), int(height))
        s.displayMode = self.displayModeMenu.get()
        s.detailLevel = self.DETAIL_LEVEL_OPTIONS[self.detailMenu.get()]
        s.showTimings = self.showFPS['indicatorValue']
        s.apply()
        s.save()

        self.show()
        self.hideSaveButton()

    def showSaveButton(self):
        self.pendingChanges = True
        self.saveButton.show()
        self.finishButton['text'] = 'Cancel'

    def hideSaveButton(self):
        self.pendingChanges = False
        self.saveButton.hide()
        self.finishButton['text'] = 'Back'

    def optionChanged(self, newValue, initialValue):
        log.debug(newValue)
        if newValue != initialValue:
            self.showSaveButton()

    def cancelPressed(self):
        if self.pendingChanges:
            self.show()
            self.hideSaveButton()
        else:
            self.parent.showMainButtons()


class AudioSettingsScreenHelper(object):

    SAVE_DELAY = 1.0  # seconds

    def __init__(self, app, scene, parent):
        self.app = app
        self.scene = scene
        self.parent = parent
        self.settings = app.soundSettings

        self.saveTask = None

        self.musicSlider = None
        self.musicLabel = None
        self.musicCheckbox = None
        self.soundSlider = None
        self.soundLabel = None
        self.soundCheckbox = None

    def show(self):
        self.musicCheckbox['indicatorValue'] = self.settings.musicEnabled
        self.soundCheckbox['indicatorValue'] = self.settings.soundEnabled
        self.musicSlider['value'] = self.settings.musicVolume
        self.soundSlider['value'] = self.settings.soundVolume

        '''
        If the command is set in the setup function, it will be immediately
        called with a value of zero, which will overwrite any volume settings
        already set by the user. Setting the command in the show function
        avoids this issue, as the initial value will be correctly set.
        '''
        self.musicSlider['command'] = self.musicAdjusted
        self.soundSlider['command'] = self.soundAdjusted

    '''
    Apply the audio settings immediately, but don't save them to disk until
    after a short delay. This is because the sliders can update the settings
    multiple times per second.
    '''
    def applySettings(self, indicatorValue=None):
        self.settings.musicEnabled = bool(self.musicCheckbox['indicatorValue'])
        self.settings.soundEnabled = bool(self.soundCheckbox['indicatorValue'])
        self.settings.musicVolume = int(self.musicSlider['value'])
        self.settings.soundVolume = int(self.soundSlider['value'])
        self.settings.apply()

        if self.saveTask is not None:
            self.app.panda.taskMgr.remove(self.saveTask)

        self.saveTask = self.app.panda.taskMgr.doMethodLater(
            self.SAVE_DELAY, self._save, 'Save Audio Settings', extraArgs=[])

    def _save(self):
        self.settings.save()
        self.saveTask = None
        log.debug('Audio settings saved to disk.')

    def musicAdjusted(self):
        self.applySettings()
        self.musicLabel['text'] = str(self.settings.musicVolume)
        log.debug('Music: %d' % self.musicSlider['value'])

    def soundAdjusted(self):
        self.applySettings()
        self.soundLabel['text'] = str(self.settings.soundVolume)
        log.debug('Sound: %d' % self.soundSlider['value'])

    def setup(self, node):
        colours = self.app.theme.colours

        SLIDER_PROPERTIES = {
            'range': (0, 100),
            'pageSize': 100,
            'scrollSize': 0,
            'parent': node,
            'scale': 0.5,
            'frameSize': (-0.85, 0.85, -0.08, 0.08),
            'thumb_relief': DGG.RIDGE,
        }

        TEXT_PROPERTIES = {
            'parent': node,
            'text_scale': 0.08,
            'text_fg': colours.listboxButtons,
            'text_align': TextNode.A_left,
            'relief': None,
            'textMayChange': True,
        }

        label = DirectLabel(
            text='Music volume',
            **TEXT_PROPERTIES
        )
        align(label, left=-0.85, midZ=0.25)

        self.musicSlider = DirectSlider(**SLIDER_PROPERTIES)
        align(self.musicSlider, left=-0.2, midZ=0.25)

        self.musicLabel = DirectLabel(
            text='100',
            **TEXT_PROPERTIES
        )
        align(self.musicLabel, left=0.70, midZ=0.25)

        label = DirectLabel(
            text='Enable music',
            **TEXT_PROPERTIES
        )
        align(label, left=-0.85, midZ=0.10)

        self.musicCheckbox = DirectCheckButton(
            scale=0.06,
            parent=node,
            command=self.applySettings,
        )
        align(self.musicCheckbox, left=-0.2, midZ=0.10)

        label = DirectLabel(
            text='Sound volume',
            **TEXT_PROPERTIES
        )
        align(label, left=-0.85, midZ=-0.05)

        self.soundSlider = DirectSlider(**SLIDER_PROPERTIES)
        align(self.soundSlider, left=-0.2, midZ=-0.05)

        self.soundLabel = DirectLabel(
            text='100',
            **TEXT_PROPERTIES
        )
        align(self.soundLabel, left=0.70, midZ=-0.05)

        label = DirectLabel(
            text='Enable sound',
            **TEXT_PROPERTIES
        )
        align(label, left=-0.85, midZ=-0.20)

        self.soundCheckbox = DirectCheckButton(
            scale=0.06,
            parent=node,
            command=self.applySettings,
        )
        align(self.soundCheckbox, left=-0.2, midZ=-0.20)

        BUTTON_PROPERTIES = {
            'scale': 0.04,
            'frameSize': (-5.0, 5.0, -1.0, 1.5),
            'parent': node,
        }

        button = DirectButton(
            text='Back',
            command=self.parent.showMainButtons,
            **BUTTON_PROPERTIES
        )
        align(button, right=0.87, z=-0.63)


class ControlSettingsScreenHelper(object):

    COLOUR_VALID = (1, 1, 1, 1)
    COLOUR_SELECTED = (0.75, 0.75, 1, 1)
    COLOUR_INVALID = (1, 0.75, 0.75, 1)

    def __init__(self, app, scene, parent):
        self.app = app
        self.scene = scene
        self.parent = parent
        self.keymap = self.app.keymap
        self.do = DirectObject()

        self.saveButton = None
        self.finishButton = None
        self.pendingChanges = False

        # The KeyboadMapping provides a dict of keys to actions: this member
        # does the opposite (provides a dict to actions to keys)
        self.keys = {}

        self.selectedAction = None
        self.inputLookup = {}
        self.layout = []

    def show(self):
        self.keys = dict((v, k) for k, v in self.keymap.actions.items())

        for column in self.layout:
            for category in column:
                for action in category:
                    if action in self.keys:
                        self.inputLookup[action]['text'] = self.keys[action]
                        self.inputLookup[action]['frameColor'] = self.COLOUR_VALID
                    else:
                        self.inputLookup[action]['frameColor'] = self.COLOUR_INVALID
                        self.keys[action] = None

    def setup(self, node):
        colours = self.app.theme.colours

        TEXT_PROPERTIES = {
            'parent': node,
            'text_scale': 0.038,
            'text_fg': colours.listboxButtons,
            'text_align': TextNode.A_right,
            'relief': None,
        }

        KEY_PROPERTIES = {
            'parent': node,
            'scale': 0.038,
            'frameColor': self.COLOUR_VALID,
            'frameSize': (-3.0, 3.0, -0.7, 0.7),
            'text_align': TextNode.A_center,
            'text_scale': 0.9,
            'text_pos': (0, -0.18),
            'relief': DGG.FLAT,
            'textMayChange': True,
            'command': self.actionSelected,
        }

        movement = [ACTION_JUMP, ACTION_DOWN, ACTION_LEFT, ACTION_RIGHT]
        menus = [ACTION_MAIN_MENU, ACTION_MORE_MENU]
        actions = [
            ACTION_UPGRADE_MENU, ACTION_USE_UPGRADE,
            ACTION_ABANDON_UPGRADE, ACTION_EDIT_PLAYER_INFO, ACTION_READY,
            ACTION_PAUSE_GAME, ACTION_EMOTE,
        ]
        misc = [ACTION_CHAT, ACTION_FOLLOW]
        upgrades = [
            upgradeClass.action for upgradeClass in sorted(
                allUpgrades, key=lambda upgradeClass: upgradeClass.order)]
        upgrades.append(ACTION_CLEAR_UPGRADE)

        display = [
            ACTION_LEADERBOARD_TOGGLE, ACTION_HUD_TOGGLE,
            ACTION_TERMINAL_TOGGLE]

        actionNames = {
            ACTION_ABANDON_UPGRADE: 'Abandon upgrade',
            ACTION_UPGRADE_MENU: 'Select upgrade',
            ACTION_USE_UPGRADE: 'Activate upgrade',
            ACTION_EDIT_PLAYER_INFO: 'Change nick / hat',
            ACTION_CHAT: 'Chat',
            ACTION_DOWN: 'Drop down',
            ACTION_EMOTE: 'Emote',
            ACTION_FOLLOW: 'Auto pan (replay)',
            ACTION_JUMP: 'Jump',
            ACTION_LEADERBOARD_TOGGLE: 'Show leaderboard',
            ACTION_LEFT: 'Move left',
            ACTION_MAIN_MENU: 'Main menu',
            ACTION_MORE_MENU: 'Advanced',
            ACTION_CLEAR_UPGRADE: 'Deselect upgrade',
            ACTION_READY: 'Toggle ready',
            ACTION_PAUSE_GAME: 'Pause/resume',
            ACTION_RIGHT: 'Move right',
            ACTION_HUD_TOGGLE: 'Toggle HUD',
            ACTION_TERMINAL_TOGGLE: 'Toggle terminal',
        }
        actionNames.update((upgradeClass.action, upgradeClass.name) for
                           upgradeClass in allUpgrades)

        # Organise the categories by column
        self.layout = [
            [movement, menus],
            [actions, display],
            [upgrades, misc],
        ]

        xPos = -0.68

        for column in self.layout:          # Each column
            yPos = 0.30
            for category in column:         # Each category
                for action in category:     # Each action
                    # Draw action name (eg. Respawn)
                    label = DirectLabel(
                        text=actionNames[action],
                        **TEXT_PROPERTIES
                    )
                    align(label, right=xPos, midZ=yPos)

                    # Create input box
                    box = DirectButton(
                        text='',
                        extraArgs=[action],
                        **KEY_PROPERTIES
                    )
                    align(box, left=xPos + 0.03, midZ=yPos)
                    self.inputLookup[action] = box

                    yPos -= 0.07  # Between items
                yPos -= 0.08      # Between categories
            xPos += 0.65          # Between columns

        BUTTON_PROPERTIES = {
            'scale': 0.04,
            'frameSize': (-5.0, 5.0, -1.0, 1.5),
            'parent': node,
        }

        self.restoreDefaultButton = DirectButton(
            text='Restore defaults',
            # scale=0.04,
            # parent=node,
            command=self.restoreDefaults,
            # text_align=TextNode.A_left,
            # pad=(0.5, 0.2)
            **BUTTON_PROPERTIES
        )
        align(self.restoreDefaultButton, midX=0, z=-0.63)

        self.saveButton = DirectButton(
            text='Save',
            command=self.save,
            **BUTTON_PROPERTIES
        )
        align(self.saveButton, left=-0.87, z=-0.63)
        self.saveButton.hide()

        self.finishButton = DirectButton(
            text='Back',
            command=self.cancelPressed,
            **BUTTON_PROPERTIES
        )
        align(self.finishButton, right=0.87, z=-0.63)

    def cancelPressed(self):
        self.deselectAction()
        if self.pendingChanges:
            self.keymap.reset()
            self.show()
            self.hideSaveButton()
        else:
            self.parent.showMainButtons()

    def save(self):
        self.keymap.apply()
        self.keymap.save()
        self.hideSaveButton()

    def showSaveButton(self):
        self.pendingChanges = True
        self.saveButton.show()
        self.finishButton['text'] = 'Cancel'

    def hideSaveButton(self):
        self.pendingChanges = False
        self.saveButton.hide()
        self.finishButton['text'] = 'Back'

    def restoreDefaults(self):
        self.deselectAction()
        self.keymap.revertToDefault()
        self.show()
        self.showSaveButton()

    def deselectAction(self):
        if self.selectedAction:
            self.inputLookup[self.selectedAction]['frameColor'] = self.COLOUR_VALID
        self.selectedAction = None
        self.do.ignoreAll()

    def actionSelected(self, action):
        self.deselectAction()
        self.selectedAction = action
        button = self.inputLookup[action]
        button['frameColor'] = self.COLOUR_SELECTED
        log.debug('Changing key for %s' % action)

        self.app.panda.buttonThrowers[0].node().setButtonDownEvent('button')
        self.do.accept('button', self.keyPressed, [action])

    def keyPressed(self, action, key):
        self.deselectAction()

        oldKey = self.keys[action]

        if oldKey == key:
            return

        # Remove the old key from the keymap
        if oldKey is not None:
            del self.keymap.actions[oldKey]

        self.inputLookup[action]['text'] = key

        # If there's a conflict, remove the conflicting action from the keymap
        if key in self.keymap.actions:
            secondAction = self.keymap.actions[key]
            log.debug('Overwriting conflicting key for %s' % secondAction)

            self.inputLookup[secondAction]['text'] = ''
            self.inputLookup[secondAction]['frameColor'] = self.COLOUR_INVALID
            self.keys[secondAction] = None

        # Update the keymap with the new key
        self.keys[action] = key
        self.keymap.actions[key] = action
        log.debug('New key for %s is %s' % (action, key))

        self.showSaveButton()
