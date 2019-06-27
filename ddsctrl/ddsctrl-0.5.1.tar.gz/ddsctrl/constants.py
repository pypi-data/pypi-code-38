# -*- coding: utf-8 -*-

""" ddsctrl/constants.py """

ORGANIZATION = "FEMTO_Engineering"
APP_NAME = "ddscontroller"
APP_BRIEF = "GUI dedicated to handle the AD9912 DDS device"
AUTHOR_NAME = "Benoit Dubois"
AUTHOR_MAIL = "benoit.dubois@femto-st.fr"
COPYRIGHT = "2016, FEMTO ENGINEERING"
LICENSE = "GNU GPL v3.0 or upper."

DEFAULT_AUTO_UPDATE = False   # Default automatic update state
DEFAULT_IFREQ = 1000000000.0  # Default DDS input frequency
DEFAULT_OFREQ = 1000.0        # Default DDS output frequency
DEFAULT_AMP = 200             # Default DDS output amplitude (between 0 to 1023)
DEFAULT_PHASE = 0             # Default DDS phase
DEFAULT_PLL_EN = False        # Default PLL enable state
DEFAULT_PLL_DOUBLER = False   # Default PLL doubler state
DEFAULT_PLL_FACTOR = 4        # Default PLL multiplication factor
DEFAULT_CP_CURRENT = 2        # Default CP current index (see CP_CURRENT dict)
DEFAULT_VCO_RANGE = 2         # Default VCO range index (see VCO_RANGE dict)
DEFAULT_HSTL_EN = False       # Default HSTL enable state
DEFAULT_CMOS_EN = False       # Default CMOS enable state
DEFAULT_HSTL_DOUBLER = False  # Default HSTL doubler state

VCO_RANGE = {0: "700 MHz to 810 MHz", 1: "900MHz to 1000 MHz", 2: "Automatic"}
CP_CURRENT = {0: "250 µA", 1: "375 µA", 2:"Off", 3: "125 µA"}
