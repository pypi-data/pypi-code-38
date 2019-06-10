""" Utility functions and classes for SRP

Context : SRP
Module  : Stats.py
Version : 1.0.0
Author  : Stefano Covino
Date    : 22/06/2010
E-mail  : stefano.covino@brera.inaf.it
URL:    : http://www.merate.mi.astro.it/utenti/covino

Usage   : to be imported

Remarks : 

History : (22/06/2010) First version.

"""


import math, random


def AsymmetricGaussianDistrib(m,sl,sr):
    discrfactor = float(math.fabs(sl))/(float(math.fabs(sl))+float(math.fabs(sr)))
    trial1 = random.uniform(0.0,1.0)
    if trial1 < discrfactor:
        # left
        extrsigma = math.fabs(random.gauss(0,math.fabs(sl)))
        finpar = m-extrsigma
    else:
        # right
        extrsigma = math.fabs(random.gauss(0,math.fabs(sr)))
        finpar = m+extrsigma
    return finpar
