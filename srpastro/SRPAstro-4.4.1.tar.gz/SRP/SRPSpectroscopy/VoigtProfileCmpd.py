""" Utility functions and classes for SRP

Context : SRP
Module  : Spectroscopy.py
Version : 1.0.0
Author  : Stefano Covino
Date    : 05/09/2011
E-mail  : stefano.covino@brera.inaf.it
URL:    : http://www.merate.mi.astro.it/utenti/covino

Usage   : to be imported

History : (05/09/2011) First version.

"""

import math
import SRP.SRPSpectroscopy as SS
from SRP.SRPSpectroscopy.VoigtFunctApprox import VoigtFunctApprox
from SRP.SRPSpectroscopy.VoigtFunctTG import VoigtFunctTG
from SRP.SRPSpectroscopy.VoigtFunct import VoigtFunct



def VoigtProfileCmpd (lambd,bpar,LambdCentr,DampCoeff,OscillStrength):
    coeffNum = 4 * math.sqrt(math.pi**3) * SS.ElectronCharge**2
    coeffDem = SS.ElectronMass * SS.SpeedofLight
    v = SS.SpeedofLight * (LambdCentr - lambd) / (LambdCentr * bpar)
    a = (LambdCentr * DampCoeff) / (4 * math.pi * bpar)
    fact = a * (coeffNum/coeffDem) * (OscillStrength/DampCoeff) 
    if -0.5 <= v <= 0.5:
        res = fact * VoigtFunctApprox (a,v)
#        print "A", "l", lambd*1e8, "a", a, "v", v, "res", res
    elif -4.5 < v < 4.5:
        res = fact * VoigtFunctTG (a,v)
#        print "TG", "l", lambd*1e8, "a", a, "v", v, "res", res
    else:
        res = fact * VoigtFunct (a,v)
#        print "INT", "l", lambd*1e8, "a", a, "v", v, "res", res
    return res