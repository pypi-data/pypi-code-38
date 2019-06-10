""" Utility functions and classes for SRP

Context : SRP
Module  : Stats.py
Version : 1.0.0
Author  : Stefano Covino
Date    : 07/06/2013
E-mail  : stefano.covino@brera.inaf.it
URL:    : http://www.merate.mi.astro.it/utenti/covino

Usage   : to be imported

Remarks : Ref: http://it.wikipedia.org/wiki/Test_F

History : (07/06/2013) First version.

"""


def FTest (oldchi2, olddof, newchi2, newdof):
    return ((oldchi2-newchi2)/(olddof-newdof))/(newchi2/newdof)