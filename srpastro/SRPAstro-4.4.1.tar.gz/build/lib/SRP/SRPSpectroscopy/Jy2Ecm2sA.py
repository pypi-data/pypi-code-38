""" Utility functions and classes for SRP

Context : SRP
Module  : Spectroscopy.py
Version : 1.0.0
Author  : Stefano Covino
Date    : 23/10/2011
E-mail  : stefano.covino@brera.inaf.it
URL:    : http://www.merate.mi.astro.it/utenti/covino

Usage   : to be imported

Purpose : Convert Jy to Ergs/s cm2 A, lambda in micron.

History : (23/10/2011) First version.

"""


def Jy2Ecm2sA (fluden, lambd):
    return fluden*3e-5/(lambd*1e4)**2