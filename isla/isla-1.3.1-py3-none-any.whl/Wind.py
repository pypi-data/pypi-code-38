import numpy as np
from scipy.stats import weibull_min
from scipy.interpolate import InterpolatedUnivariateSpline

from .IntermittentComponent import IntermittentComponent

# ignore numpy errors
np.seterr(divide='ignore', invalid='ignore')


class Wind(IntermittentComponent):
    """Wind power plant module.

    Parameters
    ----------
    data : dict
        Dataset. Pass a dict with 'wd_spd' as the key for the wind speed [m/s]
        and 'wd_dir' for the wind direction [deg] (optional). A tracker will
        be assumed to be present if no wind direction data is present. If only
        an ndarray is given, it will be assumed to be the the wind speed.
    dir : float
        Direction faced by the wind turbine [deg]. Set to 'auto' if the
        turbine has a tracker.
    z_anem : float
        Anemometer height [m] for dataset.
    z_hub : float
        Hub height [m].
    z_rough : float
        Surface roughness [m]. Depends on terrain.
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
    life : float
        Lifetime [y] of the component.
    fail_prob : float
        Probability of failure of the component.
    is_fail : bool
        True if failure probabilities should be simulated.

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
    pow_x : ndarray
        The wind speed [m/s] in a set of power output [kW] vs wind speed [m/s]
        data.
    pow_y : ndarray
        The power output [kW] in a set of power output [kW] vs wind speed [m/s]
        data.A

    References
    ----------
    ..[1] Ozbay, A. et. al., "Interference of wind turbines with different
        yaw angles of the upstream wind turbine," 42nd AIAA Fluid Dynamics\
        Conference and Exhibit, 2012.

    """

    def __init__(
        self, data, dir='auto', z_anem=10.0, z_hub=80.0, z_rough=0.0005,
        capex=2000.0, opex_fix=20.0, opex_var=0.0, opex_use=0.0,
        life=20.0, fail_prob=0.01, is_fail=False, **kwargs
    ):
        """Initializes the base class."""

        # initialize component
        super().__init__(
            data, capex, opex_fix, opex_var, opex_use,
            'Wind', '#66CCFF', None, None,
            life, fail_prob, is_fail, True, True, False, **kwargs
        )

        # extract dataset
        if isinstance(self.data, dict):  # pass dict
            self.wd_spd = self.data['wd_spd']  # wind speed [m/s]
            self.wd_dir = self.data.pop('wd_dir', None)  # wind dir [deg]
        elif isinstance(self.data, np.ndarray):  # pass ndarray
            self.wd_spd = self.data
            self.wd_dir = None

        # convert dataset to 1D array
        self.wd_spd = np.ravel(self.wd_spd)
        if self.wd_dir is not None:
            self.wd_dir = np.ravel(self.wd_dir)

        # initialize wind plant parameters
        self.pow_unit = np.array([])

        # get wind farm parameters
        self.dir = dir  # direction of plant [deg]
        self.z_anem = z_anem  # anemometer height [m]
        self.z_hub = z_hub  # hub height [m]
        self.z_rough = z_rough  # surface roughness [m]

        # adjustable wind plant parameters
        self.pow_x = kwargs.pop('pow_x', np.arange(4, 25))  # wind speed [m/s]
        self.pow_y = kwargs.pop(  # corresponding power [kW]
            'pow_y',
            np.array([
                66.3, 152, 280, 457, 690, 978,
                1296, 1598, 1818, 1935, 1980,
                1995, 1999, 2000, 2000, 2000,
                2000, 2000, 2000, 2000, 2000
            ])
        )

        # derivable wind plant parameters
        self.pow_func = InterpolatedUnivariateSpline(
            self.pow_x, self.pow_y, k=1, ext='zeros'  # pow vs speed
        )

        # update initialized parameters if essential data is complete
        self.update_init()

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
        return self.size*self.pow_unit[hr]*np.ones(self.num_case)

    @staticmethod
    def exp_curve(yr, yr_0=2016, **kwargs):
        """Experience curve for Solar PV.
        Returns the cost [USD/kW] at the given year

        Parameters
        ----------
        yr : int
            Index of the year.
        yr_0 : int
            Year where index is set to zero.

        """
        # get regression parameters
        a_sat = kwargs.pop('a_sat', 75)
        a_base = kwargs.pop('a_base', 1.5)
        r = kwargs.pop('r', 0.201)
        a = kwargs.pop('a', 96.22)
        b = kwargs.pop('b', 0.344)

        # calculate cost [USD/kWh]
        cap = a_sat/(1+(a_sat-a_base)/a_base*np.exp(-r*(yr+(yr_0-1990))))
        cost = a*cap**(-b)

    def _update_init(self):
        """Updates other parameters once essential parameters are complete."""

        # adjust wind speed [m/s] for altitude
        spd_adj = (
            self.wd_spd *
            np.log(self.z_hub/self.z_rough) /
            np.log(self.z_anem/self.z_rough)
        )

        # check if direction effects are included
        dir_fc = 1  # direction factor
        if not (self.wd_dir is None or self.dir == 'auto'):

            # power proportional to cos(difference)^3
            dir_fc = np.abs(np.cos(np.deg2rad(
                self.wd_dir-self.dir
            ))**3)

        # calculate power output [kW] per unit size
        self.pow_unit = self.pow_func(spd_adj)*dir_fc/np.max(self.pow_y)
