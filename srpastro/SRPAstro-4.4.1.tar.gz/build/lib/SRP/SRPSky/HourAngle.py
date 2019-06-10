""" Utility functions and classes for SRP

Context : SRP
Module  : Math.py
Version : 1.0.0
Author  : Stefano Covino
Date    : 09/02/2012
E-mail  : stefano.covino@brera.inaf.it
URL:    : http://www.merate.mi.astro.it/utenti/covino

Usage   : to be imported

Remarks : site should be valid pyephem site object. RA in degrees.

History : (09/02/2012) First version.

"""

import ephem
import math
from SRP.SRPSky.SiderealTime import SiderealTime


def HourAngle (ra,site):
    st = ephem.degrees(SiderealTime(site))
    return math.degrees(float(st))-ra
