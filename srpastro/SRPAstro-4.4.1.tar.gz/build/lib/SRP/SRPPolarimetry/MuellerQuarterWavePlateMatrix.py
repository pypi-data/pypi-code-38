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
from SRP.SRPPolarimetry.MuellerWavePlateMatrix import MuellerWavePlateMatrix
from SRP.SRPPolarimetry.MuellerRotationMatrix import MuellerRotationMatrix


#def MuellerQuarterWavePlateMatrix (angle=0.0):
#    m1 = MuellerRotationMatrix(angle)
#    m2 = MuellerWavePlateMatrix(math.radians(90.))
#    m3 = MuellerRotationMatrix(angle)
#    return m1*m2*m3


def MuellerQuarterWavePlateMatrix (angle=0.0):
    r1 = [1., 0., 0., 0.]
    r2 = [0., (numpy.cos(2*angle))**2, numpy.sin(2*angle)*numpy.cos(2*angle), numpy.sin(2*angle)]
    r3 = [0., numpy.sin(2*angle)*numpy.cos(2*angle), (numpy.sin(2*angle))**2, -numpy.cos(2*angle)]
    r4 = [0., -numpy.sin(2*angle), numpy.cos(2*angle), 0.]
    return numpy.matrix([r1, r2, r3, r4])