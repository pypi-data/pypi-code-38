import logging
import os

from direct.interval.IntervalGlobal import Sequence, SoundInterval

import trosnoth.data.music as music
from trosnoth.data import getPath, getPandaPath

log = logging.getLogger(__name__)


class MusicManager(object):
    '''Manages the music.'''

    def __init__(self, app):
        self.app = app
        self.index = 0
        self.playing = False

        self.interval = Sequence()
        for f in os.listdir(getPath(music)):
            if f.endswith('.ogg'):
                self.interval.append(SoundInterval(
                    self.app.panda.loader.loadMusic(getPandaPath(music, f))))
        self.interval.loop()
        self.interval.pause()

    def playMusic(self):
        self.interval.resume()
        self.playing = True

    def stopMusic(self):
        self.interval.pause()
        self.playing = False

    def isMusicPlaying(self):
        return self.playing

    def setVolume(self, volume):
         self.app.panda.musicManager.setVolume(volume / 100.0)
