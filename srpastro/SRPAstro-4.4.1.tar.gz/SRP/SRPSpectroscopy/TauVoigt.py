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

from SRP.SRPSpectroscopy.Transitions import *
from SRP.SRPSpectroscopy.VoigtProfileWells import VoigtProfileWells



def TauVoigt (lamb,NHI,bpar,zDLA,transition=Ly_a):
    res = NHI * VoigtProfileWells (lamb/(1+zDLA),bpar,transition[0]*1e-8,transition[2],transition[1])
    return res
    
