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
from SRP.SRPPhotometry.resid import resid



def centerGauss (table, x, y, r):
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
    field = table[(ymin-1):ymax,(xmin-1):xmax]
    init = [x-xmin,y-ymin,field[int(y-ymin),int(x-xmin)],r,r,field[0,0]]
    pars = fmin (resid, init, args=(field,), maxfun=10000, maxiter=10000, disp=0)
    return pars[0]+xmin-1, pars[1]+ymin-1, pars[2], 2.35*pars[3], 2.35*pars[4], pars[5]
