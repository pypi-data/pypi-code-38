import numpy as np

from .Connector import Connector

# ignore numpy errors
np.seterr(divide='ignore', invalid='ignore')


class LoadConnector(Connector):
    """Base class for load component connector. This is used by the
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

        # derivable load parameters
        self.pow_max = 0  # maximum power [kW]
        self.enr_tot = 0  # yearly consumption [kWh]
        for cp in self.comp_list:
            self.pow_max += cp.pow_max
            self.enr_tot += cp.enr_tot

    def set_num(self, num_case):
        """Changes the number of cases to simulate. Used by the Control module.

        Parameters
        ----------
        num_case : int
            Number of scenarios to simultaneously simulate. This is set by the
            Control module.

        """
        # change number of cases
        for cp in self.comp_list:
            cp.set_num(num_case)

        # change number of cases
        self.num_case = num_case
        self.pow = np.zeros(num_case)  # instantaneous power [kW]
        self.noise = np.zeros(num_case)

    def get_pow(self, hr):
        """Returns the power output [kW] at the specified time [h].

        Parameters
        ----------
        hr : int
            Time [h] in the simulation.

        """
        # calculate generated power
        pow = np.zeros(self.num_case)
        self.noise = 0
        for cp in self.comp_list:
            get_pow = cp.get_pow(hr)
            pow += get_pow
            self.noise += cp.noise*get_pow

        # noise
        self.noise = self.noise/pow

        # record power generated [kW]
        self.pow = pow  # instantaneous power [kW]

        return pow
