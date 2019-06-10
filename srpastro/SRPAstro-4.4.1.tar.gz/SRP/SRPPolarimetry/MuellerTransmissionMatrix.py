""" Utility functions and classes for SRP

Context : SRP
Module  : Polarimetry
Version : 1.0.0
Author  : Stefano Covino
Date    : 09/05/2017
E-mail  : stefano.covino@brera.inaf.it
URL:    : http://www.merate.mi.astro.it/utenti/covino

Usage   : to be imported

Remarks : from Ilyn (2017)
        : relative trasmitance for the two beams F = B/A

History : (09/05/2017) First version.

"""

import numpy as np


def MuellerTransmissionMatrix (T1=1.,T2=0.,ebeam=True):
    #
    #
    A = (T1 + T2)/2.
    #
    B = (T1 - T2)/2.
    #
    C = np.sqrt(T1*T2)
    #
    if ebeam:
        Bt = B
    else:
        Bt = -B
    #
    r1 = [A, Bt, 0., 0.]
    r2 = [Bt, A, 0., 0.]
    r3 = [0., 0., C, 0.]
    r4 = [0., 0., 0., C]
    #
    return np.matrix([r1, r2, r3, r4])
