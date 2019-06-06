from __future__ import print_function, division, unicode_literals, absolute_import
from six.moves.queue import Queue
"""
This module supplies a single class, the Container. The idea is
that the root widget (the GUI mainwindow) has a single Container
property. Since all sub-widgets can get a reference to the root
window, all sub widgets can access the Container and thus communicate,
hence avoiding the use of globals.
"""


class Container:
    """
    A simple class to hold common attributes for communication between widgets.

    Those in CAPITALS are meant to be immutable; lowercase ones get
    updated.

    The meaning of the globals is as follows (uppercase)::

    COL   : colours
    DAY   : number of seconds in a day
    EFAC  : ratio FWHM/sigma for a gaussian
    EXTINCTION : extinction, mags/airmass
    SKY   : sky brightenesses
    TINS  : Telescop/instrument data
    DEFAULT_FONT : standard font (set in drivers)
    MENU_FONT    : font for menus (set in drivers)
    ENTRY_FONT   : font for data entry fields and mutable fields

    SERVER_POST_PATH : url for posting setups to rack server

    and lowercase (all set = None to start with)::

    astro   : astronomical information
    clog    : command log widget. Used to report actions and results
    count   : count & S/N information widget
    cpars   : dictionary of configuration parameters
    fpslide : focal plane slide widget
    info    : information widget
    ipars   : instrument parameters widget (windows sizes etc)
    observe : widget of observing commands
    rlog    : response log widget. Used to report server responses
    rpars   : run parameter widget
    setup   : setup widget
    ccd_hw  : CCD hardware (temps, flow rates etc) monitoring widget
    start_filter : filter at last press of 'Start'
    logfile : file to log messages
    """

    def __init__(self):
        # Ratio of FWHM/sigma for a gaussian
        self.EFAC = 2.3548

        # FIFO Queue for retrieving exceptions from
        # threaded operations
        self.FIFO = Queue()

        # Colours
        self.COL = {
            'main':     '#d0d0ff',  # Colour for the surrounds
            'text':     '#000050',  # Text colour
            'debug':    '#a0a0ff',  # Text background for debug messages
            'warn':     '#f0c050',  # Text background for warnings
            'error':    '#ffa0a0',  # Text background for errors
            'critical': '#ff0000',  # Text background for disasters
            'start':    '#00e000',  # Start / Success button colour when enabled
            'stop':     '#ff5050',  # Stop / Failure button colour when enabled
            'startD':   '#d0e0d0',  # Start / Success button colour when disabled
            'stopD':    '#ffe0e0',  # Stop / Failure button colour when disabled
            'log':      '#e0d4ff',  # Logger windows
            }

        # Telescope / instrument info. Most of this is do with estimating count rates
        self.TINS = {
            'WHT': {
                'latitude':   28.7598742,   # latitude degrees, North positive
                'longitude': -17.8793802,   # longitude degrees, East positive
                'elevation':  2327.,     # Elevation above sea level, metres
                'plateScale': 0.3,     # Arcsecs/unbinned pixel
                'zerop': {
                    'u': 25.67,
                    'g': 27.25,
                    'r': 26.65,
                    'i': 26.79,
                    'z': 26.39
                    }
                },
            'GTC': {
                'latitude':   28.762,   # latitude degrees, North positive
                'longitude': -17.87764,   # longitude degrees, East positive
                'elevation':  2300.,     # Elevation above sea level, metres
                'plateScale': 0.081,     # Arcsecs/unbinned pixel (WHT Collimator)
                'zerop': {
                    'u': 27.47,
                    'g': 29.06,
                    'r': 28.45,
                    'i': 28.60,
                    'z': 28.20
                    }
                },
            }

        # Sky brightness, mags/sq-arsec
        self.SKY = {
            'd': {'u': 22.4, 'g': 22.2, 'r': 21.4, 'i': 20.7, 'z': 20.3},
            'g': {'u': 21.4, 'g': 21.2, 'r': 20.4, 'i': 20.1, 'z': 19.9},
            'b': {'u': 18.4, 'g': 18.2, 'r': 17.4, 'i': 17.9, 'z': 18.3},
            }

        # Extinction per unit airmass
        self.EXTINCTION = {'u': 0.5, 'g': 0.19, 'r': 0.09, 'i': 0.05, 'z': 0.04}

        # Fonts set by drivers.add_style later
        # Default font, e.g. used for fixed labels
        self.DEFAULT_FONT = None

        # Font for menus
        self.MENU_FONT = None

        # Entry font, used for data entry points and mutable
        # information
        self.ENTRY_FONT = None

        # URL for posting setups
        self.SERVER_POST_PATH = "setup"

        # Command log widget. Used to report actions and results
        self.clog = None

        # Response log widget. Used to report server responses
        self.rlog = None

        # Configuration parameter dictionary: configurable options
        self.cpars = None

        # Instrument parameters widget
        self.ipars = None

        # Run parameters widget
        self.rpars = None

        # Astronomical information widget
        self.astro = None

        # Information widget
        self.info = None

        # Focal plane slide widget
        self.fpslide = None

        # Observing widget
        self.observe = None

        # Count rates, S-to-N etc widget
        self.count = None

        # Instrument setup widget
        self.setup = None

        # ccd hw monitor widget
        self.ccd_hw = None

        # Logging file
        self.logfile = None
