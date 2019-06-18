import numpy as np

from .LoadComponent import LoadComponent

# ignore numpy errors
np.seterr(divide='ignore', invalid='ignore')


class ThermalLoad(LoadComponent):
    """Thermal Load module.

    Parameters
    ----------
    data : dict or ndarray
        Dataset. Pass a dict with 'load' as the key for the hourly load demand
        [kW] for one year. An ndarray can be passed as well.
    rec_ratio : float
        Heat recovery ratio.
    name_line : str
        Label for the load demand. This will be used in generated graphs
        and files.
    color_line : str
        Hex code (e.g. '#33CC33') of the color for the load demand. This
        will be used in generated graphs.

    Other Parameters
    ----------------
    name_line : str
        Label for the load demand. This will be used in generated graphs
        and files.
    color_line : str
        Hex code (e.g. '#33CC33') of the color for the load demand. This
        will be used in generated graphs.
    num_case : int
        Number of scenarios to simultaneously simulate. This is set by the
        Control module

    """

    def __init__(self, data, rec_ratio=0.4, **kwargs):
        """Initializes the base class."""

        # base class parameters
        settings = {
            'name_line': 'Thermal Load',  # label for load
            'color_line': '#666666',  # color for load in powerflow
            'capex': 0.0,  # CapEx [USD/kWh]
            'opex_fix': 0.0,  # size-dependent OpEx [USD/kWh-yr]
            'opex_var': 0.0,  # output-dependent OpEx [USD/kWh-yr]
            'size': 0.0,  # no size needed, must not be None
            'data': data  # dataset
        }
        settings.update(kwargs)  # replace default settings with input settings

        # initialize base class
        super().__init__(**settings)

        # extract dataset
        if isinstance(self.data, dict):  # pass dict
            self.pow_ld = self.data['load']  # load [kW]
        elif isinstance(self.data, np.ndarray):  # pass ndarray
            self.pow_ld = self.data

        # convert dataset to 1D array
        self.pow_ld = np.ravel(self.pow_ld)

        # adjustable load parameters
        self.rec_ratio = rec_ratio

        # derivable load parameters
        self.pow_max = np.max(self.pow_ld)  # largest power in load [kW]
        self.enr_tot = np.sum(self.pow_ld)  # yearly consumption [kWh]

        # initialize load parameters
        self.pow_red = np.array([])

        # update initialized parameters if essential data is complete
        self._update_config()

    def get_pow(self, hr):
        """Returns the power output [kW] at the specified time [h].

        Parameters
        ----------
        hr : int
            Time [h] in the simulation.

        """
        # record power
        self.pow = self.pow_ld[hr]*np.ones(self.num_case)-self.pow_red

        # get data from the timestep
        return self.pow

    def cost_calc(self, yr_proj, infl):
        """Calculates the cost of the component.

        Parameters
        ----------
        yr_proj : float
            Project lifetime [yr].
        infl : float
            Inflation rate.

        """

    def _config(self):
        """Updates other parameters once essential parameters are complete."""

        # update load parameters
        self.pow_red = np.zeros(self.num_case)
