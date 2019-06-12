import pygame
import trosnoth.data.sound as sound
from trosnoth.data import getPath


class SoundAction(object):
    def __init__(self, filename, channel):
        self.channel = channel
        if not pygame.mixer.get_init():
            return

        self.sound = pygame.mixer.Sound(getPath(sound, filename))
        self.channelVolume = 1

    def play(self, volume=1):
        if not pygame.mixer.get_init():
            return

        finalVol = volume * self.channelVolume
        if finalVol < 0.01:
            return

        if self.channel is None:
            channel = pygame.mixer.find_channel(True)
        else:
            channel = pygame.mixer.Channel(self.channel)

        channel.set_volume(finalVol)
        channel.play(self.sound)

    def setVolume(self, val):
        self.sound.set_volume(val)

    def setChannelsVolume(self, val):
        self.channelVolume = val


class SoundPlayer(object):
    def __init__(self):
        self.sounds = {}
        self.masterVolume = 1
        self._reservedChannels = 0
        if pygame.mixer.get_init():
            pygame.mixer.set_num_channels(16)

    def addSound(self, filename, action, channel=None):
        if not pygame.mixer.get_init():
            return

        if channel is not None and channel >= self._reservedChannels:
            self._reservedChannels = channel + 1
            pygame.mixer.set_reserved(self._reservedChannels)

        self.sounds[action] = SoundAction(filename, channel)

        # In case a sound is added after the volume has been set:
        self.sounds[action].setChannelsVolume(self.masterVolume)

    def play(self, action, volume=1):
        if not pygame.mixer.get_init():
            return

        self.sounds[action].play(volume)

    def playFromServerCommand(self, filename):
        action = 'custom:' + filename
        if action not in self.sounds:
            self.addSound(filename, action, channel=0)
        self.play(action)

    def setSoundVolume(self, action, val):
        self.sounds[action].setVolume(val)

    def setMasterVolume(self, val):
        self.masterVolume = val
        for action in list(self.sounds.values()):
            action.setChannelsVolume(val)
