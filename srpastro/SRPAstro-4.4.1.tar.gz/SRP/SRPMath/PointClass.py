""" Utility functions and classes for SRP

Context : SRP
Module  : Math.py
Version : 1.1.0
Author  : Stefano Covino
Date    : 11/02/2012
E-mail  : stefano.covino@brera.inaf.it
URL:    : http://www.merate.mi.astro.it/utenti/covino

Usage   : to be imported

Remarks :

History : (05/09/2010) First version.
        : (11/02/2012) Shift distance.

"""

import math

from .AstroAngleInput import AstroAngleInput


class Point:
    def __init__ (self, coord, shx=0.0, shy=0.0):
        self.Coord = [coord[0]+shx,coord[1]+shy]
        
    def PointDist (self, other):
        dist = math.sqrt((self.Coord[0]-other.Coord[0])**2 + (self.Coord[1]-other.Coord[1])**2)
        return dist
        
    def AngOrig (self,orig=(0.0,0.0)):
        xcoord = self.Coord[0] - orig[0]
        ycoord = self.Coord[1] - orig[1]
        if ycoord <= xcoord:
            ang = math.degrees(math.atan2(ycoord,xcoord))
        else:
            ang = math.degrees(math.atan2(xcoord,ycoord))
            ang = 90.0 - ang
        return ang
        
    def ShiftDist (self, other):    
        return other.Coord[0]-self.Coord[0], other.Coord[1]-self.Coord[1]

    def __str__(self):
        return "%g %g" % (self.Coord[0], self.Coord[1])