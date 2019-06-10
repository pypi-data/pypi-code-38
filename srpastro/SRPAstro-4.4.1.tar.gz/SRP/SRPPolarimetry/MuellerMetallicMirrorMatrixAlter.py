""" Utility functions and classes for SRP

Context : SRP
Module  : Polarimetry
Version : 1.0.0
Author  : Stefano Covino
Date    : 30/03/2017
E-mail  : stefano.covino@brera.inaf.it
URL:    : http://www.merate.mi.astro.it/utenti/covino

Usage   : to be imported

Remarks : angle is in radians, real and imaginary part of the refraction index
            can be found at: http://refractiveindex.info/
            ambri e metri sono gli indici di rifrazione dell'ambiente e del mezzo.
            From Krijger et al., Atmos. Meas. Tech., 7, 3387–3398, 2014
            

History : (30/03/2017) First version.
"""

import numpy as np
import cmath



def rp (n1,n2, phi=np.radians(45.0)):
    CF = np.cos(phi)
    SF = np.sin(phi)
    RD = ((n1/n2)*SF)
    #
    N = n2*CF - n1*np.sqrt(1-RD**2)
    D = n2*CF + n1*np.sqrt(1-RD**2)
    return N/D
#
def rs (n1,n2, phi=np.radians(45.0)):
    CF = np.cos(phi)
    SF = np.sin(phi)
    RD = ((n1/n2)*SF)
    #
    N = n1*CF - n2*np.sqrt(1-RD**2)
    D = n1*CF + n2*np.sqrt(1-RD**2)
    return N/D
#
def MuellerMetallicMirrorMatrixAlter (ambri, metri, angle=np.radians(45.0)):
    RP = rp(ambri, metri, angle)
    RS = rs(ambri, metri, angle)
    DLT = cmath.phase(RP)-cmath.phase(RS)
    r1 = [0.5*(abs(RP)**2+abs(RS)**2), 0.5*(abs(RS)**2-abs(RP)**2), 0., 0.]
    r2 = [0.5*(abs(RS)**2-abs(RP)**2), 0.5*(abs(RP)**2+abs(RS)**2), 0., 0.]
    r3 = [0., 0., abs(RP)*abs(RS)*np.cos(DLT), abs(RP)*abs(RS)*np.sin(DLT)]
    r4 = [0., 0., -abs(RP)*abs(RS)*np.sin(DLT), abs(RP)*abs(RS)*np.cos(DLT)]
    return np.matrix([r1, r2, r3, r4])
#

