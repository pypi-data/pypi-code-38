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
from SRP.SRPSpectroscopy.I_Totani import I_Totani
from SRP.SRPSpectroscopy.Ralpha import Ralpha
from SRP.SRPSpectroscopy.TauGP import TauGP



def TauIGM(lambd,xHI,zIGMl,zIGMu):
    zHost = 1.0
    zObs = lambd/SS.LambdaLymanAlpha - 1.0
    f1 = xHI * Ralpha() * TauGP(zHost) / math.pi
    f2 = ((1+zObs)/(1+zHost))**1.5
    f3 = I_Totani((1+zIGMu)/(1+zObs))-I_Totani((1+zIGMl)/(1+zObs))
    return f1*f2*f3
