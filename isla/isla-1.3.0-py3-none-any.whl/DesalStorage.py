import numpy as np

from .StorageComponent import StorageComponent

# ignore numpy errors
np.seterr(divide='ignore', invalid='ignore')


class DesalStorage(StorageComponent):
    """Base class for components that supplement other components.

    Parameters
    ----------
    pw_ratio : float
        Power required to prodcue a unit of water [kW/m^3].
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

    Other Parameters
    ----------------
    num_case : int
        Number of scenarios to simultaneously simulate. This is set by the
        Control module.

    """

    def __init__(
        self, pw_ratio=4.38, lvl_min=0.1, capex=1000.0, opex_fix=10.0,
        opex_var=0.0, opex_use=0.0, life=20.0, in_lcoe=False, **kwargs
    ):
        """Initializes the base class."""

        # initialize component
        super().__init__(
            None, 1.0, 1.0, 1.0, np.inf,
            capex, opex_fix, opex_var, opex_use,
            'Desal Storage', None, 'Water Storage', '#33CC33',
            life, 0.0, False, True, False, True, **kwargs
        )

        # initialize sink parameters
        self.wat_cost = np.array([])

        # store storage parameters
        self.pw_ratio = pw_ratio
        self.lvl_min = lvl_min
        self.in_lcoe = in_lcoe

    def rec_pow(self, pow_rec, hr):
        """Records the power at a specified time step.

        Parameters
        ----------
        pow_rec : ndarray
            Power [kW] to be recorded by component.
        hr : int
            Time [h] in the simulation.

        """
        pass

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
        pass

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
        pass

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
        pass

    def get_powmaxc(self, hr):
        """Updates the maximum possible charging power.

        Parameters
        ----------
        hr : int
            Time [h] in the simulation.

        Returns
        -------
        pow_maxc : ndarray
            Maximum possible charging power at next time step.

        """
        return np.zeros(num_case)

    def get_powmaxdc(self, hr):
        """Updates the maximum possible discharging power.

        Parameters
        ----------
        hr : int
            Time [h] in the simulation.

        Returns
        -------
        pow_maxdc : ndarray
            Maximum possible discharging power at next time step.

        """
        return np.zeros(num_case)

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
        pass

    def cost_calc(self, yr_proj, infl):
        """Calculates the cost of the component.

        Parameters
        ----------
        yr_proj : float
            Project lifetime [yr].
        infl : float
            Inflation rate.

        """
        # calculate costs
        cost_data = self._cost_calc(yr_proj, infl)
        cost_c, cost_of, cost_ov, cost_ou, cost_r, cost_f = cost_data
        self.wat_cost = cost_c+cost_of+cost_ov+cost_ou+cost_r+cost_f

        # do not include in electrical costs
        self.cost_c = self.in_lcoe*cost_c
        self.cost_of = self.in_lcoe*cost_of
        self.cost_ov = self.in_lcoe*cost_ov
        self.cost_ou = self.in_lcoe*cost_ou
        self.cost_r = self.in_lcoe*cost_r
        self.cost_f = self.in_lcoe*cost_f
        self.cost = self.in_lcoe*self.wat_cost

    def update_init(self):
        """Updates initialized parameters once size and num_case are given."""

        # check if all essential parameters are in
        if (self.num_case is not None and self.size is not None):

            # prevents optimization errors
            if self.size.size == self.num_case:

                # update power arrays
                self.pow = np.zeros(self.num_case)  # instantaneous power [kW]
                self.enr_tot = np.zeros(self.num_case)  # tot energy out [kWh]
                self.use_tot = np.zeros(self.num_case)  # tot energy out [kWh]
                self.is_full = np.ones(self.num_case)
                self.noise = np.ones(self.num_case)

                # update storage parameters
                self.soc = np.ones(self.num_case)  # SOC
                self.pow_maxc = np.zeros(self.num_case)
                self.pow_maxdc = np.zeros(self.num_case)

                # update cost parameters
                self.cost_c = np.zeros(self.num_case)  # capital cost [$]
                self.cost_of = np.zeros(self.num_case)  # fixed opex [$]
                self.cost_ov = np.zeros(self.num_case)  # var opex [$]
                self.cost_ou = np.zeros(self.num_case)  # use opex [$]
                self.cost_r = np.zeros(self.num_case)  # replacement cost [$]
                self.cost_f = np.zeros(self.num_case)  # fuel cost [$]
                self.cost = np.zeros(self.num_case)  # total cost [$]

                # update other parameters
                self._update_init()

    def _update_init(self):
        """Updates other parameters once essential parameters are complete.

        """
        # update sink parameters
        self.wat_cost = np.zeros(self.num_case)
