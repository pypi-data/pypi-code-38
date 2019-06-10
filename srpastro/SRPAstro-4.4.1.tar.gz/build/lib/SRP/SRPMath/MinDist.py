""" Utility functions and classes for SRP

Context : SRP
Module  : Math.py
Version : 1.0.0
Author  : Stefano Covino
Date    : 25/06/2010
E-mail  : stefano.covino@brera.inaf.it
URL:    : http://www.merate.mi.astro.it/utenti/covino

Usage   : to be imported

Remarks :

History : (25/06/2010) First version.

"""


def MinDist (obj,list):
        mindist = None
        for i in list:
            dist = (obj[0]-i[0])**2 + (obj[1]-i[1])**2
            if mindist == None or dist < mindist:
                mindist = dist
        return mindist
    
