""" Utility functions and classes for SRP

Context : SRP
Module  : Math.py
Version : 1.0.0
Author  : Stefano Covino
Date    : 02/09/2013
E-mail  : stefano.covino@brera.inaf.it
URL:    : http://www.merate.mi.astro.it/utenti/covino

Usage   : to be imported

Remarks : input parameters in degrees

History : (02/09/2013) First version.

"""

import numpy


# Earth rotation rate deg/sec
ERR = 4.178e-3


def AzimuthRate (dec,parang,alt):
    f1 = numpy.cos(numpy.radians(dec))
    f2 = numpy.cos(numpy.radians(parang))
    f3 = numpy.cos(numpy.radians(alt))
    return ERR*f1*f2/f3


