import pygame

from trosnoth.gui.framework import framework, prompt
from trosnoth.gui.framework.elements import TextElement
from trosnoth.gui.framework.checkbox import CheckBox
from trosnoth.gui.framework.slider import Slider
from trosnoth.gui.framework.tab import Tab
from trosnoth.trosnothgui.common import button
from trosnoth.gui.common import ScaledLocation, ScaledArea
from trosnoth.utils.event import Event


class DisplaySettingsTab(Tab, framework.TabFriendlyCompoundElement):
    def __init__(self, app, onClose=None):
        super(DisplaySettingsTab, self).__init__(app, 'Display')

        self.onClose = Event()
        if onClose is not None:
            self.onClose.addListener(onClose)

        font = self.app.screenManager.fonts.bigMenuFont
        smallNoteFont = self.app.screenManager.fonts.smallNoteFont

        colour = self.app.theme.colours.headingColour
        def mkText(text, x, y, textFont=font, anchor='topright'):
            return TextElement(self.app, text, textFont,
                    ScaledLocation(x, y, anchor),
                    colour)

        self.text = [
            mkText('X', 640, 240),
            mkText('Screen resolution', 430, 240),
            mkText('Fullscreen mode', 430, 320),
            mkText('Graphics detail', 430, 400),
            mkText('low', 460, 435, textFont=smallNoteFont, anchor='midtop'),
            mkText('high', 845, 435, textFont=smallNoteFont, anchor='midtop'),
            mkText('Show timings', 430, 485),
            mkText('Show range', 430, 565),
        ]

        self.invalidInputText = TextElement(self.app, '', font,
                ScaledLocation(512, 190, 'midtop'), (192, 0, 0))

        self.widthInput = prompt.InputBox(self.app,
                ScaledArea(460, 225, 150, 60),
                initValue=str(self.app.screenManager.size[0]), font=font,
                maxLength=4, validator=prompt.intValidator)

        self.widthInput.onEnter.addListener(lambda sender: self.saveSettings())
        self.widthInput.onClick.addListener(self.setFocus)
        self.widthInput.onTab.addListener(self.tabNext)

        self.heightInput = prompt.InputBox(self.app,
                ScaledArea(652, 225, 150, 60),
                initValue=str(self.app.screenManager.size[1]), font=font,
                maxLength=4, validator=prompt.intValidator)

        self.heightInput.onEnter.addListener(lambda sender: self.saveSettings())
        self.heightInput.onClick.addListener(self.setFocus)
        self.heightInput.onTab.addListener(self.tabNext)

        self.tabOrder = [self.widthInput, self.heightInput]

        self.fullscreenBox = CheckBox(self.app,
            ScaledLocation(460, 325),
            text='',
            font=font,
            colour=(192, 192, 192),
            initValue=self.app.screenManager.isFullScreen(),
        )
        self.fullscreenBox.onValueChanged.addListener(self.fullscreenChanged)

        displaySettings = app.displaySettings

        self.detailSlider = Slider(
            self.app, ScaledArea(460, 390, 390, 40),
            bounds=(0, len(displaySettings.DETAIL_LEVELS) - 1), snap=True)
        self.detailSlider.setVal(
            displaySettings.DETAIL_LEVELS.index(displaySettings.detailLevel))
        self.detailSlider.onValueChanged.addListener(self.detailChanged)

        self.showTimingsBox = CheckBox(self.app,
            ScaledLocation(460, 490),
            text='',
            font=font,
            colour=(192,192,192),
            initValue=displaySettings.showTimings,
        )
        self.showRangeBox = CheckBox(self.app,
            ScaledLocation(460, 570),
            text='',
            font=font,
            colour=(192, 192, 192),
            initValue=displaySettings.showRange,
        )

        self.input = [self.widthInput, self.heightInput, self.widthInput,
                self.fullscreenBox, self.detailSlider, self.showTimingsBox,
                self.showRangeBox]

        self.elements = self.text + self.input + [
            self.invalidInputText,
            button(app, 'save', self.saveSettings, (-100, -75), 'midbottom',
                    secondColour=app.theme.colours.white),
            button(app, 'cancel', self.cancelMenu, (100, -75), 'midbottom',
                    secondColour=app.theme.colours.white),
        ]
        self.setFocus(self.widthInput)

    def detailChanged(self, newLevel):
        pass

    def cancelMenu(self):
        self.fullscreenBox.setValue(self.app.screenManager.isFullScreen())
        self.showTimingsBox.setValue(self.app.displaySettings.showTimings)
        self.showRangeBox.setValue(self.app.displaySettings.showRange)
        self.heightInput.setValue(str(self.app.screenManager.size[1]))
        self.widthInput.setValue(str(self.app.screenManager.size[0]))

        self.onClose.execute()

    def saveSettings(self):
        displaySettings = self.app.displaySettings

        height = self.getInt(self.heightInput.value)
        width = self.getInt(self.widthInput.value)
        fullScreen = self.fullscreenBox.value
        detailLevel = displaySettings.DETAIL_LEVELS[self.detailSlider.getVal()]
        showTimings = self.showTimingsBox.value
        showRange = self.showRangeBox.value

        # The resolutionList is used when fullScreen is true.
        resolutionList = pygame.display.list_modes()
        resolutionList.sort()
        minResolution = resolutionList[0]
        maxResolution = resolutionList[-1]

        if not fullScreen:
            minResolution = (320, 240)

        # These values are used when fullScreen is false.
        widthRange = (minResolution[0], maxResolution[0])
        heightRange = (minResolution[1], maxResolution[1])

        if not widthRange[0] <= width <= widthRange[1]:
            self.incorrectInput('Screen width must be between %d and %d' %
                                (widthRange[0], widthRange[1]))
            width = None
            return
        if not heightRange[0] <= height <= heightRange[1]:
            self.incorrectInput('Screen height must be between %d and %d' %
                                (heightRange[0], heightRange[1]))
            height = None
            return
        if fullScreen:
            selectedResolution = (width, height)
            if selectedResolution not in resolutionList:
                self.incorrectInput('Selected resolution is not valid for '
                        'this display')
                height = width = None
                return

        self.incorrectInput('')

        # Save these values.
        displaySettings.fullScreen = fullScreen
        displaySettings.detailLevel = detailLevel
        displaySettings.showTimings = showTimings
        displaySettings.showRange = showRange
        if fullScreen:
            displaySettings.fsSize = (width, height)
        else:
            displaySettings.size = (width, height)

        # Write to file and apply.
        displaySettings.save()
        displaySettings.apply()

        self.onClose.execute()

    def getInt(self, value):
        if value == '':
            return 0
        return int(value)

    def incorrectInput(self, string):
        self.invalidInputText.setText(string)
        self.invalidInputText.setFont(self.app.screenManager.fonts.bigMenuFont)

    def fullscreenChanged(self, element):
        # If the resolution boxes haven't been touched, swap their values to
        # the appropriate resolution for the new mode.

        height = self.getInt(self.heightInput.value)
        width = self.getInt(self.widthInput.value)
        fullScreen = self.fullscreenBox.value

        if fullScreen:
            # Going to full screen mode.
            if (width, height) != self.app.displaySettings.size:
                return
            width, height = self.app.displaySettings.fsSize
        else:
            # Going from full screen mode.
            if (width, height) != self.app.displaySettings.fsSize:
                return
            width, height = self.app.displaySettings.size

        self.heightInput.setValue(str(height))
        self.widthInput.setValue(str(width))
