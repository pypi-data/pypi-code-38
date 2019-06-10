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
import SRP.SRPSpectroscopy as SS
from SRP.SRPSpectroscopy.StndCriticalDens import StndCriticalDens



def TauGP (z,H0=71.0,OmBaryon=0.04,Yprim=0.24,OmMatt=0.28):
    num1 = 3 * SS.AbsOscillStrength * SS.ClassLymAlphaDumpConst * SS.LambdaLymanAlpha**3
    num2 = StndCriticalDens(H0) * OmBaryon * (1-Yprim)
    dem1 = 8 * math.pi * SS.ProtonMass * (H0*0.1/SS.Parsec) * OmMatt**0.5
    return num1 * num2 * (1+z)**1.5 / dem1
    

