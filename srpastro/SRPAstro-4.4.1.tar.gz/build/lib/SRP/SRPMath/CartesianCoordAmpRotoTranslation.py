""" Utility functions and classes for SRP

Context : SRP
Module  : Math.py
Version : 1.0.0
Author  : Stefano Covino
Date    : 03/09/2010
E-mail  : stefano.covino@brera.inaf.it
URL:    : http://www.merate.mi.astro.it/utenti/covino

Usage   : to be imported

Remarks :

History : (03/09/2010) First version.

"""


import math


def CartesianCoordAmpRotoTranslation (inpcoord,shift,rotangle,ampfct):
        xold = inpcoord[0]
        yold = inpcoord[1]
        xshift = shift[0]
        yshift = shift[1]
        angle = math.radians(rotangle)
#        xnew = (xshift + xold*math.cos(angle) - yold*math.sin(angle))*ampfct
#        ynew = (yshift + xold*math.sin(angle) + yold*math.cos(angle))*ampfct
        xnew = ((xold-xshift)*math.cos(angle) - (yold-yshift)*math.sin(angle))*ampfct
        ynew = ((xold-xshift)*math.sin(angle) + (yold-yshift)*math.cos(angle))*ampfct
        return xnew,ynew