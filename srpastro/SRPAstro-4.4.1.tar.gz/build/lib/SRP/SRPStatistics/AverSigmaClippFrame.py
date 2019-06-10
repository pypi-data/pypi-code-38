""" Utility functions and classes for SRP

Context : SRP
Module  : Statistics.py
Version : 1.1.0
Author  : Stefano Covino
Date    : 03/08/2011
E-mail  : stefano.covino@brera.inaf.it
URL:    : http://www.merate.mi.astro.it/utenti/covino

Usage   : to be imported

Remarks : input data are lists of x and weights

History : (29/10/2010) First version.
        : (03/08/2011) Correction to weighting.

"""



import numpy

from .WeightedMeanFrame import WeightedMeanFrame




def CondSum (cumnum,cumden,x,wx,cond,it):
    r1 = (numpy.add(cumnum,numpy.multiply(x,numpy.power(wx,-2))),numpy.add(cumden,numpy.power(wx,-2)),it+1)
    r2 = (cumnum,cumden,it)
    return numpy.where (cond, r1, r2) 



def CondVar (cumnum,x,wa,cond,it):
    r1 = (numpy.add(cumnum,numpy.power(numpy.subtract(x,wa),2)),it+1)
    r2 = (cumnum,it)
    return numpy.where (cond, r1, r2) 



def AverSigmaClippFrame (x, wx=None, downsig=None, upsig=None, alla=False):
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
        if alla:
            return wa,wexp,ws,we
        else:
            return wa,wexp
    #
    numx = numpy.zeros(nx[0].shape)
    denw = numpy.zeros(nx[0].shape)
    nit  = numpy.zeros(nx[0].shape) 
    #
    for i in range(len(nx)):
        if downsig != None and upsig == None:
            # high-pass filter
            condiz = (nx[i] >= numpy.subtract(wa,numpy.multiply(ws,downsig)))
        elif downsig == None and upsig != None:
            # low-pass filter
            condiz = (nx[i] <= numpy.add(wa,numpy.multiply(ws,upsig)))
        else:
            # sigma-clipping
            condiz = (numpy.logical_and((nx[i] >= numpy.subtract(wa,numpy.multiply(ws,downsig))),(nx[i] <= numpy.add(wa,numpy.multiply(ws,upsig)))))
        #
        resi = CondSum (numx,denw,nx[i],nwx[i],condiz,nit)
        #
        numx = resi[0]
        denw = resi[1]
        nit = resi[2]
    #
    # mean
    waclp = numpy.divide(numx,denw)
    # exposure map
    wexpclp = numpy.divide(denw,numpy.max(denw))
    #
    # Go on computing only if explicitly required
    if not alla:
        return waclp,wexpclp
    # var
    numx = numpy.zeros(nx[0].shape)
    nit  = numpy.zeros(nx[0].shape) 
    #
    for i in range(len(nx)):
        if downsig != None and upsig == None:
            # high-pass filter
            condiz = (nx[i] >= numpy.subtract(wa,numpy.multiply(ws,downsig)))
        elif downsig == None and upsig != None:
            # low-pass filter
            condiz = (nx[i] <= numpy.add(wa,numpy.multiply(ws,upsig)))
        else:
            # sigma-clipping
            condiz = (numpy.logical_and((nx[i] >= numpy.subtract(wa,numpy.multiply(ws,downsig))),(nx[i] <= numpy.add(wa,numpy.multiply(ws,upsig)))))
        #
        resi = CondVar (numx,nx[i],waclp,condiz,nit)
        #
        numx = resi[0]
        nit = resi[1] 
    #
    wasclp = numpy.where(nit>1, numpy.divide(numx,nit-1), numpy.zeros(nx[0].shape))
    # std and sterr
    wsclp = numpy.sqrt(wasclp)
    weclp = numpy.where(nit>1, numpy.divide(wsclp,numpy.sqrt(nit)), numpy.zeros(nx[0].shape))
    #
    return waclp,wexpclp,wsclp,weclp


