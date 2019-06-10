""" Utility functions and classes for SRP

Context : SRP
Module  : Math
Version : 1.0.0
Author  : Stefano Covino
Date    : 18/11/2014
E-mail  : stefano.covino@brera.inaf.it
URL:    : http://www.merate.mi.astro.it/utenti/covino

Usage   : to be imported

Remarks : Angle in radians.

History : (18/11/2014) First version.

"""


import numpy



def DopplerFactor (Gamma, Theta):
    Beta = numpy.sqrt((Gamma**2 - 1.)/Gamma**2)
    return 1./(Gamma * (1.-Beta*numpy.cos(Theta)))



