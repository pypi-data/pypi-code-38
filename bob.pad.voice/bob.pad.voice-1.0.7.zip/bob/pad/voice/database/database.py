#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# @author: Pavel Korshunov <pavel.korshunov@idiap.ch>
# @date:   Tue Sep 20 15:09:22 CET 2016
#

from bob.pad.base.database import PadFile
import scipy.io.wavfile
import numpy


class PadVoiceFile(PadFile):
    """A simple base class that defines basic properties of File object for the use in PAD experiments"""

    def __init__(self, client_id, path, attack_type=None, file_id=None):
        """**Constructor Documentation**

        Initialize the Voice File object that can read WAV files.

        Parameters:

        For client_id, path, attack_type, and file_id, please refer
        to :py:class:`bob.pad.base.database.PadFile` constructor
        """
        super(PadVoiceFile, self).__init__(client_id, path, attack_type, file_id)

    def load(self, directory=None, extension='.wav'):
        path = self.make_path(directory, extension)
        rate, audio = scipy.io.wavfile.read(path)
        # We consider there is only 1 channel in the audio file => data[0]
        data = numpy.cast['float'](audio)
        return rate, data

VoicePadFile = PadVoiceFile
