import copy

import numpy as np
import scipy as sp
from scipy.stats import linregress
from scipy.interpolate import InterpolatedUnivariateSpline
from scipy.integrate import simps
from scipy.optimize import curve_fit

from .StorageComponent import StorageComponent

# ignore numpy errors
np.seterr(divide='ignore', invalid='ignore')


class LiIon(StorageComponent):
    """Lithium-ion (Li-ion) battery plant module.

    Parameters
    ----------
    dod_max : float
        Maximum depth of discharge (DOD).
    eff_c : float
        Charging efficiency.
    eff_dc : float
        Discharging efficiency.
    c_rate : float
        C-rate [kW/kWh] of the battery.
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
    fail_prob : float
        Probability of failure of the component.
    is_fail : bool
        True if failure probabilities should be simulated.

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
    cap_nom : float
        Capacity [Ah] per battery.
    volt_nom : float
        Voltage [V] per battery.
    res1 : float
        Resistor [ohm] in series with the battery in the equivalent circuit.
        Uses Thevenin model.
    res2 : float
        Resistor [ohm] in the RC component in the equivalent circuit.
    capac : float
        Capacitor [F] in the RC component in the equivalent circuit.
    ocv_x : ndarray
        The DOD in a set of OCV vs DOD data.
    ocv_y : ndarray
        The OCV [V] in a set of OCV vs DOD data.
    rate_x : ndarray
        The current [A] in a set of rate factor vs current data.
    rate_y : ndarray
        The rate factor in a set of rate factor vs current data. The rate
        factor accounts for changes in capacity with various currents.

    """

    def __init__(
        self, dod_max=0.8, eff_c=0.95, eff_dc=0.95, c_rate=1,
        capex=300.0, opex_fix=3.0, opex_var=0.0, opex_use=0.0,
        life=10, fail_prob=0.01, is_fail=False, **kwargs
    ):
        """Initializes the base class."""

        # initialize component
        super().__init__(
            None, dod_max, eff_c, eff_dc, c_rate,
            capex, opex_fix, opex_var, opex_use,
            'Li-Ion', '#0000CC', 'Li-Ion SOC', '#FF0000',
            life, fail_prob, is_fail, True, True, False, **kwargs
        )

        # adjustable battery plant parameters
        self.cap_nom = kwargs.pop('cap_nom', 100.0)  # cap per batt [Ah]
        self.volt_nom = kwargs.pop('volt_nom', 48.0)  # volt per batt [V]

        # derivable battery plant parameters
        self.size_nom = self.cap_nom*self.volt_nom/1e3  # size per batt [kWh]

        # initialize battery plant parameters
        self.num_batt = np.array([])  # number of batteries

        # adjustable electrical parameters
        self.res1 = kwargs.pop('res1', 0.44)  # R1 in equivalent circuit [ohm]
        self.res2 = kwargs.pop('res2', 0.16)  # R2 in equivalent circuit [ohm]
        self.capac = kwargs.pop('capac', 16)  # C in equivalent circuit [F]
        self.ocv_x = kwargs.pop(  # depth of discharge
            'ocv_x',
            np.array([
                0.0667, 0.1333, 0.2000, 0.2667,
                0.3333, 0.4000, 0.4667, 0.5333,
                0.6000, 0.6667, 0.7333, 0.8000,
                0.8667, 0.9333, 1.0000
            ])
        )
        self.ocv_y = kwargs.pop(  # corresponding OCV [V]
            'ocv_y',
            np.array([
                51.32, 51.20, 51.16, 51.12,
                51.08, 50.96, 50.88, 50.72,
                50.64, 50.40, 50.20, 50.00,
                49.72, 49.16, 48.24
            ])
        )
        self.rate_x = kwargs.pop(  # current [A]
            'rate_x', np.array([0.6, 1.4, 2.8, 5.6])
        )
        self.rate_y = kwargs.pop(  # corresponding rate factor
            'rate_y', np.array([0.96, 1, 1.01, 1.05])
        )

        # derivable electrical parameters
        ocv_param, err = curve_fit(  # curve fit of OCV vs DOD
            self._ocv_curve, 1-self.ocv_x, self.ocv_y
        )
        self.ocv_func = lambda v: self._ocv_curve(  # OCV as fxn of DOD
            v, ocv_param[0], ocv_param[1], ocv_param[2], ocv_param[3],
            ocv_param[4], ocv_param[5], ocv_param[6], ocv_param[7],
            ocv_param[8], ocv_param[9], ocv_param[10], ocv_param[11]
        )
        self.rate_func = InterpolatedUnivariateSpline(  # RF as fxn of curr
            self.rate_x, self.rate_y, ext='const'
        )

        # intialize electrical parameters
        self.ocv1 = np.array([])  # OCV [V] at time t+1
        self.volt_th = np.array([])  # voltage at RC circuit [V]

        # update initialized parameters if essential data is complete
        self.update_init()

    def _rec_pow(self, pow_rec, hr):
        """Records parameters at the specified time step.

        Parameters
        ----------
        pow_rec : ndarray
            Power [kW] to be recorded by component.
        hr : int
            Time [h] in the simulation.

        Notes
        -----
        This function can be modified by the user.

        """
        super()._rec_pow(pow_rec, hr)

    def _ocv_curve(self, soc, k0, k1, k2, k3, k4, k5, a1, a2, a3, a4, b1, b2):
        """Empirical equation of OCV vs SOC.

        Parameters
        ----------
        soc : ndarray
            State of charge of battery.
        k0, k1, k2, k3, k4, k5, a1, a2, a3, a4, b1, b2 : float
            Empirical constants.

        Returns
        -------
        ndarray
            OCV [V] of battery.

        References
        ----------
        ..[1] Weng, C. et. al., "An open-circuit-voltage model of lithium-ion
          batteries for effective incremental capacity analysis," 2013.

        """
        # calculate terms
        term1 = k1/(1+np.exp(a1*(soc-b1)))
        term2 = k2/(1+np.exp(a2*(soc-b2)))
        term3 = k3/(1+np.exp(a3*(soc-1)))
        term4 = k4/(1+np.exp(a4*soc))

        return term1+term2+term3+term4+k0+k5*soc

    def _get_iv(self, hr, pow_eff):
        """Get current and voltage at EMF source.

        Parameters
        ----------
        hr : int
            Time [h] in the simulation.
        pow_eff : ndarray
            Power [kW] into the equivalent circuit corrected for efficiency.

        Returns
        -------
        curr : ndarray
            Current [A] into the EMF source.
        volt : ndarray
            Voltage [V] drop in the EMF source.

        Notes
        -----
        This function can be modified by the user. Positive values indicate
        discharging. The EMF source being referred to is the EMF source in the
        equivalent circuit.

        """
        # solve for power per battery
        pow_batt = pow_eff/self.num_batt

        # solve for current and terminal voltage
        self.volt_th = (self.curr-self.volt_th/self.res2)/self.capac
        volt = self.ocv-self.volt_th-self.curr*self.res1
        curr = np.nan_to_num(pow_batt*1e3/volt)  # terminal voltage [V]

        return (curr, volt)

    def _get_soc(self, hr, curr, volt):
        """Get the SOC of the next time step.

        Parameters
        ----------
        hr : int
            Time [h] in the simulation.
        curr : ndarray
            Current [A] at the present time step.
        volt : ndarray
            Voltage [V] at the present time step.

        Returns
        -------
        soc : ndarray
            State of charge at the next time step.

        Notes
        -----
        This function can be modified by the user. Positive values indicate
        discharging. At this point, self.curr and self.volt have already been
        updated according to the values given in self._get_iv

        """
        # get change in soc
        delta_soc = curr*self.ocv*self.rate_func(self.curr)/(self.size_nom*1e3)

        return self.soc-delta_soc

    def _get_ocv(self, hr, soc):
        """Get the SOC of the next time step.

        Parameters
        ----------
        hr : int
            Time [h] in the simulation.
        soc : ndarray
            State of charge at the next time step.

        Returns
        -------
        ocv : ndarray
            Open circuit voltage of the EMF element at the next time step.

        Notes
        -----
        This function can be modified by the user. At this point, self.curr,
        self.volt, and self.soc have already been updated according to the
        values given in self._get_iv and self._get_soc.

        """
        # update OCV
        self.ocv1 = copy.deepcopy(self.ocv)  # pass by value

        return self.ocv_func(soc)

    @staticmethod
    def exp_curve(yr, yr_0=2020, **kwargs):
        """Experience curve for Li-ion.
        Returns the cost [USD/kWh] at the given year

        Parameters
        ----------
        yr : int
            Index of the year.
        yr_0 : int
            Year where index is set to zero.

        """
        # get regression parameters
        a_sat = kwargs.pop('a_sat', 2600)
        a_base = kwargs.pop('a_base', 1)
        r = kwargs.pop('r', 0.348)
        a = kwargs.pop('a', 868)
        b = kwargs.pop('b', 0.251)

        # calculate cost [USD/kWh]
        cap = a_sat/(1+(a_sat-a_base)/a_base*np.exp(-r*(yr+(yr_0-2011))))
        cost = a*cap**(-b)

        return cost

    def _update_init(self):
        """Updates other parameters once essential parameters are complete."""

        # update battery plant parameters
        self.num_batt = self.size/self.size_nom  # number of batteries

        # update electrical parameters
        self.ocv1 = self._get_ocv(0, 1)*np.ones(self.num_case)  # OCV at t-1
        self.volt_th = np.zeros(self.num_case)  # voltage at the RC circuit [V]
