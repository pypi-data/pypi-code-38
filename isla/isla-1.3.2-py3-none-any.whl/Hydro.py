import numpy as np

from .AdjustComponent import AdjustComponent


class Hydro(AdjustComponent):
    """Hydro plant module.

    Parameters
    ----------
    data : dict or ndarray
        Dataset. Pass a dict with 'v_flow' as the key for the hourly load
        demand [kW] for one year. An ndarray can be passed as well.
    head : float
        Available head [m].
    capex : float
        Capital expenses [USD/kW]. Depends on size.
    opex_fix : float
        Fixed yearly operating expenses [USD/kW-yr]. Depends on size.
    opex_var : float
        Variable yearly operating expenses [USD/kW-yr]. Depends on energy
        produced.
    fl_cost : float
        Initial cost of fuel [USD/L].
    fl_infl : float
        Inflation rate of fuel.
    life : float
        Maximum life [yr] before the component is replaced.

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
    eff : float
        Turbine efficiency.
    min_ratio : float
        Ratio of minimum power output [kW] to the load in the current time
        step.

    References
    ----------
    ..[1] HOMER, "How HOMER calculates the hydro power output," n.d.

    """

    def __init__(
        self, data, head, capex=3500.0,
        opex_fix=35.0, opex_var=0.0, life=20.0, **kwargs
    ):
        """Initializes the base class.

        """
        # base class parameters
        settings = {
            'name_solid': 'Hydro',  # label for power output
            'color_solid': '#CC33CC',  # color for power output in powerflow
            'capex': capex,  # CapEx [USD/kW]
            'opex_fix': opex_fix,  # size-dependent OpEx [USD/kW-yr]
            'opex_var': opex_var,  # output-dependent OpEx [USD/kWh-yr]
            'life': life,  # maximum life [yr]
            'data': data,  # dataset
            'is_re': True  # renewable
        }
        settings.update(kwargs)  # replace default settings with input settings

        # initialize base class
        super().__init__(**settings)

        # extract dataset
        if isinstance(self.data, dict):  # pass dict
            self.v_flow = self.data['v_flow']  # vol flow rate [m^3/s]
        elif isinstance(self.data, np.ndarray):  # pass ndarray
            self.v_flow = self.data

        # adjustable hydro parameters
        self.head = head  # available head [m]
        self.eff = kwargs.pop('eff', 0.8)  # turbine efficiency
        self.min_ratio = kwargs.pop('min_ratio', 0.1)  # ratio of min pow to ld

        # initialize hydro parameters
        self.pow_maxf = np.array([])  # maximum power [kW] due to flow

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
        pow_gen = np.minimum(  # cannot generate higher than upper bound
            np.maximum(pow_req, self.min_ratio*self.size),  # minimum to gen
            np.minimum(self.pow_maxf[hr, :], self.size)  # upper bound
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
        # capital costs [USD]
        self.cost_c = self.capex*self.size  # size [kW] based

        # operating costs [USD]
        opex_fix = self.opex_fix*self.size  # size [kW] based
        opex_var = self.opex_var*np.sum(self.pow, axis=0)  # output [kWh] based
        self.cost_o = (opex_fix+opex_var)*(
            np.sum(1/(1+self.infl)**np.arange(1, self.yr_proj+1))  # annualize
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

    def _config(self):
        """Updates other parameters once essential parameters are complete.

        """
        # calculate generated power [kW]
        self.pow_maxf = np.repeat(  # power [kW] due to flow
            np.atleast_2d(self.eff*9.81*self.head*self.v_flow).T,
            self.num_case, axis=1  # expand
        )
