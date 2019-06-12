from panda3d.core import AudioManager

import trosnoth.data.sound as sound
from trosnoth.data import getPandaPath


MAX_OF_SAME_SOUND = 3


class SoundPlayer(object):
    def __init__(self, app):
        self.app = app
        self.sfxManager = app.panda.sfxManagerList[0]
        self.keySoundManager = AudioManager.createAudioManager()
        self.keySoundManager.setConcurrentSoundLimit(1)
        self.app.panda.addSfxManager(self.keySoundManager)

        self.sounds = {}

    def addSound(self, filename, action, key=False, n=1):
        if key:
            mgr = self.keySoundManager
        else:
            mgr = self.sfxManager

        # Load multiple copies of some sounds so that they can be played
        # concurrently (e.g. several shots at a time).
        self.sounds[action] = sounds = []
        for i in range(n):
            sounds.append(self.app.panda.loader.loadSound(
                mgr, getPandaPath(sound, filename)))

    def play(self, action, volume=1.0):
        # Rotate the copies of this sound
        sounds = self.sounds[action]
        sound = sounds.pop(0)
        sounds.append(sound)

        sound.setVolume(volume)
        sound.play()

    def playFromServerCommand(self, filename):
        action = 'custom:' + filename
        if action not in self.sounds:
            self.addSound(filename, action, key=True)
        self.play(action)

    def setMasterVolume(self, val):
        self.sfxManager.setVolume(val)
        self.keySoundManager.setVolume(val)
