""" Utility functions and classes for SRP

Context : SRP
Module  : Math
Version : 1.0.0
Author  : Stefano Covino
Date    : 25/06/2010
E-mail  : stefano.covino@brera.inaf.it
URL:    : http://www.merate.mi.astro.it/utenti/covino

Usage   : to be imported

Remarks :

History : (25/06/2010) First version.

"""

import numpy
from .CartesianVectorClass import CartesianVector


def FastAngularDistance (a1,l1,a2,l2):
    v = CartesianVector()
    v.from_s(1.0, numpy.radians(a1), numpy.radians(l1))
    v2 = CartesianVector()
    v2.from_s(1.0, numpy.radians(a2), numpy.radians(l2))
    d = v.dot(v2)
    c = v.cross(v2).mod

    res = numpy.arctan2(c, d)

    return numpy.degrees(res)

