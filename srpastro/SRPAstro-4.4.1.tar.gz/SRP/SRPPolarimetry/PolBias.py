""" Utility functions and classes for SRP

Context : SRP
Module  : Polarimetry
Version : 1.0.0
Author  : Stefano Covino
Date    : 16/07/2014
E-mail  : stefano.covino@brera.inaf.it
URL:    : http://www.merate.mi.astro.it/utenti/covino

Usage   : to be imported

Remarks : Correct the measures polarization in case of low S/N
            according to Plaszczynski et al., 2014, MNRAS 439, 4048.

History : (16/07/2014) First version.
"""

import numpy


def PolBias (p, ep):
    if ep <= 0:
        return p
    else:
        fact = 1.-numpy.exp(-(p/ep)**2)
        return (p - ep**2 * fact / (2*p))

