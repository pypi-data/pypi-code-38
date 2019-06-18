import numpy as np

from .Connector import Connector

# ignore numpy errors
np.seterr(divide='ignore', invalid='ignore')


class FixedConnector(Connector):
    """Base class for fixed (intermittent) power component connector. This is
    used by the Control module to manipulate components simultaneously.

    Parameters
    ----------
    comp_list : list
        List of initialized component objects.

    """

    def __init__(self, comp_list):
        """Initializes the base class."""

        # initialize base class
        super().__init__(comp_list)

    def get_pow(self, hr):
        """Returns the power output [kW] at the specified time [h].

        Parameters
        ----------
        hr : int
            Time [h] in the simulation.

        """
        # calculate generated power
        pow = 0
        for cp in self.comp_list:
            pow += cp.get_pow(hr)

        # record power generated [kW]
        self.pow = pow  # instantaneous power [kW]
        self.enr_tot += pow  # total energy [kWh]

        return pow
