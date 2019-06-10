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


from SRP.SRPSpectroscopy.LyAlphaProfile import LyAlphaProfile


def TauDLAVoigt (lamb,NHI,bpar,zDLA):
    res = NHI * LyAlphaProfile( (lamb/(1.0+zDLA)), bpar)
    return res

