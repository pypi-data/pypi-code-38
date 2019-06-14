"""Defines earth parameters and key earth-specific calculations (ECF/ENU frame
   conversions, latitude/longitude, GMST, etc.).
"""

from __future__ import division
import numpy
import datetime
from math import pi, sin, cos
from oyb import rot

# Key Earth parameters
mu_m3ps2 = 3.986e14
tSidDay_s = 23 * 3600 + 56 * 60 + 4.0916
eqRad_m = 6.3781e6
j2000_dt = datetime.datetime(2000, 1, 1, 12, 0, 0)
flatness = 0.003353
j2 = 1.08263e-3
tSidYear_s = 365.25636 * 86400

def getGmst(t_dt):
    """Returns GMST--the angle (in radians) between the first point of Aries
       and 0-longitude--at the given *datetime.datetime* value.
    """
    dt_days = (t_dt - j2000_dt).total_seconds() / 86400
    gmst_hrs = 18.697374558 + 24.06570982441908 * dt_days
    return 2 * pi * (gmst_hrs % 24) / 24

def lla2eci(rLla_radm, t_dt):
    """Computes the geocentric inertial position of the site at the given
       lat/lon/altitude, using a spheroid earth and a specific datetime.
    """
    ra_rad = rLla_radm[1] + getGmst(t_dt)
    d = (1 - (2 * flatness - flatness**2) * sin(rLla_radm[0])**2)**0.5
    x = (eqRad_m / d + rLla_radm[2]) * cos(rLla_radm[0]) * cos(ra_rad)
    y = (eqRad_m / d + rLla_radm[2]) * cos(rLla_radm[0]) * sin(ra_rad)
    z = (eqRad_m * (1 - flatness)**2 / d + rLla_radm[2]) * sin(rLla_radm[0])
    return numpy.array([x,y,z])
    
def getQeci2ecf(t_dt):
    """Returns a 3x3 numpy.array that defines a transformation (at this level of
       fidelity, just a Z rotation) from the ECI to ECF frame at the given
       *datetime.datetime* value.
    """
    return rot.Z(getGmst(t_dt))

def getQecf2enu(rSiteLla_radm):
    """Returns a transformation matrix that converts an ECF vector to ENZ as
       perceived from a site at the given lat/lon/alt location. Note that this
       is a frame rotation only--relative range requires user subtraction.
    """
    Quen2enu = numpy.array([[0,1,0], [0,0,1], [1,0,0]])
    ry = rot.Y(-rSiteLla_radm[0])
    rz = rot.Z(rSiteLla_radm[1])
    return Quen2enu.dot(ry).dot(rz)

def getRotVel():
    """Returns the rotational velocity of the earth, in radians per second.
    """
    return 2 * pi / tSidDay_s
