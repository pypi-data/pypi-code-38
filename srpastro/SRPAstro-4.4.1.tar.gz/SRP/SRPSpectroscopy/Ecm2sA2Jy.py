""" Utility functions and classes for SRP

Context : SRP
Module  : Spectroscopy.py
Version : 1.0.0
Author  : Stefano Covino
Date    : 23/10/2011
E-mail  : stefano.covino@brera.inaf.it
URL:    : http://www.merate.mi.astro.it/utenti/covino

Usage   : to be imported

Purpose : Convert Ergs/s cm2 A to Jy, lambda in micron.

History : (23/10/2011) First version.

"""


def Ecm2sA2Jy (fluden, lambd):
    return 3e41*fluden/(3e14/lambd)**2