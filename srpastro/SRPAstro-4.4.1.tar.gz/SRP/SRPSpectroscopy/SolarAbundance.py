""" Utility functions and classes for SRP

Context : SRP
Module  : Spectroscopy.py
Version : 1.0.1
Author  : Stefano Covino
Date    : 26/05/2017
E-mail  : stefano.covino@brera.inaf.it
URL:    : http://www.merate.mi.astro.it/utenti/covino

Usage   : SolarAbundance(element=None)
            the script retrieves the solar abundance according to the table by Asplund et al. (2009)

History : (29/06/2011) First version.
        : (26/05/2017) Minor update.
"""

import SRP.SRPSpectroscopy


def SolarAbundance (element=None):
    if element == None:
        return list(SRP.SRPSpectroscopy.SolAbDict.keys())
    else:
        try:
            return SRP.SRPSpectroscopy.SolAbDict[element]
        except KeyError:
            return None
