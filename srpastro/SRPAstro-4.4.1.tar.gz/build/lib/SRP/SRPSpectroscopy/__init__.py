""" 
    
Context : SRP
Module  : Spectroscopy
Version : 1.6.0
Author  : Stefano Covino
Date    : 02/04/2013
E-mail  : stefano.covino@brera.inaf.it
URL     : http://www.me.oa-brera.inaf.it/utenti/covino


History : (17/11/2010) First named version.
        : (19/03/2011) VoigtIntegrand, VoigtFunct and VoigtFunctWells added.
        : (21/03/2011) ExtConstants, CalzettiExt and getAbs added.
        : (29/06/2011) Solar abundance table added.
        : (05/09/2011) Various constants and functions.
        : (23/10/2011) Flux density conversion.
        : (27/10/2011) FWHM variation with airmass and wavelength
        : (22/08/2012) Atmospheric extinction curves
        : (20/12/2012) New atmospheric extinction curves.
        : (22/03/2013) GetSpectrum.
        : (02/04/2013) GetSpectrumPosition.
"""


__all__ = ['Air2Vacuum', 'AirRefrIndex', 'AtmExtinction', 'CalzettiExt', 'DLACrossSection', 'Ecm2sA2Jy',
           'ExtConstants', 'FWHMvsZL', 'getAbs', 'I_Totani', 'Jy2Ecm2sA', 'LymAlphaDumpConst',
           'LyAlphaProfile', 'OzonVertExt', 'RaleyghScattering', 'Ralpha', 'SolarAbundance', 'StndCriticalDens',
           'TauDLA','TauDLAVoigt', 'TauGP', 'TauIGM', 'TauVoigt', 'Transitions', 'Vacuum2Air', 'VoigtFunct',
           'VoigtFunctApprox','VoigtFunctApproxA', 'VoigtFunctTG', 'VoigtFunctWells', 'VoigtIntegrand',
           'VoigtProfileCmpd', 'VoigtProfileWells']


import math



# Solar abundances according to Asplund M, Grevesse N., Sauval A.J. & Scott P., 2009, ARAA, 47, 481
H = 'H'
He = 'He'
Li = 'Li'
Be = 'Be'
B = 'B'
C = 'C'
N = 'N'
O = 'O'
F = 'F'
Ne = 'Ne'
Na = 'Na'
Mg = 'Mg'
Al = 'Al'
Si = 'Si'
P = 'P'
S = 'S'
Cl = 'Cl'
Ar = 'Ar'
K = 'K'
Ca = 'Ca'
Sc = 'Sc'
Ti = 'Ti'
V = 'V'
Cr = 'Cr'
Mn = 'Mn'
Fe = 'Fe'
Co = 'Co'
Ni = 'Ni'
Cu = 'Cu'
Zn = 'Zn'
SolAbDict = {H : 1.000E+00,  He : 8.510E-02,  Li : 1.120E-11,  Be : 2.400E-11,  B : 5.010E-10,
                C : 2.690E-04,  N : 6.760E-05,  O : 4.900E-04,  F : 3.630E-08,  Ne : 8.510E-05,
                Na : 1.740E-06,  Mg : 3.980E-05,  Al : 2.820E-06,  Si : 3.240E-05,  P : 2.570E-07,
                S : 1.320E-05,  Cl : 3.160E-07,  Ar : 2.510E-06,  K : 1.070E-07,  Ca : 2.190E-06,
                Sc : 1.410E-09,  Ti : 8.910E-08,  V : 8.510E-09,  Cr : 4.370E-07,  Mn : 2.690E-07,
                Fe : 3.160E-05,  Co : 9.770E-08,  Ni : 1.660E-06,  Cu : 1.550E-08,  Zn : 3.630E-08}



SpeedofLight            = 3e10                                  # cm s^-1
LambdaLymanAlpha        = 121.567e-7                            # cm
NuLymanAlpha            = SpeedofLight/LambdaLymanAlpha         # Hz
GravitationalConst      = 6.673e-8                              # cm^3 g^-1 s-2
Parsec                  = 3.08568025e18                         # cm
ProtonMass              = 1.67262158e-24                        # g
ElectronMass            = 9.10938215e-28                        # g
ElectronCharge          = 4.80320427e-10                        # cgs
AbsOscillStrength       = 0.4162
ClassLymAlphaDumpConst  = (8*math.pi**2*ElectronCharge**2)/(3*ElectronMass*SpeedofLight*LambdaLymanAlpha**2)


# Atmospheric extinction curves
CP   =   'Paranal'
CPa  =   'CerroPachon'
LP   =   'LaPalma'
LS   =   'LaSilla'
MK   =   'MaunaKea'

AtmExtCurves = {CP : 'Paranal.dat', CPa : 'CerroPachon.dat', LP : 'LaPalma.dat', LS : 'LaSilla.dat', MK : 'MaunaKea.dat'}

#
