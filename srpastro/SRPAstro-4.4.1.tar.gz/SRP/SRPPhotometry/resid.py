""" Utility functions and classes for SRP

Context : SRP
Module  : Photometry
Version : 1.0.0
Author  : Stefano Covino
Date    : 10/11/2015
E-mail  : stefano.covino@brera.inaf.it
URL:    : http://www.merate.mi.astro.it/utenti/covino

Usage   : to be imported

Remarks : 
    
History : (10/11/2015) First version.

"""

import numpy
from SRP.SRPMath.BiGauss import BiGauss



def resid (pars,field):
    x0 = pars[0]
    y0 = pars[1]
    A = pars[2]
    sx = numpy.abs(pars[3])
    sy = numpy.abs(pars[4])
    B = pars[5]
    if x0 < 0.0:
        x0 = 0.0
    elif x0 > field.shape[1]:
        x0 = field.shape[1]
    if y0 < 0.0:
        y0 = 0.0
    elif y0 > field.shape[0]:
        y0 = field.shape[0]
    #
    y = BiGauss(field,x0,y0,A,sx,sy,B)
    restot = ((y-field)**2).sum()
    return restot
