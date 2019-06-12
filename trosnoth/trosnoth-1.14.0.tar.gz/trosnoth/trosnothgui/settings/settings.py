import pygame

from trosnoth.trosnothgui.settings.display import DisplaySettingsTab
from trosnoth.trosnothgui.settings.keymap import KeymapTab
from trosnoth.trosnothgui.settings.sound import SoundSettingsTab
from trosnoth.trosnothgui.settings.themes import ThemeTab
from trosnoth.gui.framework import framework, elements
from trosnoth.gui.framework.tabContainer import TabContainer, TabSize
from trosnoth.gui.common import (ScaledArea, Location, AttachedPoint)
from trosnoth.utils.event import Event

class SettingsMenu(framework.CompoundElement):
    def __init__(self, app, onClose=None, onRestart=None,
            showThemes=False, showSound=True, showDisplay=True,
            showKeymap=True):
        super(SettingsMenu, self).__init__(app)

        self.onClose = Event()
        if onClose is not None:
            self.onClose.addListener(onClose)
        self.onRestart = Event()
        if onRestart is not None:
            self.onRestart.addListener(onRestart)

        area = ScaledArea(50,140,924, 570)
        bg = pygame.Surface((924, 500))
        bg.fill(app.theme.colours.settingsMenu)
        if app.displaySettings.alphaOverlays:
            bg.set_alpha(192)
        font = app.screenManager.fonts.bigMenuFont
        self.tabContainer = TabContainer(self.app, area, font,
                app.theme.colours.settingsTabBorder)
        bp = elements.SizedPicture(app, bg, Location(AttachedPoint((0,0),
                self.tabContainer._getTabRect)), TabSize(self.tabContainer))

        if showDisplay:
            displayTab = DisplaySettingsTab(app, onClose=self.onClose.execute)
            self.tabContainer.addTab(displayTab)

        if showKeymap:
            keymapTab = KeymapTab(app, onClose=self.onClose.execute)
            self.tabContainer.addTab(keymapTab)

        if showSound:
            soundTab = SoundSettingsTab(app, onClose=self.onClose.execute)
            self.tabContainer.addTab(soundTab)

        if showThemes:
            themeTab = ThemeTab(app, onClose=self.onClose.execute,
                    onRestart=self.onRestart.execute)
            self.tabContainer.addTab(themeTab)

        self.elements = [bp, self.tabContainer]
