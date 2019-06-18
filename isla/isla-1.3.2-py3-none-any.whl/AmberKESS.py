import numpy as np
from scipy.stats import linregress
from scipy.interpolate import InterpolatedUnivariateSpline

from .StorageComponent import StorageComponent

# ignore numpy errors
np.seterr(divide='ignore', invalid='ignore')


class AmberKESS(StorageComponent):
    """Kinetic energy storage system (KESS) module.

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
    volt_nom : float
        Nominal voltage [V] per battery.

    """

    def __init__(
        self, dod_max=1, eff_c=0.93, eff_dc=0.93, c_rate=0.25,
        capex=600.0, opex_fix=6.0, opex_var=0.0, opex_use=0.0,
        life=20, fail_prob=0.01, is_fail=False, **kwargs
    ):
        """Initializes the base class."""

        # initialize component
        super().__init__(
            None, dod_max, eff_c, eff_dc, c_rate,
            capex, opex_fix, opex_var, opex_use,
            'KESS', '#0000CC', 'KESS SOC', '#FF0000',
            life, fail_prob, is_fail, True, True, False,
            **kwargs
        )

        # get parameters
        self.volt_nom = kwargs.pop('volt_nom', 800.0)

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
        curr = pow_eff/self.volt_nom

        return (curr, self.volt_nom)

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
        delta_soc = curr*volt/self.size

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
        return self.volt_nom

    def _update_init(self):
        """Updates other parameters once essential parameters are complete."""
        pass
