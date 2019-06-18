import numpy as np
from scipy.stats import linregress

from .StorageComponent import StorageComponent

# ignore numpy errors
np.seterr(divide='ignore', invalid='ignore')


class VRBEnergy(StorageComponent):
    """Vanadium redox flow battery (VRB) plant module.
    This module models only the energy [kWh] of the VRB. A VRBPower module
    should also be initialized to model the power [kW].

    Parameters
    ----------
    pow_module : VRBPower
        The corresponding power module for the VRB.
    dod_max : float
        Maximum depth of discharge (DOD).
    eff_c : float
        Charging efficiency.
    eff_dc : float
        Discharging efficiency.
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
    num_ser : float
        Number of VRB cells in series in a stack.
    volt_eq : float
        Equilibrium voltage [V] of the VRB redox reaction.
    soc_corr : float
        SOC correction factor.
    temp : float
        Operating temperature [K].
    res_int : float
        Internal resistance [ohm] in the equivalent circuit.
    vsc : float
        Electrolye viscosity [Pa-s].
    stk_l : float
        Length [m] of a single cell in the stack.
    stk_w : float
        Width [m] of a single cell in the stack.
    stk_d : float
        Thickness [m] of a single cell in the stack.
    perm : float
        Permeability [m^2] of porous electrode.
    vol_flow : float
        Volumetric flow rate [m^3/s] of electrolyte per stack.
    pump_eff : float
        Pump efficiency.
    diff_rat : float
        Diffusion ratio of the membrane.

    """

    def __init__(
        self, pow_module, dod_max=0.9, eff_c=0.86, eff_dc=0.86,
        capex=600, opex_fix=0.0, opex_var=0.0, opex_use=0.0,
        life=10, fail_prob=0.01, is_fail=False, **kwargs
    ):
        """Initializes the base class."""

        # initialize base class
        super().__init__(
            None, dod_max, eff_c, eff_dc, np.inf,
            capex, opex_fix, opex_var, opex_use,
            'VRB', '#0000CC', 'VRB SOC', '#FF0000',
            life, fail_prob, is_fail, True, True, False,
            **kwargs
        )

        # get power module
        self.pow_module = pow_module

        # adjustable battery plant parameters
        self.volt_nom = kwargs.pop('volt_nom', 60.0)  # nominal voltage [V]
        self.num_cell = kwargs.pop('num_cell', 15)  # number of cells per stack
        self.volt_eq = kwargs.pop('volt_eq', 1.39)  # eq volt [V] of cell
        self.soc_corr = kwargs.pop('soc_corr', 1.4)  # SOC correction factor
        self.temp = kwargs.pop('temp', 316)  # operating temp [K]
        self.res_int = kwargs.pop('res_int', 0.02)  # res int [ohm] of stack
        self.vsc = kwargs.pop('vsc', 6e-3)  # viscosity [Pa-s] of electrolyte
        self.stk_l = kwargs.pop('stk_l', 0.3)  # length [m] of stack
        self.stk_w = kwargs.pop('stk_w', 0.26)  # width [m] of stack
        self.stk_d = kwargs.pop('stk_d', 3e-3)  # thickness [m] of stack
        self.perm = kwargs.pop('perm', 1.685e-10)  # permeability [m^2]
        self.vol_flow = kwargs.pop('vol_flow', 6.67e-5)  # v fl [m^3/s] of stk
        self.pump_eff = kwargs.pop('pump_eff', 0.5)  # pump efficiency
        self.diff_rat = kwargs.pop('diff_rat', 0.05)  # diffusion ratio

        # derivable battery plant parameters
        self.num_stk = self.volt_nom/(  # num of stacks
            self.num_cell*self.volt_eq
        )

        # initialize battery plant parameters
        self.pow_pump = np.array([])  # pumping power

        # update initialized parameters if essential data is complete
        self.update_init()

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
        # get power per battery unit
        pow_batt = pow_eff*self.num_stk/self.pow_module.size

        # check if power used pump exceeds charging power
        # in this case, do nothing to avoid losing power
        is_dc = np.logical_and.reduce([  # cases where pow pump > pow charge
            pow_batt < 0, pow_batt+self.pow_pump > 0
        ])
        pow_batt[is_dc] = 0  # replace cases with zero (don't charge)

        # add pump power [kW] if battery is discharged
        pow_batt = pow_batt+self.pow_pump*(pow_batt != 0)

        # solve for terminal
        curr_term = (  # terminal current [A]
            (-self.ocv+np.sqrt(self.ocv**2+4*self.res_int*pow_batt*1e3)) /
            (2*self.res_int)
        )

        # solve for diffusion current [A]
        curr_diff = self.diff_rat*curr_term/(2-self.diff_rat)

        # solve for current [A] and voltage [V] at EMF element
        # nan_to_num removes nan values which appear when no power is used
        curr = curr_term-curr_diff  # current [A]
        volt = pow_batt*1e3/curr_term  # EMF voltage [V]

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
        # solve for power [kW] into the battery module
        pow = curr*self.ocv*self.pow_module.size/(1e3*self.num_stk)

        # nan to num to prevent error when size is zero
        soc = np.nan_to_num(self.soc-pow/self.size)

        return soc

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
        # calculate OCV
        ln_socrat = np.log(soc/(1-soc))
        ln_socrat[np.isposinf(ln_socrat)] = 0  # if starting SOC is 1
        ocv = self.num_stk*self.num_cell*(
            self.volt_eq+2*self.soc_corr*8.314*self.temp/96485*ln_socrat
        )

        return ocv

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
        # calculate maximum charge [kW]
        maxc_cap = np.maximum(  # max c due to SOC
            self.size*(1-self.soc) +
            self.pow_pump*self.pow_module.size/self.num_stk,
            0  # prevents negative answers
        )
        maxc_stk = self.pow_module.size  # max c due to max power

        return np.minimum(maxc_cap, maxc_stk)

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
        # calculate maximum discharge [kW]
        maxdc_cap = np.maximum(  # max dc due to SOC
            self.size*(self.soc-(1-self.dod_max)) -
            self.pow_pump*self.pow_module.size/self.num_stk,
            0  # prevents negative answers
        )
        maxdc_stk = self.pow_module.size  # max dc due to max power

        return np.minimum(maxdc_cap, maxdc_stk)

    def _pow_pump(self):
        """Calculates the pump power [kW] for each VRB module."""

        # calculate hydraulic resistance [Pa-s/m^3] of a 1 kW stack
        res_hyd = self.vsc*self.stk_l/(self.perm*self.stk_w*self.stk_d)

        # calculate pressure drop [Pa] of stack of a 1 kW stack
        p_stk = self.vol_flow*res_hyd/(0.7*15.0)  # 15 cells in 1 kW stack

        # calculate power of pump [kW] for the module
        self.pow_pump = self.num_stk*p_stk*self.vol_flow*1e-3/self.pump_eff

    @staticmethod
    def exp_curve(yr, yr_0=2020, **kwargs):
        """Experience curve for VRB.
        Returns the cost [USD/kWh] at the given year

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
        a = kwargs.pop('a', 920)
        b = kwargs.pop('b', 0.168)

        # calculate cost [USD/kWh]
        cap = a_sat/(1+(a_sat-a_base)/a_base*np.exp(-r*(yr+(yr_0-2011))))
        cost = a*cap**(-b)

        return cost

    def _update_init(self):
        """Updates other parameters once essential parameters are complete."""

        # update battery plant parameters
        self._pow_pump()  # pump power [kW] of a 1 kW VRB stack
