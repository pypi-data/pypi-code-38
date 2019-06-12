import logging

from trosnoth.gui.framework import framework
from trosnoth.gui.framework.checkbox import CheckBox
from trosnoth.gui.framework.tab import Tab
from trosnoth.gui.framework.slider import Slider
from trosnoth.trosnothgui.common import button
from trosnoth.gui.common import ScaledLocation, ScaledArea
from trosnoth.gui.framework.elements import TextElement
from trosnoth.utils.event import Event

log = logging.getLogger()


class SoundSettingsTab(Tab, framework.CompoundElement):
    def __init__(self, app, onClose=None):
        super(SoundSettingsTab, self).__init__(app, 'Sounds')

        self.onClose = Event()
        if onClose is not None:
            self.onClose.addListener(onClose)

        font = self.app.screenManager.fonts.bigMenuFont
        colours = app.theme.colours

        text = [
            TextElement(self.app, 'Music Volume', font,
                ScaledLocation(400, 285, 'topright'), colours.headingColour),
            TextElement(self.app, 'Enable Music', font,
                ScaledLocation(400, 355, 'topright'), colours.headingColour),
            TextElement(self.app, 'Sound Volume', font,
                ScaledLocation(400, 425, 'topright'), colours.headingColour),
            TextElement(self.app, 'Enable Sound', font,
                ScaledLocation(400, 495, 'topright'), colours.headingColour),
        ]

        initVolume = app.soundSettings.musicVolume
        musicVolumeLabel = TextElement(self.app, '%d' % (initVolume,), font,
                                 ScaledLocation(870, 280, 'topleft'),
                                 colours.headingColour)


        self.musicVolumeSlider = Slider(self.app,
                ScaledArea(450, 280, 400, 40))
        onSlide = lambda volume: musicVolumeLabel.setText('%d' % volume)
        self.musicVolumeSlider.onSlide.addListener(onSlide)
        self.musicVolumeSlider.onValueChanged.addListener(onSlide)
        self.musicVolumeSlider.setVal(initVolume)

        self.musicBox = CheckBox(self.app, ScaledLocation(450, 360),
                text='', font=font, colour=(192,192,192),
                initValue=app.soundSettings.musicEnabled)

        initSndVolume = app.soundSettings.soundVolume
        soundVolumeLabel = TextElement(self.app, '%d' % (initSndVolume,), font,
                ScaledLocation(870, 420, 'topleft'), colours.headingColour)


        self.soundVolumeSlider = Slider(self.app,
                ScaledArea(450, 420, 400, 40))
        onSlide = lambda volume: soundVolumeLabel.setText('%d' % volume)
        self.soundVolumeSlider.onSlide.addListener(onSlide)
        self.soundVolumeSlider.onValueChanged.addListener(onSlide)
        self.soundVolumeSlider.setVal(initSndVolume)

        self.soundBox = CheckBox(self.app, ScaledLocation(450, 500),
                text='', font=font, colour=(192,192,192),
                initValue=app.soundSettings.soundEnabled)

        self.buttons = [
            button(app, 'save', self.saveSettings, (-100, -75), 'midbottom',
                   secondColour=app.theme.colours.white),
            button(app, 'cancel', self.onClose.execute, (100, -75),
                'midbottom', secondColour=app.theme.colours.white)
        ]

        self.elements = text + [musicVolumeLabel, self.musicVolumeSlider,
                self.musicBox, soundVolumeLabel, self.soundVolumeSlider,
                self.soundBox] + self.buttons

    def saveSettings(self, sender=None):
        playMusic, volume, playSound, sndVolume = self.getValues()

        ss = self.app.soundSettings
        ss.musicEnabled = playMusic
        ss.musicVolume = volume
        ss.soundEnabled = playSound
        ss.soundVolume = sndVolume

        ss.save()
        ss.apply()

        self.onClose.execute()

    def getValues(self):

        playMusic = self.musicBox.value
        volume = self.musicVolumeSlider.getVal()

        playSound = self.soundBox.value
        sndVolume = self.soundVolumeSlider.getVal()

        return [playMusic, volume, playSound, sndVolume]

