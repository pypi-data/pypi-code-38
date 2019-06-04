__license__ = "ISC"
__author__ = "David Kalliecharan"
__author_email__ = "david@david.science"

try:
    from .xps import *
    from . import parser
    from . import sfwagner

    # populate Wagner sensitivity factors for convienence
    sf = sfwagner.SensitivityFactors()

except ImportError as err:
    print(err)
    pass
	
