import numpy as np

from SupplementaryComponent import SupplementaryComponent

# ignore numpy errors
np.seterr(divide='ignore', invalid='ignore')


class .H2FuelCell(SupplementaryComponent):
    """Hydrogen fuel cell module.

    Parameters
    ----------
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

    Other Parameters
    ----------------
    repex : float or callable
        Replacement costs [USD/kW(h)]. Depends on size. Equal to CapEx by
        default. Can be a callable function that returns replacement costs
        starting from year zero to end of project lifetime.
    num_case : int
        Number of scenarios to simultaneously simulate. This is set by the
        Control module.
    size : int
        Size of the component [kW]. This is set by the Control module.

    Notes
    -----
    This module models only the discharging power [kW] of the hydrogen system.
    A H2Storage and H2Electrolyzer module should also be initialized to model\
    the energy [kWh] and charge power respectively.

    """

    def __init__(
        self, capex=150.0, opex_fix=6.0, opex_var=0.0, opex_use=0.0,
        life=10.0, life_use=None, **kwargs
    ):
        """Initializes the base class."""

        # initialize component
        super().__init__(
            None, capex, opex_fix, opex_var, opex_use,
            'H2 Fuel Cell', None, None, None,
            life, 0.0, False, True, True, False, **kwargs
        )

        # adjustable fuel cell parameters
        self.life_use = life_use  # hours of operation before replacement [h]

        # update initialized parameters if essential data is complete
        self.update_init()

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

        return (cost_c, cost_of, cost_ov, cost_ou, cost_r, 0)

    def _update_init(self):
        """Updates other parameters once essential parameters are complete."""
        pass

    @staticmethod
    def exp_curve(yr, yr_0=2016, **kwargs):
        """Experience curve for Solar PV.
        Returns the cost [USD/kW] at the given year.

        Parameters
        ----------
        yr : int
            Index of the year.
        yr_0 : int
            Year where index is set to zero.

        """
        # get regression parameters
        a_sat = kwargs.pop('a_sat', 97)
        a_base = kwargs.pop('a_base', 0.05)
        r = kwargs.pop('r', 0.5)
        a = kwargs.pop('a', 8361)
        b = kwargs.pop('b', 0.287)

        # calculate cost [USD/kWh]
        cap = a_sat/(1+(a_sat-a_base)/a_base*np.exp(-r*(yr+(yr_0-2013))))
        cost = a*cap**(-b)

        return cost
