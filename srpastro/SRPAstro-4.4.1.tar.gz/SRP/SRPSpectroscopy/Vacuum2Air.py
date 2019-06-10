""" Utility functions and classes for SRP

Context : SRP
Module  : Spectroscopy.py
Version : 1.0.0
Author  : Stefano Covino
Date    : 30/05/2010
E-mail  : stefano.covino@brera.inaf.it
URL:    : http://www.merate.mi.astro.it/utenti/covino

Usage   : to be imported

Remarks : An approximation to the 4th power of inverse wavenumber is used;	
        : See IUE Image Processing Manual   Page 6-15.
        : wavelength in Angstrom.

History : (30/05/2010) First version.

"""


def Vacuum2Air (vac):
    if vac < 2000.0:
        return vac
    else:
        return vac / (1.0 + 2.735182e-4 + 131.4182 / vac**2 + 2.76249e8 / vac**4)
    
