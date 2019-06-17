import numpy as np

from .GridComponent import GridComponent

# ignore numpy errors
np.seterr(divide='ignore', invalid='ignore')


class Grid(GridComponent):
    """Grid module.

    Parameters
    ----------
    pow_maxret : float
        Maximum allowed generating capacity for net metering.
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
    opex_ret : float or callable
        Savings per unit energy returned to grid [$/kWh yr]. Can be a callable
        function that returns the variable operating cost starting from year\
        zero to end of project lifetime.
    opex_use : float or callable
        Variable yearly operating expenses [$/h yr]. Depends on amount of
        usage. Can be a callable function that returns the variable
        operating cost starting from year zero to end of project lifetime.
    life : float
        Lifetime [y] of the component.
    fail_prob : float
        Probability of failure of the component.
    is_fail : bool
        True if failure probabilities should be simulated.
    is_re : bool
        True if the resource is renewable.

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
        self, pow_maxret=100, capex=0.0,
        opex_fix=0.0, opex_var=0.2, opex_ret=0.1,
        opex_use=0.0, life=20.0, fail_prob=0.0001, is_fail=False, **kwargs
    ):
        """Initializes the base class."""

        # initialize component
        super().__init__(
            None, capex, opex_fix, opex_var, opex_ret, opex_use,
            'Grid', '#333333', None, None,
            life, fail_prob, is_fail, False, True, False, **kwargs
        )

        # record grid parameters
        self.pow_maxret = pow_maxret

        # update initialized parameters if essential data is complete
        self.update_init()

    def rec_pow(self, pow_rec, hr):
        """Records the power at a specified time step.

        Parameters
        ----------
        pow_rec : ndarray
            Power [kW] to be recorded by component.
        hr : int
            Time [h] in the simulation.

        """
        # record power
        self.use_tot += pow_rec != 0

        # failure probability
        if not self.is_fail:
            noise = 1
        else:
            noise = np.random.rand(self.num_case) > self.fail_prob
        self.noise = noise
        pow_rec = pow_rec*noise

        # record additional parameters
        self._rec_pow(pow_rec, hr)

        # consider max net metering rate
        pow_rec = np.maximum(pow_rec, -self.pow_maxret)

        # record power
        self.pow = pow_rec*(pow_rec >= 0)
        self.enr_tot += pow_rec*(pow_rec >= 0)
        self.pow_ret = -pow_rec*(pow_rec < 0)
        self.enr_ret += -pow_rec*(pow_rec < 0)

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
        super()._rec_pow(pow_rec, hr)

    def opex_use_calc(self, yr_proj, infl):
        """Default method of solving usage-based operating costs.

        Parameters
        ----------
        yr_proj : float
            Project lifetime [yr].
        infl : float
            Inflation rate.

        Returns
        -------
        cost_ou : ndarray
            Total usage operating cost [$] of the component.

        """
        def ann_func(i):
            """Annunity factor"""
            return 1/(1+infl)**i

        # variable operating costs [USD], output [kWh] based
        if callable(self.opex_var):
            cost_ou = self.use_tot*np.sum(
                self.opex_hr(i)*ann_func(i)
                for i in np.arange(1, yr_proj+1)
            )
        else:
            cost_ou = self.opex_use*self.use_tot*np.sum(
               1/(1+infl)**np.arange(1, yr_proj+1)
            )

        return cost_ou

    def _update_init(self):
        """Updates other parameters once essential parameters are complete.

        """
        pass
