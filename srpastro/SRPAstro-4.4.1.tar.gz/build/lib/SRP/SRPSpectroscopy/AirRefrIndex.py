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
        :   Formula gives: [(n(l)-1]/[n(1)-1)]
        :   l (micron)

History : (23/08/2012) First version.

"""


def AirRefrIndex (l):
    return 0.23465 + 1.076e2/(146-l**-2) + 0.93161/(41 - l**-2)
