""" Utility functions and classes for SRP

Context : SRP
Module  : Math.py
Version : 1.0.0
Author  : Stefano Covino
Date    : 30/08/2013
E-mail  : stefano.covino@brera.inaf.it
URL:    : http://www.merate.mi.astro.it/utenti/covino

Usage   : to be imported

Remarks : input parameters in degrees

History : (30/08/2013) First version.

"""

import numpy


# Earth rotation rate deg/sec
ERR = 4.178e-3


def ParallacticAngleRate (lat,az,alt):
    f1 = numpy.cos(numpy.radians(lat))
    f2 = numpy.cos(numpy.radians(az))
    f3 = numpy.cos(numpy.radians(alt))
    return -ERR*f1*f2/f3


