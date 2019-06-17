import numpy as np

from .AdjustComponent import AdjustComponent


class Biomass(AdjustComponent):

    def __init__(self, **kwargs):
        """Simulates the operation of a diesel plant

        """
        # set defaults
        settings = {
            'name_solid': 'Biomass',
            'color_solid': '#00CC33',
            'capex': 2000.0,
            'opex_fix': 500.0,
            'opex_var': 0.05,
            'life': 10,
            'data': 0
        }
        settings.update(kwargs)  # replace with input settings

        # initialize base class
        super().__init__(**settings)

        # get keyword arguments
        self.fl_cost = kwargs.pop('fl_cost', 0.4)  # USD/kg
        self.fl_eff = kwargs.pop('fl_eff', 0.45)  # kg/kWh

        # try to update
        self._update_config()

    def calc_pow(self, pow_req):
        """Calculate the output power given the minimum
        required power

        Parameters
        ----------
        pow_req : ndarray
            Minimum required power

        Returns
        -------
        ndarray
            The actual power output of the diesel plant

        """
        # cannot generate power higher than size
        pow_gen = np.minimum(self.size, pow_req)

        return pow_gen

    def rec_pow(self, pow_rec, hr):
        """Records the power in the power matrix

        Parameters
        ----------
        pow_rec : ndarray
            Power to be recorded into power matrix
        hr : int
            Timestep in simulations

        """
        self.pow[hr, :] = pow_rec

    def cost_calc(self):
        """Calculates the costs accumulated by this resource

        """
        # capital costs
        self.cost_c = self.capex*self.size

        # operating costs
        opex_fix = (
            self.opex_fix*self.size *
            np.sum(1/(1+self.infl)**np.arange(1, self.yr_proj+1))
        )
        opex_var = (
            self.opex_var*np.sum(self.pow, axis=0) *
            np.sum(1/(1+self.infl)**np.arange(1, self.yr_proj+1))
        )
        self.cost_o = opex_fix+opex_var

        # replacement costs
        rep_freq = self.life*np.ones(self.num_case)
        disc_rep = np.zeros(self.num_case)  # sum of discount factors
        for i in range(0, self.num_case):
            disc_rep[i] = np.sum(
                1/(1+self.infl) **
                np.arange(0, self.yr_proj, rep_freq[i])[1:]  # remove 0
            )
        self.cost_r = self.size*self.repex*disc_rep

        # fuel costs
        self.cost_f = (
            np.sum(self.pow, axis=0)*self.fl_eff*self.fl_cost *
            np.sum((1/(1+self.infl))**np.arange(1, self.yr_proj+1))
        )

        # total cost
        self.cost = self.cost_c+self.cost_o+self.cost_r+self.cost_f

    def _config(self):
        """Updates stored values if the number of cases,
        length of simulation, size of resource,
        or inflation is changed.

        """
        pass
