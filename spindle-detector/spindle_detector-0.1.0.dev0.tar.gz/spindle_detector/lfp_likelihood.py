from functools import partial

import numpy as np
from sklearn.mixture import GaussianMixture

from spectral_connectivity import Connectivity, Multitaper

_DEFAULT_MULTITAPER_PARAMS = dict(time_halfbandwidth_product=1,
                                  time_window_duration=0.250,
                                  time_window_step=0.250)


def lfp_likelihood(spindle_band_power, spindle_model, no_spindle_model):
    """Estimates the likelihood of being in a spindle state over time given the
     spectral power of the local field potentials (LFPs).

    Parameters
    ----------
    spindle_band_power : ndarray, shape (n_time, n_signals)
    out_spindle_kde : statsmodels.nonparametric.kernel_density.KDEMultivariate
    in_spindle_kde : statsmodels.nonparametric.kernel_density.KDEMultivariate

    Returns
    -------
    log_likelihood : ndarray, shape (n_time, 2)

    """
    not_nan = np.all(~np.isnan(spindle_band_power), axis=1)
    n_time = spindle_band_power.shape[0]

    log_likelihood = np.ones((n_time, 2))

    log_likelihood[not_nan, 0] = no_spindle_model.score_samples(
        np.log(spindle_band_power[not_nan]))

    log_likelihood[not_nan, 1] = spindle_model.score_samples(
        np.log(spindle_band_power[not_nan]))

    return log_likelihood


def fit_lfp_likelihood(spindle_band_power, is_spindle,
                       model=GaussianMixture,
                       model_kwargs=dict(n_components=1)):
    """Fits the likelihood of being in a spindle state over time given the
     spectral power of the local field potentials (LFPs).

    Parameters
    ----------
    spindle_band_power : ndarray, shape (n_time, n_signals)
    is_spindle : bool ndarray, shape (n_time,)
    sampling_frequency : float

    Returns
    -------
    likelihood_ratio : function

    """

    not_nan = np.all(~np.isnan(spindle_band_power), axis=1)
    spindle_model = model(**model_kwargs).fit(
        np.log(spindle_band_power[is_spindle & not_nan] + np.spacing(1)))
    no_spindle_model = model(**model_kwargs).fit(
        np.log(spindle_band_power[~is_spindle & not_nan] + np.spacing(1)))

    return partial(lfp_likelihood, spindle_model=spindle_model,
                   no_spindle_model=no_spindle_model)


def estimate_spindle_band_power(lfps, sampling_frequency,
                                spindle_band=(10, 16), start_time=0.00,
                                multitaper_params=_DEFAULT_MULTITAPER_PARAMS):
    """Estimates the spindle power of each LFP.

    Parameters
    ----------
    lfps : ndarray, shape (n_time, n_signals)
    sampling_frequency : float
    spindle_band : (start_freq, end_freq)
    start_time : float
    multitaper_params : dict

    Returns
    -------
    time : ndarray, shape (n_time_windows,)
    spindle_band_power : ndarray (n_time_windows, n_signals)

    """
    m = Multitaper(lfps, sampling_frequency=sampling_frequency,
                   **multitaper_params)
    c = Connectivity.from_multitaper(m)
    freq_ind = ((c.frequencies > spindle_band[0]) &
                (c.frequencies < spindle_band[1]))
    power = c.power()[..., freq_ind, :]

    return c.time, power
