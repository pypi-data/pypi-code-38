import numpy as np

from .Connector import Connector

# ignore numpy errors
np.seterr(divide='ignore', invalid='ignore')


class SupplementaryConnector(Connector):
    """Base class for supplementary power component connector. This is used by the
    Control module to manipulate components simultaneously.

    Parameters
    ----------
    comp_list : list
        List of initialized component objects.

    """
    def __init__(self, comp_list):
        """Initializes the base class.

        """
        # initialize base class
        super().__init__(comp_list)
