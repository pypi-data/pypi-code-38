""" Utility functions and classes for SRP

Context : SRP
Module  : Catalogue.py
Version : 1.1.0
Author  : Stefano Covino
Date    : 23/07/2015
E-mail  : stefano.covino@brera.inaf.it
URL:    : http://www.merate.mi.astro.it/utenti/covino

Usage   : to be imported

Remarks :

History : (06/08/2010) First version.
        : (04/09/2010) New importing rules.
        : (23/07/2015) New decode for python3.
"""

from SRP.SRPNet.GetWebPage import GetWebPage


def GetVizierCat (QueryAddress, QueryString):
    data = GetWebPage(QueryAddress,QueryString)
    if data == None:
        return None
    retdata = []
    dataw = data.decode().split('\n')
    for i in dataw:
        if len(i) > 0 and i[0] != '#':
            retdata.append(i)
    return retdata
