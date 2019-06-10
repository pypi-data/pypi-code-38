""" Utility functions and classes for SRP

Context : SRP
Module  : Math.py
Version : 1.0.0
Author  : Stefano Covino
Date    : 28/01/2016
E-mail  : stefano.covino@brera.inaf.it
URL:    : http://www.merate.mi.astro.it/utenti/covino

Usage   : to be imported

Remarks :

History : (28/01/2016) First version.

"""


import numpy



def integFuct (a,b,x0,y0,r,y,plus=True):
    #        print a,b,x0,y0,r,y
    fct1 = y0*(b-a)
    fct2 = 0.5*r**2 * (numpy.arcsin((b-x0)/r) - numpy.arcsin((a-x0)/r))
    fct3 = 0.5*( (b-x0)*numpy.sqrt(r**2-(b-x0)**2) - (a-x0)*numpy.sqrt(r**2-(a-x0)**2))
    subt = (b-a)*(y-1)
    #        print fct1,fct2,fct3
    if plus:
        return fct1+fct2+fct3-subt
    else:
        return fct1-fct2-fct3-subt


