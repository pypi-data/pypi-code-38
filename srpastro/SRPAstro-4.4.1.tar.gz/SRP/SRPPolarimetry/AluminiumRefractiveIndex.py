""" Utility functions and classes for SRP

Context : SRP
Module  : Polarimetry
Version : 1.1.2
Author  : Stefano Covino
Date    : 15/02/2017
E-mail  : stefano.covino@brera.inaf.it
URL:    : http://www.merate.mi.astro.it/utenti/covino

Usage   : to be imported

Remarks : Valid only in 0.2:1.2 micron range
            Aleksandar D. Rakic. Algorithm for the determination of intrinsic 
                optical constants of metal films: application to aluminum, Appl. 
                Opt. 34, 4755-4767 (1995)

History : (05/02/2012) First version.
        : (09/04/2013) More stable linear interpolation.
        : (13/06/2016) Larger range of allowed wavelengths.
        : (15/02/2017) Porting to astropy.
"""


import numpy
import os
from scipy.interpolate import interp1d
from SRP.SRPSystem.SRPPath import SRPPath
from astropy.table import Table


def AluminiumRefractiveIndex ():
    try:
        #t = atpy.Table(os.path.join(SRPPath(),'SRPData','RefractiveIndex','METALS_Aluminium_Rakic.csv'), type='ascii')
        t = Table.read(os.path.join(SRPPath(),'SRPData','RefractiveIndex','METALS_Aluminium_Rakic.csv'), format='ascii')
    except IOError:
        return None
    #
    tw = t[(t['lambda'] >= 0.2) & (t['lambda'] <= 2.9)]
    tw.sort('lambda')
    #
    n1 = interp1d(tw['lambda'], tw['n'], kind='linear', bounds_error=False)
    k1 = interp1d(tw['lambda'], tw['k'], kind='linear', bounds_error=False)
    #
    return n1,k1

