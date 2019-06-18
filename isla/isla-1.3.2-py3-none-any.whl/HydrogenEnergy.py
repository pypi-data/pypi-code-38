import numpy as np
from scipy.stats import linregress
from scipy.interpolate import InterpolatedUnivariateSpline

from .StorageComponent import StorageComponent

# ignore numpy errors
np.seterr(divide='ignore', invalid='ignore')


class HydrogenEnergy(StorageComponent):
    """Hydrogen fuel cell, electrolyzer, and storage module.
    This module models only the energy [kWh] of the hydrogen system. A
    HydrogenPower module should also be initialized to model the power [kW].

    Parameters
    ----------
    pow_module : HydrogenPower
        The corresponding power module for the hydrogen module.
    eff_c : float
        Charging efficiency.
    eff_dc : float
        Discharging efficiency.
    dod_max : float
        Maximum depth of discharge (DOD).
    capex : float
        Capital expenses [USD/kWh]. Depends on size.
    opex_fix : float
        Fixed yearly operating expenses [USD/kWh-yr]. Depends on size.
    opex_var : float
        Variable yearly operating expenses [USD/kWh-yr]. Depends on energy
        produced.
    fl_cost : float or None
        Initial cost of fuel (hydrogen) [USD/kWh]. If the module should not
        import hydrogen fuel, set this to None.
    life : float
        Maximum life [yr] before the component is replaced

    Other Parameters
    ----------------
    repex : float
        Replacement costs [USD/kWh]. Depends on size. Equal to CapEx by
        default.
    fail_prob : float
        Probability of failure of the component
    name_solid : str
        Label for the power output. This will be used in generated graphs
        and files.
    color_solid : str
        Hex code (e.g. '#33CC33') of the color for the power output. This
        will be used in generated graphs.
    name_line : str
        Label for the state of charge. This will be used in generated
        graphs and files.
    color_line : str
        Hex code (e.g. '#33CC33') of the color for the state of charge.
        This will be used in generated graphs.
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

    """

    def __init__(
        self, pow_module, eff_c=0.95, eff_dc=0.95, dod_max=0.9,
        capex=500.0, opex_fix=5.0, opex_var=0.0, fl_cost=1.0,
        life=10.0, **kwargs
    ):
        """Initializes the base class.

        """
        # base class parameters
        settings = {
            'name_solid': 'Hydrogen',  # label for power output
            'color_solid': '#0000CC',  # color for power output in powerflow
            'name_line': 'Hydrogen SOC',  # label for SOC
            'color_line': '#FF0000',  # color for SOC in powerflow
            'capex': capex,  # CapEx [USD/kWh]
            'opex_fix': opex_fix,  # size-dependent OpEx [USD/kWh-yr]
            'opex_var': opex_var,  # output-dependent OpEx [USD/kWh-yr]
            'life': life,  # maximum battery life [yr]
            'data': 0,  # no datasets were used
            'is_re': True  # renewable
        }
        settings.update(kwargs)  # replace default settings with input settings

        # initialize base class
        super().__init__(**settings)

        # get power module
        self.pow_module = pow_module

        # initialize battery plant parameters
        self.fuel = np.array([])  # if more H2 is needed

        # adjustable battery plant parameters
        self.eff_c = eff_c  # charging efficiency
        self.eff_dc = eff_dc  # discharging efficiency
        self.dod_max = dod_max  # maximum DOD

        # adjustable economic parameters
        self.fl_cost = fl_cost  # initial fuel cost [USD/L]

        # update initialized parameters if essential data is complete
        self._update_config()

    def cost_calc(self):
        """Calculates the cost of the component.

        """
        # capital costs [USD]
        self.cost_c = self.capex*self.size  # size [kWh] based

        # operating costs [USD]
        opex_fix = self.opex_fix*self.size  # size [kWh] based
        opex_var = self.opex_var*np.sum(self.pow, axis=0)  # output [kWh] based
        self.cost_o = (opex_fix+opex_var)*(
            np.sum(1/(1+self.infl)**np.arange(1, self.yr_proj+1))  # annualize
        )

        # calculate replacement frequency [yr]
        rep_freq = self.life*np.ones(self.num_case)  # replace due to max life

        # replace nan's in rep_freq to prevent errors with arange
        rep_freq[np.isnan(rep_freq)] = self.yr_proj+1  # no replacement

        # replacement costs [USD], size [kWh] based
        disc_rep = np.zeros(self.num_case)  # initialize sum of annuity factors
        for i in range(0, self.num_case):
            disc_rep[i] = np.sum(
                1/(1+self.infl) **
                np.arange(0, self.yr_proj, rep_freq[i])[1:]  # remove year 0
            )
        self.cost_r = self.size*self.repex*disc_rep  # size [kWh] based

        # fuel costs [USD]
        if self.fl_cost is not None:
            self.cost_f = (
                np.sum(self.fuel, axis=0)*self.fl_cost *  # fuel cons [L]
                np.sum(  # sum of annuity factors
                    1/(1+self.infl) **
                    np.arange(1, self.yr_proj+1)
                )
            )
        else:
            self.cost_f = np.zeros(self.num_case)

        # total cost [USD]
        self.cost = self.cost_c+self.cost_o+self.cost_r+self.cost_f

    def rec_pow(self, pow_rec, hr):
        """Records the power at a specified time step.

        Parameters
        ----------
        pow_rec : ndarray
            Power [kW] sto be recorded into self.pow[hr, :]
        hr : int
            Time [h] in the simulation.

        Notes
        -----
        Negative values indicate charging.
        All inputs are assumed to be valid (does not go beyond maximum).

        """
        # record power [kW] discharge
        self.pow[hr, :] = pow_rec*(pow_rec > 0)

        # determine power [kW] going in or out of each battery
        pow_in = pow_rec*(pow_rec < 0)*self.eff_c
        pow_out = pow_rec*(pow_rec > 0)/self.eff_dc

        # solve for the SOC
        self._update_soc(pow_out+pow_in, hr)  # updates self.soc[hr+1, :]

        # update max powers [kW]
        self._update_max_pow(hr)  # updates self.powmaxc, self.powmaxdc

    def _config(self):
        """Updates other parameters once essential parameters are complete.

        """
        # update battery plant parameters
        self.is_full = np.ones(self.num_case, dtype=bool)  # True if batt full
        self.fuel = np.zeros((8760, self.num_case))  # extra H2 if need more

        # update max powers
        self.pow_maxc = np.zeros(self.num_case)  # max charging power [kW]
        self.pow_maxdc = self.size*self.dod_max  # max discharging power [kW]
        self._update_max_pow(-1)  # recalculate max powers

    def _update_soc(self, pow_dc, hr):
        """Updates the state of charge of the battery.

        Parameters
        ----------
        pow_dc : ndarray
            Power [kW] drawn from the battery.
        hr : int
            Time [h] in the simulation.

        """
        # prevent hr+1 from going beyond array size
        if hr != 8759:

            # update SOC
            # put nan_to_num to avoid error when size is zero
            soc_new = np.minimum(
                np.nan_to_num(self.soc[hr, :]-pow_dc/self.size),
                1  # maximum SOC
            )

            # check for cases where battery is about to go below min SOC
            is_trn = soc_new < 1-self.dod_max

            # import additional fuel [kWh] if needed
            self.fuel[hr, :] = is_trn*(1-self.dod_max-soc_new)*self.size

            # set these cases to min SOC
            soc_new[is_trn] = 1-self.dod_max
            self.soc[hr+1, :] = soc_new

            # check if full
            self.is_full = self.soc[hr+1, :] >= 1

    def _update_max_pow(self, hr):
        """Updates the maximum charge and discharge power [kW].

        Parameters
        ----------
        hr : int
            Time [h] in the simulation.

        """
        # prevent hr+1 from going beyond array size
        if hr != 8759:

            # maximum charge power [kW] depends on SOC only
            self.pow_maxc = np.maximum(
                self.size*(1-self.soc[hr+1, :]),
                0
            )

            # calculate maximum discharge [kW]
            if self.fl_cost is not None:  # import hydrogen fuel

                # maximum discharge power [kW] depends on power rating
                self.pow_maxdc = self.pow_module.size

            else:  # do not import hydrogen

                # maximum discharge power [kW] depends on power rating
                maxdc_cap = np.maximum(  # max dc due to SOC
                    self.size *
                    (self.soc[hr+1, :]-(1-self.dod_max)),
                    0
                )
                maxdc_pow = self.pow_module.size  # max dc due to rating
                self.pow_maxdc = np.minimum(maxdc_cap, maxdc_pow)
