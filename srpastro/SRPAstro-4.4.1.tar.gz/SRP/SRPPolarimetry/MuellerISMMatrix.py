""" Utility functions and classes for SRP

Context : SRP
Module  : Polarimetry
Version : 1.0.0
Author  : Stefano Covino
Date    : 02/09/2013
E-mail  : stefano.covino@brera.inaf.it
URL:    : http://www.merate.mi.astro.it/utenti/covino

Usage   : to be imported

Remarks : angle is in radians
            

History : (02/09/2013) First version.

"""


import numpy


def MuellerISMMatrix (tau=0.0,q=0.0,u=0.0,angle=0.0):
    pism = numpy.sqrt(q**2+u**2)
    A = numpy.sqrt(1.-pism**2)
    #
    r1 = [1., q, u, 0.0]
    r2 = [q, (q**2+A*u**2)/pism**2, q*u*(1.-A)/pism**2, 0.0]
    r3 = [u, q*u*(1.-A)/pism**2,(q**2+A*u**2)/pism**2, 0.0]
    r4 = [0., 0., 0.0, A]
    return numpy.expt(-tau)*numpy.matrix([r1, r2, r3, r4])
