""" Utility functions and classes for SRP

Context : SRP
Module  : Math
Version : 1.0.0
Author  : Stefano Covino
Date    : 20/09/2012
E-mail  : stefano.covino@brera.inaf.it
URL:    : http://www.merate.mi.astro.it/utenti/covino

Usage   : to be imported

Remarks :

History : (20/09/2012) First version.

"""


def PhaseAngle (ang, mina=0.0, maxa=360.0):
    while ang < mina or ang >= maxa:
        if ang < mina:
            ang = ang + (maxa-mina)
        else:
            ang = ang - (maxa-mina)
    return ang

