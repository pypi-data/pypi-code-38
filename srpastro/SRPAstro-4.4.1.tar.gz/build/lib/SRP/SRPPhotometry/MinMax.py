""" Utility functions and classes for SRP

Context : SRP
Module  : Photometry
Version : 1.0.0
Author  : Stefano Covino
Date    : 13/11/2015
E-mail  : stefano.covino@brera.inaf.it
URL:    : http://www.merate.mi.astro.it/utenti/covino

Usage   : to be imported

Remarks : 
    
History : (13/11/2015) First version.

"""

import numpy


def MinMax (table, x, y, r):
    if numpy.floor(x-r) < 1:
        xmin = 1
    else:
        xmin = int(numpy.floor(x-r))
    if numpy.ceil(x+r) > table.shape[1]:
        xmax = table.shape[1]
    else:
        xmax = int(numpy.ceil(x+r))
    if numpy.floor(y-r) < 1:
        ymin = 1
    else:
        ymin = int(numpy.floor(y-r))
    if numpy.ceil(y+r) > table.shape[0]:
        ymax = table.shape[0]
    else:
        ymax = int(numpy.ceil(y+r))
    #
    field = table[(ymin-1):ymax,(xmin-1):xmax]
    #
    maxf = field.max()
    minf = field.min()
    cMy,cMx = numpy.unravel_index(field.argmax(), field.shape)
    cmy,cmx = numpy.unravel_index(field.argmin(), field.shape)
    #
    return minf, maxf, (cmx+xmin,cmy+ymin), (cMx+xmin,cMy+ymin)

