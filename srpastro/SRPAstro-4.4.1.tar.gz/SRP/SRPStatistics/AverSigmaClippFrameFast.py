""" Utility functions and classes for SRP

Context : SRP
Module  : Statistics.py
Version : 1.0.1
Author  : Stefano Covino
Date    : 27/03/2013
E-mail  : stefano.covino@brera.inaf.it
URL:    : http://www.merate.mi.astro.it/utenti/covino

Usage   : to be imported

Remarks : input data are lists of x and weights

History : (27/08/2012) First version.
        : (27/03/2013) Bug corrections.

"""



import numpy
from .WeightedMeanFrame import WeightedMeanFrame





def AverSigmaClippFrameFast (x, wx=None, downsig=None, upsig=None):
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
    res = WeightedMeanFrame(nx,nwx)
    wa = res[0]
    ws = res[1]
    we = res[2]
    wexp = res[3]
    #
    if (downsig == None and upsig == None) or (len(nx) == 1):
        # no condition, nothing to do
        return wa,ws,we,wexp
    # generate arrays of conditions
    ncond = []
    for i in range(len(nx)):
        if downsig != None and upsig == None:
            # high-pass filter
            ncond.append(numpy.where(nx[i] >= (wa-ws*downsig), 1., 0.))
        elif downsig == None and upsig != None:
            # low-pass filter
            ncond.append(numpy.where(nx[i] <= (wa+ws*upsig), 1., 0.))
        else:
            # sigma-clipping
            ncond.append(numpy.where((nx[i] >= wa-ws*downsig) & (nx[i] <= wa+ws*upsig), 1., 0.))
    # generate conditionates arrays
    nxt = []
    nwxt = []
    for i in range(len(x)):
        nxt.append(nx[i] * ncond[i])
        nwxt.append(ncond[i] * nwx[i])
    #
    res = WeightedMeanFrame(nxt,nwxt)
    wa = res[0]
    ws = res[1]
    we = res[2]
    wexp = res[3]
    #
    return wa,ws,we,wexp
    # era wa, ncond
    #

