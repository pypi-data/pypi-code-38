""" Utility functions and classes for SRP

Context : SRP
Module  : Spectroscopy.py
Version : 1.0.0
Author  : Stefano Covino
Date    : 19/03/2011
E-mail  : stefano.covino@brera.inaf.it
URL:    : http://www.merate.mi.astro.it/utenti/covino

Usage   : to be imported

History : (19/03/2011) First version.

"""

import math

def VoigtIntegrand (y,a,v):
    num = math.e**(-y**2)
    dem = a**2 + (v-y)**2
    return num/dem
    