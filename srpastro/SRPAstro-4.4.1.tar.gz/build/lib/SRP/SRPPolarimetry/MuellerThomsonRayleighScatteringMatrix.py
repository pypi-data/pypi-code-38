""" Utility functions and classes for SRP

Context : SRP
Module  : Polarimetry
Version : 1.0.0
Author  : Stefano Covino
Date    : 02/11/2017
E-mail  : stefano.covino@brera.inaf.it
URL:    : http://www.merate.mi.astro.it/utenti/covino

Usage   : to be imported

Remarks : angle is in radians
        : based on Mattia Bulla's PhD thesis

History : (02/09/2013) First version.

"""


import numpy as np


def MuellerThomsonRayleighScatteringMatrix (angle=np.radians(0.0)):
    #
    fcp = (np.cos(angle))**2+1
    fcm = (np.cos(angle))**2-1
    fc2 = 2*np.cos(angle)
    #
    r1 = [fcp, fcm, 0.0, 0.0]
    r2 = [fcm, fcp, 0.0, 0.0]
    r3 = [0.0, 0.0, fc2, 0.0]
    r4 = [0.0, 0.0, 0.0, fc2]
    return 0.75**np.matrix([r1, r2, r3, r4])
