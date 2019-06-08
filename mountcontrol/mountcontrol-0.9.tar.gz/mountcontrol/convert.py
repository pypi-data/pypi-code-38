############################################################
# -*- coding: utf-8 -*-
#
# MOUNTCONTROL
#
# Python-based Tool for interaction with the 10micron mounts
# GUI with PyQT5 for python
# Python  v3.6.5
#
# Michael Würtenberger
# (c) 2018
#
# Licence APL2.0
#
############################################################
# standard libraries
import logging
import numpy as np
import inspect
# external packages
import skyfield.api
# local imports


__all__ = [
    'stringToDegree',
    'stringToAngle',
    'valueToAngle',
    'valueToFloat',
    'valueToInt',
    'topoToAltAz',
]
version = '0.5'
logger = logging.getLogger()


# conversion from value, which is
# sDD*MM:SS.S format to decimal value
# HH:MM:SS.SS format to decimal value
# sHH:MM:SS.SS format to decimal value
def stringToDegree(value):

    if not isinstance(value, str):
        return None
    if not len(value):
        return None
    if value.count('+') > 1:
        return None
    if value.count('-') > 1:
        return None
    # managing different coding
    value = value.replace('*', ' ')
    value = value.replace(':', ' ')
    value = value.replace('deg', ' ')
    value = value.replace('"', ' ')
    value = value.replace('\'', ' ')
    value = value.split()
    try:
        value = [float(x) for x in value]
    except Exception as e:
        ca = inspect.stack()[1][3]
        logger.debug('error: {0}, caller: {1}, value: {2}'.format(e, ca, value))
        return None
    sign = 1 if value[0] > 0 else -1
    value[0] = abs(value[0])
    if len(value) == 3:
        value = sign * (value[0] + value[1] / 60 + value[2] / 3600)
        return value
    elif len(value) == 2:
        value = sign * (value[0] + value[1] / 60)
        return value
    else:
        return None


# conversion from coord string to skyfield angle
def stringToAngle(value, preference='degrees'):
    value = stringToDegree(value)
    if value is not None:
        if preference == 'degrees':
            value = skyfield.api.Angle(degrees=value, preference='degrees')
        else:
            value = skyfield.api.Angle(hours=value, preference='hours')
    return value


# conversion from value simple to skyfield angle
def valueToAngle(value, preference='degrees'):
    value = valueToFloat(value)
    if value is not None:
        if preference == 'degrees':
            value = skyfield.api.Angle(degrees=value, preference='degrees')
        else:
            value = skyfield.api.Angle(hours=value, preference='hours')
    return value


# conversion from value to float
def valueToFloat(value):
    try:
        value = float(value)
    except Exception as e:
        ca = inspect.stack()[1][3]
        logger.debug('error: {0}, caller: {1}, value: {2}'.format(e, ca, value))
        value = None
    finally:
        return value


# conversion from value to int
def valueToInt(value):
    try:
        value = int(value)
    except Exception as e:
        ca = inspect.stack()[1][3]
        logger.debug('error: {0}, caller: {1}, value: {2}'.format(e, ca, value))
        value = None
    finally:
        return value


# conversion topo to alt az
def topoToAltAz(ha, dec, lat):
    if lat is None:
        logger.error('lat nof defined')
        return None, None
    ha = (ha * 360 / 24 + 360.0) % 360.0
    dec = np.radians(dec)
    ha = np.radians(ha)
    lat = np.radians(lat)
    alt = np.arcsin(np.sin(dec) * np.sin(lat) + np.cos(dec) * np.cos(lat) * np.cos(ha))
    value = (np.sin(dec) - np.sin(alt) * np.sin(lat)) / (np.cos(alt) * np.cos(lat))
    # we have to check for rounding error, which could happen
    if value > 1:
        value = 1
    elif value < -1:
        value = -1
    A = np.arccos(value)
    A = np.degrees(A)
    alt = np.degrees(alt)
    if np.sin(ha) >= 0.0:
        az = 360.0 - A
    else:
        az = A
    return alt, az
