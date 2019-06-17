import numpy as np

from .SinkComponent import SinkComponent

# ignore numpy errors
np.seterr(divide='ignore', invalid='ignore')


class DesalSink(SinkComponent):
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
        self, ld_module, st_module, capex=2400, opex_fix=0.0,
        opex_var=0.08, opex_use=0.0, life=6.0,
        in_lcoe=False, is_sink=False, **kwargs
    ):
        """Initializes the base class."""

        # get storage module
        self.st_module = st_module
        self.pw_ratio = self.st_module.pw_ratio

        # initialize component
        super().__init__(
            None, capex, opex_fix, opex_var, opex_use,
            'Desal Sink', '#0000FF', None, None,
            life, 0.0, False, True, **kwargs
        )

        # get load and module
        self.ld_module = ld_module

        # initialize sink parameters
        self.wat_cost = np.array([])
        self.pow_rem = np.array([])

        # store sink parameters
        self.in_lcoe = in_lcoe
        self.is_sink = is_sink

        # update initialized parameters if essential data is complete
        self.update_init()

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
        return self.pow_rem

    def rec_pow(self, pow_rec, hr):
        """Records the power at a specified time step.

        Parameters
        ----------
        pow_rec : ndarray
            Power [kW] to be recorded by component.
        hr : int
            Time [h] in the simulation.

        """
        # calculate statistical noise
        self.noise_calc(hr)

        # record additional parameters
        self._rec_pow(pow_rec, hr)

        # record power
        self.pow = np.minimum(pow_rec, self.pow_rem)
        self.enr_tot += np.minimum(pow_rec, self.pow_rem)
        self.use_tot += pow_rec != 0

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
        # consume water
        wat_req = self.ld_module.water[hr]
        self.st_module.soc = self.st_module.soc-wat_req/self.st_module.size
        self.st_module.soc[self.st_module.size == 0] = 0

        # check if water has to be generated
        pow_req = self.pw_ratio*np.maximum(
            self.st_module.size*(self.st_module.lvl_min-self.st_module.soc),
            0  # if SOC > min water level, do not force generation
        )
        pow_req[self.st_module.size == 0] = wat_req*self.pw_ratio
        self.ld_module.pow = pow_req

        # update water level
        pow_tot = np.minimum(pow_req+pow_rec, self.pow_rem)
        pow_use = np.minimum(
            (1-self.st_module.soc)*(self.pw_ratio*self.st_module.size),
            pow_tot
        )
        pow_use[self.st_module.size == 0] = wat_req*self.pw_ratio
        self.st_module.soc = np.minimum(
            self.st_module.soc+pow_tot/(self.pw_ratio*self.st_module.size),
            1
        )
        self.st_module.soc[self.st_module.size == 0] = 0
        self.ld_module.e_tot += pow_tot

        # zero sizes
        inval = np.logical_and(
            self.pow_rem < pow_use,
            self.st_module.size == 0,
        )
        self.ld_module.pow[inval] = np.nan
        self.ld_module.pow[self.size == 0] = np.nan

        # strictly sink component
        if self.is_sink:
            self.ld_module.pow[pow_req > 0] = np.nan

        # remaining power
        self.pow_rem = np.maximum(self.pow_rem-pow_use, 0)

        # reset daily
        if hr % 24 == 0:
            self.pow_rem = self.size*self.pw_ratio

    def cost_calc(self, yr_proj, infl):
        """Calculates the cost of the component.

        Parameters
        ----------
        yr_proj : float
            Project lifetime [yr].
        infl : float
            Inflation rate.

        """
        # calculate costs
        cost_data = self._cost_calc(yr_proj, infl)
        cost_c, cost_of, cost_ov, cost_ou, cost_r, cost_f = cost_data
        self.wat_cost = cost_c+cost_of+cost_ov+cost_ou+cost_r+cost_f

        # do not include in electrical costs
        self.cost_c = self.in_lcoe*cost_c
        self.cost_of = self.in_lcoe*cost_of
        self.cost_ov = self.in_lcoe*cost_ov
        self.cost_ou = self.in_lcoe*cost_ou
        self.cost_r = self.in_lcoe*cost_r
        self.cost_f = self.in_lcoe*cost_f
        self.cost = self.in_lcoe*self.wat_cost

    def opex_var_calc(self, yr_proj, infl):
        """Default method of solving variable operating costs.

        Parameters
        ----------
        yr_proj : float
            Project lifetime [yr].
        infl : float
            Inflation rate.

        Returns
        -------
        cost_ov : ndarray
            Total variable operating cost [$] of the component.

        """
        def ann_func(i):
            """Annunity factor"""
            return 1/(1+infl)**i

        # variable operating costs [USD], output [kWh] based
        if callable(self.opex_var):
            cost_ov = self.ld_module.e_tot/self.pw_ratio*np.sum(
                self.opex_var(i)*ann_func(i)
                for i in np.arange(1, yr_proj+1)
            )
        else:
            cost_ov = (
                self.ld_module.e_tot/self.pw_ratio *
                self.opex_var*np.sum(
                    1/(1+infl)**np.arange(1, yr_proj+1)
                )
            )

        return cost_ov

    def _update_init(self):
        """Updates other parameters once essential parameters are complete.

        """
        # update sink parameters
        self.wat_cost = np.zeros(self.num_case)
        self.pow_rem = self.size*self.pw_ratio
