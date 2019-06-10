""" Utility functions and classes for SRP

Context : SRP
Module  : Spectroscopy.py
Version : 1.1.0
Author  : Stefano Covino
Date    : 15/11/2013
E-mail  : stefano.covino@brera.inaf.it
URL:    : http://www.merate.mi.astro.it/utenti/covino

Usage   : to be imported

History : (21/03/2011) First version.
        : (16/06/2011) Lower limit put at 0.07 micron, while in the
            original paper it was at 0.08.
        : (15/11/2013) R can be varied.

"""


from . import ExtConstants
from .CalzettiExt import CalzettiExt
import numpy


def getAbs (ebv,glxy,lmbd, R=None):
    if not glxy in list(ExtConstants.ExtCurDict.keys()):
        return None
    else:
        if glxy == ExtConstants.SB:
            return CalzettiExt(lmbd)*ebv
        else:
            csi = 0.0
            for i in range(len(ExtConstants.ai)):
                csi = csi + ExtConstants.ai[i][glxy]/(pow(lmbd/ExtConstants.li[i][glxy],ExtConstants.ni[i][glxy])
                    + pow(ExtConstants.li[i][glxy]/lmbd,ExtConstants.ni[i][glxy]) + ExtConstants.bi[i][glxy])
            if R == None:
                return numpy.where(lmbd < 0.07, -1.0, csi * (ebv * (1+ExtConstants.ExtRDict[glxy])))
            else:
                return numpy.where(lmbd < 0.07, -1.0, csi * (ebv * (1+R)))
