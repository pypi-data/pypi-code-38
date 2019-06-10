""" Utility functions and classes for SRP

Context : SRP
Module  : Math.py
Version : 1.0.0
Author  : Stefano Covino
Date    : 24/08/2010
E-mail  : stefano.covino@brera.inaf.it
URL:    : http://www.merate.mi.astro.it/utenti/covino

Usage   : to be imported

Remarks : Output angle in degrees.

History : (24/08/2010) First version.

"""


import ephem
import math


class AstroAngleInput:
    def __init__ (self, ang, period=(0.0,360.0)):
        iang = ephem.degrees(str(ang))
        self.Angle = math.degrees(iang)
        try:
            if len(period) == 2:
                try:
                    self.Period_Low = float(period[0])
                except ValueError:
                    self.Period_Low = 0.0
                try:
                    self.Period_High = float(period[1])
                except ValueError:
                    self.Period_High = 360.0
            else:
                self.Period_Low = 0.0
                self.Period_High = 0.0
        except TypeEerror:
            self.Period_Low = 0.0
            self.Period_High = 360.0
        while not self.Period_Low <= self.Angle <= self.Period_High:
            if self.Angle > self.Period_High:
                self.Angle = self.Angle - (self.Period_High-self.Period_Low)
            else:
                self.Angle = self.Angle + (self.Period_High-self.Period_Low)
                
        
    def __str__ (self):
        msg = '%s' % (self.Angle)
        return msg
        
        