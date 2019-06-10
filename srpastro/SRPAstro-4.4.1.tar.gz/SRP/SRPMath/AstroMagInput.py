""" Utility functions and classes for SRP

Context : SRP
Module  : Math.py
Version : 1.0.0
Author  : Stefano Covino
Date    : 11/08/2010
E-mail  : stefano.covino@brera.inaf.it
URL:    : http://www.merate.mi.astro.it/utenti/covino

Usage   : to be imported

Remarks : 

History : (11/08/2010) First version.

"""


import ephem
import math

from . import MathConstants



class AstroMagInput:
    def __init__ (self, mag, emag):
        try:
            self.Mag = float(mag)
        except ValueError:
            self.Mag = MathConstants.BADMAG
        try:
            self.eMag = float(emag)
        except ValueError:
            self.eMag = MathConstants.BADMAG            
        
    def __str__ (self):
        msg = "%10.3f %9.3f" % (self.Mag, self.eMag)
        return msg