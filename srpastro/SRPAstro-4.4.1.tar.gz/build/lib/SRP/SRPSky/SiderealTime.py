""" Utility functions and classes for SRP

Context : SRP
Module  : Math.py
Version : 1.0.0
Author  : Stefano Covino
Date    : 08/02/2012
E-mail  : stefano.covino@brera.inaf.it
URL:    : http://www.merate.mi.astro.it/utenti/covino

Usage   : to be imported

Remarks : site should be valid pyephem site object.

History : (08/02/2012) First version.

"""

import math
import ephem



def SiderealTime (site):
    return site.sidereal_time()