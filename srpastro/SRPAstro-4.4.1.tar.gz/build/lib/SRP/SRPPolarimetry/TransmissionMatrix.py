""" Utility functions and classes for SRP

Context : SRP
Module  : Polarimetry
Version : 1.0.0
Author  : Stefano Covino
Date    : 21/02/2012
E-mail  : stefano.covino@brera.inaf.it
URL:    : http://www.merate.mi.astro.it/utenti/covino

Usage   : to be imported

Remarks : angle is in radians
            From Witzel et al., A&A, 2011.

History : (21/02/2012) First version.

"""

import math
import numpy


def TransmissionMatrix (ordtr=1.0,extrtr=1.0):
    #
    Tp = ordtr+extrtr
    Tm = extrtr-ordtr
    Tden = Tp**2-Tm**2
    fp = Tp/Tden
    fm = Tm/Tden
    #
    r1 = [fp, -fm, 0., 0.]
    r2 = [-fm, fp, 0., 0.]
    r3 = [-fm, Tm*fm/Tp, 1./Tp, 0.]
    r4 = [-fm, Tm*fm/Tp, 0., 1./Tp]
    return 2*ordtr*extrtr*numpy.matrix([r1, r2, r3, r4])
