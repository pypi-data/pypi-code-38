import numpy as np

from .Component import Component

# ignore numpy errors
np.seterr(divide='ignore', invalid='ignore')


class NullComp(Component):
    """Placeholder for when a component is not present."""

    def __init__(self):
        """Initializes the base class."""

        # initialize base class
        super().__init__(
            None, 0.0, 0.0, 0.0, 0.0,
            None, None, None, None,
            20.0, 0.0, False, False, True, False
        )

        # initialize parameters
        self.pow_maxc = np.array([])
        self.pow_maxdc = np.array([])
        self.soc = np.array([])
        self.is_full = np.array([])
        self.dod_max = 1
        self.pow_max = 0
        self.pow_ret = 0

    def _calc_pow(self, pow_req, hr):
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
        pow_gen : ndarray
            The power output [kW] of the component.

        Notes
        -----
        This function can be modified by the user.

        """
        return 0

    def _get_pow(self, hr):
        """Returns the power output [kW] at the specified time [h].

        Parameters
        ----------
        hr : int
            Time [h] in the simulation.

        Returns
        -------
        pow : ndarray
            Power [kW] at the current timestep.

        Notes
        -----
        This function can be modified by the user.

        """
        return 0

    def _rec_pow(self, pow_rec, hr):
        """Records parameters at the specified time step.

        Parameters
        ----------
        pow_rec : ndarray
            Power [kW] to be recorded by component.
        hr : int
            Time [h] in the simulation.

        Notes
        -----
        This function can be modified by the user.

        """
        pass

    def update_init(self):
        """Updates initialized parameters once size and num_case are given."""

        # check if all essential parameters are in
        if self.num_case is not None:

            # update component parameters
            self.size = np.zeros(self.num_case)
            self.pow = np.zeros(self.num_case)  # instantaneous power [kW]
            self.enr_tot = np.zeros(self.num_case)  # total energy output [kWh]
            self.use_tot = np.zeros(self.num_case)  # total energy output [kWh]
            self.noise = np.ones(self.num_case)

            # update cost parameters
            self.cost_c = np.zeros(self.num_case)  # capital cost [$]
            self.cost_of = np.zeros(self.num_case)  # fixed opex [$]
            self.cost_ov = np.zeros(self.num_case)  # var opex [$]
            self.cost_ou = np.zeros(self.num_case)  # use opex [$]
            self.cost_r = np.zeros(self.num_case)  # replacement cost [$]
            self.cost_f = np.zeros(self.num_case)  # fuel cost [$]
            self.cost = np.zeros(self.num_case)  # total cost [$]

            # update battery parameters
            self.pow_maxc = np.zeros(self.num_case)  # max charge pow [kW]
            self.pow_maxdc = np.zeros(self.num_case)  # max discharge pow [kW]
            self.soc = np.ones(self.num_case)  # SOC
            self.is_full = np.ones(self.num_case, dtype=bool)  # True if full

            # update other parameters
            self._update_init()

    def _update_init(self):
        """Initalize other parameters for the component."""
        pass
