import numpy as np

from .Connector import Connector


class GridConnector(Connector):
    """Base class for grid component connector. This is used by the Control
    module to manipulate components simultaneously.

    Parameters
    ----------
    comp_list : list
        List of initialized component objects.

    """

    def __init__(self, comp_list):
        """Initializes the base class."""

        # initialize base class
        super().__init__(comp_list)

        # initialize parameters
        self.pow_ret = np.array([])  # power for net metering [kW]
        self.enr_ret = np.array([])  # energy for net metering [kWh]
        self.pow_max = np.array([])
        self.noise_c = np.array([])

    def set_size(self, size):
        """Changes the size of the components. Used by the Control module.

        Parameters
        ----------
        size : dict
            Sizes [kWh] of the components. Use component objects as keys and
            sizes as values.

        """
        # reset total size
        self.size_tot = 0

        # iterate per component
        for cp in self.comp_list:
            cp.set_size(size[cp])  # set size of individual module
            self.size[cp] = size[cp]  # record in size matrix
            self.size_tot = self.size_tot+size[cp]

        # update parameters
        self.update_init()

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
        self.pow_ret = np.zeros(num_case)  # net metering [kW]
        self.enr_tot = np.zeros(num_case)  # total energy output [kWh]
        self.enr_ret = np.zeros(num_case)  # net metering [kWh]
        self.noise = np.zeros(num_case)
        self.noise_c = np.zeros(num_case)

        # update parameters
        self.update_init()

    def rec_pow(self, pow_rec, hr):
        """Records the power at a specified time step.

        Parameters
        ----------
        pow_rec : ndarray
            Power [kW] to be recorded.
        hr : int
            Time [h] in the simulation.

        """
        # initialize
        self.noise = 0
        self.noise_c = 0
        tot_c = np.zeros(self.num_case)
        tot_dc = np.zeros(self.num_case)

        for cp in self.comp_list:

            # determine if charging (-) or discharging (+)
            is_dc = pow_rec >= 0
            is_c = pow_rec < 0
            pow_dc = pow_rec*is_dc
            pow_c = -pow_rec*is_c

            # calculate (dis)charge for component
            cp_dc = is_dc*np.minimum(cp.size, pow_dc)
            cp_c = is_c*np.minimum(cp.size, pow_c)

            # calculate remaining power to distribute
            pow_rec[is_dc] = pow_rec[is_dc]-cp_dc[is_dc]
            pow_rec[is_c] = pow_rec[is_c]+cp_c[is_c]

            # record power
            cp.rec_pow(cp_dc-cp_c, hr)

            # record power generated [kW]
            self.pow = cp.pow
            self.enr_tot += cp.pow
            self.pow_ret = cp.pow_ret
            self.enr_ret += cp.pow_ret

            # noise
            self.noise += cp.noise*pow_dc
            self.noise_c += cp.noise*pow_c
            tot_c += pow_c
            tot_dc += pow_dc

        self.noise = self.noise/tot_dc
        self.noise[tot_dc == 0] = 1
        self.noise_c = self.noise_c/tot_c
        self.noise_c[tot_c == 0] = 1

    def update_init(self):
        """Updates some parameters once essential parameters are complete."""

        if (  # check ALL parameters to make sure pow_maxdc is calculated
            self.num_case != 0 and  # nonzero num_case
            not any(i is None for i in list(self.size.values()))  # sizes
        ):
            # set powers
            self.pow_max = np.zeros(self.num_case)
            for cp in self.comp_list:
                self.pow_max += cp.size
