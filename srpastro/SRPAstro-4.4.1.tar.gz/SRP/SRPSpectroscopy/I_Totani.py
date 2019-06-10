""" Utility functions and classes for SRP

Context : SRP
Module  : Spectroscopy.py
Version : 1.0.0
Author  : Stefano Covino
Date    : 03/09/2011
E-mail  : stefano.covino@brera.inaf.it
URL:    : http://www.merate.mi.astro.it/utenti/covino

Usage   : to be imported

History : (03/09/2011) First version.

"""

import math


# Holds if z_obs - z_IGM,u >> R_alpha (1+z_obs)
def I_Totani(x):
    f1 = x**4.5/(1.0-x)
    f2 = 9.0*x**3.5/7.0
    f3 = 9*x**2.5/5.0
    f4 = 3*x**1.5
    f5 = 9*x**0.5
    f6 = -9.0*(math.log((1+x**0.5)/(1-x**0.5)))/2.0
    return f1+f2+f3+f4+f5+f6

