""" Utility functions and classes for SRP

Context : SRP
Module  : Spectroscopy.py
Version : 1.0.0
Author  : Stefano Covino
Date    : 30/05/2010
E-mail  : stefano.covino@brera.inaf.it
URL:    : http://www.merate.mi.astro.it/utenti/covino

Usage   : to be imported

Remarks : See Morton (Ap. J. Suppl. 77, 119) for the formula used

History : (30/05/2010) First version.

"""

def Air2Vacuum (air):
        if air < 2000:
            return air
        else:
            sigma2 = 1.0/air**2
            fact = 1.0 + 6.4328e-5 + 2.94981e-2/(146.0 - sigma2) + 2.5540e-4/( 41.0 - sigma2)
            return air*fact