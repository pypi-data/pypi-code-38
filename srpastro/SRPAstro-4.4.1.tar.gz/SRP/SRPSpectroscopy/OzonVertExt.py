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
        :   KOz (cm^-1), TOz (atm cm)

History : (23/08/2012) First version.

"""


def OzonVertExt (KOz, TOz):
    return 1.11 * TOz * KOz
