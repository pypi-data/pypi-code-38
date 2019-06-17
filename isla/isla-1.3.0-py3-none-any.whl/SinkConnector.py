import numpy as np

from .Connector import Connector

# ignore numpy errors
np.seterr(divide='ignore', invalid='ignore')


class SinkConnector(Connector):
    """Base class for sink power component connector. This is used by the
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

        # initialize parameters
        self.pow_max = np.array([])

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

        # update initialized parameters if essential data is complete
        self.update_init()

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

        # update initialized parameters if essential data is complete
        self.update_init()

    def rec_pow(self, pow_rec, hr):
        """Records the power at a specified time step.

        Parameters
        ----------
        pow_rec : ndarray
            Power [kW] sto be recorded into self.pow[hr, :]
        hr : int
            Time [h] in the simulation.

        """
        # record power generated [kW]
        self.pow = pow_rec
        self.enr_tot += pow_rec

        # initialize
        pow_in = 0
        self.pow_max = 0

        # iterate per component
        for cp in self.comp_list:

            # determine maximum power that can be generated
            pow_dc = np.minimum(cp.calc_pow(pow_rec, hr), pow_rec)

            # record power
            cp.rec_pow(pow_dc, hr)

            # count total power in
            pow_in = pow_in+pow_dc

            # calculate power to be put into next component
            pow_rec = pow_rec-pow_dc

            # calculate max charge and discharge
            self.pow_max += cp.pow_max

    def update_init(self):
        """Updates some parameters once essential parameters are complete."""

        if (  # check ALL parameters to make sure pow_maxdc is calculated
            self.num_case != 0 and  # nonzero num_case
            not any(i is None for i in list(self.size.values()))  # sizes
        ):
            # set powers
            self.pow_max = np.zeros(self.num_case)
            for cp in self.comp_list:
                self.pow_max += cp.pow_max
