""" Utility functions and classes for SRP

Context : SRP
Module  : Spectroscopy.py
Version : 1.0.0
Author  : Stefano Covino
Date    : 23/08/2012
E-mail  : stefano.covino@brera.inaf.it
URL:    : http://www.merate.mi.astro.it/utenti/covino

Usage   : to be imported

Remarks : See Hayes & Latham (1975, ApJ, 197, 593) for the formulas used.
        :   h (km), l (micron)

History : (23/08/2012) First version.

"""

import numpy
from .AirRefrIndex import AirRefrIndex

LowerTrophosphereScaleHeigh = 7.996


def RayleighScattering (l, h):
    return 9.4977e-3 * l**-4 * AirRefrIndex(l)**2 * numpy.exp(-h/LowerTrophosphereScaleHeigh)
    
