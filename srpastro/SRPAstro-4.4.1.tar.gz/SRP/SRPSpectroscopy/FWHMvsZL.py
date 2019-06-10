""" Utility functions and classes for SRP

Context : SRP
Module  : Spectroscopy.py
Version : 1.0.0
Author  : Stefano Covino
Date    : 27/10/2011
E-mail  : stefano.covino@brera.inaf.it
URL:    : http://www.merate.mi.astro.it/utenti/covino

Usage   : to be imported

Purpose : Compute how FWHM varies with zenith distance and wavelength.

History : (27/10/2011) First version.

"""


def FWHMvsZL (fwhm, airm=1.0, lambd=0.527):
    firststep = fwhm / airm**(0.6)
    return firststep * (0.527/lambd)**-0.2
    
