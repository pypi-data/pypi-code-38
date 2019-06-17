import numpy as np

from .DispatchableComponent import DispatchableComponent

# ignore numpy errors
np.seterr(divide='ignore', invalid='ignore')


class Genset(DispatchableComponent):
    """Genset module.

    Parameters
    ----------
    fuel : Fuel object
        Fuel to be used by the generator.
    min_ratio : float
        Ratio of minimum loading to rated size.
    eff_min : float
        Efficiency at minimum loading.
    eff_max : float
        Efficiency at maximum loading.
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
    life : float
        Lifetime [y] of the component.
    life_use : float or None
        Lifetime based on usage [h].
    fail_prob : float
        Probability of failure of the component.
    is_fail : bool
        True if failure probabilities should be simulated.

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
        self, fuel, min_ratio=0.1, eff_min=0.3, eff_max=0.4,
        capex=500.0, opex_fix=5.0, opex_var=0.0, opex_use=0.0,
        life=10.0, life_use=None, fail_prob=0.014, is_fail=False, **kwargs
    ):
        """Initializes the base class."""

        # initialize base class
        super().__init__(
            None, capex, opex_fix, opex_var, opex_use,
            fuel.name_solid, fuel.color_solid, None, None,
            life, fail_prob, is_fail, fuel.is_re, True, False,
            **kwargs
        )

        # get fuel module
        self.fuel = fuel  # fuel used by genset

        # adjustable diesel plant parameters
        self.min_ratio = min_ratio  # minimum loading ratio
        self.eff_min = eff_min  # minimum efficiency
        self.eff_max = eff_max  # maximum efficiency
        self.life_use = life_use

        # initialize diesel plant parameters
        self.fl_slp = 0  # fuel slope [u/kWh]
        self.fl_int = 0  # fuel intercept [u/h]

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
        ndarray
            The power output [kW] of the component.

        """
        # calculate generated power [kW]
        cond = [
            pow_req < self.min_ratio*self.size,  # cannot go below min loading
            (pow_req >= self.min_ratio*self.size)*(pow_req < self.size),
            pow_req >= self.size  # cannot go beyond max loading (size)
        ]
        choice = [self.min_ratio*self.size, pow_req, self.size]
        pow_gen = np.select(cond, choice)

        return pow_gen

    def _rec_pow(self, pow_rec, hr):
        """Records the power at a specified time step.

        Parameters
        ----------
        pow_rec : ndarray
            Power [kW] sto be recorded into self.pow.
        hr : int
            Time [h] in the simulation.

        """
        # record fuel consumption
        fl_use = self.fl_slp*pow_rec+self.fl_int*self.size*(pow_rec != 0)
        self.fuel.rec_fl(fl_use, hr)

    def _cost_calc(self, yr_proj, infl):
        """Returns the costs of the component.

        Parameters
        ----------
        yr_proj : float
            Project lifetime [yr].
        infl : float
            Inflation rate.

        Returns
        -------
        cost_c : ndarray
            Total capital cost [$] of the component.
        cost_of : ndarray
            Total fixed operating cost [$] of the component.
        cost_ov : ndarray
            Total variable operating cost [$] of the component.
        cost_ou : ndarray
            Total usage operating cost [$] of the component.
        cost_r : ndarray
            Total replacement cost [$] of the component.
        cost_f : ndarray
            Total fuel cost of the component [$]

        Notes
        -----
        This function can be modified by the user.

        """
        # calculate replacement period
        if self.life_use is None:
            rep_per = self.life
        elif self.life is None:
            rep_per = self.life_use/self.use_tot
        else:
            rep_per = np.minimum(self.life, self.life_use/self.use_tot)

        # calculate other costs
        cost_c = self.capex_calc()
        cost_of = self.opex_fix_calc(yr_proj, infl)
        cost_ov = self.opex_var_calc(yr_proj, infl)
        cost_ou = self.opex_use_calc(yr_proj, infl)
        cost_r = self.repex_calc(yr_proj, infl, rep_per)

        # calculate fuel costs
        self.fuel.cost_calc(yr_proj, infl)
        cost_f = self.fuel.cost_f

        return (cost_c, cost_of, cost_ov, cost_ou, cost_r, cost_f)

    def _update_init(self):
        """Initalize other parameters for the component."""

        # set number of components for fuel
        self.fuel.set_num(self.num_case)

        # solve for fuel slope and intercept
        coeff = 3.6/(self.fuel.den*self.fuel.lhv)
        self.fl_slp = coeff*(
            (1/self.eff_max-self.min_ratio/self.eff_min) /
            (1-self.min_ratio)
        )
        self.fl_int = coeff/self.eff_max-self.fl_slp
