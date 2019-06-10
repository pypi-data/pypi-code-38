""" Utility functions and classes for SRP

Context : SRP
Module  : Spectroscopy.py
Version : 1.0.0
Author  : Stefano Covino
Date    : 19/03/2011
E-mail  : stefano.covino@brera.inaf.it
URL:    : http://www.merate.mi.astro.it/utenti/covino

Usage   : to be imported

History : (19/03/2011) First version.

"""

import math
import scipy.integrate
from .VoigtIntegrand import VoigtIntegrand


def VoigtFunct (a,v):
    int = scipy.integrate.quad(VoigtIntegrand,-scipy.integrate.Inf,+scipy.integrate.Inf,args=(a,v),epsrel=1e-5)
    return (a/math.pi) * int[0]
    