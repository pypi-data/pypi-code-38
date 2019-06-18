import numpy as np
from scipy.stats import linregress
from scipy.interpolate import InterpolatedUnivariateSpline

from .StorageComponent import StorageComponent

# ignore numpy errors
np.seterr(divide='ignore', invalid='ignore')


class H2Storage(StorageComponent):
    """Hydrogen storage module.

    Parameters
    ----------
    fc_module : HydrogenPower
        The corresponding fuel cell module for the hydrogen module.
    el_module : HydrogenPower
        The corresponding electrolyzer module for the hydrogen module.
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

    Notes
    -----
    This module models only the energy [kWh] of the hydrogen system. A
    H2FuelCell and H2Electrolyzer module should also be initialized to model
    the power [kW].

    """

    def __init__(
        self, fc_module, el_module, dod_max=0.9, eff_c=0.95, eff_dc=0.95,
        capex=500.0, opex_fix=5.0, opex_var=0.0, opex_use=0.0,
        life=10.0, fail_prob=0.01, is_fail=False, **kwargs
    ):
        """Initializes the base class.

        """
        # initialize base class
        super().__init__(
            None, dod_max, eff_c, eff_dc, np.inf,
            capex, opex_fix, opex_var, opex_use,
            'H2 Storage', '#0000CC', 'H2 SOC', '#FF0000',
            life, fail_prob, is_fail, True, True, False, **kwargs
        )

        # get fuel cell and electrolyzer module
        self.fc_module = fc_module
        self.el_module = el_module

        # update initialized parameters if essential data is complete
        self._update_init()

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

        return (pow_eff, 1)

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
        delta_soc = curr/self.size

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
        return 1

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
        maxc_el = self.el_module.size  # max c due to max power

        return maxc_el

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
        maxdc_fc = self.fc_module.size  # max dc due to max power

        return maxdc_fc
