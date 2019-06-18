import numpy as np
from scipy.stats import linregress
from scipy.interpolate import InterpolatedUnivariateSpline
import rainflow

from .StorageComponent import StorageComponent

# ignore numpy errors
np.seterr(divide='ignore', invalid='ignore')


class IdealStorage(StorageComponent):
    """Ideal storage module.

    Parameters
    ----------
    eff_c : float
        Charging efficiency.
    eff_dc : float
        Discharging efficiency.
    dod_max : float
        Maximum depth of discharge (DOD).
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
    repex : float or callable
        Replacement costs [USD/kWh]. Depends on size. Equal to CapEx by
        default. Can be a callable function that returns replacement costs
        starting from year zero to end of project lifetime.
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
    size_nom : float
        Size [kWh] per battery.
    deg_life : float
        Battery life [yr] if battery is repeatedly cycled to its maximum
        DOD.
    deg_max : float
        Maximum amount of degradation. Default value is 0.2.
    deg_x : ndarray
        The DOD in a set of number of cycles vs DOD data.
    deg_y : ndarray
        The number of cycles before replacement in a set of number of
        cycles vs DOD data.
    c_x : ndarray
        The SOC in a set of internal resistance while charging vs SOC data.
    c_y : ndarray
        The internal resistance [ohm] in a set of internal resistance
        while charging vs SOC data.
    dc_x : ndarray
        The SOC in a set of internal resistance while discharging vs SOC
        data.
    dc_y : ndarray
        The internal resistance [ohm] in a set of internal resistance
        while discharging vs SOC data.
    ocv_x : ndarray
        The DOD in a set of OCV vs DOD data.
    ocv_y : ndarray
        The OCV [V] in a set of OCV vs DOD data.

    """

    def __init__(
        self, eff_c=np.sqrt(0.9), eff_dc=np.sqrt(0.9), dod_max=0.8,
        capex=500.0, opex_fix=5.0, opex_var=0.0,
        life=10.0, **kwargs
    ):
        """Initializes the base class.

        """
        # base class parameters
        settings = {
            'name_solid': 'Ideal Storage',  # label for power output
            'color_solid': '#0000CC',  # color for power output in powerflow
            'name_line': 'Ideal Storage SOC',  # label for SOC
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

        # adjustable battery plant parameters
        self.eff_c = eff_c  # charging efficiency
        self.eff_dc = eff_dc  # discharging efficiency
        self.dod_max = dod_max  # maximum DOD
        self.volt_str = kwargs.pop('volt_str', 12.0)  # voltage of string
        self.volt_nom = kwargs.pop('volt_nom', 6.0)  # nominal voltage
        self.enr_nom = kwargs.pop('enr_nom', 1.20)  # size per batt [kWh]
        self.curr_max = kwargs.pop('curr_max', 167)  # maximum current [A]

        # initialize electrical parameters
        self.curr = np.array([])  # current [A] at time t
        self.volt = np.array([])  # voltage [V] at time t
        self.ocv = np.array([])  # OCV [V] at time t

        # update initialized parameters if essential data is complete
        self._update_config()

    def cost_calc(self):
        """Calculates the cost of the component.

        """
        def ann_func(i):
            """Annunity factor"""
            return 1/(1+self.infl)**i

        # capital costs [USD], size [kWh] based
        if callable(self.capex):  # if experience curve is given
            self.cost_c = np.atleast_1d(self.capex(0)*self.size)
        else:  # if fixed value is given
            self.cost_c = self.capex*self.size

        # fixed operating costs [USD], size [kWh] based
        if callable(self.opex_fix):
            opex_fix = self.size*np.sum(
                self.opex_fix(i)*ann_func(i)
                for i in np.arange(1, self.yr_proj+1)
            )
        else:
            opex_fix = self.opex_fix*self.size*np.sum(
               1/(1+self.infl)**np.arange(1, self.yr_proj+1)
            )

        # variable operating costs [USD], output [kWh] based
        if callable(self.opex_var):
            opex_var = np.sum(self.pow, axis=0)*np.sum(
                self.opex_var(i)*ann_func(i)
                for i in np.arange(1, self.yr_proj+1)
            )
        else:
            opex_var = self.opex_var*np.sum(self.pow, axis=0)*np.sum(
               1/(1+self.infl)**np.arange(1, self.yr_proj+1)
            )

        # total operating costs [USD]
        self.cost_o = opex_fix+opex_var

        # calculate replacement frequency [yr]
        rep_freq = self.life*np.ones(self.num_case)  # due to max life [yr]

        # replace nan's in rep_freq to prevent errors with arange
        rep_freq[np.isnan(rep_freq)] = self.yr_proj+1  # no replacement

        # replacement costs [USD], size [kWh] based
        if callable(self.repex):
            repex = np.zeros(self.num_case)  # initialize replacement costs
            for i in range(0, self.num_case):
                repex[i] = np.sum(  # output [kWh] based
                    self.repex(j)*ann_func(j)
                    for j in np.arange(0, self.yr_proj, rep_freq[i])
                )-self.repex(0)*ann_func(0)  # no replacement at time zero
        else:
            disc_rep = np.zeros(self.num_case)  # initialize sum of ann factors
            for i in range(0, self.num_case):
                disc_rep[i] = np.sum(
                    1/(1+self.infl) **
                    np.arange(0, self.yr_proj, rep_freq[i])[1:]  # remove yr 0
                )
            repex = disc_rep*self.repex
        self.cost_r = self.size*repex

        # total cost [USD]
        self.cost = self.cost_c+self.cost_o+self.cost_r

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

        # determine power [kW] going in or out of plant
        pow_in = pow_rec*(pow_rec < 0)*self.eff_c
        pow_out = pow_rec*(pow_rec > 0)/self.eff_dc

        # solve for current [A] and terminal voltage [V] at each battery
        self._update_iv(pow_in+pow_out, hr)

        # solve for the SOC
        self._update_soc(hr)  # updates self.soc[hr+1, :]

        # update max powers [kW]
        self._update_max_pow(hr)  # updates self.powmaxc, self.powmaxdc

    def _config(self):
        """Updates other parameters once essential parameters are complete.

        """
        # update battery plant parameters
        self.is_full = np.ones(self.num_case, dtype=bool)  # True if batt full

        # update electrical parameters
        self.curr = np.zeros(self.num_case)  # current [A] at t
        self.volt = np.zeros(self.num_case)  # volt [V] at t

        # calculate number of strings
        self.num_batt_str = self.volt_str/self.volt_nom
        self.num_str = self.size/(self.enr_nom*self.num_batt_str)

        # update max powers
        self.pow_maxc = np.zeros(self.num_case)  # max charging power [kW]
        self.pow_maxdc = self.size*self.dod_max  # max discharging power [kW]
        self._update_max_pow(-1)  # recalculate max powers

    def _update_iv(self, pow_dc, hr):
        """Updates the current [A] and terminal voltage [V].

        Parameters
        ----------
        pow_dc : ndarray
            Power [kW] drawn from the plant.
        hr : int
            Time [h] in the simulation.

        """
        # get power per string [kW]
        pow_str = pow_dc/self.num_str

        # get current per battery [A]
        curr_batt = pow_str*1e3/self.volt_str

        # update current and voltage
        # nan_to_num removes nan values which appear when no power is used
        self.curr = curr_batt  # current [A]
        self.volt = self.volt_nom  # terminal voltage [V]

    def _update_soc(self, hr):
        """Updates the state of charge of the battery.

        Parameters
        ----------
        hr : int
            Time [h] in the simulation.

        """
        # prevent hr+1 from going beyond array size
        if hr != 8759:

            # solve for power [kW] into the battery
            pow_eff = self.curr*self.volt/1e3

            # update SOC
            # put nan_to_num to avoid error when size is zero
            soc_new = np.minimum(
                np.nan_to_num(self.soc[hr, :]-pow_eff/self.enr_nom),
                1  # maximum SOC
            )

            # check for cases where battery is about to go below min SOC
            is_trn = np.logical_and(
                soc_new <= 1-self.dod_max,  # new SOC is below min SOC and
                self.soc[hr, :] > 1-self.dod_max  # previous SOC is above min
            )

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

            # calculate maximum charge [kW]
            maxc_cap = np.maximum(  # max c due to SOC
                self.size*(1-self.soc[hr+1, :]),
                0
            )
            maxc_curr = (  # max c due to max curr
                self.curr_max*self.volt_str*self.num_str *
                np.ones(self.num_case)
            )
            self.pow_maxc = np.minimum(maxc_cap, maxc_curr)

            # calculate maximum discharge [kW]
            maxdc_cap = np.maximum(  # max dc due to SOC
                self.size *
                (self.soc[hr+1, :]-(1-self.dod_max)),
                0
            )
            maxdc_curr = (  # max c due to max curr
                self.curr_max*self.volt_str*self.num_str *
                np.ones(self.num_case)
            )
            self.pow_maxdc = np.minimum(maxdc_cap, maxdc_curr)
