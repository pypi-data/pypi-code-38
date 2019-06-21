#------------------------------------------------------------------------------
# Copyright (c) 2018 LSST Systems Engineering
# Distributed under the MIT License. See LICENSE for more information.
#------------------------------------------------------------------------------
from PyQt5.QtCore import Qt

__all__ = ['boolToCheckState', 'checkStateToBool', 'convertValueOrNone', 'defaultToNoneOrValue',
           'noneToDefaultOrValue']


def boolToCheckState(value):
    """Convert a boolean to a Qt::CheckState enumeration value.

    Parameters
    ----------
    value : bool
        The boolean value.

    Returns
    -------
    Qt::CheckState
        The converted value.
    """
    return Qt.Checked if value else Qt.Unchecked

def checkStateToBool(value):
    """Convert Qt::CheckState to a boolean.

    Parameters
    ----------
    value : Qt::CheckState
        The value of the enumeration.

    Returns
    -------
    bool
        The converted value.
    """
    return True if value == Qt.Checked else False

def convertValueOrNone(value, convert=int):
    """Convert a value to a type unless NoneType.

    Parameters
    ----------
    value : anything
        The value to possibly convert.
    convert : TYPE, optional
        The type for conversion.

    Returns
    -------
    convert type
        The converted value.
    """
    return value if value is None else convert(value)

def defaultToNoneOrValue(value, default=''):
    """Convert a value to NoneType if it matches a default.

    Parameters
    ----------
    value : anything
        The value to possibly convert.
    default : anything, optional
        The default to check if NoneType return is necessary.

    Returns
    -------
    anything
        The converted value.
    """
    return None if value == default else value

def noneToDefaultOrValue(value, default=''):
    """Convert a NoneType to a default or pass back the value.

    Parameters
    ----------
    value : anything
        The value to possibly convert.
    default : anything, optional
        The default to return if value is NoneType.

    Returns
    -------
    anything
        The converted value.
    """
    return default if value is None else value
