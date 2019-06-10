""" Utility functions and classes for SRP

Context : SRP
Module  : Spectroscopy.py
Version : 1.0.0
Author  : Stefano Covino
Date    : 21/03/2011
E-mail  : stefano.covino@brera.inaf.it
URL:    : http://www.merate.mi.astro.it/utenti/covino

Usage   : to be imported

Remarks : See Calzetti et al.

History : (21/03/2011) First version.

"""


from . import ExtConstants
import numpy


def CalzettiExt (l,R=4.05):
    return numpy.where(l<0.12, -1, 
        numpy.where(l < 0.63, 2.659*(-2.156 + 1.509/l - 0.198/l**2 + 0.011/l**3) + R,
            numpy.where(l <= 2.2, 2.659*(-1.857 + 1.040/l) + R, 1.0)))

