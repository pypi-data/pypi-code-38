""" Utility functions and classes for SRP

Context : SRP
Module  : Spectroscopy.py
Version : 1.0.1
Author  : Stefano Covino
Date    : 26/05/2017
E-mail  : stefano.covino@brera.inaf.it
URL:    : http://www.merate.mi.astro.it/utenti/covino

Usage   : to be imported

History : (03/09/2011) First version.
        : (26/05/2017) Minor update.
"""

import SRP.SRPSpectroscopy as SS

def LymAlphaDumpConst (gu=3.0,gl=1.0):
    return 3 * (gl/gu) * SS.AbsOscillStrength * SS.ClassLymAlphaDumpConst

