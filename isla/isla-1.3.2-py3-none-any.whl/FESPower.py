import numpy as np

from .FixedComponent import FixedComponent

# ignore numpy errors
np.seterr(divide='ignore', invalid='ignore')


class FESPower(FixedComponent):
    """Flywheel module.
    This module models only the power [kW] of the FES. An FESEnergy and
    FESLoad module should also be initialized to model the energy [kWh] and
    parasitic load of the FES respectively.

    Parameters
    ----------
    capex : float
        Capital expenses [USD/kW]. Depends on size.
    opex_fix : float
        Fixed yearly operating expenses [USD/kW-yr]. Depends on size.
    life : float
        Maximum life [yr] before the component is replaced.

    Other Parameters
    ----------------
    repex : float
        Replacement costs [USD/kWh]. Depends on size. Equal to CapEx by
        default.
    fail_prob : float
        Probability of failure of the component.
    num_case : int
        Number of scenarios to simultaneously simulate. This is set by the
        Control module
    yr_proj : int
        Project lifetime [yr]. This is set by the Control module.
    size : int
        Size of the component [kWh]. This is set by the Control module.
    infl : float
        Inflation rate. This is set by the Control module.
    data : ndarray
        Dataset. No dataset is required for this component.

    References
    ----------
    ..[1] HOMER, "Flywheel," n.d.

    """

    def __init__(
        self, capex=0.0, opex_fix=0.0, life=10.0, **kwargs
    ):
        """Initializes the base class.

        """
        # base class parameters
        settings = {
            'name_solid': 'FES Power',  # label for power output
            'capex': capex,  # CapEx [USD/kW]
            'opex_fix': opex_fix,  # size-dependent OpEx [USD/kW-yr]
            'life': life,  # maximum battery life [yr]
            'data': 0,  # no datasets were used
            'is_re': True  # renewable
        }
        settings.update(kwargs)  # replace default settings with input settings

        # initialize base class
        super().__init__(**settings)

        # update initialized parameters if essential data is complete
        self._update_config()

    def cost_calc(self):
        """Calculates the cost of the component.

        """
        # capital costs [USD]
        self.cost_c = self.capex*self.size  # size [kW] based

        # operating costs [USD]
        self.cost_o = (  # size [kW] based
            self.opex_fix*self.size *
            np.sum(1/(1+self.infl)**np.arange(1, self.yr_proj+1))
        )

        # calculate replacement frequency [yr]
        rep_freq = self.life*np.ones(self.num_case)  # replace due to max life

        # replace nan's in rep_freq to prevent errors with arange
        rep_freq[np.isnan(rep_freq)] = self.yr_proj+1  # no replacement

        # replacement costs [USD], size [kW] based
        disc_rep = np.zeros(self.num_case)  # initialize sum of annuity factors
        for i in range(0, self.num_case):
            disc_rep[i] = np.sum(
                1/(1+self.infl) **
                np.arange(0, self.yr_proj, rep_freq[i])[1:]  # remove year 0
            )
        self.cost_r = self.size*self.repex*disc_rep  # size [kW] based

        # total cost [USD]
        self.cost = self.cost_c+self.cost_o+self.cost_r

    def get_pow(self, hr):
        """This is here to maintain the functionality of the Control module.
        All power should be recorded in the FESEnergy module.

        """
        return np.zeros(self.num_case)
