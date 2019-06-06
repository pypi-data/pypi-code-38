"""
.. module:: units
   :platform: Cross Platform
   :synopsis: Contains the Units enum

.. moduleauthor:: Drason "Emmy" Chow <emchow@iu.edu>
"""

from enum import Enum

class Units(Enum):
    """Enum that contains various units the Timer class can be set to"""

    SEC = 1
    MS = 1e3
    US = 1e6
    NS = 1e9


