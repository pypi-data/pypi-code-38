""" Utility functions and classes for SRP

Context : SRP
Module  : Stats.py
Version : 1.0.0
Author  : Stefano Covino
Date    : 22/12/2014
E-mail  : stefano.covino@brera.inaf.it
URL:    : http://www.merate.mi.astro.it/utenti/covino

Usage   : RebinData(array,width,sigmaclip=None)
          The function returns an array formed by sigma clipped
          mean in sub-arrays of given width. For the regular mean 
          put sigmaclip to None.

History : (22/12/2014) First version.

"""

import astropy.stats.funcs as asf
import numpy


def RebinData(array,width,sigmaclip=None):
    rebarr = array[:(array.size // width) * width].reshape(-1, width)
    if sigmaclip != None:
        return asf.sigma_clip(rebarr,sig=sigmaclip,axis=1).mean(axis=1)
    else:
        return rebarr.mean(axis=1)

    
    