import numpy as np
from scipy import constants as const
from .utils import human_readable

def wien_law(x):
    # see Wikipedia, "Wien's displacement law"
    b = 2.897771955e-3
    return b/x

class Wavelength(object):
    """
    Various conversions and useful calculations around laser beams of
    a specific wavelength.
    """
    def __init__(self, lambda0):
        self._lambda0 = lambda0

    @classmethod
    def from_f(cls, f):
        return cls(const.c / f)

    @classmethod
    def from_omega(cls, omega):
        return cls.from_f(omega / (2*np.pi))

    @classmethod
    def from_wavenumber(cls, wn):
        return cls(1.0 / (wn*100.0))

    @classmethod
    def from_eV(cls, eV):
        return cls.from_f(eV * const.e / const.h)

    @classmethod
    def from_temperature(cls, T):
        return cls(wien_law(T))

    @property
    def omega(self):
        return 2*np.pi*self.f

    @property
    def f(self):
        return const.c/self._lambda0

    @property
    def wavelength(self):
        return self._lambda0

    @property
    def lambda0(self):
        return self._lambda0

    @property
    def wavenumber(self):
        return 1.0 / (self._lambda0 * 100.0)

    @property
    def eV(self):
        return const.h * self.f / const.e

    @property
    def temperature(self):
        """
        Temperature of a black body whose wavelength distribution
        peaks at lambda0.
        """
        return wien_law(self._lambda0)

    @property
    def ideal_responsivity(self):
        """
        Calculate the responsivity (A/W) for an ideal photo detector with
        a quantum efficiency of 1.

        Returns
        -------
        :obj:`float`
            The ideal responsivity in A/W
        """
        return 1.0/self.eV


    def quantum_efficiency(self, responsivity):
        """
        Calculate the quantum efficiency for a given responsivity at a specific
        wavelength.

        Parameters
        ----------
        responsivity: :obj:`float`
            The actual responsivity
        
        Returns
        -------
        :obj:`float`
            Fraction of real vs. ideal responsivity.
        """
        return responsivity / self.ideal_responsivity
    

    def shotnoise(self, P):
        """
        Calculate shot noise of a laser beam.

        Parameters
        ----------
        P: :obj:`float`
            The laser power in Watts
       
        Returns
        -------
        :obj:`float`
            The shot noise in W/sqrt(Hz)
        """
        return np.sqrt(2*const.h*self.f*P)


    def RIN(self, P):
        """
        Calculate the relative intensity noise (RIN) of a shot-noise limited
        laser beam.

        Parameters
        ----------
        P: :obj:`float`
            The laser power in Watts
        
        Returns
        -------
        :obj:`float`
            The RIN in 1/sqrt(Hz)
        """
        return self.shotnoise(P) / P

    def __repr__(self):
        return f'Wavelength({human_readable(self.lambda0, "m")})'
