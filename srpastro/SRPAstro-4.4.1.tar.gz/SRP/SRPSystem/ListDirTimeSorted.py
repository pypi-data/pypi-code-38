""" Utility functions and classes for SRP

Context : SRP
Module  : System.py
Version : 1.0.1
Author  : Stefano Covino
Date    : 26/08/2011
E-mail  : stefano.covino@brera.inaf.it
URL:    : http://www.merate.mi.astro.it/utenti/covino

Usage   : to be imported

Usage   : ListDirTimeSorted (path, selpattern='',reverse=False)
            path is the directory the content of which will be sorted.
            selpattern is a string to select files.
            reverse to sort the creation time from the newest to the oldest.

History : (24/08/2011) First version.
        : (26/08/2011) Works also for non-existent directories.

"""


import os, os.path


def ListDirTimeSorted (path, selpattern='',reverse=False):
    try:
        a = [os.path.join(path, s) for s in os.listdir(path) if os.path.isfile(os.path.join(path, s)) and s.find(selpattern) >=0]
    except OSError:
        return None
    #
    a.sort(key=lambda s: os.path.getmtime(s))
    #
    if reverse:
        a.reverse()
    #
    return a