""" Utility functions and classes for SRP

Context : SRP
Module  : System.py
Version : 1.0.0
Author  : Stefano Covino
Date    : 15/06/2012
E-mail  : stefano.covino@brera.inaf.it
URL:    : http://www.merate.mi.astro.it/utenti/covino

Usage   : to be imported

Usage   : HowOldIsFile (path)
            path is a file. It reports the delay from the last modfication in
            seconds.
History : (15/06/2012) First version.

"""


import os.path, time


def HowOldIsFile (path):
    try:
        a = os.path.getmtime(path)
    except OSError:
        return -1.
    #
    return time.time()-a