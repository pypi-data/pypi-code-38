""" Utility functions and classes for SRP

Context : SRP
Module  : System
Version : 1.0.0
Author  : Stefano Covino
Date    : 29/08/2013
E-mail  : stefano.covino@brera.inaf.it
URL:    : http://www.merate.mi.astro.it/utenti/covino

Usage   : to be imported

Remarks :

History : (29/08/2013) First version.

"""


import os, os.path


def EnsureDir(f):
    d = os.path.dirname(f)
    if not os.path.exists(d):
        try:
            os.makedirs(d)
            return True
        except IOError:
            return False
