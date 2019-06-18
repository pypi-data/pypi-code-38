from abc import abstractmethod

import numpy as np

from .Component import Component

# ignore numpy errors
np.seterr(divide='ignore', invalid='ignore')


class SinkComponent(Component):
    """Base class for energy components.

    Parameters
    ----------
    data : ndarray
        Dataset. Set to zero if no dataset is required.
    capex : float or callable
        Capital expenses [$/kW(h)]. Depends on size. Can be a callable
        function that returns capital cost starting from year zero to end of
        project lifetime.
    opex_fix : float or callable
        Fixed yearly operating expenses [$/kW(h) yr]. Depends on size. Can be
        a callable function that returns the fixed operating cost starting
        from year zero to end of project lifetime.
    opex_var : float or callable
        Variable yearly operating expenses [$/kWh yr]. Depends on energy
        produced. Can be a callable function that returns the variable
        operating cost starting from year zero to end of project lifetime.
    opex_use : float or callable
        Variable yearly operating expenses [$/h yr]. Depends on amount of
        usage. Can be a callable function that returns the variable
        operating cost starting from year zero to end of project lifetime.
    name_solid : str
        Label used for the power output. Appears as a solid area in powerflows
        and as a header in .csv files. Usually the name of the component.
    color_solid : str
        Hex code (e.g. '#33CC33') of the color corresponding to name_solid.
        Appears in the solid area in powerflows.
    name_line : str
        Label used for the power output. Appears as a line in powerflows
        and as a header in .csv files. Usually the name of a Load component or
        Storage state of charge.
    color_line : str
        Hex code (e.g. '#33CC33') of the color corresponding to name_line.
        Appears in the line in powerflows.
    life : float
        Lifetime [y] of the component.
    fail_prob : float
        Probability of failure of the component.
    is_fail : bool
        True if failure probabilities should be simulated.
    is_re : bool
        True if the resource is renewable.
    is_elec : bool
        True if the resource is electrical.
    is_water : bool
        True if the resource is water.

    Other Parameters
    ----------------
    repex : float or callable
        Replacement costs [$/kW(h)]. Depends on size. Equal to CapEx by
        default. Can be a callable function that returns replacement costs
        starting from year zero to end of project lifetime.
    num_case : int
        Number of scenarios to simultaneously simulate. This is set by the
        Control module.
    size : int
        Size of the component [kW]. This is set by the Control module.

    """

    def __init__(
        self, data, capex, opex_fix, opex_var, opex_use,
        name_solid, color_solid, name_line, color_line,
        life, fail_prob, is_fail, is_re, is_elec, is_water,
        **kwargs
    ):
        """Initializes the base class."""

        # initialize component
        super().__init__(
            data, capex, opex_fix, opex_var, opex_use,
            name_solid, color_solid, name_line, color_line,
            life, fail_prob, is_fail, is_re, is_elec, is_water,
            **kwargs
        )

        # initialize sink components:
        self.pow_max = np.array([])

    @abstractmethod  # implementation required
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
        pass

    @abstractmethod  # implementation required
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
        if (self.num_case is not None and self.size is not None):

            # prevents optimization errors
            if self.size.size == self.num_case:

                # update component parameters
                self.pow = np.zeros(self.num_case)  # instantaneous power [kW]
                self.enr_tot = np.zeros(self.num_case)  # tot energy out [kWh]
                self.use_tot = np.zeros(self.num_case)  # tot energy out [kWh]
                self.noise = np.ones(self.num_case)
                self.pow_max = self.size

                # update cost parameters
                self.cost_c = np.zeros(self.num_case)  # capital cost [$]
                self.cost_of = np.zeros(self.num_case)  # fixed opex [$]
                self.cost_ov = np.zeros(self.num_case)  # var opex [$]
                self.cost_ou = np.zeros(self.num_case)  # use opex [$]
                self.cost_r = np.zeros(self.num_case)  # replacement cost [$]
                self.cost_f = np.zeros(self.num_case)  # fuel cost [$]
                self.cost = np.zeros(self.num_case)  # total cost [$]

                # update other parameters
                self._update_init()

    @abstractmethod  # implementation required
    def _update_init(self):
        """Updates other parameters once essential parameters are complete.

        """
        pass
