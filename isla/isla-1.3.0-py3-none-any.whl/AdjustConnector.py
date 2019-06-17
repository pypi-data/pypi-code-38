import numpy as np

from .Connector import Connector

# ignore numpy errors
np.seterr(divide='ignore', invalid='ignore')


class AdjustConnector(Connector):
    """Base class for adjustable power component connector. This is used by the
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
        # initialize total power generation:
        pow_gen = 0

        # iterate per component
        for cp in self.comp_list:
            pow_gen = pow_gen+cp.calc_pow(pow_req, hr)  # add to gen power
            pow_req = np.maximum(pow_req-pow_gen, 0)  # power for next comp

        return pow_gen

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

        # initialize record power
        pow_in = 0

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
