""" Utility functions and classes for SRP

Context : SRP
Module  : Polarimetry
Version : 2.0.0
Author  : Stefano Covino
Date    : 18/04/2013
E-mail  : stefano.covino@brera.inaf.it
URL:    : http://www.merate.mi.astro.it/utenti/covino

Usage   : to be imported

Remarks : return angle is in radians, inputs are I, Q, U, V, eQ, eU, eV

History : (19/02/2012) First version.
        : (18/04/2013) Error computation

"""

import numpy


def Stokes2Pol (i, q, u, v, eq=0.0, eu=0.0, ev=0.0):
    pl = numpy.sqrt(q**2 + u**2) / i
    pol = numpy.sqrt(q**2 + u**2 + v**2) / i
    theta = 0.5 * numpy.arctan2(u,q)
    chi = 0.5 * numpy.arctan2(v, pl)
    #
    epl = numpy.sqrt((q*eq)**2 + (u*eu)**2)/pl
    epol = numpy.sqrt((q*eq)**2 + (u*eu)**2 + (v*ev)**2)/pol
    etheta = 0.5*numpy.sqrt((u*eq)**2 + (q*eu)**2)/(pl**2)
    echi = 0.5*numpy.sqrt((v*epl)**2 + (pl*ev)**2)/(pol**2)
    return i, pol, theta, chi, epol, etheta, echi