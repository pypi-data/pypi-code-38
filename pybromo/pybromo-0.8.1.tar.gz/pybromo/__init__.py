#
# PyBroMo - A single molecule diffusion simulator in confocal geometry.
#
# Copyright (C) 2013-2015 Antonino Ingargiola tritemio@gmail.com
#

from ._version import get_versions
__version__ = get_versions()['version']
del get_versions

from . import loadutils as lu
from . import diffusion
from . import timestamps
from . import plot
from . import plotter

from .utils import hdf5

from .diffusion import Box, Particles, ParticlesSimulation, hashfunc
from .psflib import GaussianPSF, NumericPSF
from .timestamps import TimestampSimulation

import warnings


def deprecation(message):
    warnings.warn(message, FutureWarning, stacklevel=2)


def hash_(x):
    deprecation('The function `hash_` is deprecated, please use `hashfunc` instead.')
    return hashfunc(x)
