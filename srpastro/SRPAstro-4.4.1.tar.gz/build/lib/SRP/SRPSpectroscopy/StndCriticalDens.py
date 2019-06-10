""" Utility functions and classes for SRP

Context : SRP
Module  : Spectroscopy.py
Version : 1.0.0
Author  : Stefano Covino
Date    : 03/09/2011
E-mail  : stefano.covino@brera.inaf.it
URL:    : http://www.merate.mi.astro.it/utenti/covino

Usage   : to be imported

History : (03/09/2011) First version.

"""

import math
import SRP.SRPSpectroscopy as SS


def StndCriticalDens (H0=71.0):
    return (3 * (H0*0.1/SS.Parsec)**2) / (8 * math.pi * SS.GravitationalConst)
