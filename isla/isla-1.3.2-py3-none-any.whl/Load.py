import numpy as np
from scipy.stats import norm

from .LoadComponent import LoadComponent

# ignore numpy errors
np.seterr(divide='ignore', invalid='ignore')


class Load(LoadComponent):
    """Load module.

    Parameters
    ----------
    data : dict or ndarray
        Dataset. Pass a dict with 'load' as the key for the hourly load demand
        [kW] for one year. An ndarray can be passed as well.

    Other Parameters
    ----------------
    num_case : int
        Number of scenarios to simultaneously simulate. This is set by the
        Control module.

    """

    def __init__(self, data, **kwargs):
        """Initializes the base class."""

        # initialize component
        super().__init__(
            data, 0.0, 0.0, 0.0, 0.0,
            None, None, 'Load', '#666666',
            20.0, 0.0, False, False, True, False, **kwargs
        )

        # update initialized parameters if essential data is complete
        self.update_init()

    def _load_derive(self):
        """Derives energy parameters from dataset.

        Returns
        -------
        pow_max : ndarray
            Maximum power in the load.
        enr_tot : ndarray
            Total power in the load.

        Notes
        -----
        This function can be modified by the user.

        """
        # extract dataset
        if isinstance(self.data, dict):  # pass dict
            self.pow_ld = self.data['load']  # load [kW]
        elif isinstance(self.data, np.ndarray):  # pass ndarray
            self.pow_ld = self.data

        # convert dataset to 1D array
        self.pow_ld = np.ravel(self.pow_ld)

        return (np.max(self.pow_ld), np.sum(self.pow_ld))

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
        return self.pow_ld[hr]*np.ones(self.num_case)

    def _update_init(self):
        """Initalize other parameters for the component."""

        pass
