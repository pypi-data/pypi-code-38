""" Utility functions and classes for SRP

Context : SRP
Module  : Math
Version : 1.0.0
Author  : Stefano Covino
Date    : 25/06/2010
E-mail  : stefano.covino@brera.inaf.it
URL:    : http://www.merate.mi.astro.it/utenti/covino

Usage   : to be imported

Remarks :

History : (25/06/2010) First version.

"""

import math
import ephem



def AngularDistance (fcoord, scoord):
    ra1 = ephem.degrees(str(fcoord[0]))
    dec1 = ephem.degrees(str(fcoord[1]))
    ra2 = ephem.degrees(str(scoord[0]))
    dec2 = ephem.degrees(str(scoord[1]))
    separation = ephem.separation((ra1,dec1),(ra2,dec2))
    return math.degrees(separation)