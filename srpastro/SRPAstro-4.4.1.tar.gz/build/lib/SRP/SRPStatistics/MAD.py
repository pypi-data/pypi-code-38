""" Utility functions and classes for SRP

Context : SRP
Module  : Stats.py
Version : 1.0.0
Author  : Stefano Covino
Date    : 04/03/2013
E-mail  : stefano.covino@brera.inaf.it
URL:    : http://www.merate.mi.astro.it/utenti/covino

Usage   : MAD(table)
            table is the dataset.
          The function return the Median Absolute Deviation
        

Remarks : input is a list of (x,sigmax)

History : (30/04/2011) First version.

"""


import numpy


def MAD(table):
    median = numpy.median(table)
    mad = numpy.median(numpy.abs(table-median))
    return mad


    
    