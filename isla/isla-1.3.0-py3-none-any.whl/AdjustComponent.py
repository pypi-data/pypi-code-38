from abc import abstractmethod

import numpy as np

from .Component import Component

# ignore numpy errors
np.seterr(divide='ignore', invalid='ignore')


class AdjustComponent(Component):
    """Base class for adjustable power components.

    Parameters
    ----------
    capex : float
        Capital expenses [USD/kW]. Depends on size.
    opex_fix : float
        Fixed yearly operating expenses [USD/kW-yr]. Depends on size.
    opex_var : float
        Variable yearly operating expenses [USD/kWh-yr]. Depends on energy
        produced.
    repex : float
        Replacement costs [USD/kW]. Depends on size. Equal to CapEx by
        default.
    life : float
        Maximum life [yr] before the component is replaced
    fail_prob : float
        Probability of failure of the component
    name_solid : str
        Label for the power output. This will be used in generated graphs
        and files.
    color_solid : str
        Hex code (e.g. '#33CC33') of the color for the power output. This
        will be used in generated graphs.
    is_re : bool
        True if the resource is renewable.

    """

    def __init__(self, **kwargs):
        """Initializes the base class.

        """
        # initialize component
        super().__init__(**kwargs)

        # initialize usage arrays
        self.fl_tot = np.array([])  # total fuel [L] or [kg]
        self.use_tot = np.array([])  # number of times used

    @abstractmethod  # implementation required
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

    @abstractmethod  # implementation required
    def cost_calc(self, yr_proj, infl):
        """Calculates the cost of the component.

        Parameters
        ----------
        yr_proj : float
            Project lifetime [yr].
        infl : float
            Inflation rate.

        """
        pass

    @abstractmethod  # implementation required
    def rec_pow(self, pow_rec, hr):
        """Records the power at a specified time step.

        Parameters
        ----------
        pow_rec : ndarray
            Power [kW] sto be recorded into self.pow[hr, :]
        hr : int
            Time [h] in the simulation.

        """
        pass

    @abstractmethod  # implementation required
    def _config(self):
        """Updates other parameters once essential parameters are complete.

        """
        pass

    def _update_config(self):
        """Updates some parameters once essential parameters are complete.

        """
        # check if all essential parameters are in
        if (
            self.num_case is not None and  # number of cases to simulate
            self.size is not None  # size [kW]
        ):
            # update component parameters
            self.pow = np.zeros(self.num_case)  # instantaneous power [kW]
            self.enr_tot = np.zeros(self.num_case)   # total energy [kWh]
            self.fl_tot = np.zeros(self.num_case)  # total fuel [L] or [kg]
            self.use_tot = np.zeros(self.num_case)  # number of times used

            # update cost parameters
            self.cost_c = np.zeros(self.num_case)  # CapEx [USD] of component
            self.cost_o = np.zeros(self.num_case)  # OpEx [USD] of component
            self.cost_r = np.zeros(self.num_case)  # repl cost [USD] of comp
            self.cost_f = np.zeros(self.num_case)  # fuel cost [USD] of comp
            self.cost = np.zeros(self.num_case)  # total cost [USD] of comp

            # update failure parameters
            self.fail = np.zeros(self.num_case)  # prob of failure

            # update other parameters
            self._config()
