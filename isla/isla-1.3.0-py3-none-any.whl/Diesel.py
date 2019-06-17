import numpy as np

from .Fuel import Fuel

# ignore numpy errors
np.seterr(divide='ignore', invalid='ignore')


class Diesel(Fuel):
    """Base class for diesel.

    Parameters
    ----------
    cost : float or callable
        Cost per unit [$/L] of fuel. Can be a callable function that returns
        fuel cost starting from year zero to end of project lifetime.
    fl_infl : float
        Inflation rate of fuel.
    den : float
        Mass per unit [kg/L] of the fuel.
    lhv : float
        Lower heating value [MJ/kg] of the fuel.
    cost_ret : float or callable
        Savings per unit [$/u] of fuel produced. Can be a callable function
        that returns fuel cost starting from year zero to end of project
        lifetime.

    """

    def __init__(self, cost=0.9, fl_infl=0.03, den=0.82, lhv=43.2, cost_ret=0):
        """Initializes the base class."""

        # initialize base class
        super().__init__(
            cost, fl_infl, den, lhv, cost_ret,
            'Diesel', '#000000', False
        )

    def _rec_fl(self, fl_rec, hr):
        """Records fuel use at a specified time step.

        Parameters
        ----------
        fl_rec : ndarray
            Fuel use [u] to be recorded.
        hr : int
            Time [h] in the simulation.

        """

        # default
        super()._rec_fl(fl_rec, hr)
