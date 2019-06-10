""" Utility functions and classes for SRP

Context : SRP
Module  : Math
Version : 1.0.0
Author  : Stefano Covino
Date    : 25/06/2010
E-mail  : stefano.covino@brera.inaf.it
URL:    : http://www.merate.mi.astro.it/utenti/covino

Usage   : to be imported

Remarks : Angles in radians

History : (25/06/2010) First version.

"""

import numpy


class CartesianVector(object):
    def __init__(self, x=0.0, y=0.0, z=0.0):
        self.x = x
        self.y = y
        self.z = z

    def dot(self, v):
        return self.x * v.x + self.y * v.y + self.z * v.z

    def cross(self, v):
        n = self.__class__()
        n.x = self.y * v.z - self.z * v.y
        n.y = - (self.x * v.z - self.z * v.x)
        n.z = self.x * v.y - self.y * v.x
        return n

    @property
    def mod(self):
        return numpy.sqrt(self.x ** 2 + self.y ** 2 + self.z ** 2)

    def from_s(self, r=1.0, alpha=0.0, delta=0.0):
        self.x = r * numpy.cos(delta) * numpy.cos(alpha)
        self.y = r * numpy.cos(delta) * numpy.sin(alpha)
        self.z = r * numpy.sin(delta)
        
    def __repr__(self):
        return str(self.x, self.y, self.z)

    def __str__(self):
        self.___repr__()

