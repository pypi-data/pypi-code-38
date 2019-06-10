""" Utility functions and classes for SRP

Context : SRP
Module  : System.py
Version : 1.0.0
Author  : Stefano Covino
Date    : 05/02/2011
E-mail  : stefano.covino@brera.inaf.it
URL:    : http://www.merate.mi.astro.it/utenti/covino

Usage   : to be imported

Remarks :

History : (05/02/2012) First version.

"""


import SRP

def SRPPath():
    for i in SRP.__path__:
        if i.find('Astro.') < 0:
            return i
    return None
