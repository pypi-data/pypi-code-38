import copy

import numpy as np
from scipy.stats import linregress
from scipy.interpolate import InterpolatedUnivariateSpline

from .StorageComponent import StorageComponent

# ignore numpy errors
np.seterr(divide='ignore', invalid='ignore')


class PbAcid(StorageComponent):
    """Lead acid battery plant module.

    Parameters
    ----------
    data : ndarray
        Dataset. Set to zero if no dataset is required.
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
    name_solid : str
        Label used for the power output. Appears as a solid area in powerflows
        and as a header in .csv files. Usually the name of the component.
    color_solid : str
        Hex code (e.g. '#33CC33') of the color corresponding to name_solid.
        Appears in the solid area in powerflows.
    name_line : str
        Label used for the power output. Appears as a line in powerflows
        and as a header in .csv files. Usually the name of a Load component or
        Storage state of charge.
    color_line : str
        Hex code (e.g. '#33CC33') of the color corresponding to name_line.
        Appears in the line in powerflows.
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
    size_nom : float
        Size [kWh] per battery.
    cap_ratio : float
        Capacity ratio of the battery. Uses the kinetic battery model
    rate_const : float
        Rate constant [/hr] of the battery. Uses the kinetic battery model.
    res_int : float
        Internal resistance [ohm] of the battery. Uses the Rint model.
    ocv_x : ndarray
        The DOD in a set of OCV vs DOD data.
    ocv_y : ndarray
        The OCV [V] in a set of OCV vs DOD data.

    """

    def __init__(
        self, dod_max=0.6, eff_c=0.8, eff_dc=0.8, c_rate=1,
        capex=500.0, opex_fix=5.0, opex_var=0.0, opex_use=0.0,
        life=5, fail_prob=0.01, is_fail=False, **kwargs
    ):
        """Initializes the base class."""

        # initialize component
        super().__init__(
            None, dod_max, eff_c, eff_dc, c_rate,
            capex, opex_fix, opex_var, opex_use,
            'Pb Acid', '#0000CC', 'Pb Acid SOC', '#FF0000',
            life, fail_prob, is_fail, True, False, True,
            **kwargs
        )

        # adjustable battery plant parameters
        self.size_nom = kwargs.pop('size_nom', 0.006)  # size per batt [kWh]
        self.cap_ratio = kwargs.pop('cap_ratio', 0.308)  # capacity ratio
        self.rate_const = kwargs.pop('rate_const', 2.86)  # rate constant [/hr]

        # initialize battery plant parameters
        self.enr_av = np.array([])  # available energy [kWh] at time t
        self.enr_bd = np.array([])  # bounded energy [kWh] at time t
        self.num_batt = np.array([])  # number of battery units

        # adjustable electrical parameters
        self.curr_max = kwargs.pop('curr_max', 4)
        self.res_int = kwargs.pop('res_int', 5e-3)
        self.ocv_x = kwargs.pop(  # depth of discharge
            'ocv_x', np.array([0, 0.1, 0.52, 0.77, 1])
        )
        self.ocv_y = kwargs.pop(  # corresponding number of cycles
            'ocv_y', np.array([6.1, 6, 5.75, 5.5, 5.4])
        )

        # derivable electrical parameters
        self.ocv_func = InterpolatedUnivariateSpline(
            self.ocv_x, self.ocv_y, k=1  # OCV vs DOD
        )

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

        # solve for current when discharging
        a = -self.res_int
        b = self.ocv
        c = -pow_batt*1e3

        # update current and voltage
        curr = np.nan_to_num((-b+np.sqrt(b**2-4*a*c))/(2*a))
        volt = np.nan_to_num(pow_batt*1e3/curr)  # terminal voltage [V]

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
        delta_soc = curr*self.ocv/(self.size_nom*1e3)

        # update available and bounded charges
        self.get_av()

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

        return self.ocv_func(1-self.soc)

    def _get_powmaxc(self, hr):
        """Updates the maximum possible charging power.

        Parameters
        ----------
        hr : int
            Time [h] in the simulation.

        Returns
        -------
        pow_maxc : ndarray
            Maximum possible charging power at next time step.

        Notes
        -----
        This function can be modified by the user. At this point, self.curr,
        self.volt, self.soc, and self.ocv have already been updated according
        to the values given by self._get_iv, self._get_soc, and self._get_ocv

        """
        # copy required variables
        k = self.rate_const   # rate constant [/hr]
        c = self.cap_ratio  # capacity ratio
        ekt = np.exp(-k)  # exp(-kdt)
        p_av = self.enr_av  # available energy [kWh] at time t
        p_tot = self.enr_av+self.enr_bd  # total energy [kWh] at time t
        p_max = self.size_nom  # size of battery [kWh]

        # calculate maximum charge [kW]
        maxc_kibam = (  # max c due to kinetics
            (-k*c*p_max+k*p_av*ekt+p_tot*k*c*(1-ekt)) /
            (1-ekt+c*(k-1+ekt))
        )
        maxc_crate = (  # max c due to C-rate
            -(1-np.exp(-self.c_rate)) *
            (p_max-p_tot)
        )
        maxc_curr = (  # max c due to max current
            self.curr_max*self.ocv/1e3
        )
        maxc_kibam = np.maximum(maxc_kibam, 0)
        maxc_crate = np.maximum(maxc_crate, 0)

        # get overall max charge per battery
        maxc_all = np.minimum.reduce([maxc_kibam, maxc_crate, maxc_curr])

        return maxc_all*self.num_batt

    def _get_powmaxdc(self, hr):
        """Updates the maximum possible discharging power.

        Parameters
        ----------
        hr : int
            Time [h] in the simulation.

        Returns
        -------
        pow_maxdc : ndarray
            Maximum possible discharging power at next time step.

        Notes
        -----
        This function can be modified by the user. At this point, self.curr,
        self.volt, self.soc, and self.ocv have already been updated according
        to the values given by self._get_iv, self._get_soc, and self._get_ocv

        """
        # copy required variables
        k = self.rate_const   # rate constant [/hr]
        c = self.cap_ratio  # capacity ratio
        ekt = np.exp(-k)  # exp(-kdt)
        p_av = self.enr_av  # available energy [kWh] at time t
        p_tot = self.enr_av+self.enr_bd  # total energy [kWh] at time t

        # calculate maximum discharge [kW]
        maxdc_kibam = (  # max dc due to kinetics
            (k*p_av*ekt+p_tot*k*c*(1-ekt)) /
            (1-ekt+c*(k-1+ekt))
        )

        return maxdc_kibam*self.num_batt

    def get_av(self):
        """Solves for available and bounded energies [kWh]."""

        # solve for power [kW] into the battery
        pow_batt = self.curr*self.ocv*self.num_batt

        # copy required variables
        k = self.rate_const   # rate constant [/hr]
        c = self.cap_ratio  # capacity ratio
        ekt = np.exp(-k)  # exp(-kdt)
        p_av = self.enr_av  # available energy [kWh] at time t
        p_bd = self.enr_bd  # bounded energy [kWh] at time t
        p_tot = self.enr_av+self.enr_bd  # total energy [kWh] at time t

        # update available energy [kWh]
        self.enr_av = (
            p_av*ekt +
            (p_tot*k*c+pow_batt)*(1-ekt)/k +
            pow_batt*c*(k-1+ekt)/k
        )

        # update bounded energy [kWh]
        self.enr_bd = (
            p_bd*ekt +
            p_tot*(1-c)*(1-ekt) +
            pow_batt*(1-c)*(k-1+ekt)/k
        )

    def _update_init(self):
        """Updates other parameters once essential parameters are complete."""

        # update battery plant parameters
        self.enr_av = self.cap_ratio*self.size_nom  # available energy [kWh]
        self.enr_bd = (1-self.cap_ratio)*self.size_nom  # bounded energy [kWh]
        self.num_batt = self.size/self.size_nom
