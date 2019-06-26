import numpy as np
import pandas as pd
from scipy.optimize import curve_fit
from ..plots import beam_profile
from ..conversion.utils import human_readable

def _get_beam_data(filename, separator):
    """Using pandas to read csv files containing 2-3 columns of data, with
    header and column name lines denoted by '#'. First column containing
    position data in cm and the following beam diameter data in um for x and/or
    y direction.
    """
    df = pd.read_csv(filename, comment='#', index_col=0,
                     sep=separator, header=None)
    # convert from cm and µm to meters
    df.index *= 0.01
    df *= 0.5e-6  # also convert diameter to radius
    df.rename(columns={1: 'saggital', 2: 'tangential'}, inplace=True)
    return df


def fit_beam_data(data,
                  guess_w0=300e-6,
                  guess_z0=0.0,
                  wavelength=1064e-9,
                  plot=True,
                  separator='\t'
                  ):
    """Fit beam data obtained from a beam analyzer to the gaussian
    beam model using non-linear least squares. Returns waist size and position
    with corresponding standard deviations in X and/or Y direction. Optionally
    plots the datapoints and beam width function with fit parameters.

    Parameters
    ----------
    data: :obj:`str` or :obj:`DataFrame`
        Either the filename of a text file containing the measured data
        (header and column name lines denoted by '#';
        position data in cm in the 1st column,
        1/e^2 (13%) diameter in µm for X/Y direction in the 2nd and 3rd column),
        or a :obj:`DataFrame` following the same convention (position as index).
    guess_w0: :obj:`float`
        Initial estimate of the beam waist in m (default: 300um)
    guess_z0: :obj:`float`
        Initial estimate of the waist position in m (default: 0)
    wavelength: :obj:`float`
        Wavelength of the light in m (default: 1064nm)
    plot: :obj:`bool`
        Create plot after fitting (default: True)
    separator: :obj:`str`
        Separator between columns in measurement file (default: '\\t')

    Returns
    -------
    results: :obj:`dict` of :obj:`GaussianBeam`
        A dictionary containing :obj:`GaussianBeam` object for each fit result,
        with descriptive labels as dictionary keys.

    """
    # Maik, 18/05/2018
    if isinstance(data, str):
        data = _get_beam_data(data, separator)

    initial_guess = ([guess_w0, guess_z0])
    fit_function = lambda z, w0, z0: GaussianBeam.from_waist(w0, z0, wavelength).get_profile(z)

    results = {}
    for column in data:
        popt, pcov = curve_fit(fit_function,
                               data.index,
                               data[column],
                               bounds=([0, -10], [10e-3, 10]),
                               p0=initial_guess)
        results[column] = GaussianBeam.from_waist(popt[0], popt[1], wavelength)
        perr = np.sqrt(np.diag(pcov))
        print(u'Results for "{plane}" plane: ({w0:.1f} ± {w0s:.1f})µm @' \
              u' ({z0:.3f} ± {z0s:.3f})cm'.format(
            plane=column, w0=popt[0] * 1e6, w0s=perr[0] * 1e6,
            z0=popt[1] * 1e2, z0s=perr[1] * 1e2)
        )
    if plot:
        beam_profile(results, data)

    return results


class GaussianBeam(object):
    """
    Represents a complex gaussian beam parameter
    """

    def __init__(self, q=0 + 1j, wavelength=1.064e-6):
        self._lambda = wavelength
        self._q = q

    @classmethod
    def from_waist(cls, w0, z0, wavelength=1.064e-6):
        return cls(1j * (np.pi * w0 ** 2 / wavelength) - z0, wavelength)

    def propagate(self, d):
        """
        Returns the beam parameter after free-space propagation of d
        """
        return GaussianBeam(self._q + d)

    def get_profile(self, zpoints):
        """
        Returns the beam width at points zpoints along the beam axis.
        """
        quotient = (self._q.real + zpoints) / self._q.imag
        return self.w0 * np.sqrt(1 + quotient ** 2)

    @property
    def w0(self):
        return np.sqrt(self._q.imag * self._lambda / np.pi)

    @property
    def z0(self):
        return -self._q.real

    @property
    def zR(self):
        return self._q.imag

    @property
    def R(self):
        qi = 1 / self._q
        if qi.real == 0:
            return np.infty
        return 1 / (qi.real)

    @property
    def w(self):
        return self.get_profile(0.0)

    @property
    def divergence(self):
        """
        Calculate beam divergence (in radian).
        """
        return np.atan(self._lambda / np.pi / self.w0)

    def __repr__(self):
        return "w0={w0} @ z0={z0}".format(
            w0=human_readable(self.w0, 'm'), z0=human_readable(self.z0, 'm'))
