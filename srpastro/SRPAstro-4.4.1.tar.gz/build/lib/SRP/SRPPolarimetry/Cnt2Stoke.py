""" Utility functions and classes for SRP

Context : SRP
Module  : Polarimetry
Version : 1.0.0
Author  : Stefano Covino
Date    : 18/09/2017
E-mail  : stefano.covino@brera.inaf.it
URL:    : http://www.merate.mi.astro.it/utenti/covino

Usage   : to be imported

Remarks : angles are in radians

History : (18/09/2017) First version.
"""

import numpy as np


def Cnt2Stoke (co,eco,ce,ece):
    s = (co-ce)/(co+ce)
    es = abs(s) * np.sqrt( ((eco**2+ece**2)/(co-ce)**2) + ((eco**2+ece**2)/(co+ce)**2) )
    return s,es
