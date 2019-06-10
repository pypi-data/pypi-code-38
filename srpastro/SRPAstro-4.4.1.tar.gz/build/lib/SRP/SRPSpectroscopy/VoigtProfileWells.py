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
from SRP.SRPSpectroscopy.VoigtFunctWells import VoigtFunctWells



def VoigtProfileWells(lambds,bpar,LambdCentr,DampCoeff,OscillStrength):
    coeffNum = 4 * math.sqrt(math.pi**3) * SS.ElectronCharge**2
    coeffDem = SS.ElectronMass * SS.SpeedofLight
    a = (LambdCentr * DampCoeff) / (4 * math.pi * bpar)
    fact = a * (coeffNum/coeffDem) * (OscillStrength/DampCoeff)     
    v = SS.SpeedofLight * (LambdCentr - lambds) / (LambdCentr * bpar)
    res = VoigtFunctWells(a,v)
    res = res * fact
    return res