""" Utility functions and classes for SRP

Context : SRP
Module  : Catalogue.py
Version : 1.0.0
Author  : Stefano Covino
Date    : 06/08/2010
E-mail  : stefano.covino@brera.inaf.it
URL:    : http://www.merate.mi.astro.it/utenti/covino

Usage   : to be imported

Remarks :

History : (06/08/2010) First version.

"""


def ParseVizierCat (viscat):
    retdata = []
    if len(viscat) > 0:
        reflen = len(viscat[0].split('\t'))
        for i in viscat:
            iparsed = i.split('\t')
            if len(iparsed) == reflen:
                retdata.append(iparsed)
    return retdata