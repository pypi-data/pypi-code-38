""" Utility functions and classes for SRP

Context : SRP
Module  : Polarimetry
Version : 1.0.0
Author  : Stefano Covino
Date    : 20/08/2017
E-mail  : stefano.covino@brera.inaf.it
URL:    : http://www.merate.mi.astro.it/utenti/covino

Usage   : to be imported

Remarks : Compute the polarisation limits in case of low S/N
            according to Plaszczynski et al., 2014, MNRAS 439, 4048.

History : (20/08/2018) First version.
"""

import numpy as np


def PolBiasLims (p, conf='68'):
    if conf == '68':
        pa = 1.0
        betam = 0.72
        gammam = 0.60
        omegam = -0.83
        phim = 4.41
        #
        betaM = 0.97
        gammaM = 2.01
    elif conf=='90':
        pa = 1.64
        betam = 0.88
        gammam = 0.68
        omegam = 2.03
        phim = -0.76
        #
        betaM = 0.31
        gammaM = 2.25
    elif conf=='95':
        pa = 1.95
        betam = 0.56
        gammam = 0.48
        omegam = 1.79
        phim = -1.03
        #
        betaM = 0.22
        gammaM = 2.54
    #
    pmin = p - pa*(1+betam*np.exp(-gammam*p)*np.sin(omegam*p+phim))
    pmax = p + pa*(1-betaM*np.exp(-gammaM*p))
    #
    return pmin,pmax



