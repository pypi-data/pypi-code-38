from abc import abstractmethod

import numpy as np

# ignore numpy errors
np.seterr(divide='ignore', invalid='ignore')


class Component(object):
    """Base class for energy components.

    Parameters
    ----------
    data : ndarray
        Dataset. Set to zero if no dataset is required.
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
        Replacement costs [$/kW(h)]. Depends on size. Equal to CapEx by
        default. Can be a callable function that returns replacement costs
        starting from year zero to end of project lifetime.
    num_case : int
        Number of scenarios to simultaneously simulate. This is set by the
        Control module.
    size : int
        Size of the component [kW]. This is set by the Control module.

    """

    def __init__(
        self, data, capex, opex_fix, opex_var, opex_use,
        name_solid, color_solid, name_line, color_line,
        life, fail_prob, is_fail, is_re, is_elec, is_water,
        **kwargs
    ):
        """Initializes the base class."""

        # store essential parameters
        self.data = data  # dataset
        self.capex = capex  # capital cost [$/kW(h)]
        self.opex_fix = opex_fix  # fixed operating cost [$/kW(h) y]
        self.opex_var = opex_var  # variable operating cost [$/kWh y]
        self.opex_use = opex_use  # usage based operating cost [$/h y]
        self.name_solid = name_solid  # label for solid area in powerflow
        self.color_solid = color_solid  # display as solid area in powerflow
        self.name_line = name_line  # label for line in powerflow
        self.color_line = color_line  # display as line in powerflow
        self.life = life  # component lifetime
        self.fail_prob = fail_prob  # probability of failure
        self.is_fail = is_fail  # True if using failure prob
        self.is_re = is_re  # True if renewable
        self.is_elec = is_elec  # True if electrical
        self.is_water = is_water  # True if water

        # adjustable essential parameters
        self.num_case = kwargs.pop('num_case', None)  # num of cases to simu
        self.size = kwargs.pop('size', None)  # size of component [kW(h)]

        # initialize component parameters
        self.pow = np.array([])  # instantaneous power [kW] of component
        self.enr_tot = np.array([])  # total energy output [kWh] of component
        self.use_tot = np.array([])  # number of times used
        self.noise = np.array([])

        # adjustable economic parameters
        self.repex = kwargs.pop('repex', self.capex)  # replacement [USD/kW(h)]

        # initialize cost parameters
        self.cost_c = np.array([])  # capital cost [$] of component
        self.cost_of = np.array([])  # fixed operating cost [$] of component
        self.cost_ov = np.array([])  # var operating cost [$] of component
        self.cost_ou = np.array([])  # use operating cost [$] of component
        self.cost_r = np.array([])  # replacement cost [$] of component
        self.cost_f = np.array([])  # fuel cost [$] of component
        self.cost = np.array([])  # total cost [$] of component

        # initialize statistical parameters
        self.stat_dict = {}  # dict with statistical parameters

    def set_num(self, num_case):
        """Changes the number of cases to simulate. Used by the Control module.

        Parameters
        ----------
        num_case : int
            Number of scenarios to simultaneously simulate. This is set by the
            Control module.

        """
        # set number of cases
        self.num_case = num_case

        # update initialized parameters if essential data is complete
        self.update_init()

    def set_size(self, size):
        """Changes the size of the components. Used by the Control module.

        Parameters
        ----------
        size : int
            Size of the component [kWh]. This is set by the Control module.

        """
        # set sizes [kW] or [kWh]
        self.size = np.atleast_1d(size)  # must be in array form

        # update initialized parameters if essential data is complete
        self.update_init()

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
        # get power
        pow = self._calc_pow(pow_req, hr)

        return pow

    def _calc_pow(self, pow_req, hr):
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
        pow_gen : ndarray
            The power output [kW] of the component.

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

        # store into parameters
        self.cost_c = cost_c
        self.cost_of = cost_of
        self.cost_ov = cost_ov
        self.cost_ou = cost_ou
        self.cost_r = cost_r
        self.cost_f = cost_f

        # calculate total costs
        self.cost = cost_c+cost_of+cost_ov+cost_ou+cost_r+cost_f

    def capex_calc(self):
        """Default method of solving capital costs.

        Returns
        -------
        cost_c : ndarray
            Total capital cost [$] of the component.

        """
        # capital costs [USD], size [kW] based
        if callable(self.capex):  # if experience curve is given
            cost_c = np.atleast_1d(self.capex(0)*self.size)
        else:  # if fixed value is given
            cost_c = self.capex*self.size

        return cost_c

    def opex_fix_calc(self, yr_proj, infl):
        """Default method of solving fixed operating costs.

        Parameters
        ----------
        yr_proj : float
            Project lifetime [yr].
        infl : float
            Inflation rate.

        Returns
        -------
        cost_of : ndarray
            Total fixed operating cost [$] of the component.

        """
        def ann_func(i):
            """Annunity factor"""
            return 1/(1+infl)**i

        # fixed operating costs [USD], size [kW] based
        if callable(self.opex_fix):
            cost_of = self.size*np.sum(
                self.opex_fix(i)*ann_func(i)
                for i in np.arange(1, yr_proj+1)
            )
        else:
            cost_of = self.opex_fix*self.size*np.sum(
               1/(1+infl)**np.arange(1, yr_proj+1)
            )

        return cost_of

    def opex_var_calc(self, yr_proj, infl):
        """Default method of solving variable operating costs.

        Parameters
        ----------
        yr_proj : float
            Project lifetime [yr].
        infl : float
            Inflation rate.

        Returns
        -------
        cost_ov : ndarray
            Total variable operating cost [$] of the component.

        """
        def ann_func(i):
            """Annunity factor"""
            return 1/(1+infl)**i

        # variable operating costs [USD], output [kWh] based
        if callable(self.opex_var):
            cost_ov = self.enr_tot*np.sum(
                self.opex_var(i)*ann_func(i)
                for i in np.arange(1, yr_proj+1)
            )
        else:
            cost_ov = self.opex_var*self.enr_tot*np.sum(
               1/(1+infl)**np.arange(1, yr_proj+1)
            )

        return cost_ov

    def opex_use_calc(self, yr_proj, infl):
        """Default method of solving usage-based operating costs.

        Parameters
        ----------
        yr_proj : float
            Project lifetime [yr].
        infl : float
            Inflation rate.

        Returns
        -------
        cost_ou : ndarray
            Total usage operating cost [$] of the component.

        """
        def ann_func(i):
            """Annunity factor"""
            return 1/(1+infl)**i

        # variable operating costs [USD], output [kWh] based
        if callable(self.opex_var):
            cost_ou = self.use_tot*self.size*np.sum(
                self.opex_hr(i)*ann_func(i)
                for i in np.arange(1, yr_proj+1)
            )
        else:
            cost_ou = self.opex_use*self.use_tot*self.size*np.sum(
               1/(1+infl)**np.arange(1, yr_proj+1)
            )

        return cost_ou

    def repex_calc(self, yr_proj, infl, rep_per):
        """Default method of solving replacement costs.

        Parameters
        ----------
        yr_proj : float
            Project lifetime [yr].
        infl : float
            Inflation rate.
        rep_per : float
            Replacement period [yr]

        Returns
        -------
        cost_r : ndarray
            Total replacement cost [$] of the component.

        """
        def ann_func(i):
            """Annunity factor"""
            return 1/(1+infl)**i

        # replace with array
        if not isinstance(rep_per, (np.ndarray, list)):
            rep_per = rep_per*np.ones(self.num_case)

        # replacement costs [USD], size [kW] based
        if callable(self.repex):
            repex = np.zeros(self.num_case)  # initialize replacement costs
            for i in range(0, self.num_case):
                repex[i] = np.sum(  # output [kWh] based
                    self.repex(j)*ann_func(j)
                    for j in np.arange(0, yr_proj, rep_per[i])
                )-self.repex(0)*ann_func(0)  # no replacement at time zero
        else:
            disc_rep = np.zeros(self.num_case)  # initialize sum of ann factors
            for i in range(0, self.num_case):
                disc_rep[i] = np.sum(
                    1/(1+infl) **
                    np.arange(0, yr_proj, rep_per[i])[1:]  # remove yr 0
                )
            repex = disc_rep*self.repex
        cost_r = self.size*repex

        return cost_r

    def _cost_calc(self, yr_proj, infl):
        """Returns the costs of the component.

        Parameters
        ----------
        yr_proj : float
            Project lifetime [yr].
        infl : float
            Inflation rate.

        Returns
        -------
        cost_c : ndarray
            Total capital cost [$] of the component.
        cost_of : ndarray
            Total fixed operating cost [$] of the component.
        cost_ov : ndarray
            Total variable operating cost [$] of the component.
        cost_ou : ndarray
            Total usage operating cost [$] of the component.
        cost_r : ndarray
            Total replacement cost [$] of the component.
        cost_f : ndarray
            Total fuel cost of the component [$]

        Notes
        -----
        This function can be modified by the user.

        """
        cost_c = self.capex_calc()
        cost_of = self.opex_fix_calc(yr_proj, infl)
        cost_ov = self.opex_var_calc(yr_proj, infl)
        cost_ou = self.opex_use_calc(yr_proj, infl)
        cost_r = self.repex_calc(yr_proj, infl, self.life)

        return (cost_c, cost_of, cost_ov, cost_ou, cost_r, 0)

    def get_pow(self, hr):
        """Returns the power output [kW] at the specified time [h].

        Parameters
        ----------
        hr : int
            Time [h] in the simulation.

        Returns
        -------
        pow : ndarray
            Power [kW] at the current timestep.

        """
        # calculate statistical noise
        self.noise_calc(hr)

        # get power
        pow = self._get_pow(hr)

        # record power
        self.pow = pow
        self.enr_tot += pow
        self.use_tot += pow != 0

        return self.pow

    def _get_pow(self, hr):
        """Returns the power output [kW] at the specified time [h].

        Parameters
        ----------
        hr : int
            Time [h] in the simulation.

        Returns
        -------
        pow : ndarray
            Power [kW] at the current timestep.

        Notes
        -----
        This function can be modified by the user.

        """
        pass

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

        # record additional parameters
        self._rec_pow(pow_rec, hr)

        # record power
        self.pow = pow_rec
        self.enr_tot += pow_rec
        self.use_tot += pow_rec != 0

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

    def noise_calc(self, hr):
        """Generates noise based on statistical data.

        Parameters
        ----------
        hr : int
            Time [h] in the simulation.

        Returns
        -------
        noise : ndarray
            Factor to be multiplied to component power.

        """

        if not self.is_fail:
            noise = 1
        else:
            noise = np.random.rand(self.num_case) > self.fail_prob

        # update noise
        self.noise = noise

    def update_init(self):
        """Updates initialized parameters once size and num_case are given."""

        # check if all essential parameters are in
        if (self.num_case is not None and self.size is not None):

            # prevents optimization errors
            if self.size.size == self.num_case:

                # update component parameters
                self.pow = np.zeros(self.num_case)  # instantaneous power [kW]
                self.enr_tot = np.zeros(self.num_case)  # tot energy out [kWh]
                self.use_tot = np.zeros(self.num_case)  # tot energy out [kWh]
                self.noise = np.ones(self.num_case)

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
        """Initalize other parameters for the component."""
        pass
