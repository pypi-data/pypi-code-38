import numpy as np

from .LoadComponent import LoadComponent

# ignore numpy errors
np.seterr(divide='ignore', invalid='ignore')


class FESLoad(LoadComponent):
    """Flywheel module.
    This module models only the parasitic load of the FES. An FESEnergy and
    FESPower module should also be initialized to model the energy [kWh] and
    power [kW] of the FES respectively.

    Parameters
    ----------
    enr_module : FESEnergy
        The corresponding enr module for the FES.
    name_line : str
        Label for the load demand. This will be used in generated graphs
        and files.
    color_line : str
        Hex code (e.g. '#33CC33') of the color for the load demand. This
        will be used in generated graphs.

    Other Parameters
    ----------------
    num_case : int
        Number of scenarios to simultaneously simulate. This is set by the
        Control module
    yr_proj : int
        Project lifetime [yr]. This is set by the Control module.
    enr_ratio : float
        Ratio of parasitic load [kWh] to flywheel size [kWh]

    """

    def __init__(self, enr_module, **kwargs):
        """Initializes the base class.

        """
        # base class parameters
        settings = {
            'name_line': 'FES Load',  # label for load
            'color_line': '#666666',  # color for load in powerflow
            'capex': 0.0,  # CapEx [USD/kWh]
            'opex_fix': 0.0,  # size-dependent OpEx [USD/kWh-yr]
            'opex_var': 0.0,  # output-dependent OpEx [USD/kWh-yr]            
            'infl': 0.0,  # no inflation rate needed, must not be None
            'size': 0.0,  # no size needed, must not be None
            'data': 0  # no datasets were used
        }
        settings.update(kwargs)  # replace default settings with input settings

        # initialize base class
        super().__init__(**settings)

        # get energy module
        self.enr_module = enr_module

        # adjustable load parameters
        self.enr_ratio = kwargs.pop('enr_ratio', 0.05)  # par load/size

        # initialize load parameters
        self.load = np.array([])  # parasitic load [kWh]
        self.pow_max = 0  # maximum power [kW]
        self.enr_tot_yr = 0  # consumption per year [kWh]

        # update initialized parameters if essential data is complete
        self._update_config()

    def get_pow(self, hr):
        """Returns the power output [kW] at the specified time [h].

        Parameters
        ----------
        hr : int
            Time [h] in the simulation.

        """
        # charge flywheel with parasitic load
        self.enr_module.pow_par = self.load
        self.enr_module._update_soc(0, hr)

        # get data from the timestep
        return self.pow[hr, :]

    def cost_calc(self):
        """Calculates the cost of the component. This is here for functionality only.

        """
        pass

    def _config(self):
        """Updates other parameters once essential parameters are complete.

        """
        # update load parameters
        self.load = self.enr_module.size*self.enr_ratio
        self.pow_max = self.load  # maximum power [kW]
        self.enr_tot_yr = 8760*self.load  # consumption per year [kWh]

        # generate an expanded array with hourly timesteps
        self.pow = self.load*np.ones((8760, self.num_case))
