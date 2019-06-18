from abc import abstractmethod

import numpy as np

from .Component import Component

# ignore numpy errors
np.seterr(divide='ignore', invalid='ignore')


class FixedComponent(Component):
    """Base class for fixed (intermittent) power components.

    Parameters
    ----------
    capex : float
        Capital expenses [USD/kW]. Depends on size.
    opex_fix : float
        Fixed yearly operating expenses [USD/kW-yr]. Depends on size.
    opex_var : float
        Variable yearly operating expenses [USD/kWh-yr]. Depends on energy
        produced.
    repex : float
        Replacement costs [USD/kW]. Depends on size. Equal to CapEx by default.
    life : float
        Maximum life [yr] before the component is replaced.
    fail_prob : float
        Probability of failure of the component.
    name_solid : str
        Label for the power output. This will be used in generated graphs and
        files.
    color_solid : str
        Hex code (e.g. '#33CC33') of the color for the power output. This will
        be used in generated graphs.
    is_re : bool
        True if the resource is renewable.

    """

    def __init__(self, **kwargs):
        """Initializes the base class."""

        # initialize component
        super().__init__(**kwargs)

    @abstractmethod  # implementation required
    def cost_calc(self, yr_proj, infl):
        """Calculates the cost of the component.

        Parameters
        ----------
        yr_proj : float
            Project lifetime [yr].
        infl : float
            Inflation rate.

        """

    @abstractmethod  # implementation required
    def get_pow(self, hr):
        """Returns the power output [kW] at the specified time [h].

        Parameters
        ----------
        hr : int
            Time [h] in the simulation.

        """
        pass

    @abstractmethod  # implementation required
    def _config(self):
        """Updates other parameters once essential parameters are complete."""

        pass
