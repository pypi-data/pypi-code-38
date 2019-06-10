""" Utility functions and classes for SRP

Context : SRP
Module  : Polarimetry
Version : 2.0.0
Author  : Stefano Covino
Date    : 18/04/2013
E-mail  : stefano.covino@brera.inaf.it
URL:    : http://www.merate.mi.astro.it/utenti/covino

Usage   : to be imported

Remarks : angles are in radians

History : (19/02/2012) First version.
        : (18/04/2013) Error computation


"""

import numpy


def Pol2Stokes (i, p, t, c, ep=0.0, et=0.0, ec=0.0):
    q = p*i*numpy.cos(2*t)*numpy.cos(2*c)
    u = p*i*numpy.sin(2*t)*numpy.cos(2*c)
    v = p*i*numpy.sin(2*c)
    #
    eq = numpy.sqrt( (q*ep/p)**2 +
        (2*u*et)**2 + (2*v*numpy.cos(2*t)*ec)**2 )
    eu = numpy.sqrt( (u*ep/p)**2 +
        (2*q*et)**2 + (2*v*numpy.sin(2*t)*ec)**2 )
    ev = numpy.sqrt( (v*ep/p)**2 + (2*i*p*ec*numpy.cos(2*c))**2 )
    return i, q, u, v, eq, eu, ev