""" Utility functions and classes for SRP

Context : SRP
Module  : Polarimetry
Version : 1.0.4
Author  : Stefano Covino
Date    : 04/04/2017
E-mail  : stefano.covino@brera.inaf.it
URL:    : http://www.merate.mi.astro.it/utenti/covino

Usage   : to be imported

Remarks : angle is in radians, real and imaginary part of the refraction index
            can be found at: http://refractiveindex.info/
            From Joos et al., SPIE, 7016
            

History : (04/02/2012) First version.
        : (07/07/2016) Correction for the delta expression.
		: (09/11/2016) Using numpy only.
        : (14/02/2017) Minor bug.
        : (04/04/2017) Minor rewrite.
"""

import numpy as np


def MuellerMetallicMirrorMatrix (refrindex=1.26, extcoeff=7.19, angle=np.radians(45.0)):
    p = refrindex**2-extcoeff**2-np.sin(angle)**2
    q = 2*refrindex*extcoeff
    #
    rpiu = (1./np.sqrt(2.))*np.sqrt(p+np.sqrt(p**2+q**2))
    rmeno = (1./np.sqrt(2.))*np.sqrt(-p+np.sqrt(p**2+q**2))
    s = np.sin(angle)*np.tan(angle)
    #
    rho = np.sqrt((np.sqrt(p**2+q**2)+s**2-2*s*rpiu)/
            (np.sqrt(p**2+q**2)+s**2+2*s*rpiu))
    delta = np.arctan((2*s*rmeno)/(np.sqrt(p**2+q**2)-s**2))
    #
    r1 = [1.+rho**2, 1-rho**2, 0., 0.]
    r2 = [1.-rho**2, 1.+rho**2, 0., 0.]
    r3 = [0., 0., -2.*rho*np.cos(delta), -2.*rho*np.sin(delta)]
    r4 = [0., 0., 2.*rho*np.sin(delta), -2.*rho*np.cos(delta)]
    return 0.5*np.matrix([r1, r2, r3, r4])
