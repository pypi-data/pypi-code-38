from abc import abstractmethod

import numpy as np

from .Component import Component

# ignore numpy errors
np.seterr(divide='ignore', invalid='ignore')


class SupplementaryComponent(Component):
    """Base class for components that supplement other components.

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
        self, data, capex, opex_fix, opex_var, opex_use,
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
        return np.zeros(self.num_case)
