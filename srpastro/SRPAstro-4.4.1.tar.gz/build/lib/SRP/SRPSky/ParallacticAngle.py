""" Utility functions and classes for SRP

Context : SRP
Module  : Math.py
Version : 1.0.0
Author  : Stefano Covino
Date    : 09/02/2012
E-mail  : stefano.covino@brera.inaf.it
URL:    : http://www.merate.mi.astro.it/utenti/covino

Usage   : to be imported

Remarks : site and object should be valid pyephem objects.

History : (09/02/2012) First version.

"""

import ephem
import math
from SRP.SRPSky.HourAngle import HourAngle

import numpy as np



def parangle(HA, DEC, lat):
    """
        +
        NAME:
        parangle
        
        PURPOSE:
        To compute the parallactic angle at a given position on the sky.
        
        CATEGORY:
        Spectroscopy    
        
        CALLING SEQUENCE:
        eta, za = parangle(HA, DEC, lat)
        
        INPUTS:
        HA  - Hour angle of the object, in decimal hours (0,24)
        DEC - Declination of the object, in degrees
        lat - The latitude of the observer, in degrees
        
        KEYWORD PARAMETERS:
        CANCEL - Set on return if there is a problem
        
        OUTPUTS:
        eta - The parallactic angle
        za  - The zenith angle
        
        PROCEDURE:
        Given an objects HA and DEC and the observers latitude, the
        zenith angle and azimuth are computed.  The law of cosines
        then gives the parallactic angle.  
        
        EXAMPLE:
        NA
        
        
        MODIFICATION HISTORY:
        2000-04-05 - written by M. Cushing, Institute for Astronomy,UH
        2002-08-15 - cleaned up a bit.
        2003-10-21 - changed to pro; outputs zenith angle as well - WDV
        2011-10-07 17:58 IJMC: Converted to Python
        -"""
    
    #pro parangle, HA, DEC, lat, eta, za, CANCEL=cancel
    
    cancel = 0
    d2r = np.deg2rad(1.)
    r2d = np.rad2deg(1.)
    
    #  If HA equals zero then it is easy.
    HA = HA % 24
    #  Check to see if HA is greater than 12.
    if hasattr(HA, '__iter__'):
        HA = np.array(HA, copy=False)
        HAind = HA > 12
        if HAind.any():
            HA[HAind] = 24. - HA[HAind]
    else:
        if HA>12.:
            HA = 24. - HA
    
    HA = HA*15.
    
    #  Determine Zenith angle and Azimuth
    cos_za = np.sin(lat*d2r) * np.sin(DEC*d2r) + \
        np.cos(lat*d2r) * np.cos(DEC*d2r) * np.cos(HA*d2r)
    za     = np.arccos(cos_za) * r2d
    cos_az = (np.sin(DEC*d2r) - np.sin(lat*d2r)*np.cos(za*d2r)) / \
        (np.cos(lat*d2r) * np.sin(za*d2r))
    az     = np.arccos(cos_az)*r2d
    
    if hasattr(az, '__iter__'):
        azind = az==0
        if azind.any() and DEC<lat:
            az[azind] = 180.
    else:
        if az==0. and DEC<lat:
            az = 180.
    
    tan_eta = np.sin(HA*d2r)*np.cos(lat*d2r) / \
        (np.cos(DEC*d2r)*np.sin(lat*d2r) - \
         np.sin(DEC*d2r)*np.cos(lat*d2r)*np.cos(HA*d2r))
    eta     = np.arctan(tan_eta)*r2d
    
    if hasattr(eta, '__iter__'):
        etaind = eta < 0
        ezind = (eta==0) * (az==0)
        zaind = za > 90
        if etaind.any():
            eta[etaind] += 180.
        elif ezind.any():
            eta[ezind] = 180.
        if zaind.any():
            eta[zaind] = np.nan
    else:
        if eta < 0:
            eta += 180.
        elif eta==0 and az==0:
            eta = 180.
        if za>90:
            eta = np.nan
    
    HA = HA/15.0
    
    return eta, za



"""
def ParallacticAngle (object,site):
    f1 = math.cos(site.lat)
    f2 = math.sin(math.radians(HourAngle(math.degrees(float(object.a_ra)),site)))
    f3 = math.cos(object.a_dec)
    if f3 == 0:
        factsin = 0.0
    else:
        factsin = f1*f2/f3
        if factsin < -1:
            factsin = -1.0
        elif factsin > 1.0:
            factsin = 1.0
    #
    f1 = math.sin(site.lat)
    f2 = math.sin(object.a_dec)
    f3 = math.cos(object.a_dec)
    f4 = math.sin(object.alt)
    f5 = math.cos(object.alt)
    if f3 == 0.0 or f5 == 0.0:
        factcos = 1.0
    else:
        factcos = (f1-f2*f4)/(f3*f5)
        if factcos < -1:
            factcos = -1.0
        elif factcos > 1.0:
            factcos = 1.0
    #
#    f1 = math.sin(site.lat)
#    f2 = math.cos(object.alt)
#    f3 = math.cos(site.lat)
#    f4 = math.sin(object.alt)
#    f5 = math.cos(math.radians(HourAngle(math.degrees(float(object.a_ra)),site)))
#    f6 = math.cos(object.a_dec)
#    if f6 == 0.0:
#        factcos2 = 1.0
#    else:
#        factcos2 = (f1*f2-f3*f4*f5)/f6
    #
    if factsin >= 0 and factcos >= 0: 
        pac = math.degrees(math.acos(factcos))
    elif factsin < 0 and factcos >= 0:
        pac = -math.degrees(math.acos(factcos))
    elif factsin >= 0 and factcos < 0:
        pac = math.degrees(math.acos(factcos))
    elif factsin < 0 and factcos < 0:
        pac = -math.degrees(math.acos(factcos))
#    return pac
    print pac, math.degrees(math.atan2(factsin,factcos)), factcos, factsin
    return math.degrees(math.atan2(factsin,factcos))
"""




def ParallacticAngle (object,site):
    HA = HourAngle(math.degrees(float(object.a_ra)),site)
    f1 = math.sin(math.radians(HA))
    f2 = math.cos(object.a_dec)
    f3 = math.tan(site.lat)
    f4 = math.sin(object.a_dec)
    f5 = math.cos(math.radians(HA))
    return -math.degrees(math.atan2(-f1,f2*f3-f4*f5))




"""
def ParallacticAngle (object,site):
    HA = 24*HourAngle(math.degrees(float(object.a_ra)),site)/360.0
    DEC = math.degrees(float(object.a_dec))
    LAT = math.degrees(site.lat)
    #
    eta, za = parangle(HA, DEC, LAT)
    #
    return eta
"""