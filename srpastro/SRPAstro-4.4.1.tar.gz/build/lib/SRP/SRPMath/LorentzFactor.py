""" Utility functions and classes for SRP

Context : SRP
Module  : Math
Version : 1.0.0
Author  : Stefano Covino
Date    : 18/11/2014
E-mail  : stefano.covino@brera.inaf.it
URL:    : http://www.merate.mi.astro.it/utenti/covino

Usage   : to be imported

Remarks :

History : (18/11/2014) First version.

"""


import numpy



def LorentzFactor (Beta):
    Beta = 1./numpy.sqrt(1-Beta**2)
    return Beta



