""" Utility functions and classes for SRP

Context : SRP
Module  : Photometry
Version : 1.0.0
Author  : Stefano Covino
Date    : 15/02/2012
E-mail  : stefano.covino@brera.inaf.it
URL:    : http://www.merate.mi.astro.it/utenti/covino

Usage   : to be imported

Remarks : 
    
History : (15/02/2012) First version.

"""

import math
import numpy


def Counts2Mag (cnt, ecnt, zp=0.0):
    mag = -2.5*numpy.log10(numpy.array(cnt)) + zp
    emag = (2.5/math.log(10))*(numpy.array(ecnt)/numpy.array(cnt))
    return mag, emag