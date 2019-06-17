import numpy as np

from .SupplementaryComponent import SupplementaryComponent

# ignore numpy errors
np.seterr(divide='ignore', invalid='ignore')


class H2Electrolyzer(SupplementaryComponent):
    """Hydrogen electrolyzer module.

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
    This module models only the charging power [kW] of the hydrogen system. A
    H2Storage and H2FuelCell module should also be initialized to model the
    energy [kWh] and discharge power respectively.

    """

    def __init__(
        self, capex=150.0, opex_fix=6.0, opex_var=0.0, opex_use=0.0,
        life=10.0, **kwargs
    ):
        """Initializes the base class."""

        # initialize component
        super().__init__(
            None, capex, opex_fix, opex_var, opex_use,
            'H2 Electrolyzer', None, None, None,
            life, 0.0, False, True, True, False, **kwargs
        )

        # update initialized parameters if essential data is complete
        self.update_init()

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
        a_sat = kwargs.pop('a_sat', 96)
        a_base = kwargs.pop('a_base', 0.21)
        r = kwargs.pop('r', 0.326)
        a = kwargs.pop('a', 3762)
        b = kwargs.pop('b', 0.282)

        # calculate cost [USD/kWh]
        cap = a_sat/(1+(a_sat-a_base)/a_base*np.exp(-r*(yr+(yr_0-2011))))
        cost = a*cap**(-b)

        return cost
