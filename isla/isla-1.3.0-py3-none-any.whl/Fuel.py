from abc import abstractmethod

import numpy as np

# ignore numpy errors
np.seterr(divide='ignore', invalid='ignore')


class Fuel(object):
    """Base class for fuel.

    Parameters
    ----------
    cost : float or callable
        Cost per unit [$/u] of fuel. Can be a callable function that returns
        fuel cost starting from year zero to end of project lifetime.
    fl_infl : float
        Inflation rate of fuel.
    den : float
        Mass per unit [kg/u] of the fuel.
    lhv : float
        Lower heating value [MJ/kg] of the fuel.
    cost_ret : float or callable
        Savings per unit [$/u] of fuel produced. Can be a callable function
        that returns fuel cost starting from year zero to end of project
        lifetime.
    name_solid : str
        Label used for the power output. Appears as a solid area in powerflows
        and as a header in .csv files. Usually the name of the component.
    color_solid : str
        Hex code (e.g. '#33CC33') of the color corresponding to name_solid.
        Appears in the solid area in powerflows.
    is_re : bool
        True if the resource is renewable.

    """

    def __init__(
        self, cost, fl_infl, den, lhv, cost_ret,
        name_solid, color_solid, is_re
    ):
        """Initializes the base class."""

        # store fuel parameters
        self.cost = cost
        self.fl_infl = fl_infl
        self.den = den  # density
        self.lhv = lhv  # LHV
        self.cost_ret = cost_ret  # savings
        self.name_solid = name_solid  # name on plot
        self.color_solid = color_solid  # color on plot
        self.is_re = is_re  # True if renewable

        # initialize fuel parameters
        self.fl_tot = 0  # total fuel used
        self.fl_ret = 0  # total fuel created
        self.fl_use = 0  # times that fuel is used
        self.cost_f = 0  # total cost of fuel
        self.num_case = None  # number of cases to simu

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
        self.fl_tot = np.zeros(num_case)  # total fuel used
        self.fl_ret = np.zeros(num_case)  # total fuel created
        self.fl_use = np.zeros(num_case)  # times that fuel is used
        self.cost_f = np.zeros(num_case)  # total cost of fuel

    def rec_fl(self, fl_rec, hr):
        """Records fuel use at a specified time step.

        Parameters
        ----------
        fl_rec : ndarray
            Fuel use [u] to be recorded.
        hr : int
            Time [h] in the simulation.

        """
        # record additional parameters
        self._rec_fl(fl_rec, hr)

        # record fuel used
        self.fl_tot += fl_rec*(fl_rec > 0)
        self.fl_ret += fl_rec*(fl_rec < 0)
        self.fl_use += fl_rec != 0

    @abstractmethod
    def _rec_fl(self, fl_rec, hr):
        """Records fuel use at a specified time step.

        Parameters
        ----------
        fl_rec : ndarray
            Fuel use [u] to be recorded.
        hr : int
            Time [h] in the simulation.

        """
        pass

    def cost_calc(self, yr_proj, infl):
        """Calculates the cost of fuel.

        Parameters
        ----------
        yr_proj : float
            Project lifetime [yr].
        infl : float
            Inflation rate.

        """
        # calculate costs
        self.cost_f = self._cost_calc(yr_proj, infl)

    def fl_use_calc(self, yr_proj, infl):
        """Default method of solving fuel use costs.

        Parameters
        ----------
        yr_proj : float
            Project lifetime [yr].
        infl : float
            Inflation rate.

        """
        def annfl_func(i):
            """Annunity factor for fuel"""
            return ((1+self.fl_infl)/(1+infl))**i

        # fuel costs [$]
        if callable(self.cost):
            cost_f = self.fl_tot*np.sum(
                self.cost(i)*annfl_func(i)
                for i in np.arange(1, yr_proj+1)
            )
        else:
            cost_f = self.fl_tot*self.cost*np.sum(
                    ((1+self.fl_infl)/(1+infl)) **
                    np.arange(1, yr_proj+1)
                )

        return cost_f

    def fl_ret_calc(self, yr_proj, infl):
        """Default method of solving fuel production savings.

        Parameters
        ----------
        yr_proj : float
            Project lifetime [yr].
        infl : float
            Inflation rate.

        """
        def annfl_func(i):
            """Annunity factor for fuel"""
            return ((1+self.fl_infl)/(1+infl))**i

        # fuel savings [$]
        if callable(self.cost):
            save_f = self.fl_ret*np.sum(
                self.cost_ret(i)*annfl_func(i)
                for i in np.arange(1, yr_proj+1)
            )
        else:
            save_f = self.fl_ret*self.cost_ret*np.sum(
                    ((1+self.fl_infl)/(1+infl)) **
                    np.arange(1, yr_proj+1)
                )

        return save_f

    def _cost_calc(self, yr_proj, infl):
        """Calculates the cost of fuel.

        Parameters
        ----------
        yr_proj : float
            Project lifetime [yr].
        infl : float
            Inflation rate.

        Notes
        -----
        This function can be modified by the user.

        """
        cost_f = self.fl_use_calc(yr_proj, infl)
        save_f = self.fl_ret_calc(yr_proj, infl)

        return cost_f-save_f
