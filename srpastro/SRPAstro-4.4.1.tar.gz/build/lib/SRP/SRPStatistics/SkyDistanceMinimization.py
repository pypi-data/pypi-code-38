""" Utility functions and classes for SRP

Context : SRP
Module  : Stats.py
Version : 1.0.1
Author  : Stefano Covino
Date    : 16/05/2017
E-mail  : stefano.covino@brera.inaf.it
URL:    : http://www.merate.mi.astro.it/utenti/covino

Usage   : to be imported

Remarks : 

History : (24/00/2010) First version.
        : (16/05/2017) Minor update.
"""


import math
import numpy
import scipy.optimize as so

import astLib.astCoords as aLaC

from SRPFITS.Frames.Pixel2WCS import Pixel2WCS


def SkyDistSum (pars, oldvars, newvars, head):
    tot = 0.0
    head.UpgradeWCSHeader(pars)
    newc = Pixel2WCS(head.FitsFrame.Header,oldvars)
    for i,l in zip(newc,newvars):
        tot = tot + (aLaC.calcAngSepDeg(i[0],i[1],l[0],l[1]))*3600.0
    return tot


def SkyDistanceMinimization (guessparset, oldcoord, refcoord, head):
    rc = numpy.array(refcoord)
    oc = numpy.array(oldcoord)
    xopt = so.fmin(SkyDistSum, guessparset, args=(oc,rc,head), disp=0)
    return xopt, SkyDistSum(xopt,oc,rc,head)/len(oc)

