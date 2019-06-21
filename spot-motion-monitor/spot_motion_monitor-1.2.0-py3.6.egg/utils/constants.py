#------------------------------------------------------------------------------
# Copyright (c) 2018 LSST Systems Engineering
# Distributed under the MIT License. See LICENSE for more information.
#------------------------------------------------------------------------------
import enum

"""Contants for program use.

Attributes
----------
COLORMAPS : tuple
    Set of colormaps provided by the program.
DEFAULT_FPS : int
    The default Frames per Second.
DEFAULT_PSD_ARRAY_SIZE : int
    The default size of the Power Spectrum Distribution plot vertical axis.
HTML_NU : str
    The HTML string representation for the Greek letter nu.
LARGE_VALUE_FOR_VALIDATOR
    Default value for QIntValidators.
NO_DATA_VALUE : str
    Default text for no camera data value.
ONE_SECOND_IN_MILLISECONDS : int
    One second expressed in milliseconds.
STATUSBAR_FAST_TIMEOUT : int
    A fast timeout for the status bar.
TIMEFMT : str
    Formatting for date/time strings.
"""
ONE_SECOND_IN_MILLISECONDS = 1000
STATUSBAR_FAST_TIMEOUT = 100
DEFAULT_FPS = 1
NO_DATA_VALUE = " --- "
DEFAULT_PSD_ARRAY_SIZE = 25
COLORMAPS = ('viridis', 'plasma', 'inferno', 'magma', 'cividis')
TIMEFMT = '%Y-%m-%d %H:%M:%S'
HTML_NU = '&#957;'
LARGE_VALUE_FOR_VALIDATOR = 1e9

class AutoscaleState(enum.Enum):
    """Enumeration for handling autoscale states.

    Attributes
    ----------
    OFF : int
        Turn autoscaling off.
    ON : int
        Turn autoscaling on.
    PARTIAL : int
        Autoscaling is on until as number of frames recorded, then turned off.
    """
    OFF = 0
    PARTIAL = 1
    ON = 2
