""" Utility functions and classes for SRP

Context : SRP
Module  : Stats.py
Version : 1.0.0
Author  : Stefano Covino
Date    : 04/12/2012
E-mail  : stefano.covino@brera.inaf.it
URL:    : http://www.merate.mi.astro.it/utenti/covino

Usage   : to be imported

Remarks : inputs are a list of parameters and a list of choices for 
            the fit: e.g. [(1,0.2),(1,-0.34),(0,0.01),(-1,0.2)]

History : (04/12/2012) First version.

"""


def GenFitPars (pars, args):
    pari = []
    if len(pars) != len(args):
        raise Exception("Input vectors must be of the same length.")
    for ii in range(len(pars)):
        if args[ii][0] > 0:
            pari.append(pars[ii])
        elif args[ii][0] == 0:
            pari.append(args[ii][1])
        else:
            if not (1 <= abs(args[ii][0]) <= len(pars)):
                raise Exception("Parameter to couple not existent.")
            pari.append(pars[abs(args[ii][0])-1])
    return pari


