import numpy as np

from .LoadComponent import LoadComponent

# ignore numpy errors
np.seterr(divide='ignore', invalid='ignore')


class Desalinate(LoadComponent):
    """Reverse osmosis desalination plant module.

    Parameters
    ----------
    data : dict or ndarray
        Dataset. Pass a dict with 'vol' as the key for the hourly water demand
        [m^3] for one year. An ndarray can be passed as well.
    pow_vol : float
        Power required per cubic meter of water produced [kWh/m^3].
    capex : float or callable
        Capital expenses [USD/kWh]. Depends on size. Can be a callable
        function that returns capital cost starting from year zero to end of
        project lifetime.
    opex_fix : float or callable
        Fixed yearly operating expenses [USD/kWh-yr]. Depends on size. Can be
        a callable function that returns the fixed operating cost starting
        from year zero to end of project lifetime.
    opex_var : float or callable
        Variable yearly operating expenses [USD/kWh-yr]. Depends on energy
        produced. Can be a callable function that returns the variable
        operating cost starting from year zero to end of project lifetime.
    life : float
        Maximum life [yr] before the component is replaced.

    Other Parameters
    ----------------
    name_line : str
        Label for the load demand. This will be used in generated graphs and
        files.
    color_line : str
        Hex code (e.g. '#33CC33') of the color for the load demand. This will
        be used in generated graphs.
    num_case : int
        Number of scenarios to simultaneously simulate. This is set by the
        Control module.

    """

    def __init__(
        self, data, pow_vol=4.38, capex=13000.0,
        opex_fix=0.0, opex_var=0.02, life=20.0, **kwargs
    ):
        """Initializes the base class."""

        # base class parameters
        settings = {
            'name_line': 'Desalination',  # label for load
            'color_line': '#666666',  # color for load in powerflow
            'capex': capex,  # CapEx [USD/kWh]
            'opex_fix': opex_fix,  # size-dependent OpEx [USD/kWh-yr]
            'opex_var': opex_var,  # output-dependent OpEx [USD/kWh-yr]
            'life': life,  # maximum life [yr]
            'size': 0.0,  # no size needed, must not be None
            'data': data  # dataset
        }
        settings.update(kwargs)  # replace default settings with input settings

        # initialize base class
        super().__init__(**settings)

        # adjustable RO plant parameters
        self.pow_vol = pow_vol

        # extract dataset
        if isinstance(self.data, dict):  # pass dict
            self.vol = self.data['vol']  # load [kW]
        elif isinstance(self.data, np.ndarray):  # pass ndarray
            self.vol = self.data

        # convert dataset to 1D array
        self.vol = np.ravel(self.vol)

        # determine power requirement [kW]
        self.pow_ld = self.vol*self.pow_vol

        # derivable load parameters
        self.pow_max = np.max(self.pow_ld)  # largest power in load [kW]
        self.enr_tot = np.sum(self.pow_ld)  # yearly consumption [kWh]

        # update initialized parameters if essential data is complete
        self._update_config()

    def get_pow(self, hr):
        """Returns the power output [kW] at the specified time [h].

        Parameters
        ----------
        hr : int
            Time [h] in the simulation.

        """
        # record power
        self.pow = self.pow_ld[hr]*np.ones(self.num_case)

        # get data from the timestep
        return self.pow

    def cost_calc(self, yr_proj, infl):
        """Calculates the cost of the component.

        Parameters
        ----------
        yr_proj : float
            Project lifetime [yr].
        infl : float
            Inflation rate.

        """
        def ann_func(i):
            """Annunity factor"""
            return 1/(1+infl)**i

        # capital costs [USD], size [kWh] based
        if callable(self.capex):  # if experience curve is given
            self.cost_c = np.atleast_1d(self.capex(0)*self.pow_max)
        else:  # if fixed value is given
            self.cost_c = self.capex*self.pow_max

        # fixed operating costs [USD], size [kWh] based
        if callable(self.opex_fix):
            opex_fix = self.pow_max*np.sum(
                self.opex_fix(i)*ann_func(i)
                for i in np.arange(1, yr_proj+1)
            )
        else:
            opex_fix = self.opex_fix*self.pow_max*np.sum(
               1/(1+infl)**np.arange(1, yr_proj+1)
            )

        # variable operating costs [USD], output [kWh] based
        if callable(self.opex_var):
            opex_var = self.enr_tot*np.sum(
                self.opex_var(i)*ann_func(i)
                for i in np.arange(1, yr_proj+1)
            )
        else:
            opex_var = self.opex_var*self.enr_tot*np.sum(
               1/(1+infl)**np.arange(1, yr_proj+1)
            )

        # total operating costs [USD]
        self.cost_o = opex_fix+opex_var

        # calculate replacement frequency [yr]
        rep_freq = self.life*np.ones(self.num_case)  # due to max life [yr]

        # replace nan's in rep_freq to prevent errors with arange
        rep_freq[np.isnan(rep_freq)] = yr_proj+1  # no replacement

        # replacement costs [USD], size [kWh] based
        if callable(self.repex):
            repex = np.zeros(self.num_case)  # initialize replacement costs
            for i in range(0, self.num_case):
                repex[i] = np.sum(  # output [kWh] based
                    self.repex(j)*ann_func(j)
                    for j in np.arange(0, yr_proj, rep_freq[i])
                )-self.repex(0)*ann_func(0)  # no replacement at time zero
        else:
            disc_rep = np.zeros(self.num_case)  # initialize sum of ann factors
            for i in range(0, self.num_case):
                disc_rep[i] = np.sum(
                    1/(1+infl) **
                    np.arange(0, yr_proj, rep_freq[i])[1:]  # remove yr 0
                )
            repex = disc_rep*self.repex
        self.cost_r = self.pow_max*repex

        # total cost [USD]
        self.cost = self.cost_c+self.cost_o+self.cost_r

    def _config(self):
        """Updates other parameters once essential parameters are complete."""

        pass
