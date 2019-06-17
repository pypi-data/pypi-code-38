from abc import abstractmethod

import numpy as np

from .Component import Component

# ignore numpy errors
np.seterr(divide='ignore', invalid='ignore')


class StorageComponent(Component):
    """Base class for storage components.

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
    is_re : bool
        True if the resource is renewable.
    is_elec : bool
        True if the resource is electrical.
    is_water : bool
        True if the resource is water.

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

    """

    def __init__(
        self, data, dod_max, eff_c, eff_dc, c_rate,
        capex, opex_fix, opex_var, opex_use,
        name_solid, color_solid, name_line, color_line,
        life, fail_prob, is_fail, is_re, is_elec, is_water,
        **kwargs
    ):
        """Initializes the base class."""

        # initialize component
        super().__init__(
            data, capex, opex_fix, opex_var, opex_use,
            name_solid, color_solid, name_line, color_line,
            life, fail_prob, is_fail, is_re, is_elec, is_water,
            **kwargs
        )

        # store storage parameters
        self.dod_max = dod_max
        self.eff_c = eff_c
        self.eff_dc = eff_dc
        self.c_rate = c_rate

        # initialize storage parameters
        self.volt = np.array([])
        self.curr = np.array([])
        self.soc = np.array([])
        self.is_full = np.array([])
        self.ocv = np.array([])
        self.pow_maxc = np.array([])
        self.pow_maxdc = np.array([])

    def rec_pow(self, pow_rec, hr):
        """Records the power at a specified time step.

        Parameters
        ----------
        pow_rec : ndarray
            Power [kW] to be recorded by component.
        hr : int
            Time [h] in the simulation.

        """
        # calculate statistical noise
        self.noise_calc(hr)

        # record power
        self.use_tot += pow_rec != 0

        # failure probability
        if not self.is_fail:
            noise = 1
        else:
            noise = np.random.rand(self.num_case) > self.fail_prob
        self.noise = noise
        pow_rec = pow_rec*noise

        # record power
        self.pow = pow_rec*(pow_rec >= 0)
        self.enr_tot += pow_rec*(pow_rec >= 0)

        # record additional parameters
        self._rec_pow(pow_rec, hr)

        # apply efficiencies
        pow_dc = pow_rec*(pow_rec >= 0)/self.eff_dc
        pow_c = -pow_rec*self.eff_c*(pow_rec < 0)
        pow_eff = pow_dc-pow_c

        # calculate parameters for next time step
        self.curr, self.volt = self._get_iv(hr, pow_eff)
        self.soc = self.get_soc(hr, self.curr, self.volt)
        self.soc[self.size == 0] = 1
        self.is_full = self.soc >= 1
        self.ocv = self._get_ocv(hr, self.soc)
        self.pow_maxc = self.get_powmaxc(hr)
        self.pow_maxdc = self.get_powmaxdc(hr)
        self.pow_maxc[self.size == 0] = 0
        self.pow_maxdc[self.size == 0] = 0

    @abstractmethod
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

    def get_soc(self, hr, curr, volt):
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

        """
        # get new SOC
        soc_new = self._get_soc(hr, curr, volt)

        # should not go over 1
        soc_new = np.minimum(soc_new, 1)

        # should not go below minimum unless forced to
        is_trn = np.logical_and(
            soc_new <= 1-self.dod_max,  # new SOC is below min SOC and
            self.soc > 1-self.dod_max  # previous SOC is above min
        )
        soc_new[is_trn] = 1-self.dod_max  # set to min SOC

        return soc_new

    @abstractmethod
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

    @abstractmethod
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
        # calculate maximum charge [kW]
        maxc_cap = np.maximum(  # max c due to SOC
            self.size*(1-self.soc),
            0  # prevents negative answers
        )
        maxc_crate = self.c_rate*self.size  # max c due to C-rate
        maxc_main = np.minimum(maxc_cap, maxc_crate)
        maxc_other = self._get_powmaxc(hr)  # other constraints

        return np.minimum(maxc_main, maxc_other)

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
        return np.inf

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
        # calculate maximum charge [kW]
        maxdc_cap = np.maximum(  # max c due to SOC
            self.size*(self.soc-(1-self.dod_max)),
            0  # prevents negative answers
        )
        maxdc_other = self._get_powmaxdc(hr)  # other constraints

        return np.minimum(maxdc_cap, maxdc_other)

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
        return np.inf

    @abstractmethod
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
                self.noise = np.ones(self.num_case)

                # update storage parameters
                self.soc = np.ones(self.num_case)  # SOC
                self.volt = self._get_ocv(-1, np.ones(self.num_case))
                self.curr = np.zeros(self.num_case)
                self.is_full = np.ones(self.num_case)
                self.ocv = self._get_ocv(-1, np.ones(self.num_case))
                self.pow_maxc = np.zeros(self.num_case)
                self.pow_maxdc = self.size*self.dod_max*np.ones(self.num_case)

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
