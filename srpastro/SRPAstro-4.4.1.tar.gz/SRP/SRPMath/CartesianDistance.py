""" Utility functions and classes for SRP

Context : SRP
Module  : Math.py
Version : 1.0.0
Author  : Stefano Covino
Date    : 08/11/2010
E-mail  : stefano.covino@brera.inaf.it
URL:    : http://www.merate.mi.astro.it/utenti/covino

Usage   : to be imported

Remarks :

History : (08/11/2010) First version.

"""


import math


def CartesianDistance (fcoord, scoord):
    sqdist = (fcoord[0]-scoord[0])**2 + (fcoord[1]-scoord[1])**2
    return math.sqrt(sqdist)
    
    