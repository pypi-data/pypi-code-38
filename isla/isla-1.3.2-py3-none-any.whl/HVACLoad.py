import numpy as np

from .LoadComponent import LoadComponent

# ignore numpy errors
np.seterr(divide='ignore', invalid='ignore')


class HVACLoad(LoadComponent):
    """Load module.

    Parameters
    ----------
    data : dict or ndarray
        Dataset. Pass a dict with 'temp' as the key for the hourly temperature
        [K] for one year. An ndarray can be passed as well.
    ig_int : float
        Internal gain [W/m^2].
    ua_int : float
        y-intercept [W/m^2] of the UA line as a function of temperature [K].
    ua_slp : float
        Slope [W/m^2-K] of the UA line as a function of temperature [K].
    temp_set : float
        Setpoint temperature [K].
    cool_const : float
        Constant cooling gain [W/m^2].
    shade_cf : float
        Shading coefficient.
    area_cond : float
        Conditioned floor area [m^2].
    area_win : ndarray or float
        Area [m^2] of each window.
    shgf_ave : ndarray or float
        Corresponding solar heat gain factor [W/m^2] of each window.

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
    yr_proj : int
        Project lifetime [yr]. This is set by the Control module.

    References
    ----------
    ..[1] White, J., Reichmuth, H., "Simplified method for predicting building
      energy consumption using average monthly temperatures," Energy
      Conversion Engineering Conference, 1996.

    """

    def __init__(
        self, data, ig_int=0.09295, ua_int=0.4647,
        ua_slp=-0.01952, temp_set=294, cool_const=0.06971,
        shade_cf=0.75, area_cond=200, area_win=25,
        shgf_ave=100, **kwargs
    ):
        """Initializes the base class.

        """
        # base class parameters
        settings = {
            'name_line': 'Load',  # label for load
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
            self.temp = self.data['temp']  # load [kW]
        elif isinstance(self.data, np.ndarray):  # pass ndarray
            self.temp = self.data

        # adjustable load parameters
        self.ig_int = ig_int  # internal gain [W/m^2]
        self.ua_int = ua_int  # UA gain y-int [W/m^2]
        self.ua_slp = ua_slp  # UA gain slope [W/m^2-K]
        self.temp_set = temp_set  # setpoint temperature [K]
        self.cool_const = cool_const  # const cooling gain [W/m^2]
        self.shade_cf = shade_cf  # shading coefficient
        self.area_cond = area_cond  # cond floor area [m^2]
        self.area_win = area_win  # window area
        self.shgf_ave = shgf_ave  # SHGF at Jul 21 [W/m^2]

        # calculate load [kW]
        self._cool_calc()

        # derivable load parameters
        self.pow_max = np.max(self.load)  # largest power in load [kW]
        self.enr_tot_yr = np.sum(self.load)  # yearly consumption [kWh]

        # update initialized parameters if essential data is complete
        self._update_config()

    def get_pow(self, hr):
        """Returns the power output [kW] at the specified time [h].

        Parameters
        ----------
        hr : int
            Time [h] in the simulation.

        """
        # get data from the timestep
        return self.pow[hr, :]

    def cost_calc(self):
        """Calculates the cost of the component. This is here for functionality only.

        """
        pass

    def _config(self):
        """Updates other parameters once essential parameters are complete.

        """
        # generate an expanded array with hourly timesteps
        self.pow = np.repeat(
            self.load.reshape((8760, 1)),
            self.num_case, axis=1
        )

    def _cool_calc(self):
        """Calculates the required cooling load.

        """
        # calculate solar gain [W/m^2]
        gain_sol = (
            self.shade_cf/self.area_cond *
            np.sum(self.area_win*self.shgf_ave)
        )

        # adjust slope of UA line
        ua_slp_adj = self.ua_slp*(self.ua_int+gain_sol)/self.ua_int

        # solve for coefficients of retained gain curve
        s = self.temp_set  # copy
        a = np.array([  # coefficient matrix
            [0, 0, 0, 1],
            [s**3, s**2, s, 1],
            [0, 0, 1, 0],
            [3*s**2, 2*s, 1, 0]
        ])
        b = np.array([
            [self.ig_int-self.cool_const],
            [ua_slp_adj*s+self.ig_int],
            [0],
            [ua_slp_adj]
        ])
        coeff = np.linalg.solve(a, b)

        # evaluate retained gain curve
        def ret_func(t):
            """Returns the retained gain curve.

            Parameters
            ----------
            t : ndarray
                Temperature [K] for a year.

            """
            return coeff[0]*t**3+coeff[1]*t**2+coeff[2]*t+coeff[3]
        ret_curve = ret_func(self.temp)

        # calculate cooling load [kW]
        self.load = (self.ig_int-ret_curve)*self.area_cond/1e3
