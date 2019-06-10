""" Utility functions and classes for SRP

Context : SRP
Module  : Stats.py
Version : 1.0.0
Author  : Stefano Covino
Date    : 04/03/2013
E-mail  : stefano.covino@brera.inaf.it
URL:    : http://www.merate.mi.astro.it/utenti/covino

Usage   : StDev(table,mean=None)
            table is the dataset and mean is the point to be used for mean.
          The function return the standard deviation
        

Remarks : input is an array

History : (30/04/2011) First version.

"""


import numpy


def StDev(table,mean=None):
    if mean == None:
        mn = numpy.mean(table)
    else:
        mn = mean 
    StDev = numpy.sqrt(((table-mn)**2).sum()/len(table))
    return StDev


    
    