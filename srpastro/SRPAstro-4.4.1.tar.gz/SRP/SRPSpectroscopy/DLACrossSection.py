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

import math
from SRP.SRPSpectroscopy.LymAlphaDumpConst import LymAlphaDumpConst
import SRP.SRPSpectroscopy as SS


def DLACrossSection (nu):
    num1 = 3 * SS.LambdaLymanAlpha**2 * SS.AbsOscillStrength * SS.ClassLymAlphaDumpConst
    den1 = 8 * math.pi
    num2 = LymAlphaDumpConst() * (nu/SS.NuLymanAlpha)**4
    den2 = 4 * math.pi**2 * (nu - SS.NuLymanAlpha)**2 + (LymAlphaDumpConst()**2 * (nu/SS.NuLymanAlpha)**6)/4.0
    return (num1*num2)/(den1*den2)
