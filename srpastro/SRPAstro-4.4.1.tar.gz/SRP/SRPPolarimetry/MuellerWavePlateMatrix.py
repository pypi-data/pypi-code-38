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
            

History : (29/02/2012) First version.

"""

import math
import numpy


def MuellerWavePlateMatrix (angle=0.0):
    r1 = [1., 0., 0., 0.]
    r2 = [0., 1.0, 0., 0.]
    r3 = [0., 0., math.cos(angle), -math.sin(angle)]
    r4 = [0., 0., math.sin(angle), math.cos(angle)]
    return numpy.matrix([r1, r2, r3, r4])
