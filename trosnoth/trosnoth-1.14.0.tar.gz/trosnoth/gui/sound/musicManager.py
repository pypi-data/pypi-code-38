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

import logging
import os
import pygame

import trosnoth.data.music as music
from trosnoth.data import getPath

log = logging.getLogger(__name__)

# NO_MORE_MUSIC must not collide with any pygame events.
NO_MORE_MUSIC = 234

pygame.mixer.music.set_endevent(NO_MORE_MUSIC)

class MusicManager(object):
    '''Manages the music.'''

    def __init__(self):
        try:
            pygame.mixer.init(44100)
        except:
            log.error('Could not initialise audio.')
        self.index = 0
        self.volume = 100
        self.filenames = []
        for f in os.listdir(getPath(music)):
            if f.endswith('.ogg'):
                self.addMusicFile(f)

    def processEvent(self, event):
        if event.type == NO_MORE_MUSIC:
            self.musicEnded()
            return None
        else:
            return event

    def addMusicFile(self, filename):
        self.filenames.append(filename)

    def playMusic(self):
        if not pygame.mixer.get_init():
            return

        curFile = self.filenames[self.index]
        pygame.mixer.music.load(getPath(music, curFile))
        pygame.mixer.music.play(0)
        self.setVolume(self.volume)

    def playNext(self):
        self.index = (self.index + 1) % len(self.filenames)
        curFile = self.filenames[self.index]
        pygame.mixer.music.load(getPath(music, curFile))
        pygame.mixer.music.play()

    def musicEnded(self):
        self.playNext()
        self.setVolume(self.volume)

    def stopMusic(self):
        if pygame.mixer.get_init():
            pygame.mixer.music.stop()

    def isMusicPlaying(self):
        if not pygame.mixer.get_init():
            return False

        return pygame.mixer.music.get_busy()

    def setVolume(self, volume):
        if not pygame.mixer.get_init():
            return

        self.volume = volume
        # Valid range is 0.0 - 1.0
        decimalVolume = volume / 100.0
        pygame.mixer.music.set_volume(decimalVolume)

