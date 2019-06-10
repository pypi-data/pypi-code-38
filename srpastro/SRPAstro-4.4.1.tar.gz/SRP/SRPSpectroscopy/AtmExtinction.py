""" Utility functions and classes for SRP

Context : SRP
Module  : Spectroscpy
Version : 1.1.0
Author  : Stefano Covino
Date    : 23/07/2015
E-mail  : stefano.covino@brera.inaf.it
URL:    : http://www.merate.mi.astro.it/utenti/covino

Usage   : to be imported

Remarks : l (micron)

History : (22/08/2012) First version.
        : (23/07/2015) python3 porting.
"""


import os
from scipy.interpolate import interp1d
from SRP.SRPSystem.SRPPath import SRPPath
from astropy.table import Table



def AtmExtinction (l, fname):
    try:
        t = Table.read(os.path.join(SRPPath(),'SRPData','AtmExtinction',fname), format='ascii')
    except IOError:
        return None
    #
    a = interp1d(t['col1'], t['col2'], kind='quadratic', bounds_error=True)
    #
    la = l*1e4
    try:
        return a(la)
    except ValueError:
        return None

