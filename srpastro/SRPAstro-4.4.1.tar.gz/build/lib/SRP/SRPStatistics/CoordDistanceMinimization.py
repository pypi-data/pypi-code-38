""" Utility functions and classes for SRP

Context : SRP
Module  : Stats.py
Version : 1.0.0
Author  : Stefano Covino
Date    : 04/09/2010
E-mail  : stefano.covino@brera.inaf.it
URL:    : http://www.merate.mi.astro.it/utenti/covino

Usage   : to be imported

Remarks : 

History : (04/00/2010) First version.

"""


import math
import numpy
import scipy.optimize as so

from SRP.SRPMath.CartesianCoordAmpRotoTranslation import CartesianCoordAmpRotoTranslation

# vars
#   0 x,y
#   1 rx,ry
# pars
#   0   xshift
#   1   yshift
#   2   rotangle
#   3   amplfactor

def SquareDistSum (parms, oldvars, newvars):
    tot = 0.0
    for i,l in zip(oldvars,newvars):
        newc = CartesianCoordAmpRotoTranslation((i[0],i[1]),(parms[0],parms[1]),parms[2],math.fabs(parms[3]))
#        print i, newc, l
        tot = tot + math.sqrt((l[0]-newc[0])**2 + (l[1]-newc[1])**2)
    return tot


def CoordDistanceMinimization (refcoord, oldcoord, guessparset):
    rc = numpy.array(refcoord)
    oc = numpy.array(oldcoord)
    xopt = so.fmin(SquareDistSum, guessparset, args=(oc,rc), disp=0)
    return xopt, SquareDistSum(xopt,oc,rc)/len(oc)
    
