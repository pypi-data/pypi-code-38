""" Utility functions and classes for SRP

Context : SRP
Module  : System.py
Version : 1.0.0
Author  : Stefano Covino
Date    : 17/08/2011
E-mail  : stefano.covino@brera.inaf.it
URL:    : http://www.merate.mi.astro.it/utenti/covino

Usage   : to be imported

Remarks :

History : (17/08/2011) First version.

"""


import os


def Touch(fname, times = None):
    with file(fname, 'a'):
        os.utime(fname, times)
        
