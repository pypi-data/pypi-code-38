""" Utility functions and classes for SRP

Context : SRP
Module  : Polarimetry
Version : 1.0.0
Author  : Stefano Covino
Date    : 17/02/2017
E-mail  : stefano.covino@brera.inaf.it
URL:    : http://www.merate.mi.astro.it/utenti/covino

Usage   : to be imported

Remarks : Rayleigh sky model according to Harrington et al. (2011, PASP, 123, 799 and
            2016, SPIE,9912,37).
        : cos(γ) = sin(θs)sin(θ)cos(ψ) + cos(θs)cos(θ) where γ is the angular distance 
            between the telescope pointing and the sun, θs is the solar zenith angle, 
            θ is the angular distance between the telescope pointing and the zenith, 
            and ψ is the azimuthal angle between the solar direction and the telescope 
            pointing.

History : (17/02/2017) First version.
"""

import numpy as np


def Gamma (ThetaS, Theta, Phi):
    ts = np.radians(ThetaS)
    t = np.radians(Theta)
    p = np.radians(Phi)
    #
    s = np.sin(ts)*np.sin(t)*np.cos(p)+np.cos(ts)*np.cos(t)
    return np.degrees(np.arcsin(s))


def RayleighSkyModel (gamma, dmax=100.0):
    gm = np.radians(gamma)
    return dmax * (np.sin(gm))**2 / (1 + (np.cos(gm))**2)
