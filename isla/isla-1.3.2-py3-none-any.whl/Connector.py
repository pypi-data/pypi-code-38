from abc import abstractmethod

import numpy as np

# ignore numpy errors
np.seterr(divide='ignore', invalid='ignore')


class Connector(object):
    """Base class for energy component connector. This is used by the Control
    module to manipulate components simultaneously.

    Parameters
    ----------
    comp_list : list
        List of initialized component objects.

    """

    def __init__(self, comp_list):
        """Initializes the base class."""

        # get list of components
        self.comp_list = comp_list  # list of components

        # derivable component parameters
        self.size = dict.fromkeys(comp_list)  # dict of sizes

        # initialize component parameters
        self.pow = np.array([])  # instantaneous power [kW] of component
        self.enr_tot = np.array([])  # total energy output [kWh] of component
        self.noise = np.array([])
        self.num_case = 0  # number of cases to simulate

        # initialize cost parameters
        self.cost_c = np.array([])  # capital cost [$] of component
        self.cost_of = np.array([])  # fixed operating cost [$] of component
        self.cost_ov = np.array([])  # var operating cost [$] of component
        self.cost_ou = np.array([])  # use operating cost [$] of component
        self.cost_r = np.array([])  # replacement cost [$] of component
        self.cost_f = np.array([])  # fuel cost [$] of component
        self.cost = np.array([])  # total cost [$] of component

    def set_data(self, data):
        """Changes the dataset to be used by the component. Used by the Control module.

        Parameters
        ----------
        data : dict
            Dataset to be used by the component. Use component objects as keys
            and dataset as values.

        """
        # change dataset
        for cp in self.comp_list:
            cp.set_data(data[cp])

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
        self.enr_tot = np.zeros(num_case)  # total energy output [kWh]
        self.noise = np.zeros(num_case)

    def set_size(self, size):
        """Changes the size of the components. Used by the Control module.

        Parameters
        ----------
        size : dict
            Sizes [kW] or [kWh] of the components. Use component objects as
            keys and sizes as values.

        """
        # change sizes of components
        for cp in self.comp_list:
            cp.set_size(size[cp])  # set size of individual module
            self.size[cp] = size[cp]  # record in size matrix

    def get_pow(self, hr):
        """Returns the power output [kW] at the specified time [h].

        Parameters
        ----------
        hr : int
            Time [h] in the simulation.

        """
        pass

    def calc_pow(self, pow_req, hr):
        """Returns the power output [kW] of the component given the minimum
        required power [kW] and timestep.

        Parameters
        ----------
        pow_req : ndarray
            Minimum required power [kW].
        hr : int
            Time [h] in the simulation.

        Returns
        -------
        ndarray
            The power output [kW] of the component.

        """
        pass

    def rec_pow(self, pow_rec, hr):
        """Records the power at a specified time step.

        Parameters
        ----------
        pow_rec : ndarray
            Power [kW] sto be recorded into self.pow.
        hr : int
            Time [h] in the simulation.

        """
        pass

    def fail_calc(self):
        """Calculates the probability of failure of the component."""

        # calculate failure probability for each component
        for cp in self.comp_list:
            cp.fail_calc()

    def cost_calc(self, yr_proj, infl):
        """Calculates the cost of the component.

        Parameters
        ----------
        yr_proj : float
            Project lifetime [yr].
        infl : float
            Inflation rate.

        """
        # calculate the cost of each component
        for cp in self.comp_list:
            cp.cost_calc(yr_proj, infl)

        # initialize cost arrays
        self.cost_c = np.zeros(self.num_case)  # capital cost [$]
        self.cost_of = np.zeros(self.num_case)  # fixed opex [$]
        self.cost_ov = np.zeros(self.num_case)  # var opex [$]
        self.cost_ou = np.zeros(self.num_case)  # use opex [$]
        self.cost_r = np.zeros(self.num_case)  # replacement cost [$]
        self.cost_f = np.zeros(self.num_case)  # fuel cost [$]
        self.cost = np.zeros(self.num_case)  # total cost [$]

        # add each cost
        for cp in self.comp_list:
            self.cost_c += cp.cost_c
            self.cost_of += cp.cost_of
            self.cost_ov += cp.cost_ov
            self.cost_ou += cp.cost_ou
            self.cost_r += cp.cost_r
            self.cost_f += cp.cost_f
            self.cost += cp.cost
