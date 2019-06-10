""" Utility functions and classes for SRP

Context : SRP
Module  : Polarimetry
Version : 1.0.0
Author  : Stefano Covino
Date    : 29/02/2012
E-mail  : stefano.covino@brera.inaf.it
URL:    : http://www.merate.mi.astro.it/utenti/covino

Usage   : to be imported

Remarks : angle is in radians
            

History : (22/05/2015) First version.

"""

import math
import numpy


def MuellerPolarizerMatrix (angle, eff=1.0):
    C = numpy.cos(2*angle)
    S = numpy.sin(2*angle)
    r1 = [1., eff*C, eff*S, 0.]
    r2 = [eff*C, eff*C**2, eff*C*S, 0.]
    r3 = [eff*S, eff*C*S, eff*S**2, 0.]
    r4 = [0., 0., 0., 0.]
    return 0.5*numpy.matrix([r1, r2, r3, r4])
