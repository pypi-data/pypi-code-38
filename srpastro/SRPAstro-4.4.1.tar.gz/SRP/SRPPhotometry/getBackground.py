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
from astropy.stats import sigma_clip




def getBackground (table, x, y, rmin, rmax, sig=5.):
    if numpy.floor(x-rmax) < 1:
        xmin = 1
    else:
        xmin = int(numpy.floor(x-rmax))
    if numpy.ceil(x+rmax) > table.shape[1]:
        xmax = table.shape[1]
    else:
        xmax = int(numpy.ceil(x+rmax))
    if numpy.floor(y-rmax) < 1:
        ymin = 1
    else:
        ymin = int(numpy.floor(y-rmax))
    if numpy.ceil(y+rmax) > table.shape[0]:
        ymax = table.shape[0]
    else:
        ymax = int(numpy.ceil(y+rmax))
    field = table[ymin-1:ymax,xmin-1:xmax]
    #
    xf = numpy.arange(field.shape[1])
    xfn = numpy.arange(field.shape[0])
    yf = xfn[:,numpy.newaxis]
    #
    d = numpy.sqrt((x-(xf+xmin-0.5))**2 + (y-(yf+ymin-0.5))**2)
    l = field[(d >= rmin) & (d <= rmax)]
    ls = sigma_clip(l,sigma=sig)
    #
    mean = numpy.mean(ls)
    std = numpy.std(ls)
    return mean,std,std/numpy.sqrt(len(ls)),1.,len(ls)