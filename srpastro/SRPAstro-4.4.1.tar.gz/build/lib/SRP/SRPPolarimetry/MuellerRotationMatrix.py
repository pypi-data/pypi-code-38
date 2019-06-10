""" Utility functions and classes for SRP

Context : SRP
Module  : Polarimetry
Version : 1.0.1
Author  : Stefano Covino
Date    : 08/11/2016
E-mail  : stefano.covino@brera.inaf.it
URL:    : http://www.merate.mi.astro.it/utenti/covino

Usage   : to be imported

Remarks : angle is in radians
            From Joos et al., SPIE, 7016

History : (04/02/2012) First version.
        : (08/11/2016) numpy instead of math

"""

import numpy as np


def MuellerRotationMatrix (angle=np.radians(0.0)):
    r1 = [1., 0., 0., 0.]
    r2 = [0., np.cos(2*angle), np.sin(2*angle), 0.]
    r3 = [0., -np.sin(2*angle), np.cos(2*angle), 0.]
    r4 = [0., 0., 0., 1.]
    return np.matrix([r1, r2, r3, r4])
