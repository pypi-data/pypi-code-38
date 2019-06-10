""" Utility functions and classes for SRP

Context : SRP
Module  : Stats.py
Version : 1.2.0
Author  : Stefano Covino
Date    : 27/08/2012
E-mail  : stefano.covino@brera.inaf.it
URL:    : http://www.merate.mi.astro.it/utenti/covino

Usage   : to be imported

Remarks : input date are lists of x and weights

History : (28/10/2010) First version.
        : (03/08/2011) Correction in weighting.
        : (27/08/2012) Better managment of invalid floating point operations and of weights arrays.

"""


import math

import numpy


def WeightedMeanFrame(x,wx=None):
    oldsettings = numpy.seterr(all='ignore')
    nx = []
    nwx = []
    # generate numpy arrays
    for i in range(len(x)):
        nx.append(numpy.array(x[i]))
        if wx != None:
            nwx.append(numpy.array(wx[i]))
        else:
            nwx.append(numpy.ones(nx[0].shape))
    #
    if len(nx) == 1:
        return nx[0], numpy.zeros(nx[0].shape), numpy.zeros(nx[0].shape), numpy.ones(nx[0].shape)
    #    
    numx = numpy.zeros(nx[0].shape)
    denw = numpy.zeros(nx[0].shape)
    #
    for i in range(len(nx)):
        numx = numx + nx[i] * nwx[i]
        denw = denw + nwx[i]
    # mean
    wa = numpy.divide(numx,denw)
    # var
    numx = numpy.zeros(nx[0].shape)
    #
    for i in range(len(nx)):
        numx = numx + (nx[i]-wa)**2
    if len(nx) > 1:
        was = numpy.divide(numx,len(nx)-1)
    else:
        was = numpy.zeros(nx[0].shape)
    # std 
    ws = numpy.sqrt(was)
    # 
    we = numpy.divide(ws,math.sqrt(len(nx)))
    # exposure map
    wexp = numpy.divide(denw,numpy.max(denw))
    #
    numpy.seterr(**oldsettings)
    return numpy.nan_to_num(wa),numpy.nan_to_num(ws),numpy.nan_to_num(we),numpy.nan_to_num(wexp)

