""" Utility functions and classes for SRP

Context : SRP
Module  : Statsistics
Version : 1.0.0
Author  : Stefano Covino
Date    : 04/04/2013
E-mail  : stefano.covino@brera.inaf.it
URL:    : http://www.merate.mi.astro.it/utenti/covino

Usage   : to be imported

Remarks : inputs are a 1D vectors to be cross-correlated. Optionally you can
            give a vector of x-axis units. It returns the cross-correlation 
            value.

History : (04/04/2013) First version.

"""

import numpy


def XCorr_1D (data, refdata, xdata=None):
    if data.ndim == 1 and refdata.ndim == 1:
        ycorr = numpy.correlate(data, refdata, mode="full")
        xcorr = numpy.arange(ycorr.size)
        lags = xcorr - (data.size-1)
        if xdata == None:
            distPerLag = 1.
        elif xdata.ndim == 1:
            distPerLag = (xdata[-1] - xdata[0])/float(xdata.size)
        else:
            return None
        #
        offsets = -lags*distPerLag
        #
        mx = ycorr.argmax()
        ox = offsets[mx]
        return ox
    else:
        return None
