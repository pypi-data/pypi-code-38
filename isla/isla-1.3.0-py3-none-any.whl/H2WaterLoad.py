import numpy as np

from .LoadComponent import LoadComponent

# ignore numpy errors
np.seterr(divide='ignore', invalid='ignore')


class .H2WaterLoad(LoadComponent):
    """Water generation from electrolysis module.

    Parameters
    ----------
    data : dict or ndarray
        Dataset. Pass a dict with 'water' as the key for the hourly water
        demand [m^3] for one year. An ndarray can be passed as well.
    eff : float
        Efficiency of water production.

    Other Parameters
    ----------------
    name_line : str
        Label for the load demand. This will be used in generated graphs and
        files.
    color_line : str
        Hex code (e.g. '#33CC33') of the color for the load demand. This will
        be used in generated graphs.
    num_case : int
        Number of scenarios to simultaneously simulate. This is set by the
        Control module.

    """

    def __init__(self, data, eff=0.85, **kwargs):
        """Initializes the base class."""

        # base class parameters
        settings = {
            'name_line': 'H2 Water Load',  # label for load
            'color_line': '#666666',  # color for load in powerflow
            'capex': 0.0,  # CapEx [USD/kWh]
            'opex_fix': 0.0,  # size-dependent OpEx [USD/kWh-yr]
            'opex_var': 0.0,  # output-dependent OpEx [USD/kWh-yr]
            'infl': 0.0,  # no inflation rate needed, must not be None
            'size': 0.0,  # no size needed, must not be None
            'data': data  # dataset
        }
        settings.update(kwargs)  # replace default settings with input settings

        # initialize base class
        super().__init__(**settings)

        # extract dataset
        if isinstance(self.data, dict):  # pass dict
            self.vol_wat = self.data['water']  # load [kW]
        elif isinstance(self.data, np.ndarray):  # pass ndarray
            self.vol_wat = self.data

        # calculate corresponding load
        self.pow_ld = 2e3*eff*self.vol_wat

        # derivable load parameters
        self.pow_max = np.max(self.pow_ld)  # largest power in load [kW]
        self.enr_tot = np.sum(self.pow_ld)  # yearly consumption [kWh]

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
        self.pow = self.pow_ld[hr]*np.ones(self.num_case)

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
        pass

    def _config(self):
        """Updates other parameters once essential parameters are complete."""

        pass
