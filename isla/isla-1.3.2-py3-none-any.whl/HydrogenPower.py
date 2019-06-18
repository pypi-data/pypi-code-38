import numpy as np

from .FixedComponent import FixedComponent

# ignore numpy errors
np.seterr(divide='ignore', invalid='ignore')


class HydrogenPower(FixedComponent):
    """Hydrogen fuel cell, electrolyzer, and storage module.
    This module models only the power [kW] of the hydrogen system. A
    HydrogenEnergy module should also be initialized to model the energy [kWh].

    Parameters
    ----------
    capex : float
        Capital expenses [USD/kW]. Depends on size.
    opex_fix : float
        Fixed yearly operating expenses [USD/kW-yr]. Depends on size.
    repex : float
        Replacement costs [USD/kW]. Depends on size. Equal to CapEx by
        default.
    life : float
        Maximum life [yr] before the component is replaced

    Other Parameters
    ----------------
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

    Notes
    -----
    A separate power module for hydrogen exists so that energy and power can be
    sized separately. As such, this module does not function like the other
    modules. This module should not be used to record power. This module uses
    the FixedComponent base class for functionality only.

    """

    def __init__(
        self, capex=150.0, opex_fix=6.0, life=10.0, **kwargs
    ):
        """Initializes the base class.

        """
        # base class parameters
        settings = {
            'name_solid': 'Hydrogen Power',  # label for power output
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

    def get_pow(self, hr):
        """This is here to maintain the functionality of the Control module.
        All power should be recorded in the Hydrogen Energy module.

        """
        return np.zeros(self.num_case)

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
        rep_freq = self.life*np.ones(self.num_case)  # replacement frequency

        # replace nan's in rep_freq to prevent errors with arange
        rep_freq[np.isnan(rep_freq)] = self.yr_proj+1  # no replacement

        # replacement costs [USD], size [kW] based
        disc_rep = np.zeros(self.num_case)
        for i in range(0, self.num_case):
            disc_rep[i] = np.sum(
                1/(1+self.infl) **
                np.arange(0, self.yr_proj, rep_freq[i])[1:]  # remove 0
            )
        self.cost_r = self.size*self.repex*disc_rep  # size [kW] based

        # total cost [USD]
        self.cost = self.cost_c+self.cost_o+self.cost_r
