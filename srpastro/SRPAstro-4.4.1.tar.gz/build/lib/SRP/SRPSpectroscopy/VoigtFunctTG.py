""" Utility functions and classes for SRP

Context : SRP
Module  : Spectroscopy.py
Version : 1.0.0
Author  : Stefano Covino
Date    : 05/09/2011
E-mail  : stefano.covino@brera.inaf.it
URL:    : http://www.merate.mi.astro.it/utenti/covino

Usage   : to be imported

History : (05/09/2011) First version.

"""


import math 


def VoigtFunctTG (a,v):
    F = v**2
    H0 = math.exp(-F)
    Q = 1.5*F
    res1 = H0
    res2 = a/(math.pi**0.5 * F)
    res3 = H0**2 * (4*F*F + 7*F + 4 + Q) - Q - 1
    return res1-res2*res3

