import numpy as np

from .IntermittentComponent import IntermittentComponent

# ignore numpy errors
np.seterr(divide='ignore', invalid='ignore')


class CombBase(IntermittentComponent):
    """Base load module of combustion power plants.

    Parameters
    ----------
    dp_module : CombPeak object
        Peaking module of the comustion power plant.

    Notes
    -----
    This module models only the minimum power output of a combustion power
    plant. A CombPeak module should also be initialized.

    """

    def __init__(self, dp_module, **kwargs):
        """Initializes the base class."""

        # initialize component
        super().__init__(
            None, 0.0, 0.0, 0.0, 0.0,
            dp_module.name_solid, dp_module.color_solid, None, None,
            dp_module.life, dp_module.fail_prob, dp_module.is_fail,
            dp_module.is_re, True, False, **kwargs
        )

        # get dispatchable module
        self.dp_module = dp_module

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
        return (0, 0, 0, 0, 0, 0)

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
        return self.dp_module.size*self.dp_module.min_ratio
