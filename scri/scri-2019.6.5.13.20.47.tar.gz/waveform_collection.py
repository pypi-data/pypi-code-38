# Copyright (c) 2018, Michael Boyle
# See LICENSE file for details: <https://github.com/moble/scri/blob/master/LICENSE>

from __future__ import print_function, division, absolute_import

from . import (Inertial, WaveformModes, SpinWeights, h, sigma, psi0, psi1, psi2, psi3)
from .waveform_base import WaveformBase, waveform_alterations


# class WaveformCollection(object):
#     """A collection of waveforms to be treated uniformly

#     This is a simple container that collects several Waveform objects.  They are all required to 

#     """
#     def __init__(self, *args, **kwargs):
        
