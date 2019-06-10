""" Utility functions and classes for SRP

Context : SRP
Module  : Math.py
Version : 1.0.0
Author  : Stefano Covino
Date    : 27/11/2015
E-mail  : stefano.covino@brera.inaf.it
URL:    : http://www.merate.mi.astro.it/utenti/covino

Usage   : to be imported

Remarks :

History : (27/11/2015) First version.

"""


import numpy



def findPercArea (x,y,r,xp,yp,ntrial=10000):
    #
    xpp = numpy.random.uniform(xp-1,xp,ntrial)
    ypp = numpy.random.uniform(yp-1,yp,ntrial)
    #
    dist = numpy.sqrt((x-xpp)**2+(y-ypp)**2)
    l = dist[dist <= r]
    #
    return float(len(l))/ntrial


