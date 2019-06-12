"""Defines vector rotation (lower case) and frame tranformations (upper case).
   Both transformations can be concatenated to be performed in right-to-left
   upon a given vector operator. Note that the *dot()* method must be used,
   since these functions return a 2d *numpy.array* object.
"""

import numpy
from math import sin, cos, atan2

def x(tht_rad):
    """Returns a 3x3 numpy array (matrix) that, when used to multiply a vector
       (using the *dot* method), results in that vector rotated about the x axis
       by the given angle (in radians).
    """
    return numpy.array([
        [1, 0, 0],
        [0, cos(tht_rad), -sin(tht_rad)],
        [0, sin(tht_rad), cos(tht_rad)]])

def y(tht_rad):
    """Returns a 3x3 numpy array (matrix) that, when used to multiply a vector
       (using the *dot* method), results in that vector rotated about the y axis
       by the given angle (in radians).
    """
    return numpy.array([
        [cos(tht_rad), 0, sin(tht_rad)],
        [0, 1, 0],
        [-sin(tht_rad), 0, cos(tht_rad)]])

def z(tht_rad):
    """Returns a 3x3 numpy array (matrix) that, when used to multiply a vector
       (using the *dot* method), results in that vector rotated about the z axis
       by the given angle (in radians).
    """
    return numpy.array([
        [cos(tht_rad), -sin(tht_rad), 0],
        [sin(tht_rad), cos(tht_rad), 0],
        [0, 0, 1]])
        
def X(tht_rad):
    """Returns a 3x3 numpy array (matrix) that, when used to multiply a vector
       (using the *dot* method), results in that vector evaluated in a new frame
       defined by a rotation about the x axis by the given angle (in radians).
    """
    return numpy.array([
        [1, 0, 0],
        [0, cos(tht_rad), sin(tht_rad)],
        [0, -sin(tht_rad), cos(tht_rad)]])

def Y(tht_rad):
    """Returns a 3x3 numpy array (matrix) that, when used to multiply a vector
       (using the *dot* method), results in that vector evaluated in a new frame
       defined by a rotation about the y axis by the given angle (in radians).
    """
    return numpy.array([
        [cos(tht_rad), 0, -sin(tht_rad)],
        [0, 1, 0],
        [sin(tht_rad), 0, cos(tht_rad)]])

def Z(tht_rad):
    """Returns a 3x3 numpy array (matrix) that, when used to multiply a vector
       (using the *dot* method), results in that vector evaluated in a new frame
       defined by a rotation about the z axis by the given angle (in radians).
    """
    return numpy.array([
        [cos(tht_rad), sin(tht_rad), 0],
        [-sin(tht_rad), cos(tht_rad), 0],
        [0, 0, 1]])

def xyz2sph(xyz):
    """Transforms cartesian coordinates into a spherical coordinate system (with
       polar singularities at +/- z). Returns a 3-component numpy array with
       +z rotation (radians), -y rotation (radians), and radius values.
    """
    xy = (xyz[0]**2 + xyz[1]**2)**0.5
    phi_rad = atan2(xyz[1], xyz[0])
    tht_rad = atan2(xyz[2], xy)
    r = (xyz[0]**2 + xyz[1]**2 + xyz[2]**2)**0.5
    return numpy.array([phi_rad, tht_rad, r])
    
def sph2xyz(sph):
    """Transforms spherical coordinates into a cartesian coordinates system
       (assuming polar singularities at +/- z). Accepts a 3-component array/list
       with +z rotation (radians), -y rotation (radians), and radius values.
    """
    x = cos(sph[0]) * cos(sph[1])
    y = sin(sph[0]) * cos(sph[1])
    z = sin(sph[1])
    return sph[2] * numpy.array([x, y, z])
