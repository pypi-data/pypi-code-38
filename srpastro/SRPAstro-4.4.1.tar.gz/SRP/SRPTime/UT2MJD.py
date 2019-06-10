""" Utility functions and classes for SRP

Context : SRP
Module  : Time
Version : 1.0.0
Author  : Stefano Covino
Date    : 27/09/2012
E-mail  : stefano.covino@brera.inaf.it
URL:    : http://www.merate.mi.astro.it/utenti/covino

Usage   : to be imported

Remarks :

History : (27/09/2012) First version.

"""

import SRP.SRPTime as SST
import SRP.TimeAstro_algs as TimeAstro_algs


def UT2MJD (y,mo,d,h,mi,s):
    ltime = y,mo,d,h,mi,s
    jd = TimeAstro_algs.to_julian(ltime)
    return jd - SST.JD2MJD


