""" Utility functions and classes for SRP

Context : SRP
Module  : Math.py
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

def BiGauss (data,x0,y0,A,sx,sy,B):
    x = numpy.arange(data.shape[1])
    xn = numpy.arange(data.shape[0])
    y = xn[:,numpy.newaxis]
    return A*numpy.exp( (-(x-x0)**2)/(2*sx**2) + (-(y-y0)**2)/(2*sy**2) ) + B