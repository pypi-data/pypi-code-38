""" Utility functions and classes for SRP

Context : SRP
Module  : Math.py
Version : 1.0.0
Author  : Stefano Covino
Date    : 18/11/2015
E-mail  : stefano.covino@brera.inaf.it
URL:    : http://www.merate.mi.astro.it/utenti/covino

Usage   : to be imported

Remarks :

History : (18/11/2015) First version.

"""

import numpy

def raw_moment(data, iord, jord):
    nrows, ncols = data.shape
    y, x = numpy.mgrid[:nrows, :ncols]
    data = data * x**iord * y**jord
    return data.sum()
