import numpy as np

from .LoadComponent import LoadComponent

# ignore numpy errors
np.seterr(divide='ignore', invalid='ignore')


class DesalLoad(LoadComponent):
    """Reverse osmosis desalination plant module.

    Notes
    -----
    This module models only the power [kW] demand of the desalination plant. A
    DesalSink and DesalStorage module should also be initialized to model the
    desalination power sink and water storage respectively.

    """

    def __init__(self, data, **kwargs):
        """Initializes the base class."""

        # initialize component
        super().__init__(
            data, 0.0, 0.0, 0.0, 0.0,
            None, None, 'DesalLoad', '#666666',
            20.0, 0.0, False, False, True, True, **kwargs
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
            self.water = self.data['water']  # load [kW]
        elif isinstance(self.data, np.ndarray):  # pass ndarray
            self.water = self.data

        # convert dataset to 1D array
        self.water = np.ravel(self.water)

        return (np.zeros(self.num_case), np.zeros(self.num_case))

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
        return self.pow

    def _update_init(self):
        """Updates other parameters once essential parameters are complete.

        """
        self.enr_tot = np.zeros(self.num_case)
