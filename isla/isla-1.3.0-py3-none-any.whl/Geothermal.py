import numpy as np

from .AdjustComponent import AdjustComponent

# ignore numpy errors
np.seterr(divide='ignore', invalid='ignore')


class Geothermal(AdjustComponent):
    """Geothermal plant module.

    Parameters
    ----------
    capex : float
        Capital expenses [USD/kW]. Depends on size.
    opex_fix : float
        Fixed yearly operating expenses [USD/kW-yr]. Depends on size.
    opex_var : float
        Variable yearly operating expenses [USD/kW-yr]. Depends on energy
        produced.
    dr_cost : float
        Drilling cost [USD] per well.
    life : float
        Maximum life [yr] before the component is replaced

    Other Parameters
    ----------------
    repex : float
        Replacement costs [USD/kW]. Depends on size. Equal to CapEx by
        default.
    fail_prob : float
        Probability of failure of the component
    name_solid : str
        Label for the power output. This will be used in generated graphs
        and files.
    color_solid : str
        Hex code (e.g. '#33CC33') of the color for the power output. This
        will be used in generated graphs.
    num_case : int
        Number of scenarios to simultaneously simulate. This is set by the
        Control module
    yr_proj : int
        Project lifetime [yr]. This is set by the Control module.
    size : int
        Size of the component [kW]. This is set by the Control module.
    infl : float
        Inflation rate. This is set by the Control module.
    data : ndarray
        Dataset. No dataset is required for this component.
    min_ratio : ndarray
        Ratio of minimum power output [kW] to the load in the current time
        step.
    dec_rate_base : float
        Decline rate [/yr] of base case.
    size_base : float
        Corresponding size [kW] of base case.
    pow_well : float
        Power output per well.
    rsv : float
        Minimum reserve capacity
    rsv_init : float
        Initial minimum reserve capacity
    dr_stop : float
        Time [yr] when drilling should be stopped.

    References
    ----------
    ..[1] Sanyal, S., "Cost of geothermal power and factors that affect
        it," Twenty-Ninth Workshop on Geothermal Reservoir Engineering, 2004.

    """

    def __init__(
        self, capex=3e3, opex_fix=30.0, opex_var=0.0,
        dr_cost=2e6, life=20.0, **kwargs
    ):
        """Initializes the base class.

        """
        # base class parameters
        settings = {
            'name_solid': 'Geothermal',  # label for power output
            'color_solid': '#000000',  # color for power output in powerflow
            'capex': capex,  # CapEx [USD/kW]
            'opex_fix': opex_fix,  # size-dependent OpEx [USD/kW-yr]
            'opex_var': opex_var,  # output-dependent OpEx [USD/kWh-yr]
            'life': life,  # maximum life [yr]
            'data': 0,  # no datasets were used
            'is_re': True  # renewable
        }
        settings.update(kwargs)  # replace default settings with input settings

        # initialize base class
        super().__init__(**settings)

        # adjustable geothermal plant parameters
        self.dr_cost = dr_cost  # drill cost per well [USD]
        self.min_ratio = kwargs.pop('min_ratio', 0.1)  # ratio of min pow to ld
        self.dec_rate_base = kwargs.pop('dec_rate_base', 0.05)  # base d [/yr]
        self.size_base = kwargs.pop('size_base', 50e3)  # base size [kW]
        self.pow_well = kwargs.pop('pow_well', 5e3)  # power per well [kW]
        self.rsv = kwargs.pop('rsv', 0.1)  # minimum reserve capacity
        self.rsv_init = kwargs.pop('rsv_init', 0.2)  # initial minimum reserve
        self.dr_stop = kwargs.pop('dr_stop', 0.67*life)  # stop drilling [yr]

        # initalize geothermal plant parameters
        self.dec_rate = np.array([])  # decline rate [/yr]
        self.num_well = np.array([])  # number of wells

        # update initialized parameters if essential data is complete
        self._update_config()

    def calc_pow(self, pow_req, hr):
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
        pow_gen = np.minimum(  # cannot generate higher than size
            np.maximum(  # cannot generate lower than minimum loading
                pow_req,
                self.min_ratio*self.size
            ),
            self.size
        )

        return pow_gen

    def rec_pow(self, pow_rec, hr):
        """Records the power at a specified time step.

        Parameters
        ----------
        pow_rec : ndarray
            Power [kW] sto be recorded into self.pow[hr, :]
        hr : int
            Time [h] in the simulation.

        """
        # record power generated [kW]
        self.pow[hr, :] = pow_rec

    def cost_calc(self):
        """Calculates the cost of the component.

        """
        # copy required variables
        r = self.rsv  # minimum reserve ratio
        nw = self.num_well  # number of wells
        pw = self.pow_well  # power per well
        cw = self.dr_cost  # drilling cost per well [USD]
        td = self.dr_stop  # time to stop drilling [yr]

        # calculate drilling frequency [yr]
        tc = (pw*nw/((1+r)*self.size)-1)/self.dec_rate
        tc[np.isnan(tc)] = self.yr_proj+1  # prevents nan errors

        # capital costs [USD]
        self.cost_c = (
            self.capex*self.size +  # size [kWh] based
            nw*cw  # drilling costs
        )

        # operating costs [USD]
        opex_fix = self.opex_fix*self.size  # size [kWh] based
        opex_var = self.opex_var*np.sum(self.pow, axis=0)  # output [kWh] based
        self.cost_o = (opex_fix+opex_var)*(
            np.sum(1/(1+self.infl)**np.arange(1, self.yr_proj+1))  # annualize
        )

        # calculate replacement frequency [yr]
        rep_freq = self.life*np.ones(self.num_case)  # frequency of replacement

        # replace nan's in rep_freq to prevent errors with arange
        rep_freq[np.isnan(rep_freq)] = self.yr_proj+1  # no replacement

        # replacement costs [USD], size [kW] based
        disc_rep = np.zeros(self.num_case)  # initialize sum of annuity factors
        for i in range(0, self.num_case):
            disc_rep[i] = np.sum(
                1/(1+self.infl) **
                np.arange(0, self.yr_proj, rep_freq[i])[1:]  # remove year 0
            )
        rep_life = self.repex*disc_rep  # replacement of component

        # drilling new wells
        disc_rep = np.zeros(self.num_case)  # initialize sum of annuity factors
        for i in range(0, self.num_case):
            disc_rep[i] = np.sum(
                1/(1+self.infl) **
                np.arange(0, td, tc[i])[1:]  # remove year 0
            )
        rep_drill = nw*cw*disc_rep  # replacement of component

        # total replacement costs
        self.cost_r = rep_life+rep_drill

        # total cost [USD]
        self.cost = self.cost_c+self.cost_o+self.cost_r

    def _dec_calc(self):
        """Calculates the decline rate [/yr].

        """
        self.dec_rate = (
            self.dec_rate_base *
            self.size*np.log(self.size) /
            (self.size_base*np.log(self.size_base))
        )

    def _config(self):
        """Updates other parameters once essential parameters are complete.

        """
        # update geothermal plant parameters
        self._dec_calc()  # calculate decline rate [/yr]

        # calculate number of wells
        self.num_well = np.ceil(self.size*(1+self.rsv_init)/self.pow_well)
